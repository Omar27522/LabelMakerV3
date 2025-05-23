"""
Frame-based implementation of the Create Label functionality.
This module provides a frame that can be embedded in the welcome window
instead of opening a separate dialog.
"""

import os
import sys
import logging
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import pyautogui
import subprocess
import pyperclip
import platform

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_title_section, create_colored_button, create_form_field_group
from src.utils.barcode_operations import process_barcode
from src.utils.sheets_operations import write_to_google_sheet
from src.utils.file_utils import get_central_log_file_path, ensure_directory_exists, directory_exists, file_exists, find_files_by_sku
from src.utils.log_manager import log_shipping_event
from src.utils.text_context_menu import add_context_menu
from src.utils.jdl_automation import JDLAutomation
from src.utils.receive import ReceiveManager
from src.utils.exceptions import ExceptionsManager
from src.ui.window_transparency import TransparencyManager, create_transparency_toggle_button
from src.ui.returns_data_dialog import ReturnsDataDialog
from src.ui.container_card_dialog import ContainerCardDialog
from src.ui.exceptions_dialog import ExceptionsDialog

# Configure logging
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(logs_dir, 'label_maker.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CreateLabelFrame(tk.Frame):
    """Frame-based implementation of the Create Label functionality"""
    
    def __init__(self, parent, config_manager, update_label_count_callback, return_to_welcome_callback):
        """
        Initialize the Create Label frame
        
        Args:
            parent: Parent widget
            return_to_welcome_callback: Callback function to return to welcome screen
            config_manager: The application's configuration manager
        """
        # Flag to track initialization state to prevent flickering
        self._initializing = True
        
        # Flag to track which phase of the receive workflow we're in
        self._receive_workflow_phase = 0  # 0=not started, 1=after first browser tab, 2=after container card
        
        super().__init__(parent, bg='white')
        self.return_to_welcome_callback = return_to_welcome_callback
        self.config_manager = config_manager
        self.update_label_count_callback = update_label_count_callback
        
        # Initialize variables
        self.tracking_var = tk.StringVar()
        self.sku_var = tk.StringVar()
        self.mirror_print_var = tk.BooleanVar(value=config_manager.settings.mirror_print if hasattr(config_manager.settings, 'mirror_print') else False)
        self.print_enabled_var = tk.BooleanVar(value=True)  # Print enabled by default
        self.stay_on_top_var = tk.BooleanVar(value=config_manager.settings.stay_on_top if hasattr(config_manager.settings, 'stay_on_top') else False)
        self.transparency_var = tk.BooleanVar(value=config_manager.settings.transparency_enabled if hasattr(config_manager.settings, 'transparency_enabled') else True)
        self.receive_mode_var = tk.BooleanVar(value=config_manager.settings.receive_mode if hasattr(config_manager.settings, 'receive_mode') else True)  # Receive mode enabled by default
        self.exceptions_mode_var = tk.BooleanVar(value=config_manager.settings.exceptions_mode if hasattr(config_manager.settings, 'exceptions_mode') else False)  # Exceptions mode disabled by default
        
        # Load saved settings if available
        if hasattr(self.config_manager.settings, 'receive_mode'):
            self.receive_mode_var.set(self.config_manager.settings.receive_mode)
        if hasattr(self.config_manager.settings, 'exceptions_mode'):
            self.exceptions_mode_var.set(self.config_manager.settings.exceptions_mode)
        if hasattr(self.config_manager.settings, 'stay_on_top'):
            self.stay_on_top_var.set(self.config_manager.settings.stay_on_top)
            
            # Apply stay-on-top setting immediately
            if self.stay_on_top_var.get():
                self.winfo_toplevel().attributes('-topmost', True)
        
        # Create the UI elements
        self._create_ui()
        
        # Start periodic check for browser tab state
        self._start_browser_tab_check()
        
        # Bind to the custom browser tab events
        self.bind_all("<<BrowserTabClosed>>", self._on_browser_tab_closed)
        self.bind_all("<<BrowserTabOpened>>", self._on_browser_tab_opened)
        
        # Initialize transparency manager
        self.transparency_manager = TransparencyManager(
            self.winfo_toplevel(),  # Use the top-level window
            opacity=config_manager.settings.transparency_level,
            enabled=self.transparency_var.get()
        )
        
        # Set up the UI in its final state immediately to prevent flickering
        # Disable the SKU field
        self.field_widgets["SKU:"]["widget"].config(state="disabled")
        logging.info("Explicitly disabled SKU field during initialization")
        
        # Hide the Close Tab button
        if hasattr(self, 'close_tab_button'):
            self.close_tab_button.pack_forget()
            
        # Set focus to tracking number field
        self._focus_tracking_field()
        
        # Mark initialization as complete
        self.after(500, self._complete_initialization)
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Create a frame for the content with reduced vertical padding
        content_frame = tk.Frame(self, bg='white', padx=20, pady=10)
        content_frame.pack(fill='both', expand=True)
        
        # Add a return button in the top-left corner
        return_frame = tk.Frame(content_frame, bg='white')
        return_frame.pack(fill='x', pady=(0, 5))
        
        return_button = create_colored_button(
            return_frame,
            text="← Return",
            color="#4CAF50",  # Green
            hover_color="#A5D6A7",  # Light Green
            command=self.return_to_welcome_callback,
            big=False
        )
        return_button.config(
            width=10,
            height=1,
            font=("Arial", 10, "bold")
        )
        return_button.pack(side='left')
        
        # Add the R toggle button for receive mode
        def toggle_receive_mode():
            current_state = self.receive_mode_var.get()
            self.receive_btn.config(
                bg='#FF5722' if current_state else '#D3D3D3',  # Orange if on, Light Gray if off
                relief='sunken' if current_state else 'raised'
            )
            # If receive mode is being turned on, turn off exceptions mode
            if current_state and self.exceptions_mode_var.get():
                self.exceptions_mode_var.set(False)
                toggle_exceptions_mode()
            # Save the setting
            self.config_manager.settings.receive_mode = current_state
            self.config_manager.save_settings()
            # Update UI based on receive mode
            if current_state:
                self._update_status("Receive mode activated", 'blue')
            else:
                self._update_status("Receive mode deactivated", 'black')
        
        # Set initial button state based on saved setting
        initial_receive_color = '#FF5722' if self.receive_mode_var.get() else '#D3D3D3'  # Orange if on, Light Gray if off
        initial_receive_relief = 'sunken' if self.receive_mode_var.get() else 'raised'
        
        self.receive_btn = tk.Button(
            return_frame,
            text="R",
            bg=initial_receive_color, 
            fg="white",
            relief=initial_receive_relief,
            width=3,
            font=("Arial", 10, "bold"),
            command=lambda: [self.receive_mode_var.set(not self.receive_mode_var.get()),
                            toggle_receive_mode()]
        )
        self.receive_btn.pack(side='left', padx=2)
        

        
        # Add a button to open the Returns Data Dialog
        def open_returns_data_dialog():
            ReturnsDataDialog(self.winfo_toplevel(), self.config_manager)
        
        returns_data_button = tk.Button(
            return_frame,
            text="📄",
            bg="#2196F3",  # Light blue
            fg="white",
            font=("Arial", 10, "bold"),  # Match the font size of the Returns button
            command=open_returns_data_dialog,
            width=3,
            padx=3  # Add horizontal padding inside the button
        )
        returns_data_button.pack(side='left', padx=5)
        
        # Add a pin button on the right side to toggle stay-on-top
        def toggle_stay_on_top():
            current_state = self.stay_on_top_var.get()
            self.pin_btn.config(
                bg='#FFD700' if current_state else '#D3D3D3',  # Gold if on, Light Gray if off
                relief='sunken' if current_state else 'raised'
            )
            # Get the root window (Tk instance) and update its topmost state
            root = self.winfo_toplevel()
            root.attributes('-topmost', current_state)
            # Ensure window is lifted and focused when topmost is enabled
            if current_state:
                root.lift()
                root.focus_force()
            # Save the setting
            self.config_manager.settings.stay_on_top = current_state
            self.config_manager.save_settings()
        
        # Create pin button with label
        pin_frame = tk.Frame(return_frame, bg='white')
        pin_frame.pack(side='right')
        
        # Add the E toggle button for exceptions mode
        def toggle_exceptions_mode():
            current_state = self.exceptions_mode_var.get()
            self.exceptions_btn.config(
                bg='#2196F3' if current_state else '#D3D3D3',  # Light blue if on, Light Gray if off
                relief='sunken' if current_state else 'raised'
            )
            # If exceptions mode is being turned on, turn off receive mode
            if current_state and self.receive_mode_var.get():
                self.receive_mode_var.set(False)
                toggle_receive_mode()
            # Save the setting
            self.config_manager.settings.exceptions_mode = current_state
            self.config_manager.save_settings()
            # Update UI based on exceptions mode
            if current_state:
                self._update_status("Exceptions mode activated", 'blue')
            else:
                self._update_status("Exceptions mode deactivated", 'black')
        
        # Set initial button state based on saved setting
        initial_exceptions_color = '#2196F3' if self.exceptions_mode_var.get() else '#D3D3D3'  # Light blue if on, Light Gray if off
        initial_exceptions_relief = 'sunken' if self.exceptions_mode_var.get() else 'raised'
        
        self.exceptions_btn = tk.Button(
            pin_frame,
            text="E",
            bg=initial_exceptions_color, 
            fg="white",
            relief=initial_exceptions_relief,
            width=3,
            font=("Arial", 10, "bold"),
            command=lambda: [self.exceptions_mode_var.set(not self.exceptions_mode_var.get()),
                            toggle_exceptions_mode()]
        )
        self.exceptions_btn.pack(side='left', padx=(2, 8))  # Add more padding on the right side
        
        #pin_label = tk.Label(pin_frame, text="Pin:", bg='white', font=('TkDefaultFont', 10))
        #pin_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Set initial button state based on saved setting
        initial_pin_color = '#FFD700' if self.stay_on_top_var.get() else '#D3D3D3'  # Gold if on, Light Gray if off
        initial_pin_relief = 'sunken' if self.stay_on_top_var.get() else 'raised'
        
        self.pin_btn = tk.Button(pin_frame, text="📌", bg=initial_pin_color, 
                           relief=initial_pin_relief, width=3,
                           font=('TkDefaultFont', 14), anchor='center')
        
        self.pin_btn.config(
            command=lambda: [self.stay_on_top_var.set(not self.stay_on_top_var.get()),
                           toggle_stay_on_top()]
        )
        self.pin_btn.pack(side=tk.LEFT, padx=2)
        
        # Apply the initial stay-on-top state
        if self.stay_on_top_var.get():
            root = self.winfo_toplevel()
            root.attributes('-topmost', True)
        
        # Title
        self.title_frame = tk.Frame(content_frame, bg='white')
        self.title_frame.pack(pady=(0, 10))
        
        self.title_label = tk.Label(
            self.title_frame,
            text="Create New Label",
            font=("Arial", 16, "bold"),
            bg='white',
            fg='#333333'
        )
        self.title_label.pack()
        
        # Create form fields
        fields = [
            {
                "label": "Tracking Number:",
                "var_type": "string",
                "default": "",
                "width": 30,
                "required": False
            },
            {
                "label": "SKU:",
                "var_type": "string",
                "default": "",
                "width": 30,
                "required": True
            }
        ]
        
        form_frame = tk.Frame(content_frame, bg='white')
        form_frame.pack(fill='x', pady=5)
        
        self.field_widgets = create_form_field_group(form_frame, fields)
        
        # Create a frame for the tracking number row to hold the close tab button
        tracking_frame = self.field_widgets["Tracking Number:"]["frame"]
        
        # Create the Close Tab button (initially hidden)
        self.close_tab_button = create_colored_button(
            tracking_frame,
            text="Close Tab",
            color="#FF5722",  # Orange
            hover_color="#D84315",  # Darker orange
            command=self._close_browser_tab
        )
        # Place it after the tracking number field
        self.close_tab_button.pack(side=tk.RIGHT, padx=(5, 0))
        self.close_tab_button.pack_forget()  # Initially hidden
        
        # Store references to the variables
        self.tracking_var = self.field_widgets["Tracking Number:"]["var"]
        self.sku_var = self.field_widgets["SKU:"]["var"]
        
        # Add context menus to text fields
        add_context_menu(self.field_widgets["Tracking Number:"]["widget"])
        add_context_menu(self.field_widgets["SKU:"]["widget"])
        
        # Add focus to tracking number field
        self.field_widgets["Tracking Number:"]["widget"].focus_set()
        
        # Initially disable the SKU field until a valid tracking number is entered
        self.field_widgets["SKU:"]["widget"].config(state="disabled")
        
        # Add auto-copy and tab functionality for tracking number field
        def on_tracking_enter(event):
            # Get the tracking number
            tracking_number = self.tracking_var.get().strip()
            
            # Check if receive mode is enabled
            receive_mode_enabled = self.receive_mode_var.get()
            
            # Check if exceptions mode is enabled
            exceptions_mode_enabled = self.exceptions_mode_var.get()
            
            # Validate tracking number - required unless in receive mode (and not in exceptions mode)
            if not tracking_number and (not receive_mode_enabled or exceptions_mode_enabled):
                self._update_status("Please enter a tracking number", 'red')
                messagebox.showerror("Missing Tracking Number", "A tracking number is required.\n\nPlease enter a valid tracking number.")
                return "break"  # Prevent default Enter behavior
            elif not tracking_number and receive_mode_enabled and not exceptions_mode_enabled:
                # In receive mode (but not exceptions mode), we allow blank tracking numbers
                self._update_status("Receive mode: proceeding with blank tracking number", 'blue')
                logging.info("Receive mode: proceeding with blank tracking number")
                tracking_number = ""  # Ensure it's an empty string, not None
                
                # Enable the SKU field immediately when using blank tracking number in receive mode
                self.field_widgets["SKU:"]["widget"].config(state="normal")
                self.field_widgets["SKU:"]["widget"].focus_set()
                return "break"  # Prevent default Enter behavior
            
            # Validate tracking number length (skip if blank in receive mode)
            if tracking_number and len(tracking_number) <= 12:
                self._update_status("Tracking number must be longer than 12 characters", 'red')
                messagebox.showerror("Invalid Tracking Number", "Tracking number must be longer than 12 characters.\n\nPlease enter a valid tracking number.")
                # Clear the invalid tracking number
                self.tracking_var.set("")
                return "break"  # Prevent default Enter behavior
            
            # Copy to clipboard
            if tracking_number:
                self.clipboard_clear()
                self.clipboard_append(tracking_number)
                
                # Process the tracking number with JDL automation if enabled and exceptions mode is not enabled
                if (hasattr(self.config_manager.settings, 'jdl_automation_enabled') and 
                    self.config_manager.settings.jdl_automation_enabled and 
                    not exceptions_mode_enabled):
                    self._process_tracking_with_jdl(tracking_number)
                    
                    # Show the Close Tab button
                    self.close_tab_button.pack(side=tk.RIGHT, padx=(5, 0))
                    
                    # Keep the SKU field disabled until the Close Tab button is clicked
                    self._update_status("Click 'Close Tab' button to continue", 'blue')
                else:
                    # If JDL automation is not enabled, enable the SKU field immediately
                    logging.info(f"JDL automation not used - enabling SKU field immediately")
                    logging.info(f"JDL automation enabled setting: {hasattr(self.config_manager.settings, 'jdl_automation_enabled') and self.config_manager.settings.jdl_automation_enabled}")
                    logging.info(f"Exceptions mode: {exceptions_mode_enabled}")
                    self.field_widgets["SKU:"]["widget"].config(state="normal")
                    self.field_widgets["SKU:"]["widget"].focus_set()
                    
                # Clear any previous error messages if not using JDL
                if not (hasattr(self.config_manager.settings, 'jdl_automation_enabled') and self.config_manager.settings.jdl_automation_enabled):
                    self._update_status("", 'black')
            
            return "break"  # Prevent default Enter behavior
        
        # Bind Enter key to the tracking number field
        self.field_widgets["Tracking Number:"]["widget"].bind("<Return>", on_tracking_enter)
        
        # Add functionality to print label when Enter is pressed in the SKU field
        def on_sku_enter(event):
            import re
            # Check if receive mode is enabled
            receive_mode_enabled = self.receive_mode_var.get()
            
            # Verify tracking number is present before proceeding (unless in receive mode)
            tracking_number = self.tracking_var.get().strip()
            if not tracking_number and not receive_mode_enabled:
                self._update_status("Please enter a tracking number first", 'red')
                error_dialog = messagebox.showerror("Missing Tracking Number", "A tracking number is required.\n\nPlease enter a valid tracking number.")
                
                # Get a reference to the tracking field
                tracking_field = self.field_widgets["Tracking Number:"]["widget"]
                
                # Define a function to handle the dialog close event
                def on_dialog_close(event=None):
                    # Focus and select all text in the tracking field
                    tracking_field.focus_set()
                    tracking_field.select_range(0, 'end')
                    tracking_field.icursor('end')
                
                # Schedule multiple attempts to ensure selection works
                self.after(50, on_dialog_close)
                self.after(100, on_dialog_close)
                self.after(200, on_dialog_close)
                return "break"  # Prevent default Enter behavior
            
            # Validate SKU format (must be exactly 12 digits)
            sku = self.sku_var.get().strip()
            if not re.fullmatch(r"\d{12}", sku):
                self._update_status("SKU must be exactly 12 digits", 'red')
                error_dialog = messagebox.showerror("Invalid SKU", "SKU must be exactly 12 digits (numbers only).\n\nPlease enter a valid SKU.")
                
                # Get a reference to the SKU field
                sku_field = self.field_widgets["SKU:"]["widget"]
                
                # Define a function to handle the dialog close event
                def on_dialog_close(event=None):
                    # Clear the SKU field
                    self.sku_var.set("")
                    # Focus the SKU field
                    sku_field.focus_set()
                
                # Schedule multiple attempts to ensure it works
                self.after(50, on_dialog_close)
                self.after(100, on_dialog_close)
                self.after(200, on_dialog_close)
                return "break"  # Prevent default Enter behavior
            
            # Print the label
            self._print_label()
            return "break"  # Prevent default Enter behavior
        
        # Bind Enter key to the SKU field
        self.field_widgets["SKU:"]["widget"].bind("<Return>", on_sku_enter)
        
        # Options frame
        options_frame = tk.Frame(content_frame, bg='white')
        options_frame.pack(fill='x', pady=10)
        
        # Mirror print toggle
        def toggle_mirror_print():
            current_state = self.mirror_print_var.get()
            self.mirror_btn.config(
                bg='#90EE90' if current_state else '#C71585',  # Green if on, Pink if off
                relief='sunken' if current_state else 'raised'
            )
            # Save the mirror print state
            self.config_manager.settings.mirror_print = current_state
            self.config_manager.save_settings()
        
        # Set initial button state based on saved setting
        initial_color = '#90EE90' if self.mirror_print_var.get() else '#C71585'
        initial_relief = 'sunken' if self.mirror_print_var.get() else 'raised'
        
        # Create mirror button with label
        mirror_label = tk.Label(options_frame, text="M P:", bg='white', font=('TkDefaultFont', 10))
        mirror_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.mirror_btn = tk.Button(options_frame, text=" ", bg=initial_color, 
                               relief=initial_relief, width=3,
                               font=('TkDefaultFont', 14), anchor='center')
        
        self.mirror_btn.config(
            command=lambda: [self.mirror_print_var.set(not self.mirror_print_var.get()),
                           toggle_mirror_print()]
        )
        self.mirror_btn.pack(side=tk.LEFT, padx=2)
        
        # Add a spacer
        spacer = tk.Frame(options_frame, width=20, bg='white')
        spacer.pack(side=tk.LEFT)
        
        # Print toggle
        def toggle_print_enabled():
            current_state = self.print_enabled_var.get()
            
            # Update button appearance
            self.print_btn.config(
                bg='#90EE90' if current_state else '#C71585',  # Green if on, Pink if off
                relief='sunken' if current_state else 'raised'
            )
            
            # Update text color in input fields
            tracking_field = self.field_widgets["Tracking Number:"]["widget"]
            sku_field = self.field_widgets["SKU:"]["widget"]
            
            # Royal blue (#4169E1) when printing is disabled, black when enabled
            text_color = 'black' if current_state else '#4169E1'  # Royal Blue
            
            tracking_field.config(fg=text_color)
            sku_field.config(fg=text_color)
            
            # Update title label with strikethrough when printing is disabled
            if current_state:
                # Normal font without strikethrough
                self.title_label.config(font=("Arial", 16, "bold"))
            else:
                # Add strikethrough to the title
                self.title_label.config(font=("Verdana", 20, "bold", "overstrike"))
            
            # Update the Print Label button
            if current_state:
                # Normal print mode
                self.print_button.config(
                    text="Print Label",
                    bg="#4CAF50",  # Green
                    activebackground="#A5D6A7"  # Light Green
                )
            else:
                # Logging only mode
                self.print_button.config(
                    text="Send Label",
                    bg="#4169E1",  # Dark Green
                    activebackground="#228B22"  # Forest Green
                )
        
        # Create print button with label
        print_label = tk.Label(options_frame, text="Print:", bg='white', font=('TkDefaultFont', 10))
        print_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.print_btn = tk.Button(options_frame, text=" ", bg='#90EE90', 
                               relief='sunken', width=3,
                               font=('TkDefaultFont', 14), anchor='center')
        
        self.print_btn.config(
            command=lambda: [self.print_enabled_var.set(not self.print_enabled_var.get()),
                           toggle_print_enabled()]
        )
        self.print_btn.pack(side=tk.LEFT, padx=2)
        
        # Initialize the Print Label button based on the initial print state
        initial_print_state = self.print_enabled_var.get()
        if not initial_print_state:
            # If printing is initially disabled, update the button appearance
            # This will be called after the print_button is created
            self.after(100, lambda: self._initialize_disabled_print_state())
        
        # Add a spacer
        spacer2 = tk.Frame(options_frame, width=20, bg='white')
        spacer2.pack(side=tk.LEFT)
        
        # Transparency toggle
        def toggle_transparency():
            current_state = self.transparency_var.get()
            
            # Update the transparency manager
            self.transparency_manager.set_enabled(current_state)
            
            # Update button appearance
            self.transparency_btn.config(
                bg='#90EE90' if current_state else '#C71585',  # Green if on, Pink if off
                relief='sunken' if current_state else 'raised'
            )
            
            # Save the setting
            self.config_manager.settings.transparency_enabled = current_state
            self.config_manager.save_settings()
        
        # Create transparency button with label
        transparency_label = tk.Label(options_frame, text="Tr:", bg='white', font=('TkDefaultFont', 10))
        transparency_label.pack(side=tk.LEFT, padx=(0, 5))
        
        initial_state = self.transparency_var.get()
        self.transparency_btn = tk.Button(options_frame, text=" ", 
                               bg='#90EE90' if initial_state else '#C71585',  # Green if on, Pink if off
                               relief='sunken' if initial_state else 'raised', width=3,
                               font=('TkDefaultFont', 14), anchor='center')
        
        self.transparency_btn.config(
            command=lambda: [self.transparency_var.set(not self.transparency_var.get()),
                           toggle_transparency()]
        )
        self.transparency_btn.pack(side=tk.LEFT, padx=2)
        
        # Create button frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        # Create Print Button
        self.print_button = create_colored_button(
            button_frame,
            text="Print Label",
            color="#4CAF50",  # Green
            hover_color="#A5D6A7",  # Light Green
            command=self._print_label,
            big=True
        )
        self.print_button.pack(side='left', padx=(0, 10))
        
        # Create Clear Button
        clear_button = create_colored_button(
            button_frame,
            text="Clear",
            color="#9E9E9E",  # Gray
            hover_color="#E0E0E0",  # Light Gray
            command=self._clear_fields,
            big=False
        )
        clear_button.config(width=10, height=2)
        clear_button.pack(side='left')
        
        # Status frame
        status_frame = tk.Frame(content_frame, bg='white')
        status_frame.pack(fill='x', pady=(20, 0))
        
        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 10),
            bg='white',
            fg='black'
        )
        self.status_label.pack(anchor='w')
    
    def _print_label(self):
        """Handle the print label button click"""
        import re
        # Get input values
        tracking_number = self.tracking_var.get().strip()
        sku = self.sku_var.get().strip()
        
        # Check if receive mode is enabled
        receive_mode_enabled = self.receive_mode_var.get()
        
        # Validate tracking number - required unless in receive mode
        if not tracking_number and not receive_mode_enabled:
            self._update_status("Please enter a tracking number", 'red')
            # Show the error dialog
            messagebox.showerror("Missing Tracking Number", "A tracking number is required.\n\nPlease enter a valid tracking number.")
            
            # Use keyboard shortcut to select all text after dialog closes
            tracking_field = self.field_widgets["Tracking Number:"]["widget"]
            tracking_field.focus_set()
            self.after(100, lambda: self._select_all_with_keyboard(tracking_field))
            return False, "No tracking number provided"
        elif not tracking_number and receive_mode_enabled:
            # In receive mode, we allow blank tracking numbers
            self._update_status("Receive mode: proceeding with blank tracking number", 'blue')
            logging.info("Receive mode: proceeding with blank tracking number")
            tracking_number = ""  # Ensure it's an empty string, not None
        
        # Validate SKU format (must be exactly 12 digits)
        if not re.fullmatch(r"\d{12}", sku):
            self._update_status("SKU must be exactly 12 digits", 'red')
            # Show the error dialog
            messagebox.showerror("Invalid SKU", "SKU must be exactly 12 digits (numbers only).\n\nPlease enter a valid SKU.")
            
            # Clear and focus the SKU field after dialog closes
            sku_field = self.field_widgets["SKU:"]["widget"]
            self.sku_var.set("")
            sku_field.focus_set()
            return False, "Invalid SKU format"
        
        # Validate tracking number length (skip if blank in receive mode)
        if tracking_number and len(tracking_number) <= 12:
            self._update_status("Tracking number must be longer than 12 characters", 'red')
            # Show the error dialog
            messagebox.showerror("Invalid Tracking Number", "Tracking number must be longer than 12 characters.\n\nPlease enter a valid tracking number.")
            
            # Use keyboard shortcut to select all text after dialog closes
            tracking_field = self.field_widgets["Tracking Number:"]["widget"]
            tracking_field.focus_set()
            self.after(100, lambda: self._select_all_with_keyboard(tracking_field))
            return False, "Invalid tracking number length"
        
        # Get configuration
        mirror_print = self.mirror_print_var.get()
        print_enabled = self.print_enabled_var.get()
        
        # Get labels directory from configuration
        labels_dir = self.config_manager.settings.last_directory if hasattr(self.config_manager.settings, 'last_directory') else None
        
        # Validate labels directory
        if not labels_dir or not directory_exists(labels_dir):
            error_msg = f"Labels directory not configured or does not exist: {labels_dir}"
            self._update_status(error_msg, 'red')
            messagebox.showerror("Error", error_msg)
            return False, error_msg
        
        # Create a function to update status
        def update_status(message, color='black'):
            self._update_status(message, color)
        
        # If print is disabled, just log the information without printing
        if not print_enabled:
            # Log the shipping record using the new logging system
            log_shipping_event(
                tracking_number=tracking_number,
                sku=sku,
                action="log_only",
                status="success",
                details="No print - logging only"
            )
            
            # Also add to the original shipping_records database to ensure records appear in the Records tab
            from src.utils.database_operations import add_shipping_record
            add_shipping_record(tracking_number, sku, "No print - logging only")
            
            # Write to Google Sheets if configured
            if (hasattr(self.config_manager.settings, 'google_sheet_url') and 
                self.config_manager.settings.google_sheet_url and 
                hasattr(self.config_manager.settings, 'google_sheet_name') and
                self.config_manager.settings.google_sheet_name):
                write_to_google_sheet(
                    self.config_manager, 
                    tracking_number, 
                    sku, 
                    update_status
                )
            
            # Show success message
            self._show_success_message(f"Info for {sku} recorded (no print)")
            
            # Check if receive mode or exceptions mode is enabled
            if self.receive_mode_var.get():
                # Store the current values before clearing
                self.current_tracking = tracking_number
                self.current_sku = sku
                # Open container card dialog without clearing fields yet
                self._open_container_card_dialog()
            elif self.exceptions_mode_var.get():
                # Store the current values before clearing
                self.current_tracking = tracking_number
                self.current_sku = sku
                # Open exceptions dialog without clearing fields yet
                self._open_exceptions_dialog()
            else:
                # If neither mode is enabled, clear fields immediately
                self._clear_fields()
            
            # Update the label count
            if self.update_label_count_callback:
                self.update_label_count_callback()
                
            return True, "Info recorded without printing"
        
        # Use our utility function to process the barcode
        try:
            # Define a function to run after successful printing
            def after_print_success():
                # Log the shipping record using the new logging system ONLY after successful printing
                log_shipping_event(
                    tracking_number=tracking_number,
                    sku=sku,
                    action="print",
                    status="success",
                    details="Label printed successfully"
                )
                
                # Also add to the original shipping_records database to ensure records appear in the Records tab
                from src.utils.database_operations import add_shipping_record
                add_shipping_record(tracking_number, sku, "Label printed successfully")
                
                # Write to Google Sheets ONLY after successful printing
                if (hasattr(self.config_manager.settings, 'google_sheet_url') and 
                    self.config_manager.settings.google_sheet_url and 
                    hasattr(self.config_manager.settings, 'google_sheet_name') and
                    self.config_manager.settings.google_sheet_name):
                    # Use a separate thread for Google Sheets to avoid blocking UI
                    def sheets_task():
                        try:
                            write_to_google_sheet(
                                self.config_manager, 
                                tracking_number, 
                                sku, 
                                update_status
                            )
                        except Exception as e:
                            print(f"Error writing to Google Sheets: {str(e)}")
                    
                    import threading
                    sheets_thread = threading.Thread(target=sheets_task)
                    sheets_thread.daemon = True
                    sheets_thread.start()
                
                # Show success message in the title
                self._show_success_message(f"Label for {sku or tracking_number} printed successfully!")
                
                # Check if receive mode or exceptions mode is enabled and process accordingly
                if self.receive_mode_var.get():
                    # Store the current values before clearing
                    self.current_tracking = tracking_number
                    self.current_sku = sku
                    # Open container card dialog without clearing fields yet
                    self._open_container_card_dialog()
                elif self.exceptions_mode_var.get():
                    # Store the current values before clearing
                    self.current_tracking = tracking_number
                    self.current_sku = sku
                    # Open exceptions dialog without clearing fields yet
                    self._open_exceptions_dialog()
                else:
                    # If neither mode is enabled, clear fields immediately
                    self._clear_fields()
                
                # Update the label count
                if self.update_label_count_callback:
                    self.update_label_count_callback()
            
            # Use the simpler approach from the BAK version
            from src.utils.barcode_operations import process_barcode
            
            # Check if we have a valid tracking number or SKU
            if not tracking_number and not sku:
                error_msg = "Either tracking number or SKU is required"
                self._update_status(error_msg, 'red')
                messagebox.showerror("Error", error_msg)
                return False, error_msg
                
            # Use our utility function to process the barcode
            success, message = process_barcode(
                tracking_number,
                sku,
                labels_dir,
                mirror_print,
                update_status,
                after_print_success
            )
            
            # Use pyautogui to automatically press Enter after a shorter delay
            if success:
                try:
                    # Reduced wait time for the print dialog to appear (from 2000ms to 1000ms)
                    print("Waiting for print dialog to appear...")
                    self.after(1000, lambda: self._press_enter_for_print_dialog())
                except Exception as e:
                    print(f"Error setting up auto-press Enter: {str(e)}")
            else:
                # Show error message if process_barcode failed
                self._update_status(f"Error: {message}", 'red')
                if message == "Label creation has been disabled":
                    self._show_create_label_dialog(sku)
                else:
                    messagebox.showerror("Error", message)
                self._clear_fields()
                
            return success, message
            
        except Exception as e:
            error_msg = str(e)
            self._update_status(f"Error processing barcode: {error_msg}", 'red')
            messagebox.showerror("Error", f"Error processing barcode: {error_msg}")
            self._clear_fields()
            return False, error_msg
    
    def _press_enter_for_print_dialog(self):
        """Press Enter key to confirm print dialog"""
        try:
            print("Pressing Enter to confirm print dialog...")
            pyautogui.press('enter')
            print("Enter key pressed")
        except Exception as e:
            print(f"Error pressing Enter: {str(e)}")
    
    def _clear_fields(self):
        """Clear all form fields"""
        self.tracking_var.set("")
        self.sku_var.set("")
        self._update_status("", 'black')
        
        # Disable the SKU field again
        self.field_widgets["SKU:"]["widget"].config(state="disabled")
        logging.info("SKU field disabled during form clearing")
        
        # Schedule additional attempts to ensure the SKU field stays disabled
        # This prevents other code from re-enabling it during the loop-around process
        for delay in [100, 300, 500]:
            self.after(delay, lambda: self.field_widgets["SKU:"]["widget"].config(state="disabled"))
        
    def _complete_initialization(self):
        """Mark initialization as complete and perform any final setup"""
        self._initializing = False
        logging.info("CreateLabelFrame initialization complete")
        
        # Ensure the SKU field is disabled one final time
        if hasattr(self, 'field_widgets') and "SKU:" in self.field_widgets:
            self.field_widgets["SKU:"]["widget"].config(state="disabled")
    
    def _focus_tracking_field(self):
        """Set focus to the tracking number field if it's empty"""
        if hasattr(self, 'field_widgets') and "Tracking Number:" in self.field_widgets:
            self.field_widgets["Tracking Number:"]["widget"].focus_set()
    
    def _update_status(self, message, color='black'):
        """Update the status message"""
        self.status_var.set(message)
        self.status_label.config(fg=color)
        
    def _initialize_disabled_print_state(self):
        """Initialize the UI elements when printing is disabled"""
        # Update the Print Label button
        self.print_button.config(
            text="Send Label",
            bg="#006400",  # Dark Green
            activebackground="#228B22"  # Forest Green
        )
        
        # Update text color in input fields
        tracking_field = self.field_widgets["Tracking Number:"]["widget"]
        sku_field = self.field_widgets["SKU:"]["widget"]
        tracking_field.config(fg='#4169E1')  # Royal Blue
        sku_field.config(fg='#4169E1')  # Royal Blue
        
        # Add strikethrough to the title
        self.title_label.config(font=("Arial", 16, "bold", "overstrike"))
    
    def _show_success_message(self, message):
        """Show a success message with marquee effect in the title and revert back after a delay"""
        # Save the original text
        original_text = self.title_label.cget("text")
        original_font = self.title_label.cget("font")
        
        # Change the title to the success message with green color and bold font
        self.title_label.config(text=message, fg='#4CAF50', font=("Arial", 14, "bold"))
        
        # Create marquee effect variables
        self.marquee_active = True
        self.marquee_text = message
        self.marquee_position = 0
        self.marquee_direction = 1  # 1 for right, -1 for left
        
        # Start the marquee animation
        self._update_marquee()
        
        # Schedule to stop the marquee and revert back to original title after 8 seconds
        self.after(8000, lambda: self._stop_marquee(original_text, original_font))
    
    def _update_marquee(self):
        """Update the marquee animation frame"""
        if not hasattr(self, 'marquee_active') or not self.marquee_active:
            return
            
        # Get current text
        text = self.marquee_text
        
        # Add some padding
        padded_text = " " * 5 + text + " " * 5
        
        # Calculate the display window (what part of the text to show)
        display_length = min(len(padded_text), 30)  # Limit display length
        
        # Update position based on direction
        self.marquee_position += self.marquee_direction
        
        # Reverse direction if we hit the edges
        if self.marquee_position >= len(padded_text) - display_length:
            self.marquee_direction = -1
        elif self.marquee_position <= 0:
            self.marquee_direction = 1
        
        # Extract the visible portion
        visible_text = padded_text[self.marquee_position:self.marquee_position + display_length]
        
        # Update the label
        self.title_label.config(text=visible_text)
        
        # Schedule the next update
        self.after(100, self._update_marquee)
    
    def _stop_marquee(self, original_text, original_font):
        """Stop the marquee animation and restore the original text"""
        self.marquee_active = False
        self.title_label.config(text=original_text, fg='#333333', font=original_font)
        
    def _select_all_text(self, entry_widget):
        """Select all text in an Entry widget"""
        # Multiple attempts to ensure selection works
        def select_text():
            entry_widget.focus_set()
            entry_widget.selection_range(0, 'end')
            entry_widget.icursor('end')
            
        # Schedule multiple attempts with increasing delays
        self.after(50, select_text)
        self.after(100, select_text)
        self.after(200, select_text)
        
    def _select_all_with_keyboard(self, widget):
        """Select all text using keyboard shortcut simulation"""
        # Force focus to the widget
        self.focus_force()
        widget.focus_set()
        
        # Use pyautogui to simulate Ctrl+A (select all)
        try:
            # First ensure the widget has focus
            self.update_idletasks()
            
            # Use pyautogui to simulate Ctrl+A
            pyautogui.hotkey('ctrl', 'a')
            
            # As a backup, also try the normal selection method
            widget.selection_range(0, 'end')
            widget.icursor('end')
            
            # Make another attempt after a delay
            self.after(200, lambda: self._select_all_backup(widget))
        except Exception as e:
            print(f"Error selecting text: {str(e)}")
            # Fall back to the standard method
            widget.selection_range(0, 'end')
            widget.icursor('end')
    
    def _select_all_backup(self, widget):
        """Backup attempt to select all text"""
        try:
            # Try to ensure the widget has focus
            widget.focus_set()
            
            # Try both methods again
            widget.selection_range(0, 'end')
            widget.icursor('end')
            pyautogui.hotkey('ctrl', 'a')
        except:
            pass
    
    def _show_create_label_dialog(self, sku):
        """
        Show a custom dialog with a 'Create Label' button when a label needs to be created
        
        Args:
            sku: The SKU to pass to the Label Maker application
        """
        # Create a custom dialog
        dialog = tk.Toplevel(self)
        dialog.title("Error")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.transient(self)  # Set to be on top of the parent window
        dialog.grab_set()  # Modal dialog
        
        # Make sure the dialog appears in the center of the parent window
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Create a frame for the icon and message
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        # Create and place the error icon
        try:
            # Use a standard error icon
            error_icon = tk.Label(frame, text="❌", font=("Arial", 24), fg="red")
            error_icon.grid(row=0, column=0, padx=(0, 15), sticky="n")
        except:
            # Fallback if custom icon fails
            error_icon = tk.Label(frame, text="X", font=("Arial", 24), fg="red")
            error_icon.grid(row=0, column=0, padx=(0, 15), sticky="n")
        
        # Create and place the message
        message = tk.Label(
            frame, 
            text="This label needs to be created in Label Maker.",
            font=("Arial", 10), 
            justify="left",
            wraplength=300
        )
        message.grid(row=0, column=1, sticky="w")
        
        # Create a frame for the buttons
        button_frame = tk.Frame(dialog, padx=10, pady=10)
        button_frame.pack(fill="x", side="bottom")
        
        # Function to handle the Create Label button click
        def on_create_label():
            dialog.destroy()
            self._launch_label_maker(sku)
        
        # Create and place the buttons
        create_button = tk.Button(
            button_frame, 
            text="Create Label", 
            command=on_create_label,
            width=15,
            default="active"  # Make this the default button (activated by Enter)
        )
        create_button.pack(side="right", padx=5)
        
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy,
            width=10
        )
        cancel_button.pack(side="right", padx=5)
        
        # Set focus to the Create Label button
        create_button.focus_set()
        
        # Bind Enter key to the Create Label button
        dialog.bind("<Return>", lambda event: on_create_label())
        
        # Make the dialog modal
        dialog.wait_window()
    
    def _launch_label_maker(self, sku):
        """
        Launch the Label Maker application with the given SKU
        
        Args:
            sku: The SKU to pass to the Label Maker application
        """
        try:
            # Get the root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Path to the Label Maker directory
            label_maker_dir = os.path.join(root_dir, "Label Maker")
            
            # Path to main.pyw
            main_pyw = os.path.join(label_maker_dir, "main.pyw")
            
            if not os.path.exists(main_pyw):
                messagebox.showerror("Error", f"Label Maker application not found at: {main_pyw}")
                return
            
            # Launch the Label Maker application
            self._update_status(f"Launching Label Maker for SKU: {sku}", 'blue')
            
            # Use subprocess to launch the application
            process = subprocess.Popen(
                [sys.executable, main_pyw],
                cwd=label_maker_dir
            )
            
            # Wait a moment for the application to start
            self.after(2000, lambda: self._fill_upc_field(sku))
        
        except Exception as e:
            error_msg = str(e)
            self._update_status(f"Error launching Label Maker: {error_msg}", 'red')
            messagebox.showerror("Error", f"Error launching Label Maker: {error_msg}")

    def _fill_upc_field(self, sku):
        """
        Use pyautogui to fill in the UPC code field in the Label Maker application
        
        Args:
            sku: The SKU to enter in the UPC field
        """
        try:
            # First press Tab to focus the UPC field (assuming it's the first field)
            pyautogui.press('tab')
            
            # Clear any existing text and type the SKU
            pyautogui.hotkey('ctrl', 'a')  # Select all text
            pyautogui.press('delete')      # Delete selected text
            pyautogui.write(sku)           # Type the SKU
            
            self._update_status(f"SKU {sku} entered in Label Maker", 'green')
        except Exception as e:
            error_msg = str(e)
            self._update_status(f"Error filling UPC field: {error_msg}", 'red')
            # Don't show an error dialog here as it's not critical
            
    

    def _process_tracking_with_jdl(self, tracking_number):
        """
        Process the tracking number with JDL Global IWMS automation
        
        Args:
            tracking_number: The tracking number to process
        """
        try:
            # Update status
            self._update_status(f"Processing tracking number with JDL automation: {tracking_number}", 'blue')
            
            # Check if we need to process in reverse order based on the setting
            reverse_order = False
            if hasattr(self.config_manager.settings, 'reverseinbound_creation'):
                reverse_order = self.config_manager.settings.reverseinbound_creation
            
            # Create a list with just this tracking number
            # In a real implementation, you might want to batch these
            tracking_numbers = [tracking_number]
            
            # If reverse order is enabled, reverse the list
            if reverse_order:
                tracking_numbers = list(reversed(tracking_numbers))
                self._update_status("Using reverse order for JDL processing", 'blue')
            
            # Get JDL credentials from settings or ask user
            username = ""
            password = ""
            
            if hasattr(self.config_manager.settings, 'jdl_username') and hasattr(self.config_manager.settings, 'jdl_password'):
                username = self.config_manager.settings.jdl_username
                password = self.config_manager.settings.jdl_password
            
            if not username or not password:
                # In a real implementation, you would prompt for credentials
                # For now, just log a message
                self._update_status("JDL credentials not found in settings", 'orange')
                return
            
            # Get the singleton instance of JDL automation
            # This ensures we maintain the same browser session throughout the day
            jdl = JDLAutomation.get_instance(self.config_manager)
            
            # Process in a separate thread to avoid blocking the UI
            import threading
            thread = threading.Thread(
                target=self._jdl_automation_thread,
                args=(jdl, tracking_numbers, username, password),
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            error_msg = str(e)
            self._update_status(f"Error processing tracking number with JDL: {error_msg}", 'red')
            logging.error(f"Error processing tracking number with JDL: {error_msg}")
            
            # Make sure the SKU field is enabled
            self.field_widgets["SKU:"]["widget"].config(state="normal")
            self.field_widgets["SKU:"]["widget"].focus_set()
            
            # Hide the Close Tab button
            self.close_tab_button.pack_forget()
            
    def _close_browser_tab(self, from_simulate_method=False):
        """
        Close the browser tab and enable the SKU field.
        This method is called when the user clicks the 'Close Tab' button.
        
        Args:
            from_simulate_method: Whether this method is being called from simulate_close_tab_button_click.
                                Used to prevent recursive loops.
        """
        try:
            # Get the JDL automation instance
            jdl = JDLAutomation.get_instance(self.config_manager)
            
            # Reset the browser tab state directly
            JDLAutomation.browser_tab_open = False
            logging.info("Reset browser_tab_open flag to False")
            
            # Hide the Close Tab button
            if hasattr(self, 'close_tab_button'):
                self.close_tab_button.pack_forget()
                logging.info("Close Tab button hidden directly")
            
            # Enable the SKU field for the current tracking number
            if "SKU:" in self.field_widgets:
                # Only clear the SKU field, preserve the tracking number
                self.sku_var.set("")
                
                # Enable the SKU field so user can enter SKU for the current tracking number
                self.field_widgets["SKU:"]["widget"].config(state="normal")
                logging.info("SKU field enabled after browser tab closed")
                
                # Focus on the SKU field for immediate entry
                self.field_widgets["SKU:"]["widget"].focus_set()
                
                # Schedule multiple focus attempts to ensure SKU field gets focus
                for delay in [50, 100, 200, 300]:
                    self.after(delay, lambda: self.field_widgets["SKU:"]["widget"].focus_set())
                
                logging.info("SKU field focused for entry")
                    
            # Update status
            self._update_status("Browser tab closed. Ready for next tracking number.", 'green')
            
            # Bring the window to the front and force focus
            self.winfo_toplevel().lift()
            self.winfo_toplevel().focus_force()
            
            # Actually close the browser tab (do this after UI updates)
            try:
                close_success = jdl.close()
                if not close_success:
                    logging.warning("Browser tab close operation reported failure but UI is already updated")
            except Exception as close_error:
                logging.error(f"Error in actual tab close operation: {str(close_error)}")
            
        except Exception as e:
            error_msg = str(e)
            self._update_status(f"Error in tab close handler: {error_msg}", 'red')
            logging.error(f"Error in tab close handler: {error_msg}")
            
            # Still try to hide the button and enable the SKU field in case of error
            try:
                # Use from_close_tab_method=True to prevent recursive loop
                if not from_simulate_method:
                    self.simulate_close_tab_button_click(enable_sku=True, from_close_tab_method=True)
                else:
                    # Direct fallback if we're already coming from simulate method
                    if "SKU:" in self.field_widgets:
                        self.field_widgets["SKU:"]["widget"].config(state="normal")
                    self._hide_close_tab_button()
            except Exception as sim_error:
                logging.error(f"Error in fallback simulate_close_tab_button_click: {str(sim_error)}")
                # Direct fallback if the simulate method fails
                if "SKU:" in self.field_widgets:
                    self.field_widgets["SKU:"]["widget"].config(state="normal")
                self._hide_close_tab_button()
        
        # Schedule additional attempts to hide the button just in case
        # This ensures it will be hidden even if there are timing issues
        for delay in [100, 500, 1000, 2000, 5000]:
            self.after(delay, self._hide_close_tab_button)
    
    def _force_hide_close_tab_button(self):
        """
        Force hide the close tab button with no conditions.
        This is a direct method that always hides the button no matter what.
        """
        if hasattr(self, 'close_tab_button'):
            logging.info("Force hiding Close Tab button")
            self.close_tab_button.pack_forget()
            
            # Also try to destroy and recreate it if it's still visible
            if self.close_tab_button.winfo_viewable():
                logging.warning("Close Tab button still visible after pack_forget, trying destroy")
                try:
                    self.close_tab_button.destroy()
                    # Recreate it but keep it hidden
                    tracking_frame = self.field_widgets["Tracking Number:"]["frame"]
                    self.close_tab_button = create_colored_button(
                        tracking_frame,
                        text="Close Tab",
                        color="#FF5722",  # Orange
                        hover_color="#D84315",  # Darker orange
                        command=self._close_browser_tab
                    )
                    # Don't pack it - keep it hidden
                except Exception as e:
                    logging.error(f"Error recreating Close Tab button: {str(e)}")
        
    def _ensure_close_tab_button_hidden(self):
        """
        Ensure that the close tab button is hidden regardless of what happened in the close process.
        This is a failsafe method called on a timeout to guarantee the button state is correct.
        """
        try:
            if hasattr(self, 'close_tab_button'):
                logging.info("Failsafe: Ensuring close tab button is hidden")
                self.close_tab_button.pack_forget()
                # Also ensure SKU field is enabled
                if "SKU:" in self.field_widgets:
                    self.field_widgets["SKU:"]["widget"].config(state="normal")
        except Exception as e:
            logging.error(f"Error in _ensure_close_tab_button_hidden: {str(e)}")
    
    def simulate_close_tab_button_click(self, enable_sku=False, from_close_tab_method=False):
        """
        Simulate a click on the Close Tab button.
        This is used by JDLAutomation to force the button to be hidden.
        
        Args:
            enable_sku: Whether to enable the SKU field after hiding the button.
                       Default is False to preserve the disabled state during initialization.
            from_close_tab_method: Whether this method is being called from _close_browser_tab.
                                  Used to prevent recursive loops.
        """
        logging.info("simulate_close_tab_button_click called - hiding Close Tab button")
        try:
            # Prevent recursive loop between this method and _close_browser_tab
            if not from_close_tab_method and hasattr(self, '_close_browser_tab'):
                # Only call _close_browser_tab if we're not already being called from it
                self._close_browser_tab(from_simulate_method=True)
                logging.info("Successfully simulated Close Tab button click")
            else:
                # Just hide the button without calling _close_browser_tab again
                if hasattr(self, 'close_tab_button'):
                    self.close_tab_button.pack_forget()
                    logging.info("Close Tab button hidden successfully")
                    
                # Only enable the SKU field if explicitly requested
                # This prevents enabling it during initialization
                if enable_sku and "SKU:" in self.field_widgets:
                    self.field_widgets["SKU:"]["widget"].config(state="normal")
                    self.field_widgets["SKU:"]["widget"].focus_set()
                    logging.info("SKU field enabled and focused")
        except Exception as e:
            logging.error(f"Error simulating Close Tab button click: {str(e)}")
        
        # Return True to indicate success
        return True

    def _on_browser_tab_closed(self, event=None):
        """
        Handle the custom BrowserTabClosed event.
        This is triggered when JDLAutomation closes a browser tab.
        
        Args:
            event: The event object (not used)
        """
        logging.info("Received BrowserTabClosed event - hiding Close Tab button")
        try:
            # Hide the Close Tab button
            if hasattr(self, 'close_tab_button'):
                self.close_tab_button.pack_forget()
                logging.info("Close Tab button hidden due to BrowserTabClosed event")
            
            # Check if we're in receive mode
            receive_mode_enabled = hasattr(self, 'receive_mode_var') and self.receive_mode_var.get()
            
            if receive_mode_enabled:
                # In receive mode, behavior depends on which phase we're in
                # For receive mode, we need to handle the workflow differently
                # Store the current tracking number to ensure it's not lost
                current_tracking = self.tracking_var.get()
                logging.info(f"Preserving tracking number: {current_tracking}")
                
                # Check which phase we're in based on the container card dialog
                # We can determine this by checking if we have a current_container_card attribute
                is_second_phase = hasattr(self, 'current_container_card') and self.current_container_card
                
                if is_second_phase:
                    # Second phase - after container card entry and second browser tab
                    logging.info("Detected second phase of receive workflow (after container card)")
                    
                    if "SKU:" in self.field_widgets:
                        # Clear fields
                        self.tracking_var.set("")
                        self.sku_var.set("")
                        
                        # Disable SKU field
                        self.field_widgets["SKU:"]["widget"].config(state="disabled")
                        logging.info("SKU field disabled after complete receive workflow")
                        
                        # Focus on tracking number field
                        if "Tracking Number:" in self.field_widgets:
                            self.field_widgets["Tracking Number:"]["widget"].focus_set()
                            logging.info("Focus set to tracking number field for next entry")
                        
                        # Reset phase and container card
                        self._receive_workflow_phase = 0
                        self.current_container_card = None
                        logging.info("Receive workflow phase reset to 0 (workflow complete)")
                        
                        # Update status
                        self._update_status("Receive workflow completed. Ready for next entry.", 'green')
                else:
                    # First phase - after tracking number entry and first browser tab
                    logging.info("Detected first phase of receive workflow (after tracking number)")
                    
                    if "SKU:" in self.field_widgets:
                        # Only clear the SKU field, preserve the tracking number
                        self.sku_var.set("")
                        
                        # Enable the SKU field
                        self.field_widgets["SKU:"]["widget"].config(state="normal")
                        self.field_widgets["SKU:"]["widget"].focus_set()
                        logging.info("SKU field enabled after first browser tab closed")
                        
                        # Update phase
                        self._receive_workflow_phase = 1
                        logging.info("Receive workflow phase updated to 1 (after first browser tab)")
                    
                    # Update status
                    self._update_status("Browser tab closed. Continue with SKU entry.", 'green')
                    
                    # Ensure the tracking number is preserved
                    self.tracking_var.set(current_tracking)
            else:
                # Standard behavior - preserve tracking number and enable SKU field
                if "SKU:" in self.field_widgets:
                    # Only clear the SKU field, preserve the tracking number
                    self.sku_var.set("")
                    
                    # Enable the SKU field
                    self.field_widgets["SKU:"]["widget"].config(state="normal")
                    self.field_widgets["SKU:"]["widget"].focus_set()
                    logging.info("SKU field enabled due to BrowserTabClosed event")
                    
                # Update status
                self._update_status("Browser tab closed. Continue with SKU entry.", 'green')
        except Exception as e:
            logging.error(f"Error handling BrowserTabClosed event: {str(e)}")
            
    def _on_browser_tab_opened(self, event=None):
        """
        Handle the custom BrowserTabOpened event.
        This is triggered when a browser tab is opened, especially in Receive mode.
        
        Args:
            event: The event object (not used)
        """
        logging.info("Received BrowserTabOpened event - showing Close Tab button")
        try:
            # Show the Close Tab button but make it non-clickable
            self._show_close_tab_button_as_indicator()
            
            # Disable the SKU field while the browser tab is open
            if "SKU:" in self.field_widgets:
                self.field_widgets["SKU:"]["widget"].config(state="disabled")
                logging.info("SKU field disabled while browser tab is open")
                
            # Update status
            self._update_status("Browser tab opened. Wait for processing to complete.", 'blue')
        except Exception as e:
            logging.error(f"Error handling BrowserTabOpened event: {str(e)}")
            
    def _show_close_tab_button_as_indicator(self):
        """
        Show the Close Tab button as a non-clickable indicator that a browser tab is open.
        """
        try:
            if hasattr(self, 'close_tab_button'):
                logging.info("Showing Close Tab button as non-clickable indicator")
                # Make the button visible
                self.close_tab_button.pack(side=tk.RIGHT, padx=(5, 0))
                # But make it non-clickable
                self.close_tab_button.config(state="disabled")
                # Change the color to indicate it's just an indicator
                self.close_tab_button.config(bg="#FFA07A")  # Light salmon color
                logging.info("Close Tab button shown as non-clickable indicator")
        except Exception as e:
            logging.error(f"Error showing Close Tab button as indicator: {str(e)}")
            
    def _hide_close_tab_button(self):
        """
        Hide the Close Tab button.
        """
        try:
            if hasattr(self, 'close_tab_button'):
                logging.info("Hiding Close Tab button")
                # Hide the button
                self.close_tab_button.pack_forget()
                # Reset its color for next time
                self.close_tab_button.config(bg="#FF5722")  # Original orange color
                logging.info("Close Tab button hidden")
        except Exception as e:
            logging.error(f"Error hiding Close Tab button: {str(e)}")
            
    def _start_browser_tab_check(self):
        """
        Start a periodic check of the browser tab state to ensure UI elements are properly updated.
        This is a more reliable approach than relying on events or state tracking.
        """
        logging.info("Starting periodic browser tab state check")
        self._check_browser_tab_state()
        
    def _check_browser_tab_state(self):
        """
        Periodically check if a browser tab is open and update UI elements accordingly.
        This ensures the Close Tab button is only visible when a browser tab is actually open.
        """
        try:
            # Skip UI updates during initialization to prevent flickering
            if hasattr(self, '_initializing') and self._initializing:
                logging.debug("Skipping browser tab state check during initialization")
                self.after(2000, self._check_browser_tab_state)
                return
            # Get JDL automation instance
            jdl = JDLAutomation.get_instance(self.config_manager)
            
            # Check if a browser tab is actually open using a platform-specific approach
            browser_open = False
            
            # Instead of just checking if browsers are running (which is too broad),
            # we'll check if JDL automation thinks a browser tab is open
            if hasattr(jdl, 'browser_tab_open'):
                browser_open = jdl.browser_tab_open
                logging.debug(f"Using JDL automation browser_tab_open state: {browser_open}")
            else:
                # Fallback to the old method if needed
                if platform.system() == "Windows":
                    import subprocess
                    import re
                    
                    # Only check for browsers if JDL automation has been used
                    # This prevents showing the button when browsers are open for other reasons
                    scan_url = getattr(self.config_manager.settings, 'scan_url', '')
                    if scan_url and hasattr(jdl, 'last_used') and jdl.last_used:
                        browsers = ["chrome", "firefox", "msedge", "iexplore", "opera"]
                        for browser in browsers:
                            try:
                                # Use tasklist to check if browser is running
                                result = subprocess.run(
                                    ["tasklist", "/FI", f"IMAGENAME eq {browser}.exe"],
                                    capture_output=True,
                                    text=True,
                                    check=False
                                )
                                if browser in result.stdout.lower():
                                    logging.debug(f"Detected running browser: {browser}")
                                    browser_open = True
                                    break
                            except Exception as e:
                                logging.debug(f"Error checking for browser {browser}: {str(e)}")
            
            # Update UI based on actual browser state
            if browser_open:
                # Browser is open, show the button as a non-clickable indicator
                if hasattr(self, 'close_tab_button'):
                    # Only update if not already visible
                    if not self.close_tab_button.winfo_viewable():
                        logging.info("Browser detected as open, showing Close Tab button as indicator")
                        self._show_close_tab_button_as_indicator()
                        
                        # Disable the SKU field while the browser tab is open
                        if "SKU:" in self.field_widgets:
                            self.field_widgets["SKU:"]["widget"].config(state="disabled")
            else:
                # Browser is not open, hide the button
                if hasattr(self, 'close_tab_button'):
                    # Only update if currently visible
                    if self.close_tab_button.winfo_viewable():
                        logging.info("Browser detected as closed, hiding Close Tab button")
                        self._hide_close_tab_button()
                        
                        # Only enable the SKU field if a tracking number has been entered
                        # This prevents enabling it during initialization
                        tracking_number = self.tracking_var.get().strip() if hasattr(self, 'tracking_var') else ""
                        if tracking_number and "SKU:" in self.field_widgets:
                            logging.info(f"Browser closed and tracking number present ({tracking_number}), enabling SKU field")
                            self.field_widgets["SKU:"]["widget"].config(state="normal")
                            self.field_widgets["SKU:"]["widget"].focus_set()
                        else:
                            logging.info("Browser closed but no tracking number, keeping SKU field disabled")
                            # Ensure the SKU field stays disabled
                            if "SKU:" in self.field_widgets:
                                self.field_widgets["SKU:"]["widget"].config(state="disabled")
                
                # Also update JDL automation state to match reality
                if hasattr(jdl, 'browser_tab_open') and jdl.browser_tab_open:
                    jdl.browser_tab_open = False
                    logging.info("Updated JDL automation state to match reality (no browser tab open)")
        except Exception as e:
            logging.error(f"Error in _check_browser_tab_state: {str(e)}")
        
        # Schedule the next check (every 2 seconds)
        self.after(2000, self._check_browser_tab_state)
        
    def _ensure_close_tab_button_visible(self):
        """
        Ensure that the close tab button is visible when a browser tab is open.
        This is needed regardless of whether receive mode is enabled or not.
        """
        try:
            if hasattr(self, 'close_tab_button'):
                logging.info("Ensuring close tab button is visible")
                # Check if JDL automation has a browser tab open
                jdl = JDLAutomation.get_instance(self.config_manager)
                if hasattr(jdl, 'browser_tab_open') and jdl.browser_tab_open:
                    # Make the button visible
                    self.close_tab_button.pack(side=tk.RIGHT, padx=(5, 0))
                    self.close_tab_button.config(state="normal")
                    logging.info("Close tab button is now visible")
                    
                    # Disable the SKU field while the browser tab is open
                    if "SKU:" in self.field_widgets:
                        self.field_widgets["SKU:"]["widget"].config(state="disabled")
                        logging.info("SKU field disabled while browser tab is open")
        except Exception as e:
            logging.error(f"Error in _ensure_close_tab_button_visible: {str(e)}")
        
    # This method has been removed as it was a duplicate of the one at line 1329
        
    def _open_container_card_dialog(self):
        """
        Open the container card dialog for receive mode.
        """
        def on_container_card_submit(container_card):
            # Process the container card
            self._update_status(f"Container card {container_card} submitted", 'blue')
            logging.info(f"Container card submitted: {container_card}")
            
            # Store the container card number for later use - but DO NOT copy to clipboard yet
            # The container card will be copied to clipboard only when needed in the automation process
            self.current_container_card = container_card
            
            # Log the complete receive operation
            if hasattr(self, 'current_tracking') and hasattr(self, 'current_sku'):
                logging.info(f"Complete receive operation: Tracking={self.current_tracking}, SKU={self.current_sku}, Container={container_card}")
            
            try:
                # Get the receive manager instance
                from src.utils.receive import ReceiveManager
                receive_manager = ReceiveManager.get_instance(self.config_manager)
                
                # Directly open the JDL scan page
                logging.info("Directly opening JDL scan page")
                self._update_status("Opening JDL scan page...", 'blue')
                
                # Open the scan page
                success = receive_manager.open_jdl_scan_page()
                if success:
                    self._update_status("JDL scan page opened successfully", 'green')
                    logging.info("JDL scan page opened successfully")
                else:
                    self._update_status("Failed to open JDL scan page", 'red')
                    logging.error("Failed to open JDL scan page")
                
                # Define the automation function
                def run_automation():
                    try:
                        # Wait a moment for the first automation process to complete
                        logging.info("Waiting for first automation process to complete...")
                        self.after(0, lambda: self._update_status("Waiting for first automation to complete...", 'blue'))
                        import time
                        time.sleep(3)  # Give the first automation process time to finish
                        
                        logging.info("Starting JDL scan automation process")
                        self.after(0, lambda: self._update_status("Starting JDL scan automation process...", 'blue'))
                        
                        # Log the values we'll be using
                        logging.info(f"Will use tracking number: {self.current_tracking}")
                        logging.info(f"Will use container card: {container_card}")
                        logging.info(f"Will use SKU: {self.current_sku}")
                        
                        # Define a callback function to handle specific errors
                        def error_callback(error_type, sku):
                            if error_type == "barcode_error":
                                logging.info(f"Barcode error callback triggered for SKU: {sku}")
                                # Switch from R to E mode
                                self.after(0, lambda: self._switch_to_exceptions_mode(sku))
                        
                        # Start the automation process with the error callback
                        result = receive_manager.automate_jdl_scan_process(
                            self.current_tracking,
                            container_card,
                            self.current_sku,
                            error_callback=error_callback
                        )
                        
                        # Handle the result
                        if result == "barcode_error":
                            self.after(0, lambda: self._update_status(f"Barcode error detected for SKU: {self.current_sku}", 'orange'))
                            logging.warning(f"Barcode error detected for SKU: {self.current_sku}")
                            # The mode switch will be handled by the callback
                        elif result:
                            self.after(0, lambda: self._update_status("JDL scan automation completed successfully", 'green'))
                            logging.info("JDL scan automation completed successfully")
                        else:
                            self.after(0, lambda: self._update_status("JDL scan automation failed", 'red'))
                            logging.error("JDL scan automation failed")
                    except Exception as e:
                        error_msg = str(e)
                        logging.error(f"Error in JDL scan automation: {error_msg}")
                        self.after(0, lambda: self._update_status(f"Error in JDL scan automation: {error_msg}", 'red'))
                
                # Run the automation in a separate thread
                import threading
                threading.Thread(target=run_automation, daemon=True).start()
                logging.info("Started JDL scan automation thread")
            
            except Exception as e:
                error_msg = str(e)
                logging.error(f"Error in receive process: {error_msg}")
                self._update_status(f"Error in receive process: {error_msg}", 'red')
            
            # Clear the fields after container card is processed
            self._clear_fields()
        
        # Create and show the dialog
        from src.ui.container_card_dialog import ContainerCardDialog
        ContainerCardDialog(self.winfo_toplevel(), self.config_manager, on_container_card_submit)
        
    def _switch_to_exceptions_mode(self, sku=None):
        """Switch from Receive mode to Exceptions mode"""
        logging.info(f"Switching from Receive mode to Exceptions mode for SKU: {sku or 'unknown'}")
        
        # Turn off receive mode
        self.receive_mode_var.set(False)
        self.receive_btn.config(
            bg='#D3D3D3',  # Light Gray for off
            relief='raised'
        )
        
        # Turn on exceptions mode
        self.exceptions_mode_var.set(True)
        self.exceptions_btn.config(
            bg='#2196F3',  # Light blue for on
            relief='sunken'
        )
        
        # Save the settings
        self.config_manager.settings.receive_mode = False
        self.config_manager.settings.exceptions_mode = True
        self.config_manager.save_settings()
        
        # Update status
        self._update_status(f"Switched to Exceptions mode due to barcode error with SKU: {sku or 'unknown'}", 'blue')
        
        # Pre-select the "SKU Mismatch" exception type in the dialog
        self.default_exception_type = "SKU Mismatch"
        
        # Open the exceptions dialog
        self.after(500, self._open_exceptions_dialog)  # Slight delay to ensure UI updates first
    
    def _open_exceptions_dialog(self):
        """Open the exceptions dialog for exception processing"""
        # Only process if exceptions mode is enabled
        if not self.exceptions_mode_var.get():
            self._update_status("Exceptions mode is not enabled", 'orange')
            return
            
        tracking_number = self.tracking_var.get().strip()
        sku = self.sku_var.get().strip()
        
        if not tracking_number:
            self._update_status("Please enter a tracking number first", 'red')
            self._focus_tracking_field()
            return
        
        try:
            logging.info(f"Opening exceptions dialog for tracking number: {tracking_number}")
            
            def on_exceptions_submit(exception_type):
                """Callback when the exceptions dialog is submitted"""
                try:
                    # Get the exceptions manager instance
                    from src.utils.exceptions import ExceptionsManager
                    exceptions_manager = ExceptionsManager.get_instance(self.config_manager)
                    
                    # Process the exception with tracking number, SKU, and exception type
                    success = exceptions_manager.handle_exception_type(exception_type, tracking_number, sku)
                    
                    if success:
                        self._update_status(f"Exception process started for {tracking_number}", 'blue')
                    else:
                        self._update_status("Failed to start exception process", 'red')
                        
                except Exception as e:
                    error_msg = str(e)
                    logging.error(f"Error in exception process: {error_msg}")
                    self._update_status(f"Error in exception process: {error_msg}", 'red')
                
                # Clear the fields after exception is processed
                self._clear_fields()
            
            # Create and show the dialog
            from src.ui.exceptions_dialog import ExceptionsDialog
            ExceptionsDialog(self.winfo_toplevel(), self.config_manager, on_exceptions_submit)
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error opening exceptions dialog: {error_msg}")
            self._update_status(f"Error opening exceptions dialog: {error_msg}", 'red')
    
    def _jdl_automation_thread(self, jdl, tracking_numbers, username, password):
        """
        Thread function for JDL automation to avoid blocking the UI
        
        Args:
            jdl: JDLAutomation instance
            tracking_numbers: List of tracking numbers to process
            username: JDL username
            password: JDL password
        """
        try:
            # Import the visual logger here to ensure it's available
            try:
                from src.utils.jdl_automation import visual_logger
                # Make sure the visual logger is shown (must use after to ensure it's on the main thread)
                self.after(0, lambda: visual_logger.show())
                self.after(0, lambda: visual_logger.log("Starting JDL automation process", "INFO"))
            except ImportError as e:
                logging.error(f"Could not import visual logger: {str(e)}")
            
            # Update status
            self.after(0, lambda: self._update_status("Starting JDL automation process...", 'blue'))
            
            # Process tracking numbers using the new create_after_sales_orders function
            from src.utils.jdl_automation import create_after_sales_orders
            success_count, failed_numbers = create_after_sales_orders(
                self.config_manager, tracking_numbers, username, password)
            
            # Update status based on results
            if success_count == len(tracking_numbers):
                self.after(0, lambda: self._update_status(f"Successfully processed all tracking numbers in JDL", 'green'))
            elif success_count > 0:
                self.after(0, lambda: self._update_status(
                    f"Processed {success_count} of {len(tracking_numbers)} tracking numbers in JDL", 'orange'))
            else:
                self.after(0, lambda: self._update_status("Failed to process any tracking numbers in JDL", 'red'))
                
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self._update_status(f"Error in JDL automation thread: {error_msg}", 'red'))
            logging.error(f"JDL automation thread error: {error_msg}")
            
            # Log to visual logger if available
            try:
                from src.utils.jdl_automation import visual_logger
                self.after(0, lambda: visual_logger.log(f"Error: {error_msg}", "ERROR"))
            except ImportError:
                pass
                
        finally:
            # Ensure the Close Tab button is visible for the user to close the tab
            # This is needed regardless of whether receive mode is enabled or not
            self.after(0, self._ensure_close_tab_button_visible)
            
            # Set a timeout to automatically hide the button if it's not clicked within a reasonable time
            # This helps prevent the button from staying visible indefinitely
            self.after(60000, self._ensure_close_tab_button_hidden)  # 60 seconds timeout

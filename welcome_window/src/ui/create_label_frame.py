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

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_title_section, create_colored_button, create_form_field_group
from src.utils.barcode_operations import process_barcode
from src.utils.sheets_operations import write_to_google_sheet
from src.utils.file_utils import get_central_log_file_path, ensure_directory_exists, directory_exists, file_exists, find_files_by_sku
from src.utils.log_manager import log_shipping_event
from src.utils.text_context_menu import add_context_menu
from src.ui.window_transparency import TransparencyManager, create_transparency_toggle_button
from src.ui.returns_data_dialog import ReturnsDataDialog

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
            config_manager: Configuration manager instance
            update_label_count_callback: Callback to update label count after successful label creation
            return_to_welcome_callback: Callback to return to the welcome screen
        """
        super().__init__(parent, bg='white')
        
        # Store references
        self.parent = parent
        self.config_manager = config_manager
        self.update_label_count_callback = update_label_count_callback
        self.return_to_welcome_callback = return_to_welcome_callback
        
        # Initialize variables
        self.tracking_var = tk.StringVar()
        self.sku_var = tk.StringVar()
        self.mirror_print_var = tk.BooleanVar(value=config_manager.settings.mirror_print if hasattr(config_manager.settings, 'mirror_print') else False)
        self.print_enabled_var = tk.BooleanVar(value=True)  # Print enabled by default
        self.stay_on_top_var = tk.BooleanVar(value=config_manager.settings.stay_on_top if hasattr(config_manager.settings, 'stay_on_top') else False)
        self.transparency_var = tk.BooleanVar(value=config_manager.settings.transparency_enabled if hasattr(config_manager.settings, 'transparency_enabled') else True)
        
        # Create UI
        self._create_ui()
        
        # Initialize transparency manager
        self.transparency_manager = TransparencyManager(
            self.winfo_toplevel(),  # Use the top-level window
            opacity=config_manager.settings.transparency_level,
            enabled=self.transparency_var.get()
        )
        
        # Set focus to tracking number field
        self._focus_tracking_field()
    
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
        returns_data_button.pack(side='left', padx=80)
        
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
            
            # Validate tracking number
            if not tracking_number:
                self._update_status("Please enter a tracking number", 'red')
                messagebox.showerror("Missing Tracking Number", "A tracking number is required.\n\nPlease enter a valid tracking number.")
                return "break"  # Prevent default Enter behavior
            
            # Validate tracking number length
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
                
                # Enable and move focus to SKU field
                self.field_widgets["SKU:"]["widget"].config(state="normal")
                self.field_widgets["SKU:"]["widget"].focus_set()
                
                # Clear any previous error messages
                self._update_status("", 'black')
            
            return "break"  # Prevent default Enter behavior
        
        # Bind Enter key to the tracking number field
        self.field_widgets["Tracking Number:"]["widget"].bind("<Return>", on_tracking_enter)
        
        # Add functionality to print label when Enter is pressed in the SKU field
        def on_sku_enter(event):
            import re
            # Verify tracking number is present before proceeding
            tracking_number = self.tracking_var.get().strip()
            if not tracking_number:
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
        
        # Validate tracking number - now required in all cases
        if not tracking_number:
            self._update_status("Please enter a tracking number", 'red')
            # Show the error dialog
            messagebox.showerror("Missing Tracking Number", "A tracking number is required.\n\nPlease enter a valid tracking number.")
            
            # Use keyboard shortcut to select all text after dialog closes
            tracking_field = self.field_widgets["Tracking Number:"]["widget"]
            tracking_field.focus_set()
            self.after(100, lambda: self._select_all_with_keyboard(tracking_field))
            return False, "No tracking number provided"
        
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
        
        # Validate tracking number length
        if len(tracking_number) <= 12:
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
            
            # Clear input fields for next label
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
                
                # Clear input fields for next label
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
        
        # Set focus to the tracking number field
        self._focus_tracking_field()
    
    def _focus_tracking_field(self):
        """Set focus to the tracking number field if it's empty"""
        if not self.tracking_var.get().strip():
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

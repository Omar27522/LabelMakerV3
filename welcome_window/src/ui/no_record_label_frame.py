"""
Frame-based implementation of the No Record Label functionality.
This module provides a frame that can be embedded in the welcome window
to print labels without recording them in logs or Google Sheets.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import datetime
import pyautogui
import time

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_title_section, create_colored_button, create_form_field_group
from src.utils.barcode_operations import find_or_create_barcode, print_barcode
from src.utils.file_utils import directory_exists, file_exists

class NoRecordLabelFrame(tk.Frame):
    """Frame-based implementation of the No Record Label functionality"""
    
    def __init__(self, parent, config_manager, return_to_welcome_callback):
        """
        Initialize the No Record Label frame
        
        Args:
            parent: Parent widget
            config_manager: Configuration manager instance
            return_to_welcome_callback: Callback to return to the welcome screen
        """
        super().__init__(parent, bg='white')
        
        # Store references
        self.parent = parent
        self.config_manager = config_manager
        self.return_to_welcome_callback = return_to_welcome_callback
        
        # Initialize variables
        self.sku_var = tk.StringVar()
        self.mirror_print_var = tk.BooleanVar(value=config_manager.settings.mirror_print if hasattr(config_manager.settings, 'mirror_print') else False)
        self.stay_on_top_var = tk.BooleanVar(value=config_manager.settings.stay_on_top if hasattr(config_manager.settings, 'stay_on_top') else False)
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Create title section - function returns (frame, title_label, subtitle_label)
        title_frame, self.title_label, _ = create_title_section(
            self, 
            "NO Record Label", 
            "Print labels without recording them"
        )
        title_frame.pack(fill='x', padx=20, pady=(20, 0))
        
        # Add a return button in the top-left corner
        return_frame = tk.Frame(self, bg='white')
        return_frame.pack(fill='x', padx=10, pady=5)
        
        return_button = tk.Button(
            return_frame,
            text="← Return",
            font=("Arial", 10, "bold"),
            bg="#4CAF50",  # Green
            fg="white",
            command=self.return_to_welcome_callback,
            width=10,
            height=1
        )
        return_button.pack(side='left')
        
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
        
        pin_label = tk.Label(pin_frame, text="Pin:", bg='white', font=('TkDefaultFont', 10))
        pin_label.pack(side=tk.LEFT, padx=(0, 5))
        
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
        
        # Create a frame for the content with padding
        content_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Create form fields
        fields = [
            {
                "label": "SKU:",
                "var_type": "string",
                "default": "",
                "width": 30,
                "required": True
            }
        ]
        
        form_frame = tk.Frame(content_frame, bg='white')
        form_frame.pack(fill='x', pady=10)
        
        self.field_widgets = create_form_field_group(form_frame, fields)
        
        # Store references to the variables
        self.sku_var = self.field_widgets["SKU:"]["var"]
        
        # Add focus to SKU field
        self.field_widgets["SKU:"]["widget"].focus_set()
        
        # Add Enter key binding for SKU field
        def on_sku_enter(event):
            self._print_label()
            return "break"  # Prevent default behavior
        
        self.field_widgets["SKU:"]["widget"].bind("<Return>", on_sku_enter)
        
        # Create options frame for toggle buttons
        options_frame = tk.Frame(content_frame, bg='white')
        options_frame.pack(fill='x', pady=(10, 0))
        
        # Mirror print toggle
        def toggle_mirror_print():
            current_state = self.mirror_print_var.get()
            self.mirror_btn.config(
                bg='#90EE90' if current_state else '#C71585',  # Green if on, Pink if off
                relief='sunken' if current_state else 'raised'
            )
            # Update the config setting
            self.config_manager.settings.mirror_print = current_state
            self.config_manager.save_settings()
        
        # Set initial color based on current setting
        initial_color = '#90EE90' if self.mirror_print_var.get() else '#C71585'
        initial_relief = 'sunken' if self.mirror_print_var.get() else 'raised'
        
        # Create mirror button with label
        mirror_label = tk.Label(options_frame, text="Mirror Print:", bg='white', font=('TkDefaultFont', 10))
        mirror_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.mirror_btn = tk.Button(options_frame, text=" ", bg=initial_color, 
                               relief=initial_relief, width=3,
                               font=('TkDefaultFont', 14), anchor='center')
        
        self.mirror_btn.config(
            command=lambda: [self.mirror_print_var.set(not self.mirror_print_var.get()),
                           toggle_mirror_print()]
        )
        self.mirror_btn.pack(side=tk.LEFT, padx=2)
        
        # Create button frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        # Create Print Button
        print_button = create_colored_button(
            button_frame,
            text="Print Label",
            color="#4CAF50",  # Green
            hover_color="#A5D6A7",  # Light Green
            command=self._print_label,
            big=True
        )
        print_button.pack(side='left', padx=(0, 10))
        
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
        # Get values from form
        sku = self.sku_var.get().strip()
        
        # Validate SKU
        if not sku:
            self._update_status("Please enter an SKU", 'red')
            self.field_widgets["SKU:"]["widget"].focus_set()
            return
        
        # Check if labels directory exists
        labels_dir = self.config_manager.settings.last_directory
        if not directory_exists(labels_dir):
            self._update_status(f"Labels directory not found: {labels_dir}", 'red')
            return
        
        # Get mirror print setting from the toggle button
        mirror_print = self.mirror_print_var.get()
        
        # Define a status callback function to update the status label
        def update_status(message, color):
            self._update_status(message, color)
            self.update()
        
        # Try to find the barcode file for the SKU
        barcode_file = None
        
        try:
            # Look for the SKU file directly without creating a new one
            sku_file = os.path.join(labels_dir, f"{sku}.txt")
            
            if file_exists(sku_file):
                barcode_file = sku_file
            else:
                # Try to find it in the database
                success, barcode_path, is_new, message = find_or_create_barcode(
                    "",  # No tracking number
                    sku,
                    labels_dir,
                    status_callback=update_status
                )
                
                if success:
                    barcode_file = barcode_path
                else:
                    self._update_status(f"Error: {message}", 'red')
                    messagebox.showerror("Error", f"Could not find a label for SKU: {sku}")
                    return
            
            # Print the barcode if we found it
            if barcode_file:
                print("Starting print process...")
                
                # First start the print process
                success, message = print_barcode(
                    barcode_file,
                    mirror_print,
                    update_status
                )
                
                # Wait longer before trying to handle the print dialog
                # This ensures the dialog is fully loaded before we try to interact with it
                self.after(1000, self._press_enter_for_print_dialog)
                
                if success:
                    # Show success message
                    self._show_success_message(f"Label for {sku} printed successfully!")
                    
                    # Clear input fields for next label
                    self._clear_fields()
                else:
                    self._update_status(f"Error: {message}", 'red')
            else:
                self._update_status(f"Error: No label file found for SKU: {sku}", 'red')
                messagebox.showerror("Error", f"No label file found for SKU: {sku}")
        
        except Exception as e:
            self._update_status(f"Error: {str(e)}", 'red')
            messagebox.showerror("Error", f"An error occurred while printing: {str(e)}")
    
    def _press_enter_for_print_dialog(self):
        """Press Enter to confirm the print dialog"""
        try:
            # Just press Enter once to confirm the print dialog
            # This simpler approach may prevent confusing the dialog
            print("Pressing Enter to confirm print dialog...")
            pyautogui.press('enter')
            print("Enter key pressed for print dialog")
        except Exception as e:
            print(f"Error pressing Enter: {str(e)}")
    
    def _clear_fields(self):
        """Clear all input fields"""
        self.sku_var.set("")
        self.field_widgets["SKU:"]["widget"].focus_set()
        self._update_status("", 'black')  # Clear status
    
    def _update_status(self, message, color='black'):
        """Update the status label"""
        self.status_var.set(message)
        self.status_label.config(fg=color)
    
    def _show_success_message(self, message):
        """Show a success message in the title and status"""
        # Update the title with a success message
        self.title_label.config(text=message, fg='green')
        
        # Schedule to revert the title after 3 seconds
        self.after(3000, lambda: self.title_label.config(text="NO Record Label", fg='#333333'))
        
        # Also update the status
        self._update_status(message, 'green')

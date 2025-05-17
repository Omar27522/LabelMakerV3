"""
Exceptions Dialog for handling exception cases.
This module provides a dialog for confirming exception processing.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from functools import partial
import win32gui

from src.utils.exceptions import ExceptionsManager

logger = logging.getLogger(__name__)

class ExceptionsDialog:
    """Dialog for confirming exception processing"""
    
    def __init__(self, parent, config_manager, on_submit_callback=None, tracking_number=None):
        """
        Initialize the exceptions dialog.
        
        Args:
            parent: The parent window
            config_manager: The application's configuration manager
            on_submit_callback: Callback function to call when confirmed
            tracking_number: Optional tracking number associated with this exception
        """
        self.parent = parent
        self.config_manager = config_manager
        self.on_submit_callback = on_submit_callback
        self.tracking_number = tracking_number
        
        # Get the exceptions manager instance
        self.exceptions_manager = ExceptionsManager.get_instance(config_manager)
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Process Exception")
        self.dialog.geometry("400x250")  # Adjusted height for dropdown style
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="white")
        
        # Set dialog icon
        try:
            self.dialog.iconbitmap("icon.ico")  # Use your application icon if available
        except:
            pass  # If icon not found, use default
        
        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Initialize exception type variable
        # Check if the parent has a default exception type set
        default_type = "Return to Sender"  # Default to Return to Sender
        if hasattr(parent, 'default_exception_type') and parent.default_exception_type:
            default_type = parent.default_exception_type
            
        self.exception_type_var = tk.StringVar(value=default_type)
        
        # Register this dialog with the exceptions manager
        try:
            # Get the window handle
            self.hwnd = win32gui.FindWindow(None, "Process Exception")
            if self.hwnd and self.tracking_number:
                # Register with exceptions manager
                self.exceptions_manager.register_exception_dialog(
                    self.exception_type_var.get().lower(), 
                    self.tracking_number, 
                    self.hwnd
                )
                
                # Set up protocol handler for window close
                self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception as e:
            logger.error(f"Error registering dialog with exceptions manager: {str(e)}")
        
        # Center the dialog on the parent window
        self.center_on_parent()
        
        # Create the UI elements
        self._create_ui()
        
        # Force focus to this dialog
        self.dialog.focus_force()
        self.dialog.lift()
        
    def center_on_parent(self):
        """Center the dialog on the parent window"""
        parent = self.parent
        
        # Get the parent window dimensions and position
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calculate position for the dialog
        dialog_width = 400
        dialog_height = 200
        position_x = parent_x + (parent_width - dialog_width) // 2
        position_y = parent_y + (parent_height - dialog_height) // 2
        
        # Set the position
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{position_x}+{position_y}")
        
    def _create_ui(self):
        """Create the user interface elements"""
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = tk.Label(
            main_frame,
            text="Process Exception",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title_label.pack(pady=(0, 15))
        
        # Exception type label
        type_label = tk.Label(
            main_frame,
            text="Exception Type:",
            font=("Arial", 12, "bold"),
            anchor='w',
            bg="white"
        )
        type_label.pack(fill=tk.X, pady=(0, 5))
        
        # Define exception types with their colors
        self.exception_types = [
            {"name": "SKU Mismatch", "bg": "#FFAEC9"},  # Pink
            {"name": "RMA on label but not in system", "bg": "#FFEAA0"},  # Light yellow
            {"name": "Fraudulent / Suspicious package / E", "bg": "#A0E8E5"},  # Light teal
            {"name": "Return to Sender", "bg": "#A0E8A0"}  # Light green
        ]
        
        # Create a frame for the exception type dropdown
        exception_frame = tk.Frame(main_frame, bg="white")
        exception_frame.pack(fill=tk.X, pady=5)
        
        # Create a custom dropdown-style listbox
        # Set default to Return to Sender (index 3)
        self.selected_exception_index = 3
        
        # Create the main selection display box
        self.selection_display = tk.Frame(exception_frame, bg=self.exception_types[3]["bg"], 
                                         height=40, relief=tk.SUNKEN, borderwidth=1)
        self.selection_display.pack(fill=tk.X, pady=2)
        
        # Add the text to the selection display
        self.selection_label = tk.Label(self.selection_display, 
                                       text=self.exception_types[3]["name"],
                                       font=("Arial", 12, "bold"),
                                       bg=self.exception_types[3]["bg"])
        self.selection_label.pack(fill=tk.BOTH, expand=True, pady=8)
        
        # Create dropdown container (initially hidden)
        self.dropdown_frame = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, borderwidth=1)
        
        # Create option buttons in the dropdown
        self.option_buttons = []
        for i, exception in enumerate(self.exception_types):
            btn = tk.Button(
                self.dropdown_frame,
                text=exception["name"],
                bg=exception["bg"],
                font=("Arial", 12),
                relief=tk.FLAT,
                borderwidth=1,
                height=2,
                anchor="center",
                command=partial(self._select_exception_type, i)
            )
            btn.pack(fill=tk.X)
            self.option_buttons.append(btn)
        
        # Bind click event to show/hide dropdown
        self.selection_display.bind("<Button-1>", self._toggle_dropdown)
        self.selection_label.bind("<Button-1>", self._toggle_dropdown)
        
        # Bind keyboard navigation
        self.dialog.bind("<Up>", self._previous_option)
        self.dialog.bind("<Down>", self._next_option)
        self.dialog.bind("<Return>", self._on_submit)
        
        # Information label
        info_label = tk.Label(
            main_frame,
            text="Click 'Process' to open the exceptions page.\nClick 'Close Tab' when finished.",
            font=("Arial", 12),
            justify=tk.CENTER,
            bg="white"
        )
        info_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack(pady=15)
        
        # Process button
        process_button = tk.Button(
            buttons_frame,
            text="Process",
            command=self._on_submit,
            bg="#4CAF50",  # Green
            fg="white",
            font=("Arial", 12, "bold"),
            width=10,
            relief=tk.RAISED,
            borderwidth=2
        )
        process_button.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self._on_cancel,
            bg="#f44336",  # Red
            fg="white",
            font=("Arial", 12, "bold"),
            width=10,
            relief=tk.RAISED,
            borderwidth=2
        )
        cancel_button.pack(side=tk.LEFT, padx=10)
        
    def _toggle_dropdown(self, event=None):
        """Show or hide the dropdown"""
        if self.dropdown_frame.winfo_ismapped():
            self.dropdown_frame.pack_forget()
        else:
            self.dropdown_frame.pack(fill=tk.X, pady=0)
    
    def _previous_option(self, event=None):
        """Select the previous option"""
        index = (self.selected_exception_index - 1) % len(self.exception_types)
        self._select_exception_type(index)
        
    def _next_option(self, event=None):
        """Select the next option"""
        index = (self.selected_exception_index + 1) % len(self.exception_types)
        self._select_exception_type(index)
        
    def _select_exception_type(self, index):
        """Select an exception type by index"""
        self.selected_exception_index = index
        exception = self.exception_types[index]
        self.exception_type_var.set(exception["name"])
        
        # Update the selection display
        self.selection_label.config(text=exception["name"], bg=exception["bg"])
        self.selection_display.config(bg=exception["bg"])
        
        # Hide the dropdown after selection
        if self.dropdown_frame.winfo_ismapped():
            self.dropdown_frame.pack_forget()
    
    def _on_submit(self, event=None):
        """Handle the process button click"""
        # Get the selected exception type
        exception = self.exception_types[self.selected_exception_index]
        exception_type = exception["name"].lower()
        logger.info(f"Exception processing confirmed for type: {exception_type}")
        
        # Call the callback if provided
        if self.on_submit_callback:
            self.on_submit_callback(exception_type)
            
        # Close the dialog using _on_close to ensure proper unregistration
        self._on_close()
        
    def _on_cancel(self):
        """Handle the cancel button click"""
        logger.info("Exception processing canceled")
        self._on_close()
        
    def _on_close(self):
        """Handle the dialog close event"""
        # Unregister from exceptions manager
        if hasattr(self, 'tracking_number') and self.tracking_number:
            try:
                self.exceptions_manager.unregister_exception_dialog(
                    self.exception_type_var.get().lower(),
                    self.tracking_number
                )
            except Exception as e:
                logger.error(f"Error unregistering dialog: {str(e)}")
        
        # Destroy the dialog
        self.dialog.destroy()

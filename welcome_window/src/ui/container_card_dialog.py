"""
Container Card Dialog for receiving shipments.
This module provides a dialog for entering container card numbers during receive operations.
"""
import tkinter as tk
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)

class ContainerCardDialog:
    """Dialog for entering container card numbers"""
    
    def __init__(self, parent, config_manager, on_submit_callback=None):
        """
        Initialize the container card dialog.
        
        Args:
            parent: The parent window
            config_manager: The application's configuration manager
            on_submit_callback: Callback function to call when a container card is submitted
        """
        self.parent = parent
        self.config_manager = config_manager
        self.on_submit_callback = on_submit_callback
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Container Card Entry")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on the parent window
        self.center_on_parent()
        
        # Create the UI elements
        self._create_ui()
        
        # Set focus to the entry field
        self.container_card_entry.focus_set()
        
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
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = tk.Label(
            main_frame,
            text="Enter Container Card Number",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Container card entry
        entry_frame = tk.Frame(main_frame)
        entry_frame.pack(fill=tk.X, pady=10)
        
        container_card_label = tk.Label(
            entry_frame,
            text="Container Card #:",
            font=("Arial", 12)
        )
        container_card_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.container_card_var = tk.StringVar()
        self.container_card_entry = tk.Entry(
            entry_frame,
            textvariable=self.container_card_var,
            font=("Arial", 12),
            width=20
        )
        self.container_card_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind Enter key to submit
        self.container_card_entry.bind("<Return>", self._on_submit)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        # Submit button
        submit_button = tk.Button(
            buttons_frame,
            text="Submit",
            command=self._on_submit,
            bg="#4CAF50",  # Green
            fg="white",
            font=("Arial", 12),
            width=10
        )
        submit_button.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self._on_cancel,
            bg="#f44336",  # Red
            fg="white",
            font=("Arial", 12),
            width=10
        )
        cancel_button.pack(side=tk.LEFT, padx=10)
        
    def _on_submit(self, event=None):
        """Handle the submit button click or Enter key press"""
        container_card = self.container_card_var.get().strip()
        
        if not container_card:
            messagebox.showerror("Error", "Please enter a container card number.")
            return
            
        # Validate container card format if needed
        # For example, you might want to check if it matches a specific pattern
        
        logger.info(f"Container card submitted: {container_card}")
        
        # Call the callback if provided
        if self.on_submit_callback:
            self.on_submit_callback(container_card)
            
        # Close the dialog
        self.dialog.destroy()
        
    def _on_cancel(self):
        """Handle the cancel button click"""
        logger.info("Container card entry canceled")
        self.dialog.destroy()

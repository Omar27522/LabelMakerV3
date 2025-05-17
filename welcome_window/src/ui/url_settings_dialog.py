"""
URL Settings Dialog for configuring application URLs.
This module provides a dialog for managing URLs used in the application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import re

logger = logging.getLogger(__name__)

class URLSettingsDialog:
    """Dialog for configuring application URLs"""
    
    def __init__(self, parent, config_manager, on_save_callback=None):
        """
        Initialize the URL settings dialog.
        
        Args:
            parent: The parent window
            config_manager: The application's configuration manager
            on_save_callback: Callback function to call when settings are saved
        """
        self.parent = parent
        self.config_manager = config_manager
        self.on_save_callback = on_save_callback
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("URL Settings")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog on the parent window
        self.center_on_parent()
        
        # Create the UI elements
        self._create_ui()
        
    def center_on_parent(self):
        """Center the dialog on the parent window"""
        parent = self.parent
        
        # Get the parent window dimensions and position
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calculate position for the dialog
        dialog_width = 600
        dialog_height = 500
        position_x = parent_x + (parent_width - dialog_width) // 2
        position_y = parent_y + (parent_height - dialog_height) // 2
        
        # Set the position
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{position_x}+{position_y}")
        
    def _create_ui(self):
        """Create the user interface elements"""
        # Main frame with padding
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = tk.Label(
            main_frame,
            text="URL Settings",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create a frame for the URL fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add a scrollbar
        canvas = tk.Canvas(fields_frame)
        scrollbar = ttk.Scrollbar(fields_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # URL field variables
        self.url_vars = {
            "scan_url": tk.StringVar(value=self.config_manager.settings.scan_url or ""),
            "receive_url": tk.StringVar(value=self.config_manager.settings.receive_url or ""),
            "exception_base_url": tk.StringVar(value=self.config_manager.settings.exception_base_url or ""),
            "sku_mismatch_url": tk.StringVar(value=self.config_manager.settings.sku_mismatch_url or ""),
            "rma_missing_url": tk.StringVar(value=self.config_manager.settings.rma_missing_url or ""),
            "suspicious_package_url": tk.StringVar(value=self.config_manager.settings.suspicious_package_url or ""),
            "return_to_sender_url": tk.StringVar(value=self.config_manager.settings.return_to_sender_url or "")
        }
        
        # URL field labels
        url_labels = {
            "scan_url": "Scan Page URL:",
            "receive_url": "Receive Page URL:",
            "exception_base_url": "Exception Base URL:",
            "sku_mismatch_url": "SKU Mismatch URL:",
            "rma_missing_url": "RMA Missing URL:",
            "suspicious_package_url": "Suspicious Package URL:",
            "return_to_sender_url": "Return to Sender URL:"
        }
        
        # Create URL fields
        row = 0
        for key, label_text in url_labels.items():
            # Create label
            label = ttk.Label(
                scrollable_frame,
                text=label_text,
                font=("Arial", 11)
            )
            label.grid(row=row, column=0, sticky="w", padx=5, pady=5)
            
            # Create entry
            entry = ttk.Entry(
                scrollable_frame,
                textvariable=self.url_vars[key],
                width=50
            )
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            
            row += 1
            
            # Add a separator after the base URLs
            if key == "exception_base_url":
                separator = ttk.Separator(scrollable_frame, orient="horizontal")
                separator.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
                row += 1
                
                # Add a label for the exception-specific URLs
                exception_label = ttk.Label(
                    scrollable_frame,
                    text="Exception-Specific URLs (override base URL if provided):",
                    font=("Arial", 11, "bold")
                )
                exception_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
                row += 1
        
        # Add a note about URL formats
        note_label = ttk.Label(
            scrollable_frame,
            text="Note: URLs should include the protocol (e.g., https://) and domain.",
            font=("Arial", 10, "italic"),
            foreground="gray"
        )
        note_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=10)
        
        # Add a note about empty values
        empty_note_label = ttk.Label(
            scrollable_frame,
            text="Leave fields empty to use default values.",
            font=("Arial", 10, "italic"),
            foreground="gray"
        )
        empty_note_label.grid(row=row+1, column=0, columnspan=2, sticky="w", padx=5, pady=0)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        # Save button
        save_button = tk.Button(
            buttons_frame,
            text="Save",
            command=self._on_save,
            bg="#4CAF50",  # Green
            fg="white",
            font=("Arial", 12),
            width=10
        )
        save_button.pack(side=tk.LEFT, padx=10)
        
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
        
        # Reset button
        reset_button = tk.Button(
            buttons_frame,
            text="Reset to Defaults",
            command=self._on_reset,
            bg="#2196F3",  # Blue
            fg="white",
            font=("Arial", 12)
        )
        reset_button.pack(side=tk.LEFT, padx=10)
        
    def _validate_urls(self):
        """Validate the URL formats"""
        # URL regex pattern
        url_pattern = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
        
        invalid_urls = []
        
        # Check each URL
        for key, var in self.url_vars.items():
            url = var.get().strip()
            if url and not re.match(url_pattern, url):
                invalid_urls.append(key)
        
        return invalid_urls
        
    def _on_save(self):
        """Handle the save button click"""
        # Validate URLs
        invalid_urls = self._validate_urls()
        if invalid_urls:
            # Format the invalid URLs for display
            formatted_urls = "\n".join([f"- {key}" for key in invalid_urls])
            messagebox.showerror(
                "Invalid URLs",
                f"The following URLs have invalid formats:\n{formatted_urls}\n\nPlease correct them or leave them empty."
            )
            return
        
        # Update settings
        self.config_manager.settings.scan_url = self.url_vars["scan_url"].get().strip()
        self.config_manager.settings.receive_url = self.url_vars["receive_url"].get().strip()
        self.config_manager.settings.exception_base_url = self.url_vars["exception_base_url"].get().strip()
        self.config_manager.settings.sku_mismatch_url = self.url_vars["sku_mismatch_url"].get().strip()
        self.config_manager.settings.rma_missing_url = self.url_vars["rma_missing_url"].get().strip()
        self.config_manager.settings.suspicious_package_url = self.url_vars["suspicious_package_url"].get().strip()
        self.config_manager.settings.return_to_sender_url = self.url_vars["return_to_sender_url"].get().strip()
        
        # Save settings
        success = self.config_manager.save_settings()
        
        if success:
            logger.info("URL settings saved successfully")
            messagebox.showinfo("Success", "URL settings saved successfully.")
            
            # Call the callback if provided
            if self.on_save_callback:
                self.on_save_callback()
                
            # Close the dialog
            self.dialog.destroy()
        else:
            logger.error("Failed to save URL settings")
            messagebox.showerror("Error", "Failed to save URL settings.")
    
    def _on_cancel(self):
        """Handle the cancel button click"""
        logger.info("URL settings canceled")
        self.dialog.destroy()
        
    def _on_reset(self):
        """Handle the reset button click"""
        # Confirm reset
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all URLs to default values?"):
            # Reset all URL variables to empty
            for var in self.url_vars.values():
                var.set("")
            
            logger.info("URL settings reset to defaults")

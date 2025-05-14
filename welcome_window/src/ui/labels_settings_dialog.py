"""
Labels Settings Dialog for the Label Maker application.
This module provides a dialog for managing label settings, including import and export options.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import threading

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_colored_button
from src.utils.label_database import import_csv

class LabelsSettingsDialog(tk.Toplevel):
    """Dialog for managing label settings"""
    
    def __init__(self, parent, config_manager, callback=None):
        """
        Initialize the Labels Settings Dialog
        
        Args:
            parent: Parent widget
            config_manager: Configuration manager instance
            callback: Function to call after successful import/export
        """
        super().__init__(parent)
        
        # Store references
        self.parent = parent
        self.config_manager = config_manager
        self.callback = callback
        
        # Configure dialog
        self.title("Label Settings")
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Set dialog position centered on parent
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
        
        # Status variable
        self.status_var = tk.StringVar(value="Ready")
        
        # Create UI
        self._create_ui()
        
        # Make dialog modal
        self.focus_set()
        self.wait_window()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Create main container with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Label Database Settings",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Create buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=10)
        
        # Import button
        import_button = create_colored_button(
            buttons_frame,
            text="Import CSV Data",
            color="#4CAF50",
            hover_color="#45a049",
            command=self._import_csv
        )
        import_button.pack(fill='x', pady=5)
        

        
        # Separator
        ttk.Separator(main_frame).pack(fill='x', pady=15)
        
        # Close button
        close_button = ttk.Button(
            main_frame,
            text="Close",
            command=self.destroy
        )
        close_button.pack(side='right', pady=10)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', side='bottom', pady=(10, 0))
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side='left')
    
    def _import_csv(self):
        """Import label metadata from a CSV file"""
        # Get file path
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import CSV"
        )
        
        if not file_path:
            return
        
        # Ask if we should replace existing data
        replace = messagebox.askyesno(
            "Import Options",
            "Do you want to replace existing data? Click 'No' to append to existing data."
        )
        
        # Update status
        self.status_var.set("Importing data...")
        self.update_idletasks()
        
        # Define import function for threading
        def import_thread():
            try:
                # Import the CSV
                success, count = import_csv(file_path, replace)
                
                # Update UI from main thread
                self.after(0, lambda: self._import_complete(success, count))
            except Exception as e:
                # Handle errors
                self.after(0, lambda: self._import_error(str(e)))
        
        # Start import in a separate thread
        threading.Thread(target=import_thread).start()
    
    def _import_complete(self, success, count):
        """Handle completion of CSV import"""
        if success:
            messagebox.showinfo("Import Complete", f"Successfully imported {count} records")
            # Call callback if provided
            if self.callback:
                self.callback()
        else:
            messagebox.showerror("Import Error", "Failed to import data")
        
        # Update status
        self.status_var.set("Ready")
    
    def _import_error(self, error_msg):
        """Handle error during CSV import"""
        messagebox.showerror("Import Error", f"Error importing data: {error_msg}")
        self.status_var.set("Ready")
    


def create_labels_settings_dialog(parent, config_manager, callback=None):
    """
    Create and return a Labels Settings Dialog
    
    Args:
        parent: Parent widget
        config_manager: Configuration manager instance
        callback: Function to call after successful import/export
        
    Returns:
        LabelsSettingsDialog: The created dialog
    """
    return LabelsSettingsDialog(parent, config_manager, callback)

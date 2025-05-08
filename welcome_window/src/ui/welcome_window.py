import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.config.config_manager import ConfigManager
from src.utils.file_utils import directory_exists, count_files_in_directory, get_project_root, file_exists
from src.utils.ui_utils import center_window
from src.utils.ui_components import (
    create_title_section, create_colored_button, create_button_grid, 
    create_version_label, create_form_field_group, create_status_bar, 
    create_sheets_status_display
)
from src.utils.barcode_operations import find_or_create_barcode, print_barcode, process_barcode
from src.utils.sheets_operations import write_to_google_sheet, create_google_sheets_dialog
from src.utils.returns_operations import load_returns_data, update_log_file, create_returns_dialog, create_edit_dialog
from src.utils.settings_operations import create_settings_dialog, update_sheets_status_display
from src.utils.dialog_handlers import (
    create_settings_dialog_handler, create_google_sheets_dialog_handler
)
from src.ui.create_label_frame import CreateLabelFrame
from src.ui.returns_data_dialog import create_returns_data_dialog
from src.ui.jdl_automation_frame import JDLAutomationFrame

# Third-party imports
import pyautogui
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import logging
import subprocess
import time

class WindowState:
    """Class to track and manage window state across the application"""
    
    def __init__(self):
        """Initialize the window state"""
        self.windows = []
        self.active_window = None
    
    def add_window(self, window):
        """Add a window to the state tracker"""
        self.windows.append(window)
        self.active_window = window
    
    def remove_window(self, window):
        """Remove a window from the state tracker"""
        if window in self.windows:
            self.windows.remove(window)
            
        # Update active window
        if self.windows:
            self.active_window = self.windows[-1]
        else:
            self.active_window = None
    
    def get_active_window(self):
        """Get the currently active window"""
        return self.active_window

class WelcomeWindow(tk.Tk):
    """Main welcome window for the Label Maker application"""
    
    def __init__(self):
        """Initialize the welcome window"""
        super().__init__()

        # Initialize window state
        self.window_state = WindowState()
        self.window_state.add_window(self)

        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Initialize stay on top variable
        self.stay_on_top_var = tk.BooleanVar(value=self.config_manager.settings.stay_on_top if hasattr(self.config_manager.settings, 'stay_on_top') else False)
        
        # Track open dialogs to prevent duplicates
        self.open_dialogs = {
            'create_label': None,
            'returns_data': None,
            'settings': None,
            'google_sheets': None
        }

        # Window setup
        self.title("Welcome")
        self.geometry("400x400")  # Window size
        self.resizable(False, False)  # Prevent resizing
        
        # Configure window style
        self.configure(bg='white')
        
        # Remove maximize button but keep minimize
        self.attributes('-toolwindow', 1)  # Remove minimize/maximize buttons
        self.attributes('-toolwindow', 0)  # Restore minimize button
        
        # Create a container frame for different "pages"
        self.container_frame = tk.Frame(self, bg='white')
        self.container_frame.pack(fill='both', expand=True)
        
        # Create the main content frame (welcome screen)
        self.welcome_frame = tk.Frame(self.container_frame, bg='white')
        self.welcome_frame.pack(fill='both', expand=True)
        
        # Add title
        self._create_title_section()
        
        # Create buttons in the welcome frame
        self._create_button_section()
        
        # Add version label
        self._create_version_label()
        
        # Create a status bar frame at the bottom of the welcome frame
        self.status_bar_frame = tk.Frame(self.welcome_frame, bg='white')
        self.status_bar_frame.pack(side='bottom', fill='x')
        
        # Create Google Sheets status display
        self.sheets_status_frame, self.sheets_status_label = create_sheets_status_display(
            self.status_bar_frame,
            "Not Connected",
            "red"
        )
        self.sheets_status_frame.pack(side='left', anchor='sw', padx=10, pady=10)
        
        # Initialize the Google Sheets status display
        self._update_sheets_status_display()
        
        # Create the create label frame (initially hidden)
        self.create_label_frame = None
    
    def _create_title_section(self):
        """Create the title section of the window"""
        # Get the labels directory from config
        labels_dir = self.config_manager.settings.last_directory
        
        # Count labels if directory exists
        label_count = 0
        if labels_dir and os.path.exists(labels_dir):
            # Count files in the directory (assuming all files are labels)
            label_count = count_files_in_directory(labels_dir)
        
        # Create title section with label count
        title_frame, self.label_count_label, _ = create_title_section(
            self.welcome_frame, 
            f"{label_count} Labels", 
            "Label Maker V3"
        )
        
        title_frame.pack(pady=20)
    
    def _create_button_section(self):
        """Create the button section of the window"""
        # Button colors (Material Design)
        colors = {
            'user': ('#4CAF50', '#A5D6A7'),        # Green, Light Green
            'management': ('#2196F3', '#90CAF9'),   # Blue, Light Blue
            'labels': ('#FF9800', '#FFCC80'),       # Orange, Light Orange
            'settings': ('#9E9E9E', '#E0E0E0')      # Gray, Light Gray
        }
        
        # Define button specifications
        button_specs = [
        {
            'text': 'User',
            'colors': colors['user'],
            'command': self.user_action,
            'big': True,
            'grid': (0, 0, 2, 1),
            'padx': 15,
            'pady': 10,
            'sticky': 'nsew'
        },
        {
            'text': 'Management',
            'colors': colors['management'],
            'command': self.management_action,
            'grid': (0, 1, 1, 1),
            'padx': 10,
            'pady': 5,
            'sticky': 'nsew'
        },
        {
            'text': 'Labels',
            'colors': colors['labels'],
            'command': self.labels_action,
            'grid': (1, 1, 1, 1),
            'padx': 10,
            'pady': 5,
            'sticky': 'nsew'
        },
        {
            'text': 'Settings',
            'colors': colors['settings'],
            'command': self.settings_action,
            'grid': (2, 0, 1, 2),
            'padx': 10,
            'pady': 5,
            'sticky': 'ew'
        }
    ]
        
        # Create button grid
        button_frame, buttons = create_button_grid(self.welcome_frame, button_specs, num_columns=2)
        
        # Configure grid weights
        button_frame.grid_columnconfigure(0, weight=3)  # More weight to User button column
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        
        # Store buttons for later reference
        self.user_btn = buttons['user']
        self.management_btn = buttons['management']
        self.labels_btn = buttons['labels']
        self.settings_btn = buttons['settings']
        
        # Pack the button frame
        button_frame.pack(expand=True, padx=20)
    
    def _create_button(self, parent, text, color_pair, command, big=False):
        """
        Create a colored button with hover effect
        
        Args:
            parent: Parent widget
            text (str): Button text
            color_pair (tuple): Tuple of (normal_color, hover_color)
            command: Button command
            big (bool): Whether this is a big button
            
        Returns:
            tk.Button: The created button
        """
        color, light_color = color_pair
        return create_colored_button(parent, text, color, light_color, command, big)
    
    def _create_version_label(self):
        """Create the version label"""
        # Create version label in the bottom-right corner
        version_frame = tk.Frame(self.welcome_frame, bg='white')
        version_frame.pack(side='right', anchor='se', padx=10, pady=10)
        
        # Make the "Ver." part clickable
        ver_label = tk.Label(
            version_frame, 
            text="Ver.", 
            font=("Arial", 8),
            fg="blue",
            cursor="hand2",
            bg='white'
        )
        ver_label.pack(side='left')
        ver_label.bind("<Button-1>", lambda e: self.no_record_label_action())
        
        # Add underline when hovering
        def on_enter(e):
            ver_label.config(font=("Arial", 8, "underline"))
        def on_leave(e):
            ver_label.config(font=("Arial", 8))
        
        ver_label.bind("<Enter>", on_enter)
        ver_label.bind("<Leave>", on_leave)
        
        # Version number (not clickable)
        version_num_label = tk.Label(
            version_frame, 
            text="1.0.1.1", 
            font=("Arial", 8),
            bg='white'
        )
        version_num_label.pack(side='left')
    
    def user_action(self):
        """Handle the User button click"""
        try:
            # Check if labels directory is set
            if not self.config_manager.settings.last_directory:
                messagebox.showerror("Error", "Please set the labels directory in Settings first.")
                return
            
            # Check if dialog is already open
            if self.open_dialogs['create_label'] is not None:
                # Bring to front
                self.open_dialogs['create_label'].lift()
                self.open_dialogs['create_label'].focus_force()
                return
                
            # Hide the welcome frame
            self.welcome_frame.pack_forget()
            
            # Create the Create Label frame
            create_label_frame = CreateLabelFrame(
                self.container_frame, 
                self.config_manager, 
                self.update_label_count,
                self.return_to_welcome
            )
            create_label_frame.pack(fill='both', expand=True)
            
            # Store reference to the frame
            self.open_dialogs['create_label'] = create_label_frame
            
            # Update the window title
            self.title("Create Label")
            
            # Apply stay-on-top setting if enabled
            if self.stay_on_top_var.get():
                self.attributes('-topmost', True)
                self.lift()
                self.focus_force()
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def management_action(self):
        """Handler for Management button click"""
        try:
            # Check if labels directory is set and exists
            if not self.config_manager.settings.last_directory or not directory_exists(self.config_manager.settings.last_directory):
                messagebox.showinfo("Labels Required", 
                    "Please select a Labels directory before managing files.\n\n"
                    "Click the 'Settings' button to set your Labels directory.")
                return
                
            # Get the path to the Label Maker main.pyw file
            project_root = get_project_root()
            label_maker_dir = os.path.join(project_root, 'Label Maker')
            label_maker_main = os.path.join(label_maker_dir, 'main.pyw')
            
            if not file_exists(label_maker_main):
                messagebox.showerror("Error", f"Label Maker main file not found at: {label_maker_main}")
                return
            
            # Hide welcome window
            self.withdraw()
            
            # Run Label Maker with the --view-files argument
            process = subprocess.Popen([sys.executable, label_maker_main, "--view-files"])
            
            # Set up a check to monitor when the process terminates
            def check_process():
                if process.poll() is not None:
                    # Process has terminated, show welcome window again
                    self.deiconify()
                    self.lift()
                    self.focus_force()
                    return
                # Check again after 1 second
                self.after(1000, check_process)
                
            # Start monitoring the process
            self.after(1000, check_process)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Label Maker: {str(e)}")
            self.deiconify()  # Show welcome window again
    
    def labels_action(self):
        """Handler for Labels button click - Display and edit returns data"""
        # Check if dialog is already open
        if self.open_dialogs['returns_data'] is not None:
            # If dialog exists but was destroyed, remove the reference
            if not self.open_dialogs['returns_data'].winfo_exists():
                self.open_dialogs['returns_data'] = None
            else:
                # Dialog exists, bring it to front
                dialog = self.open_dialogs['returns_data']
                dialog.deiconify()
                dialog.lift()
                dialog.focus_force()
                return
        
        # Create the Returns Data dialog using our new SQLite-based implementation
        dialog = create_returns_data_dialog(self, self.config_manager)
        
        # Store reference to the dialog
        self.open_dialogs['returns_data'] = dialog
        
        # Set up callback for when dialog is closed
        def on_dialog_close():
            self.open_dialogs['returns_data'] = None
            dialog.destroy()
            
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
    
    def settings_action(self):
        """Open settings dialog"""
        # Check if dialog is already open
        if self.open_dialogs['settings'] is not None:
            # If dialog exists but was destroyed, remove the reference
            if not self.open_dialogs['settings'].winfo_exists():
                self.open_dialogs['settings'] = None
            else:
                # Dialog exists, bring it to front
                dialog = self.open_dialogs['settings']
                
                # Check if dialog is minimized (iconified)
                if dialog.state() == 'iconic':
                    dialog.deiconify()  # Restore the window
                
                dialog.lift()
                dialog.focus_force()
                return
        
        # Call the create_settings_dialog_handler function from our dialog_handlers module
        dialog = create_settings_dialog_handler(
            self,
            self.config_manager,
            self.update_label_count
        )
        
        # Store reference to the dialog
        self.open_dialogs['settings'] = dialog
        
        # Set up callback for when dialog is closed
        def on_dialog_close():
            self.open_dialogs['settings'] = None
            dialog.destroy()
            
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
    
    def open_sheets_dialog(self):
        """Open the Google Sheets configuration dialog"""
        # This method will now be called from the Settings dialog
        # We'll keep it for backward compatibility, but it should redirect to Settings
        
        # Check if Settings dialog is already open
        if self.open_dialogs['settings'] is not None and self.open_dialogs['settings'].winfo_exists():
            # Settings dialog exists, bring it to front
            dialog = self.open_dialogs['settings']
            
            # Check if dialog is minimized (iconified)
            if dialog.state() == 'iconic':
                dialog.deiconify()  # Restore the window
            
            dialog.lift()
            dialog.focus_force()
            
            # Trigger the Google Sheets button in the Settings dialog
            if hasattr(dialog, 'sheets_button') and dialog.sheets_button:
                dialog.sheets_button.invoke()
        else:
            # Open Settings dialog first
            self.settings_action()
            
            # Then open Google Sheets dialog from Settings
            if self.open_dialogs['settings'] is not None and self.open_dialogs['settings'].winfo_exists():
                dialog = self.open_dialogs['settings']
                if hasattr(dialog, 'sheets_button') and dialog.sheets_button:
                    dialog.sheets_button.invoke()
    
    def _update_sheets_status_display(self):
        """Update the Google Sheets status display"""
        try:
            # Reload the config manager to get the latest settings
            self.config_manager = ConfigManager()
            
            # Get the sheets configuration
            sheets_config = self.config_manager.settings
            
            # Determine the status text and color
            if not sheets_config.google_sheet_url:
                status_text = "Not Connected"
                status_color = "red"
                sheet_name = None
                on_click = None
            elif sheets_config.google_sheets_connection_status == "Connected":
                status_text = "Connected"
                status_color = "green"
                sheet_name = sheets_config.google_sheet_name
                on_click = self._reset_google_sheets_rows
            else:
                status_text = "Configured (Not Tested)"
                status_color = "orange"
                sheet_name = sheets_config.google_sheet_name
                on_click = self.test_sheets_connection
            
            # Create a new status display with the sheet name
            if hasattr(self, 'sheets_status_frame'):
                self.sheets_status_frame.destroy()
            
            self.sheets_status_frame, self.sheets_status_label = create_sheets_status_display(
                self.status_bar_frame,
                status_text,
                status_color,
                sheet_name
            )
            self.sheets_status_frame.pack(side='left', anchor='sw', padx=10, pady=10)
            
            # Make the label clickable if it has an on_click function
            if on_click:
                self.sheets_status_label.bind("<Button-1>", lambda e: on_click())
                self.sheets_status_label.bind("<Enter>", lambda e: self.sheets_status_label.config(cursor="hand2", font=("Arial", 8, "underline")))
                self.sheets_status_label.bind("<Leave>", lambda e: self.sheets_status_label.config(cursor="", font=("Arial", 8)))
            
        
            # Force UI update
            self.update_idletasks()
        except Exception as e:
            print(f"Error updating sheets status display: {str(e)}")
    
    def _reset_google_sheets_rows(self):
        """Reset Google Sheets rows to default values"""
        # Show confirmation dialog
        confirm = messagebox.askyesno("Reset Google Sheets rows", "Reset Google Sheets rows to default values?")
        
        if not confirm:
            return
            
        try:
            # Reload the config manager to get the latest settings
            self.config_manager = ConfigManager()
            
            # Set all row values to 3
            self.config_manager.settings.google_sheet_tracking_row = 3
            self.config_manager.settings.google_sheet_sku_row = 3
            self.config_manager.settings.google_sheet_steps_row = 3
            
            # Save the settings
            from dataclasses import asdict
            import json
            settings_dict = asdict(self.config_manager.settings)
            with open(self.config_manager.settings_file, 'w') as f:
                json.dump(settings_dict, f, indent=4)
                
            # Update the display
            self._update_sheets_status_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset rows: {str(e)}")
    
    def test_sheets_connection(self):
        """Test the connection to Google Sheets without opening the full dialog"""
        from src.utils.sheets_utils import validate_sheet_url, test_sheet_connection
        from src.utils.file_utils import get_credentials_file_path, file_exists
        from tkinter import messagebox
        
        try:
            # Get Google Sheets configuration
            sheets_config = self.config_manager.settings
            
            # Check if Google Sheets is configured
            if not (sheets_config.google_sheet_url and sheets_config.google_sheet_name):
                messagebox.showerror("Error", "Google Sheets is not fully configured. Please open the settings to configure it.")
                return
            
            # Check for credentials file
            creds_file = get_credentials_file_path()
            if not file_exists(creds_file):
                messagebox.showerror("Error", f"Credentials file not found at:\n{creds_file}\n\nPlease create a service account and download the credentials file.")
                return
            
            # Validate the sheet URL
            is_valid, result = validate_sheet_url(sheets_config.google_sheet_url)
            if not is_valid:
                messagebox.showerror("Error", result)
                return
            
            # Test connection
            success, message = test_sheet_connection(result, sheets_config.google_sheet_name)
            
            if success:
                # Update connection status
                self.config_manager.settings.google_sheets_connection_status = "Connected"
                self.config_manager.save_settings()
                
                # Update the display
                self._update_sheets_status_display()
                
                messagebox.showinfo("Success", "Connected to Google Sheet successfully!")
            else:
                # Update connection status
                self.config_manager.settings.google_sheets_connection_status = "Connection Failed"
                self.config_manager.save_settings()
                
                # Update the display
                self._update_sheets_status_display()
                
                messagebox.showerror("Error", f"Could not connect to Google Sheet.\n\nError: {message}")
                
        except ImportError:
            messagebox.showerror("Error", "Required libraries not installed. Please install gspread and oauth2client to connect to Google Sheets.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{str(e)}")
    
    def update_label_count(self, directory=None):
        """Update the label count display based on the current directory"""
        # Get the labels directory from config
        labels_dir = directory or self.config_manager.settings.last_directory
        
        # Count labels if directory exists using our utility function
        label_count = count_files_in_directory(labels_dir)
        
        # Update the label count display
        if hasattr(self, 'label_count_label'):
            self.label_count_label.config(text=f"{label_count} Labels")
        
        if hasattr(self, 'label_count_var'):
            self.label_count_var.set(str(label_count))
    
    def center_window(self, window=None):
        """
        Center a window on the screen
        
        Args:
            window: Window to center (defaults to self)
        """
        if window is None:
            window = self
            
        center_window(window)
    
    def _save_settings(self, dialog, directory):
        """
        Save settings to the config file
        
        Args:
            dialog: Settings dialog to close on success
            directory: Labels directory path
        """
        try:
            # Validate directory
            if directory and not directory_exists(directory):
                messagebox.showerror("Error", "The selected directory does not exist.")
                return
                
            # Update settings
            self.config_manager.settings.last_directory = directory
            
            # Save settings using the config manager
            if self.config_manager.save_settings():
                # Close dialog
                dialog.destroy()
                
                # Update label count
                self.update_label_count()
            else:
                messagebox.showerror("Error", "Failed to save settings.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving settings: {str(e)}")
    
    def return_to_welcome(self):
        """Return to the welcome screen"""
        # Hide any visible frames
        for widget in self.container_frame.winfo_children():
            widget.pack_forget()
        
        # Show the welcome frame
        self.welcome_frame.pack(fill='both', expand=True)
        
        # Update the window title
        self.title("Welcome")
        
        # Clear references to open dialogs
        for key in self.open_dialogs:
            self.open_dialogs[key] = None
        
        # Update label count
        self.update_label_count()

    def no_record_label_action(self):
        """Handle the No Record Label action when Ver. is clicked"""
        try:
            # Check if labels directory is set
            if not self.config_manager.settings.last_directory:
                messagebox.showerror("Error", "Please set the labels directory in Settings first.")
                return
            
            # Hide the welcome frame
            self.welcome_frame.pack_forget()
            
            # Create the no record label frame if it doesn't exist
            if not hasattr(self, 'no_record_label_frame') or not self.no_record_label_frame:
                # Import here to avoid circular imports
                from src.ui.no_record_label_frame import NoRecordLabelFrame
                
                self.no_record_label_frame = NoRecordLabelFrame(
                    self.container_frame,
                    self.config_manager,
                    self.return_to_welcome
                )
            
            # Show the no record label frame
            self.no_record_label_frame.pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            # Log the error
            print(f"Error in no_record_label_action: {str(e)}")
            # Return to welcome screen
            self.return_to_welcome()
    
    def jdl_automation_action(self):
        """Handle the JDL Automation button click"""
        try:
            # Hide the welcome frame
            self.welcome_frame.pack_forget()
            
            # Create the JDL automation frame if it doesn't exist
            if not hasattr(self, 'jdl_automation_frame') or not self.jdl_automation_frame:
                self.jdl_automation_frame = JDLAutomationFrame(
                    self.container_frame,
                    self.config_manager,
                    self.return_to_welcome
                )
            
            # Show the JDL automation frame
            self.jdl_automation_frame.pack(fill='both', expand=True)
            
            # Update window title
            self.title("JDL Global IWMS Automation")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            # Log the error
            print(f"Error in jdl_automation_action: {str(e)}")
            # Return to welcome screen
            self.return_to_welcome()

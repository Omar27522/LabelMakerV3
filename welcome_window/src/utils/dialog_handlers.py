"""
Dialog handling utilities for the Label Maker application.
Contains functions for creating and managing various dialogs.
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
import ctypes
from PIL import Image, ImageTk

# Import utility functions
from src.utils.file_utils import file_exists, get_credentials_file_path, directory_exists
from src.utils.ui_components import create_title_section, create_colored_button, create_status_bar
from src.utils.returns_operations import load_returns_data, update_log_file, create_returns_dialog, create_edit_dialog
from src.utils.settings_operations import create_settings_dialog
from src.utils.sheets_operations import create_google_sheets_dialog
from src.config.config_manager import ConfigManager

def set_taskbar_icon(dialog, icon_name):
    """
    Set the window icon for a dialog without changing the taskbar icon
    
    Args:
        dialog: Dialog to set icon for
        icon_name: Name of the icon file (without path)
    """
    try:
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Path to the icon file
        icon_path = os.path.join(script_dir, "assets", icon_name)
        
        # Check if the icon file exists
        if os.path.exists(icon_path):
            # Load the icon
            icon = ImageTk.PhotoImage(Image.open(icon_path))
            # Set the icon
            dialog.iconphoto(False, icon)
            # Keep a reference to the icon to prevent garbage collection
            dialog._icon = icon
        else:
            print(f"Icon file not found: {icon_path}")
    except Exception as e:
        print(f"Error setting icon: {e}")

def create_labels_dialog(parent):
    """
    Create a dialog for viewing and editing returns data
    
    Args:
        parent: Parent window
        
    Returns:
        None
    """
    # Create a dialog for viewing and editing returns data
    dialog, tree, content_frame = create_returns_dialog(parent)
    
    # Make this dialog a transient window of the parent
    dialog.transient(parent)
    
    # Set window icon (not taskbar icon)
    set_taskbar_icon(dialog, "returnsdata_64.png")
    
    # Load returns data
    load_returns_data(tree)
    
    # Button Frame
    button_frame = tk.Frame(content_frame, bg='white')
    button_frame.pack(fill='x', pady=(10, 0))
    
    # Add Edit button
    edit_button = create_colored_button(
        button_frame,
        "Edit",
        '#2196F3',  # Blue
        '#1976D2',  # Darker Blue
        lambda: edit_selected_record(tree)
    )
    edit_button.pack(side='right', padx=(10, 0))
    
    # Add Refresh button
    refresh_button = create_colored_button(
        button_frame,
        "Refresh",
        '#4CAF50',  # Green
        '#45a049',  # Darker Green
        lambda: load_returns_data(tree)
    )
    refresh_button.pack(side='right')
    
    # Function to edit selected record
    def edit_selected_record(tree):
        # Get selected item
        selected_item = tree.selection()
        
        # Check if an item is selected
        if not selected_item:
            messagebox.showinfo("No Selection", "Please select a record to edit.")
            return
        
        # Create edit dialog
        success = create_edit_dialog(dialog, tree, selected_item)
        
        # Refresh the treeview if record was edited
        if success:
            load_returns_data(tree)
    
    # Return the dialog and tree
    return dialog, tree

def create_settings_dialog_handler(parent, config_manager, update_label_count_callback):
    """
    Create a settings dialog with handlers for saving settings.
    
    Args:
        parent: The parent window
        config_manager: The configuration manager
        update_label_count_callback: Callback for updating the label count
        
    Returns:
        The created settings dialog
    """
    # Function to handle saving settings
    def save_settings(dialog, directory, transparency_enabled=None, transparency_level=None, reverseinbound_creation=None, inbound_processing_delay=None, jdl_automation_enabled=None, jdl_username=None, jdl_password=None, jdl_main_url=None, jdl_after_sales_url=None, show_automation_log=None, jdl_visual_logger_mode=None):
        # Save the directory to settings
        config_manager.settings.last_directory = directory
        
        # Save transparency settings if provided
        if transparency_enabled is not None:
            config_manager.settings.transparency_enabled = transparency_enabled
        
        if transparency_level is not None:
            # Ensure the transparency level is within valid range (0.1 to 1.0)
            config_manager.settings.transparency_level = max(0.1, min(1.0, transparency_level))
        
        # Save reverseinbound_creation setting if provided
        if reverseinbound_creation is not None:
            config_manager.settings.reverseinbound_creation = reverseinbound_creation
        
        # Save inbound processing delay if provided
        if inbound_processing_delay is not None:
            try:
                # Convert to float and ensure it's within valid range (0.0 to 10.0)
                delay_value = float(inbound_processing_delay)
                config_manager.settings.inbound_processing_delay = max(0.0, min(10.0, delay_value))
            except (ValueError, TypeError):
                # If conversion fails, use default value
                config_manager.settings.inbound_processing_delay = 0.5
        
        # Save JDL automation settings if provided
        if jdl_automation_enabled is not None:
            config_manager.settings.jdl_automation_enabled = jdl_automation_enabled
            
        if jdl_username is not None:
            config_manager.settings.jdl_username = jdl_username
            
        if jdl_password is not None:
            config_manager.settings.jdl_password = jdl_password
            
        # Save JDL URL settings if provided
        if jdl_main_url is not None:
            config_manager.settings.jdl_main_url = jdl_main_url
            
        if jdl_after_sales_url is not None:
            config_manager.settings.jdl_after_sales_url = jdl_after_sales_url
            
        # Save show_automation_log setting if provided
        if show_automation_log is not None:
            config_manager.settings.show_automation_log = show_automation_log
        
        # Save JDL visual logger mode if provided
        if jdl_visual_logger_mode is not None:
            config_manager.settings.jdl_visual_logger_mode = jdl_visual_logger_mode
            
        # Save all settings
        config_manager.save_settings()
        
        # Update transparency for all windows if transparency settings changed
        if transparency_enabled is not None or transparency_level is not None:
            # Update transparency for the main window
            if hasattr(parent, 'transparency_manager'):
                parent.transparency_manager.set_enabled(config_manager.settings.transparency_enabled)
                parent.transparency_manager.set_opacity(config_manager.settings.transparency_level)
        
        # Close the dialog
        dialog.destroy()
    
    # Function to open Google Sheets dialog
    def open_sheets_dialog():
        # Create Google Sheets dialog
        sheets_dialog = create_google_sheets_dialog_handler(parent, config_manager)
        
        # Return the dialog so it can be managed by the settings dialog
        return sheets_dialog
    
    # Create settings dialog
    settings_dialog, _ = create_settings_dialog(
        parent, 
        config_manager, 
        update_label_count_callback, 
        open_sheets_dialog, 
        save_settings
    )
    
    # Make this dialog a transient window of the parent
    settings_dialog.transient(parent)
    
    # Set window icon (not taskbar icon)
    set_taskbar_icon(settings_dialog, "settings_64.png")
    
    return settings_dialog

def create_google_sheets_dialog_handler(parent, config_manager, update_callback=None):
    """
    Create a Google Sheets configuration dialog with handlers for saving settings.
    
    Args:
        parent: The parent window
        config_manager: The configuration manager
        update_callback: Optional callback to update the UI after settings are saved
        
    Returns:
        The created Google Sheets dialog
    """
    # Create Google Sheets dialog
    sheets_dialog = create_google_sheets_dialog(parent, config_manager, update_callback)
    
    # Make this dialog a transient window of the parent
    sheets_dialog.transient(parent)
    
    # Set window icon (not taskbar icon)
    set_taskbar_icon(sheets_dialog, "icon_64.png")
    
    return sheets_dialog

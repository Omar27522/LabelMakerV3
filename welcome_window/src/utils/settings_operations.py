"""
Utility functions for handling settings operations.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys

from src.config.config_manager import ConfigManager
from src.utils.ui_utils import center_window, create_button, make_window_modal
from src.ui.log_migration_dialog import show_log_migration_dialog

def create_settings_dialog(parent, config_manager, update_label_count_callback, open_sheets_dialog_callback, save_settings_callback):
    """
    Create a dialog for viewing and editing application settings.
    
    Args:
        parent: The parent window
        config_manager: The configuration manager
        update_label_count_callback: Callback for updating the label count
        open_sheets_dialog_callback: Callback for opening the Google Sheets dialog
        save_settings_callback: Callback for saving the settings
        
    Returns:
        tuple: (dialog, directory_var) - The dialog window and the directory variable
    """
    # Create settings dialog
    settings_dialog = tk.Toplevel(parent)
    settings_dialog.title("Settings")
    settings_dialog.geometry("500x400")
    settings_dialog.resizable(False, False)
    settings_dialog.configure(bg='white')
    # Remove transient and grab_set to allow separate taskbar icon
    # settings_dialog.transient(parent)  # Make dialog modal
    # settings_dialog.grab_set()  # Make dialog modal
    
    # Center the dialog
    center_window(settings_dialog)
    
    # Create a main frame to hold the canvas and scrollbar
    main_frame = tk.Frame(settings_dialog, bg='white')
    main_frame.pack(fill='both', expand=True)
    
    # Create a canvas for scrolling
    canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
    canvas.pack(side='left', fill='both', expand=True)
    
    # Add a scrollbar to the canvas
    scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y')
    
    # Configure the canvas to use the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Create a frame inside the canvas to hold the content
    content_frame = tk.Frame(canvas, bg='white', padx=20, pady=20)
    
    # Create a window inside the canvas to hold the content frame
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor='nw')
    
    # Function to update the scrollregion when the content frame changes size
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))
    
    # Function to update the canvas window size when the canvas changes size
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    # Bind events to update the scrollregion and canvas window size
    content_frame.bind('<Configure>', on_frame_configure)
    canvas.bind('<Configure>', on_canvas_configure)
    
    # Bind mousewheel events for scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
    
    # Bind mousewheel for Windows
    canvas.bind_all('<MouseWheel>', on_mousewheel)
    
    # Title section with Sheet Manager button
    title_section = tk.Frame(content_frame, bg='white')
    title_section.pack(fill='x', pady=(0, 10))
    
    # Title
    title_label = tk.Label(
        title_section, 
        text="Settings", 
        font=("Arial", 16, "bold"), 
        bg='white'
    )
    title_label.pack(side='left', pady=(0, 10))
    
    # Function to open Sheet Manager
    def open_sheet_manager():
        try:
            # Path to Sheet Manager main.pyw
            sheet_manager_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                            'Sheet Manager', 'main.pyw')
            
            # Check if the file exists
            if not os.path.exists(sheet_manager_path):
                messagebox.showerror("Error", f"Sheet Manager not found at: {sheet_manager_path}")
                return
                
            # Launch Sheet Manager using Python executable
            python_exe = sys.executable
            subprocess.Popen([python_exe, sheet_manager_path], 
                           shell=True,  # Use shell on Windows
                           creationflags=subprocess.CREATE_NEW_CONSOLE)  # Create new console window
            
            # Close the settings dialog
            settings_dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Sheet Manager: {str(e)}")
    
    # Sheet Manager Button
    sheet_manager_btn = create_button(
        title_section,
        text="Open Sheet Manager",
        command=open_sheet_manager,
        bg='#1976d2',
        fg='white',
        padx=10,
        pady=5
    )
    sheet_manager_btn.pack(side='right', padx=(10, 0), pady=(0, 10))
    
    # Labels Directory Section
    directory_section = tk.LabelFrame(content_frame, text="Labels Directory", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
    directory_section.pack(fill='x', pady=(0, 15))
    
    # Directory path
    directory_var = tk.StringVar(value=config_manager.settings.last_directory or "")
    directory_entry = tk.Entry(directory_section, textvariable=directory_var, font=("Arial", 10), width=50)
    directory_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
    
    # Browse button
    browse_button = create_button(
        directory_section,
        text="Browse",
        command=lambda: [
            directory_var.set(filedialog.askdirectory(
                initialdir=directory_var.get() or os.path.expanduser("~"),
                title="Select Labels Directory"
            )),
            update_label_count_callback(directory_var.get())
        ],
        bg='#2196F3',
        padx=10,
        pady=5
    )
    browse_button.pack(side='right')
    
    # Label count
    count_frame = tk.Frame(directory_section, bg='white')
    count_frame.pack(fill='x', pady=(10, 0))
    
    count_label = tk.Label(
        count_frame, 
        text="Labels in directory:", 
        font=("Arial", 10), 
        bg='white'
    )
    count_label.pack(side='left')
    
    label_count_var = tk.StringVar(value="0")
    label_count = tk.Label(
        count_frame, 
        textvariable=label_count_var, 
        font=("Arial", 10, "bold"), 
        bg='white'
    )
    label_count.pack(side='left', padx=(5, 0))
    
    # Update label count
    update_label_count_callback(directory_var.get())
    
    # Transparency Settings Section
    transparency_section = tk.LabelFrame(content_frame, text="Transparency Settings", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
    transparency_section.pack(fill='x', pady=(0, 15))
    
    # Transparency enabled checkbox
    transparency_enabled_var = tk.BooleanVar(value=config_manager.settings.transparency_enabled)
    transparency_enabled_cb = tk.Checkbutton(
        transparency_section,
        text="Enable transparency when window is inactive",
        variable=transparency_enabled_var,
        font=("Arial", 10),
        bg='white'
    )
    transparency_enabled_cb.pack(anchor='w', pady=(5, 10))
    
    # Transparency level frame
    transparency_level_frame = tk.Frame(transparency_section, bg='white')
    transparency_level_frame.pack(fill='x', pady=(0, 5))
    
    # Transparency level label
    tk.Label(
        transparency_level_frame,
        text="Transparency Level (1-10):",
        font=("Arial", 10),
        bg='white'
    ).pack(side='left')
    
    # Convert transparency level from 0.0-1.0 to 1-10 for display
    current_transparency = config_manager.settings.transparency_level
    display_value = int(current_transparency * 10)
    if display_value < 1: display_value = 1
    if display_value > 10: display_value = 10
    
    # Transparency level spinbox
    transparency_level_var = tk.StringVar(value=str(display_value))
    transparency_spinbox = tk.Spinbox(
        transparency_level_frame,
        from_=1,
        to=10,
        width=5,
        textvariable=transparency_level_var,
        font=("Arial", 10)
    )
    transparency_spinbox.pack(side='left', padx=(10, 0))
    
    # Helper text
    tk.Label(
        transparency_section,
        text="(1 = Most transparent, 10 = Least transparent)",
        font=("Arial", 8, "italic"),
        fg='gray',
        bg='white'
    ).pack(anchor='w', pady=(0, 5))
    
    # Google Sheets Section
    sheets_section = tk.LabelFrame(content_frame, text="Google Sheets Integration", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
    sheets_section.pack(fill='x', pady=(0, 15))

    # Connection status
    status_text = "Not Connected"
    status_color = 'red'

    # Check if Google Sheets is configured
    if (config_manager.settings.google_sheet_url and 
        config_manager.settings.google_sheet_name):
        status_text = "Connected"
        status_color = 'green'

    status_frame = tk.Frame(sheets_section, bg='white')
    status_frame.pack(fill='x', pady=(5, 5))

    tk.Label(status_frame, text="Status:", font=("Arial", 10), bg='white').pack(side='left')
    sheets_status_label = tk.Label(
        status_frame,
        text=status_text,
        font=("Arial", 10, "bold"),
        fg=status_color,
        bg='white'
    )
    sheets_status_label.pack(side='left', padx=(5, 0))
    
    # Add sheet info if connected
    if status_text == "Connected":
        sheet_info = f"{config_manager.settings.google_sheet_name}"
        tk.Label(status_frame, text=" | Sheet:", font=("Arial", 10), bg='white').pack(side='left', padx=(10, 0))
        tk.Label(status_frame, text=sheet_info, font=("Arial", 10, "italic"), bg='white').pack(side='left', padx=(5, 0))
    
    # Store reference to sheets dialog
    settings_dialog.sheets_dialog = None
    
    # Function to open Google Sheets dialog as a child of Settings
    def open_sheets_dialog_as_child():
        # If a sheets dialog is already open, just bring it to front
        if settings_dialog.sheets_dialog is not None and settings_dialog.sheets_dialog.winfo_exists():
            # Check if dialog is minimized (iconified)
            if settings_dialog.sheets_dialog.state() == 'iconic':
                settings_dialog.sheets_dialog.deiconify()  # Restore the window
            
            settings_dialog.sheets_dialog.lift()
            settings_dialog.sheets_dialog.focus_force()
            return
            
        # Call the original callback to create the dialog
        sheets_dialog = open_sheets_dialog_callback()
        
        if sheets_dialog:
            # Store reference to the sheets dialog
            settings_dialog.sheets_dialog = sheets_dialog
            
            # Make sheets dialog a child of settings dialog
            sheets_dialog.transient(settings_dialog)
            
            # Make sheets dialog modal to settings dialog
            sheets_dialog.grab_set()
            
            # When sheets dialog is closed, update the settings dialog
            def on_sheets_dialog_close():
                # Release grab
                sheets_dialog.grab_release()
                
                # Clear reference
                settings_dialog.sheets_dialog = None
                
                # Destroy the dialog
                sheets_dialog.destroy()
                
                # Update the status display
                nonlocal config_manager
                config_manager = ConfigManager()
                update_sheets_status_display(parent, config_manager, sheets_status_label)
                
                # Give focus back to settings dialog
                settings_dialog.lift()
                settings_dialog.focus_force()
                
            # Set the close protocol
            sheets_dialog.protocol("WM_DELETE_WINDOW", on_sheets_dialog_close)
    
    # Configure button
    configure_button = create_button(
        sheets_section,
        text="Configure Google Sheets",
        command=open_sheets_dialog_as_child,
        bg='#2196F3',
        padx=10,
        pady=5
    )
    configure_button.pack(pady=(5, 5))
    
    # Store reference to the button for external access
    settings_dialog.sheets_button = configure_button
    
    # Add Log Management Section
    log_section = tk.LabelFrame(content_frame, text="Log Management", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
    log_section.pack(fill='x', pady=(0, 15))
    
    # Description
    log_desc = tk.Label(
        log_section,
        text="Manage shipping logs and migrate from legacy systems to the new centralized log database.",
        font=("Arial", 10),
        bg='white',
        wraplength=450,
        justify='left'
    )
    log_desc.pack(pady=(5, 10), fill='x')
    
    # Log Management Button
    log_button = create_button(
        log_section,
        text="Open Log Management",
        command=lambda: show_log_migration_dialog(settings_dialog),
        bg='#2196F3',
        padx=10,
        pady=5
    )
    log_button.pack(pady=(0, 5))
    
    # Button Frame
    button_frame = tk.Frame(content_frame, bg='white')
    button_frame.pack(fill='x', pady=(10, 0))
    
    # Save Button
    save_button = create_button(
        button_frame,
        text="Save",
        command=lambda: save_settings_callback(
            settings_dialog, 
            directory_var.get(),
            transparency_enabled_var.get(),
            float(transparency_level_var.get()) / 10.0  # Convert from 1-10 to 0.1-1.0
        ),
        bg='#4CAF50',
        padx=15,
        pady=5
    )
    save_button.pack(side='right', padx=(10, 0))
    
    # Cancel Button
    cancel_button = create_button(
        button_frame,
        text="Cancel",
        command=settings_dialog.destroy,
        bg='#F44336',
        padx=15,
        pady=5
    )
    cancel_button.pack(side='right')
    
    # When settings dialog is closed, also close any child dialogs
    def on_settings_dialog_close():
        # Close sheets dialog if open
        if settings_dialog.sheets_dialog is not None and settings_dialog.sheets_dialog.winfo_exists():
            settings_dialog.sheets_dialog.destroy()
        
        # Destroy settings dialog
        settings_dialog.destroy()
    
    # Set the close protocol
    settings_dialog.protocol("WM_DELETE_WINDOW", on_settings_dialog_close)
    
    return settings_dialog, directory_var

def update_sheets_status_display(parent, config_manager, sheets_status_label):
    """
    Update the Google Sheets status display in the welcome window.
    
    Args:
        parent: The parent window
        config_manager: The configuration manager
        sheets_status_label: The label to update
        
    Returns:
        None
    """
    # Update the Google Sheets status display
    status_text = "Not Connected"
    status_color = 'red'
    
    # Check if Google Sheets is configured
    if (config_manager.settings.google_sheet_url and 
        config_manager.settings.google_sheet_name):
        
        # Check if credentials file exists
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials.json')
        if os.path.exists(credentials_path):
            status_text = "Connected"
            status_color = 'green'
        else:
            status_text = "Missing Credentials"
            status_color = 'orange'
    
    # Update the status label
    sheets_status_label.config(text=status_text, fg=status_color)
    
    return status_text, status_color

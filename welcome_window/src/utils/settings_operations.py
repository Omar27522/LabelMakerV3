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
    
    # Variable for JDL log status
    jdl_log_status_var = tk.StringVar()
    
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
    
    # Add Inbound Creation Settings Section
    inbound_section = tk.LabelFrame(content_frame, text="Inbound Creation Settings", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
    inbound_section.pack(fill='x', pady=(0, 15))
    
    # Reverse Inbound Creation checkbox
    reverseinbound_creation_var = tk.BooleanVar(value=config_manager.settings.reverseinbound_creation)
    reverseinbound_creation_cb = tk.Checkbutton(
        inbound_section,
        text="Enable reverse inbound creation",
        variable=reverseinbound_creation_var,
        font=("Arial", 10),
        bg='white'
    )
    reverseinbound_creation_cb.pack(anchor='w', pady=(5, 5))
    
    # Description for reverse inbound
    inbound_desc = tk.Label(
        inbound_section,
        text="When enabled, inbound creation will be processed in reverse order.",
        font=("Arial", 8, "italic"),
        fg='gray',
        bg='white',
        wraplength=450,
        justify='left'
    )
    inbound_desc.pack(pady=(0, 10), fill='x')
    
    # Processing delay frame
    delay_frame = tk.Frame(inbound_section, bg='white')
    delay_frame.pack(fill='x', pady=(5, 5))
    
    # Processing delay label
    tk.Label(
        delay_frame,
        text="Processing delay (seconds):",
        font=("Arial", 10),
        bg='white'
    ).pack(side='left')
    
    # Get the current delay value or use default of 0.5 seconds
    default_delay = 0.5
    if hasattr(config_manager.settings, 'inbound_processing_delay'):
        default_delay = config_manager.settings.inbound_processing_delay
    
    # Processing delay spinbox
    inbound_delay_var = tk.StringVar(value=str(default_delay))
    inbound_delay_spinbox = tk.Spinbox(
        delay_frame,
        from_=0.0,
        to=10.0,
        increment=0.1,
        width=5,
        textvariable=inbound_delay_var,
        font=("Arial", 10)
    )
    inbound_delay_spinbox.pack(side='left', padx=(10, 0))
    
    # Description for delay
    delay_desc = tk.Label(
        inbound_section,
        text="Sets a delay between processing each item. Useful for slower network connections or to avoid rate limiting.",
        font=("Arial", 8, "italic"),
        fg='gray',
        bg='white',
        wraplength=450,
        justify='left'
    )
    delay_desc.pack(pady=(0, 5), fill='x')
    
    # Add JDL Automation Settings Section
    jdl_section = tk.LabelFrame(content_frame, text="JDL Automation Settings", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
    jdl_section.pack(fill='x', pady=(0, 15))
    
    # JDL Automation Enabled
    jdl_automation_enabled_value = False # Default value
    if hasattr(config_manager.settings, 'jdl_automation_enabled'):
        config_value = config_manager.settings.jdl_automation_enabled
        if isinstance(config_value, bool):
            jdl_automation_enabled_value = config_value
        # Add handling for string representations of boolean if necessary, e.g.:
        # elif isinstance(config_value, str) and config_value.lower() in ['true', 'false']:
        #     jdl_automation_enabled_value = config_value.lower() == 'true'
        # else, it remains False (or log a warning)

    jdl_automation_enabled_var = tk.BooleanVar(value=jdl_automation_enabled_value)
    jdl_automation_enabled_cb = tk.Checkbutton(
        jdl_section,
        text="Enable JDL Global IWMS automation",
        variable=jdl_automation_enabled_var,
        font=("Arial", 10),
        bg='white'
    )
    jdl_automation_enabled_cb.pack(anchor='w', pady=(5, 10))
    
    # JDL Credentials
    credentials_frame = tk.Frame(jdl_section, bg='white')
    credentials_frame.pack(fill='x', pady=(0, 5))
    
    # Username field
    username_frame = tk.Frame(credentials_frame, bg='white')
    username_frame.pack(fill='x', pady=(5, 5))
    
    tk.Label(
        username_frame,
        text="Username:",
        font=("Arial", 10),
        bg='white',
        width=15,
        anchor='w'
    ).pack(side='left')
    
    jdl_username_var = tk.StringVar(value=config_manager.settings.jdl_username 
                                   if hasattr(config_manager.settings, 'jdl_username') else "")
    username_entry = tk.Entry(
        username_frame,
        textvariable=jdl_username_var,
        font=("Arial", 10),
        width=30
    )
    username_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
    
    # Password field
    password_frame = tk.Frame(credentials_frame, bg='white')
    password_frame.pack(fill='x', pady=(5, 5))
    
    tk.Label(
        password_frame,
        text="Password:",
        font=("Arial", 10),
        bg='white',
        width=15,
        anchor='w'
    ).pack(side='left')
    
    jdl_password_var = tk.StringVar(value=config_manager.settings.jdl_password 
                                   if hasattr(config_manager.settings, 'jdl_password') else "")
    jdl_password_entry = tk.Entry(
        password_frame,
        textvariable=jdl_password_var,
        font=("Arial", 10),
        width=30,
        show="*"
    )
    jdl_password_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
    
    # JDL Activity Log Mode Control
    jdl_log_mode_frame = tk.Frame(jdl_section, bg='white') 
    jdl_log_mode_frame.pack(fill='x', pady=(10, 5), anchor='w')

    jdl_log_mode_label = tk.Label(jdl_log_mode_frame, text="JDL Activity Log:", font=("Arial", 10), bg='white')
    jdl_log_mode_label.pack(side='left')

    jdl_log_status_display_label = tk.Label(jdl_log_mode_frame, textvariable=jdl_log_status_var, font=("Arial", 10, "bold"), bg='white')
    jdl_log_status_display_label.pack(side='left', padx=(5, 10))

    # Helper function to update JDL log status display
    def _update_jdl_log_status_display_in_settings_dialog():
        current_mode = getattr(config_manager.settings, 'jdl_visual_logger_mode', 'show')
        if current_mode.lower() == 'disabled':
            jdl_log_status_var.set("Disabled")
        else:
            jdl_log_status_var.set("Enabled")

    # Helper function to toggle JDL log mode
    def _toggle_jdl_log_mode_in_settings_dialog():
        current_mode = getattr(config_manager.settings, 'jdl_visual_logger_mode', 'show')
        new_mode = 'disabled' if current_mode.lower() != 'disabled' else 'show'
        config_manager.settings.jdl_visual_logger_mode = new_mode
        
        # Show confirmation message BEFORE calling the callback that might destroy the dialog
        messagebox.showinfo("Settings Updated", f"JDL Activity Log has been set to {new_mode}.", parent=settings_dialog)

        if save_settings_callback:
            # Call save_settings_callback with individual arguments
            # The first argument is the dialog instance itself.
            save_settings_callback(
                settings_dialog, # dialog instance
                directory_var.get(), # directory
                # Pass other settings as keyword arguments
                transparency_enabled=transparency_enabled_var.get() if 'transparency_enabled_var' in locals() and transparency_enabled_var is not None else getattr(config_manager.settings, 'transparency_enabled', False),
                transparency_level=transparency_level_scale.get() if 'transparency_level_scale' in locals() and transparency_level_scale is not None else getattr(config_manager.settings, 'transparency_level', 1.0),
                reverseinbound_creation=reverse_inbound_creation_var.get() if 'reverse_inbound_creation_var' in locals() and reverse_inbound_creation_var is not None else getattr(config_manager.settings, 'reverseinbound_creation', False),
                inbound_processing_delay=inbound_delay_var.get() if 'inbound_delay_var' in locals() and inbound_delay_var is not None else getattr(config_manager.settings, 'inbound_processing_delay', 0.5),
                jdl_automation_enabled=jdl_automation_enabled_var.get(),
                jdl_username=jdl_username_var.get(),
                jdl_password=jdl_password_var.get(),
                jdl_main_url=jdl_main_url_var.get() if 'jdl_main_url_var' in locals() and jdl_main_url_var is not None else getattr(config_manager.settings, 'jdl_main_url', ''),
                jdl_after_sales_url=jdl_after_sales_url_var.get() if 'jdl_after_sales_url_var' in locals() and jdl_after_sales_url_var is not None else getattr(config_manager.settings, 'jdl_after_sales_url', ''),
                show_automation_log=show_automation_log_var.get() if 'show_automation_log_var' in locals() and show_automation_log_var is not None else getattr(config_manager.settings, 'show_automation_log', False),
                jdl_visual_logger_mode=new_mode # Our new setting
            )
        
        _update_jdl_log_status_display_in_settings_dialog()

    # Revert to original button style
    jdl_log_toggle_button = create_button(
        jdl_log_mode_frame,
        text="🔒", 
        command=_toggle_jdl_log_mode_in_settings_dialog,
        # Assuming standard button styling from create_button, or add specific bg/fg if needed
        # bg='#e0e0e0', # Example, if create_button doesn't handle it or you want override
        # fg='black',
        padx=5, 
        pady=2  # Adjust padding as per original lock button design
    )
    jdl_log_toggle_button.pack(side='left', padx=5, pady=2)

    # Initial update of the JDL log status display
    _update_jdl_log_status_display_in_settings_dialog()

    # JDL URLs
    urls_frame = tk.Frame(jdl_section, bg='white')
    urls_frame.pack(fill='x', pady=(10, 5))
    
    # URL section label
    url_section_label = tk.Label(urls_frame, text="JDL Website URLs", font=("Arial", 10, "bold"), bg='white')
    url_section_label.pack(anchor='w', pady=(0, 5))
    
    # Main URL field
    main_url_frame = tk.Frame(urls_frame, bg='white')
    main_url_frame.pack(fill='x', pady=(5, 5))
    
    tk.Label(
        main_url_frame,
        text="Main URL:",
        font=("Arial", 10),
        bg='white',
        width=15,
        anchor='w'
    ).pack(side='left')
    
    jdl_main_url_var = tk.StringVar(value=config_manager.settings.jdl_main_url 
                                   if hasattr(config_manager.settings, 'jdl_main_url') else "https://iwms.us.jdlglobal.com/")
    main_url_entry = tk.Entry(
        main_url_frame,
        textvariable=jdl_main_url_var,
        font=("Arial", 10),
        width=30
    )
    main_url_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
    
    # After Sales URL field
    after_sales_url_frame = tk.Frame(urls_frame, bg='white')
    after_sales_url_frame.pack(fill='x', pady=(5, 5))
    
    tk.Label(
        after_sales_url_frame,
        text="After Sales URL:",
        font=("Arial", 10),
        bg='white',
        width=15,
        anchor='w'
    ).pack(side='left')
    
    jdl_after_sales_url_var = tk.StringVar(value=config_manager.settings.jdl_after_sales_url 
                                         if hasattr(config_manager.settings, 'jdl_after_sales_url') else "https://iwms.us.jdlglobal.com/#/createAfterSalesOrder")
    after_sales_url_entry = tk.Entry(
        after_sales_url_frame,
        textvariable=jdl_after_sales_url_var,
        font=("Arial", 10),
        width=30
    )
    after_sales_url_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
    
    # URL description
    url_desc = tk.Label(
        urls_frame,
        text="These URLs are used for connecting to the JDL Global IWMS system. Only modify if the system URLs have changed.",
        font=("Arial", 8, "italic"),
        fg='gray',
        bg='white',
        wraplength=450,
        justify='left'
    )
    url_desc.pack(pady=(0, 5), fill='x')
    
    # Automation Log Settings
    log_frame = tk.Frame(jdl_section, bg='white')
    log_frame.pack(fill='x', pady=(10, 5))
    
    # Log section label
    log_section_label = tk.Label(log_frame, text="Automation Activity Log", font=("Arial", 10, "bold"), bg='white')
    log_section_label.pack(anchor='w', pady=(0, 5))
    
    # Show Automation Log checkbox
    show_automation_log_var = tk.BooleanVar(value=config_manager.settings.show_automation_log 
                                         if hasattr(config_manager.settings, 'show_automation_log') else False)
    show_automation_log_cb = tk.Checkbutton(
        log_frame,
        text="Show Automation Activity Log automatically when processing tracking numbers",
        variable=show_automation_log_var,
        font=("Arial", 10),
        bg='white'
    )
    show_automation_log_cb.pack(anchor='w', pady=(5, 5))
    
    # Description for automation log
    log_desc = tk.Label(
        log_frame,
        text="When enabled, the Automation Activity Log will appear automatically when processing tracking numbers. When disabled, you can still open it manually using the button below.",
        font=("Arial", 8, "italic"),
        fg='gray',
        bg='white',
        wraplength=450,
        justify='left'
    )
    log_desc.pack(pady=(0, 5), fill='x')
    
    # Function to toggle the JDL Automation Activity Log
    def toggle_automation_log():
        try:
            # Import here to avoid circular imports
            from src.utils.jdl_automation import JDLVisualLogger
            
            # Get the logger instance
            logger = JDLVisualLogger.get_instance()
            
            # Toggle the visibility
            if logger.is_visible:
                logger.hide()
                toggle_log_button.config(
                    text="Show Automation Activity Log",
                    bg='#2196F3'  # Blue when log is hidden
                )
            else:
                logger.show()
                toggle_log_button.config(
                    text="Hide Automation Activity Log",
                    bg='#4CAF50'  # Green when log is visible
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle Automation Activity Log: {str(e)}")
    
    # Check if the logger is visible
    log_visible = False
    try:
        from src.utils.jdl_automation import JDLVisualLogger
        logger = JDLVisualLogger.get_instance()
        log_visible = logger.is_visible
    except:
        pass
    
    # Create toggle button with appropriate initial text
    toggle_log_button = tk.Button(
        log_frame,
        text="Hide Automation Activity Log" if log_visible else "Show Automation Activity Log",
        command=toggle_automation_log,
        bg='#4CAF50' if log_visible else '#2196F3',  # Green if visible, Blue if hidden
        fg='white',
        padx=10,
        pady=5
    )
    toggle_log_button.pack(pady=(0, 5))
    
    # Login to JDL button
    def login_to_jdl():
        # Save current settings first
        temp_save_settings = lambda: save_settings_callback(
            settings_dialog, 
            directory_var.get(),
            transparency_enabled_var.get(),
            float(transparency_level_var.get()) / 10.0,
            reverseinbound_creation_var.get(),  # Add the new reverseinbound_creation setting
            float(inbound_delay_var.get()),     # Add the new inbound_processing_delay setting
            jdl_automation_enabled_var.get(),   # Add the JDL automation enabled setting
            jdl_username_var.get(),             # Add the JDL username
            jdl_password_var.get(),             # Add the JDL password
            jdl_main_url_var.get(),            # Add the JDL main URL
            jdl_after_sales_url_var.get(),     # Add the JDL after sales URL
            show_automation_log_var.get()      # Add the show automation log setting
        )
        temp_save_settings()
        
        # Import here to avoid circular imports
        try:
            from src.utils.jdl_automation import JDLAutomation
        except ImportError:
            messagebox.showerror("Error", "Could not import JDL automation module. Please check your installation.")
            return
        
        # Show a message to the user
        messagebox.showinfo("JDL Login", "Opening the JDL Global IWMS website. Please log in with your credentials.")
        
        # Get the JDL automation instance and open the browser
        try:
            # Just open the browser to the login page
            import webbrowser
            # Use the configurable URL
            main_url = jdl_main_url_var.get()
            if not main_url.startswith("http"):
                main_url = "https://" + main_url
            webbrowser.open(main_url)
            
            messagebox.showinfo("Browser Opened", f"The JDL Global IWMS website has been opened in your default browser. Please log in with your credentials.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    # Login button frame
    login_button_frame = tk.Frame(jdl_section, bg='white')
    login_button_frame.pack(fill='x', pady=(5, 10))
    
    login_button = create_button(
        login_button_frame,
        text="Login to JDL Now",
        command=login_to_jdl,
        bg='#2196F3',
        padx=10,
        pady=5
    )
    login_button.pack(pady=(0, 5))
    
    # Description
    jdl_desc = tk.Label(
        jdl_section,
        text="When enabled, tracking numbers will be automatically processed in JDL Global IWMS when entered.",
        font=("Arial", 8, "italic"),
        fg='gray',
        bg='white',
        wraplength=450,
        justify='left'
    )
    jdl_desc.pack(pady=(0, 5), fill='x')
    
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
            float(transparency_level_var.get()) / 10.0,  # Convert from 1-10 to 0.1-1.0
            reverseinbound_creation_var.get(),  # Add the new reverseinbound_creation setting
            float(inbound_delay_var.get()),     # Add the new inbound_processing_delay setting
            jdl_automation_enabled_var.get(),   # Add the JDL automation enabled setting
            jdl_username_var.get(),             # Add the JDL username
            jdl_password_var.get(),             # Add the JDL password
            jdl_main_url_var.get(),            # Add the JDL main URL
            jdl_after_sales_url_var.get(),     # Add the JDL after sales URL
            show_automation_log_var.get()      # Add the show automation log setting
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

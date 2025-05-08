import tkinter as tk
from tkinter import ttk, messagebox
import os

class SettingsDialog:
    def __init__(self, parent, config_manager):
        """Initialize the settings dialog
        
        Args:
            parent: The parent window
            config_manager: The configuration manager
        """
        self.parent = parent
        self.config = config_manager
        self.config_manager = config_manager
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Label Maker Settings")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # Set to be on top of the parent window
        self.dialog.grab_set()  # Modal window
        
        # Center the dialog
        self.center_window()
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.general_tab = ttk.Frame(self.notebook)
        self.jdl_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.general_tab, text="General")
        self.notebook.add(self.jdl_tab, text="JDL URLs")
        
        # Create the general settings tab
        self.create_general_tab()
        
        # Create the JDL URLs tab
        self.create_jdl_tab()
        
        # Create the buttons frame
        self.buttons_frame = tk.Frame(self.dialog)
        self.buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create the save button
        self.save_button = tk.Button(
            self.buttons_frame, 
            text="Save", 
            command=self.save_settings,
            bg='#27ae60',  # Green
            fg='white',
            activebackground='#2ecc71'  # Lighter green
        )
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        # Create the cancel button
        self.cancel_button = tk.Button(
            self.buttons_frame, 
            text="Cancel", 
            command=self.dialog.destroy,
            bg='#e74c3c',  # Red
            fg='white',
            activebackground='#c0392b'  # Darker red
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def center_window(self):
        """Center the dialog window on the screen"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_general_tab(self):
        """Create the general settings tab"""
        # Create a frame for the general settings
        general_frame = tk.Frame(self.general_tab)
        general_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a label for the Window Settings section
        window_settings_label = tk.Label(general_frame, text="Window Settings", font=("Arial", 10, "bold"))
        window_settings_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # Create the always on top checkbox
        self.always_on_top_var = tk.BooleanVar(value=self.config.settings.always_on_top)
        self.always_on_top_cb = tk.Checkbutton(
            general_frame, 
            text="Always on top", 
            variable=self.always_on_top_var
        )
        self.always_on_top_cb.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Create the auto close browser tabs checkbox
        self.auto_close_tabs_var = tk.BooleanVar(value=self.config.settings.auto_close_browser_tabs)
        self.auto_close_tabs_cb = tk.Checkbutton(
            general_frame, 
            text="Auto-close browser tabs", 
            variable=self.auto_close_tabs_var
        )
        self.auto_close_tabs_cb.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Create the transparency level slider
        tk.Label(general_frame, text="Transparency:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.transparency_var = tk.DoubleVar(value=self.config.settings.transparency_level)
        self.transparency_slider = tk.Scale(
            general_frame, 
            from_=0.1, 
            to=1.0, 
            resolution=0.1, 
            orient=tk.HORIZONTAL,
            variable=self.transparency_var
        )
        self.transparency_slider.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Create a label for the Log Settings section
        log_settings_label = tk.Label(general_frame, text="Log Settings", font=("Arial", 10, "bold"))
        log_settings_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(15, 10))
        
        # Create the automation activity log checkbox
        # Default to True if the setting doesn't exist yet
        default_log_enabled = True
        if hasattr(self.config.settings, 'automation_activity_log_enabled'):
            default_log_enabled = self.config.settings.automation_activity_log_enabled
        
        self.automation_log_var = tk.BooleanVar(value=default_log_enabled)
        self.automation_log_cb = tk.Checkbutton(
            general_frame, 
            text="Enable Automation Activity Log", 
            variable=self.automation_log_var
        )
        self.automation_log_cb.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Add a help text for the automation log setting
        help_text = "When enabled, detailed logs of automation activities will be recorded."
        automation_log_help = tk.Label(
            general_frame,
            text=help_text,
            font=("Arial", 8, "italic"),
            fg="gray",
            wraplength=400,
            justify=tk.LEFT
        )
        automation_log_help.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Add more general settings as needed
    
    def create_jdl_tab(self):
        """Create the JDL URLs tab"""
        # Create a frame for the JDL URLs
        jdl_frame = tk.Frame(self.jdl_tab)
        jdl_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the reverse inbound URL field
        tk.Label(jdl_frame, text="Reverse Inbound URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.reverse_url_var = tk.StringVar(value=self.config_manager.settings.jdl_reverse_inbound_url if hasattr(self.config_manager.settings, 'jdl_reverse_inbound_url') else "https://iwms.us.jdlglobal.com/#/createAfterSalesOrder")
        self.reverse_url_entry = tk.Entry(jdl_frame, textvariable=self.reverse_url_var, width=50)
        self.reverse_url_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Create the receive URL field
        tk.Label(jdl_frame, text="Receive URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.receive_url_var = tk.StringVar(value=self.config_manager.settings.jdl_receive_url if hasattr(self.config_manager.settings, 'jdl_receive_url') else "https://iwms.us.jdlglobal.com/#/scan")
        self.receive_url_entry = tk.Entry(jdl_frame, textvariable=self.receive_url_var, width=50)
        self.receive_url_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Add a reset button to restore default URLs
        self.reset_button = tk.Button(
            jdl_frame, 
            text="Reset to Defaults", 
            command=self.reset_urls,
            bg='#3498db',  # Blue
            fg='white',
            activebackground='#2980b9'  # Darker blue
        )
        self.reset_button.grid(row=2, column=1, sticky=tk.E, pady=10)
        
        # Add a help text
        help_text = "These URLs are used for the browser tabs opened by the Inbound and Receive buttons."
        tk.Label(jdl_frame, text=help_text, wraplength=400, justify=tk.LEFT).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=10
        )
    
    def reset_urls(self):
        """Reset the URLs to their default values"""
        self.reverse_url_var.set("https://iwms.us.jdlglobal.com/#/createAfterSalesOrder")
        self.receive_url_var.set("https://iwms.us.jdlglobal.com/#/scan")
        messagebox.showinfo("URLs Reset", "The JDL URLs have been reset to their default values.")
    
    def save_settings(self):
        """Save the settings to the config"""
        # Update the config with the new values
        self.config.settings.always_on_top = self.always_on_top_var.get()
        self.config.settings.transparency_level = self.transparency_var.get()
        self.config.settings.auto_close_browser_tabs = self.auto_close_tabs_var.get()
        
        # Save Automation Activity Log setting
        self.config.settings.automation_activity_log_enabled = self.automation_log_var.get()
        
        # Save JDL URLs
        if hasattr(self.config.settings, 'jdl_reverse_inbound_url'):
            self.config.settings.jdl_reverse_inbound_url = self.reverse_url_var.get()
        if hasattr(self.config.settings, 'jdl_receive_url'):
            self.config.settings.jdl_receive_url = self.receive_url_var.get()
        
        # Save the settings to the file
        self.config.save_settings()
        
        # Close the dialog
        self.dialog.destroy()

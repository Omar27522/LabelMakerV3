"""
Sheet View Frame - Main working area for the Sheets Manager application.
"""
import tkinter as tk
from tkinter import ttk
from ui.sheetAutomation import SheetAutomationFrame

class SheetViewFrame(tk.Frame):
    """
    Main working frame for interacting with the selected Google Sheet.
    This is where sheet data viewing and manipulation will happen.
    """
    def __init__(self, parent, main_window=None, on_return=None):
        super().__init__(parent, bg="white")
        self.parent = parent
        self._main_window = main_window if main_window is not None else parent
        self.on_return = on_return
        self._create_widgets()
        
    def _create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#1976d2", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="Sheet Manager", font=("Roboto", 16, "bold"), 
                        fg="white", bg="#1976d2")
        title.pack(side=tk.LEFT, padx=20)
        
        # Settings button in header
        settings_btn = tk.Button(header, text="Settings", command=self._open_settings,
                                bg="#607d8b", fg="white", font=("Roboto", 10),
                                relief=tk.FLAT, padx=10)
        settings_btn.pack(side=tk.RIGHT, padx=(0,10), pady=15)

        # Return button in header
        return_btn = tk.Button(header, text="Change Sheet", command=self._on_return,
                              bg="#1565c0", fg="white", font=("Roboto", 10),
                              relief=tk.FLAT, padx=10)
        return_btn.pack(side=tk.RIGHT, padx=(10,10), pady=15)
        
        # Main content area - placeholder for future sheet functionality
        content = tk.Frame(self, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Placeholder message
        placeholder = tk.Label(content, text="Sheet View - Ready for implementation",
                             font=("Roboto", 14), fg="#555555", bg="white")
        placeholder.pack(pady=30)
        
        sheet_info = tk.Label(content, text="This frame will contain sheet viewing and editing functionality.",
                            font=("Roboto", 12), fg="#777777", bg="white", wraplength=500)
        sheet_info.pack(pady=10)
        
        # Automation button
        automation_btn = tk.Button(content, text="Open Sheet Automation", 
                                 bg="#FF9800", fg="white", font=("Roboto", 11, "bold"),
                                 relief=tk.FLAT, padx=15, pady=8,
                                 command=self._open_automation)
        automation_btn.pack(pady=20)
        
        # Status bar
        status_bar = tk.Frame(self, bg="#f5f5f5", height=30)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_bar, text="Ready", bg="#f5f5f5", fg="#555555",
                                   font=("Roboto", 9), anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def _on_return(self):
        """Handle the return button click to go back to connection frame"""
        if self.on_return:
            self.on_return()
    
    def _open_automation(self):
        """Open the Sheet Automation frame"""
        # Clear current frame
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Create and show automation frame
        automation_frame = SheetAutomationFrame(self.parent, on_return=self._return_from_automation)
        automation_frame.pack(fill=tk.BOTH, expand=True)
    
    def _open_settings(self):
        """Open the Settings UI dialog with Scripts Manager access"""
        import tkinter as tk
        import tkinter.messagebox as messagebox
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.geometry("320x180")
        settings_win.transient(self)
        settings_win.grab_set()

        label = tk.Label(settings_win, text="Sheets Manager Settings", font=("Roboto", 12, "bold"))
        label.pack(pady=(18, 10))

        scripts_btn = tk.Button(settings_win, text="Open Scripts Manager", bg="#1976d2", fg="white", font=("Roboto", 10, "bold"), command=self._open_scripts_manager)
        scripts_btn.pack(pady=(10, 0))

        close_btn = tk.Button(settings_win, text="Close", command=settings_win.destroy)
        close_btn.pack(pady=14)

    def _open_scripts_manager(self):
        # Call the main window's _show_scripts_manager if available
        if hasattr(self._main_window, '_show_scripts_manager'):
            self._main_window._show_scripts_manager()
        else:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", "Cannot open Scripts Manager from here.")

    def _return_from_automation(self):
        """Return from automation frame back to sheet view"""
        # Clear automation frame
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Recreate and show self
        self.__init__(self.parent, on_return=self.on_return)
        self.pack(fill=tk.BOTH, expand=True)

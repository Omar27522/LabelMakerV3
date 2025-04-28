import os
import sys
import tkinter as tk
import traceback
import atexit
import socket
import time
import ctypes
from utils.dpi import set_dpi_awareness
from ui.window_utils import set_taskbar_icon
import json

# Set DPI awareness before creating any windows
set_dpi_awareness()

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Logger placeholder (customize as needed)
from utils.logger import setup_logger

logger = setup_logger()

from utils.single_instance import SingleInstanceApp
from utils.error_handling import handle_exception
from utils.cleanup import cleanup

class SheetsManagerWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sheets Manager")
        self.geometry("800x525") #LETS CHANGE THIS so IT expands automatically so all the content fits.*/
        self.configure(bg="#f7f9fa")
        self._create_widgets()

    def _create_widgets(self):
        from modules.welcome import WelcomeModule
        from modules.connection import ConnectionModule
        from modules.sheet_view import SheetViewModule
        from modules.scripts_manager import ScriptsManagerModule
        from config.settings_manager import settings_manager

        # Menu bar (remove Features menu)
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        # You can add other menus here as needed (e.g., File, Edit, Help)

        # Container for swapping modules
        self._module_container = tk.Frame(self, bg="#f7f9fa")
        self._module_container.pack(fill=tk.BOTH, expand=True)
        
        # Check settings to determine which frame to show first
        connection_status = settings_manager.get('google_sheets', 'google_sheets_connection_status')
        sheet_url = settings_manager.get('google_sheets', 'google_sheet_url')
        sheet_name = settings_manager.get('google_sheets', 'google_sheet_name')
        
        if connection_status == "Connected" and sheet_url and sheet_name:
            # If we have valid settings, go straight to sheet view
            logger.info(f"Starting with sheet view for {sheet_name}")
            self._show_sheet_view()
        else:
            # If no valid settings, start with welcome
            logger.info("No valid settings found. Starting with welcome screen.")
            self._show_welcome()

    def _show_welcome(self):
        from modules.welcome import WelcomeModule
        self._clear_module()
        self._welcome_module = WelcomeModule(self._module_container, on_start=self._show_connection)
        self._welcome_module.get_frame().pack(fill=tk.BOTH, expand=True)

    def _show_connection(self):
        from modules.connection import ConnectionModule
        self._clear_module()
        self._connection_module = ConnectionModule(self._module_container, on_connect=self._show_sheet_view)
        self._connection_module.get_frame().pack(fill=tk.BOTH, expand=True)
        
    def _show_sheet_view(self):
        from modules.sheet_view import SheetViewModule
        self._clear_module()
        self._sheet_view_module = SheetViewModule(self._module_container, main_window=self, on_return=self._show_connection)
        self._sheet_view_module.get_frame().pack(fill=tk.BOTH, expand=True)

    def _clear_module(self):
        for widget in self._module_container.winfo_children():
            widget.destroy()

    def _show_scripts_manager(self):
        from modules.scripts_manager import ScriptsManagerModule
        self._clear_module()
        self._scripts_manager_module = ScriptsManagerModule(self._module_container, on_back=self._show_sheet_view)
        self._scripts_manager_module.get_frame().pack(fill=tk.BOTH, expand=True)

    def _on_start(self):
        # This method can be connected to WelcomeModule if needed
        tk.messagebox.showinfo("Sheets Manager", "Let's build out the Sheets Manager module!")

if __name__ == "__main__":
    try:
        sys.excepthook = handle_exception
        atexit.register(cleanup)
        single_instance = SingleInstanceApp()
        if not single_instance.is_first_instance:
            logger.info("Application is already running. Exiting.")
            try:
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Sheets Manager", "Sheets Manager is already running.")
            except:
                pass
            sys.exit(0)
        myappid = 'SheetsManager.MainWindow.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        logger.info(f"Set AppUserModelID to {myappid}")
        root = SheetsManagerWindow()
        set_taskbar_icon(root)
        single_instance.set_app(root)
        atexit.register(single_instance.cleanup)
        root.mainloop()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

import os
import sys
import tkinter as tk
import traceback
import atexit
import ctypes
import socket
import time

# Set DPI awareness before creating any windows
# This prevents scaling issues when interacting with system dialogs
try:
    # Try the newer API first (Windows 10+)
    awareness = ctypes.c_int(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
except AttributeError:
    # Fall back to older API (Windows 8.1 and earlier)
    ctypes.windll.user32.SetProcessDPIAware()
except Exception as e:
    # If it fails, just log it and continue
    print(f"Failed to set DPI awareness: {e}")

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.utils.logger import setup_logger
from src.ui.welcome_window import WelcomeWindow

# Setup logger
logger = setup_logger()

class SingleInstanceApp:
    """Ensures only one instance of the application is running"""
    
    def __init__(self, port=12345, app_name="LabelMaker"):
        """
        Initialize the single instance app
        
        Args:
            port: Port to use for socket communication
            app_name: Unique name for this application
        """
        self.port = port
        self.app_name = app_name
        self.sock = None
        self.app = None
        self.mutex_name = f'Global\\{app_name}SingleInstance'
        self.is_first_instance = self._check_instance()
    
    def _check_instance(self):
        """
        Check if another instance is already running
        
        Returns:
            bool: True if this is the first instance, False otherwise
        """
        # Try using a named mutex (most reliable on Windows)
        try:
            import win32event
            import win32api
            import winerror
            
            # Try to create a named mutex
            self.mutex = win32event.CreateMutex(None, False, self.mutex_name)
            last_error = win32api.GetLastError()
            
            # If the mutex already exists, another instance is running
            if last_error == winerror.ERROR_ALREADY_EXISTS:
                logger.info("Another instance is already running (detected by mutex)")
                return False
                
            logger.info("First instance of application started (mutex created)")
            return True
            
        except Exception as e:
            logger.error(f"Error using mutex approach: {e}")
            
            # Fall back to socket approach if mutex fails
            try:
                # Try to create a socket server
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind(('localhost', self.port))
                self.sock.listen(5)
                
                logger.info("First instance of application started (socket bound)")
                return True
            except socket.error as e:
                # Socket is already in use, another instance is running
                logger.info(f"Another instance is already running (socket in use): {e}")
                return False
    
    def set_app(self, app):
        """Set the application instance"""
        self.app = app
        logger.info("App reference set in SingleInstanceApp")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            # Close the socket if it exists
            if hasattr(self, 'sock') and self.sock:
                try:
                    self.sock.close()
                    self.sock = None
                    logger.info("Socket closed during cleanup")
                except Exception as e:
                    logger.error(f"Error closing socket: {e}")
            
            # Release the mutex if it exists
            if hasattr(self, 'mutex'):
                try:
                    import win32api
                    win32api.CloseHandle(self.mutex)
                    logger.info("Mutex released during cleanup")
                except Exception as e:
                    logger.error(f"Error releasing mutex: {e}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default handler for KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

    # Show error message to user
    try:
        error_msg = f"An unexpected error occurred:\n\n{str(exc_value)}\n\nPlease check the logs for details."
        tk.messagebox.showerror("Error", error_msg)
    except:
        pass  # If showing the error dialog fails, at least we logged the error

def cleanup():
    """Cleanup resources before exit"""
    logger.info("Application shutting down")
    try:
        # Use system temp directory instead of relative path
        temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, file))
                except:
                    pass
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def set_taskbar_icon(root):
    """Set the taskbar icon"""
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "icon_64.png")

        if os.path.exists(icon_path):
            # Load and set the icon using PhotoImage for the window icon
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)  # True makes this the default for all future windows
            # Keep reference to prevent garbage collection
            root._icon = icon
            
            print(f"Successfully set taskbar icon from {icon_path}")
        else:
            logger.warning(f"Icon file not found at {icon_path}")
            # Try alternate path
            icon_path = os.path.join(script_dir, "assets", "icon", "icon_64.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(True, icon)
                root._icon = icon
                print(f"Successfully set taskbar icon from alternate path {icon_path}")
            else:
                logger.warning(f"Icon file not found at alternate path {icon_path}")
    except Exception as e:
        logger.error(f"Failed to set taskbar icon: {str(e)}")

if __name__ == "__main__":
    try:
        # Set exception handler
        sys.excepthook = handle_exception
        
        # Register cleanup function
        atexit.register(cleanup)
        
        # Check if another instance is already running
        single_instance = SingleInstanceApp()
        
        if not single_instance.is_first_instance:
            # Another instance is already running
            logger.info("Application is already running. Exiting.")
            
            # Show a message to the user
            try:
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Label Maker", "Label Maker is already running.")
            except:
                pass
                
            sys.exit(0)
        
        # Set the taskbar icon
        # This MUST be done before creating any windows
        myappid = 'LabelMaker.WelcomeWindow.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        logger.info(f"Set AppUserModelID to {myappid}")

        # Create the application
        root = WelcomeWindow()

        # Set the window icon
        set_taskbar_icon(root)
        
        # Set the application reference in the single instance app
        single_instance.set_app(root)
        
        # Register cleanup function
        atexit.register(single_instance.cleanup)
        
        # Start the application
        root.mainloop()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

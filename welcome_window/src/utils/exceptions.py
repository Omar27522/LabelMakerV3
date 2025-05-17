"""
Exceptions module for handling exception cases.
This module provides functionality for processing exceptions in a separate workflow.
"""
import os
import sys
import time
import logging
import webbrowser
import threading
import pyautogui
import pyperclip
import datetime

# Configure logging
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(logs_dir, 'label_maker.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set up logging
logger = logging.getLogger(__name__)

class ExceptionsManager:
    """Class for managing exception operations."""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, config_manager=None):
        """Get the singleton instance of ExceptionsManager"""
        with cls._lock:
            if cls._instance is None:
                if config_manager is None:
                    raise ValueError("config_manager must be provided when creating a new instance")
                cls._instance = cls(config_manager)
            return cls._instance
    
    def __init__(self, config_manager):
        """
        Initialize the exceptions manager.
        
        Args:
            config_manager: The application's configuration manager
        """
        self.config_manager = config_manager
        self._active_exception_dialogs = {}
        logger.info("ExceptionsManager initialized")
    
    def process_exception(self, tracking_number, sku=None):
        """
        Process an exception operation for a tracking number.
        
        Args:
            tracking_number: The tracking number to process
            sku: Optional SKU number associated with the tracking number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Processing exception for tracking number: {tracking_number}, SKU: {sku or 'N/A'}")
            
            # Store the tracking number and SKU
            self.current_tracking = tracking_number
            self.current_sku = sku
            
            # Log the exception event
            try:
                from src.utils.log_manager import log_shipping_event
                log_shipping_event(
                    tracking_number=tracking_number,
                    sku=sku,
                    action="exception",
                    status="initiated",
                    details=f"Exception processing initiated for tracking number: {tracking_number}"
                )
            except ImportError:
                logger.warning("Could not import log_shipping_event function")
            
            # Show the enhanced exception selection dialog
            try:
                from src.utils.exception_dialog import show_exception_dialog
                exception_type = show_exception_dialog(tracking_number, sku)
                
                if exception_type:
                    logger.info(f"Selected exception type: {exception_type}")
                    return self.handle_exception_type(exception_type, tracking_number, sku)
                else:
                    logger.info("Exception selection canceled by user")
                    return False
            except ImportError:
                logger.warning("Could not import show_exception_dialog function, falling back to default behavior")
                
                # Fallback to default behavior
                url = "about:blank"
                logger.info(f"Opening empty website for exception handling")
                
                # Open in a new browser tab
                success = webbrowser.open(url, new=2)
                
                if success:
                    logger.info("Successfully opened empty website for exception handling")
                    
                    # Wait a few seconds
                    logger.info("Waiting 5 seconds before closing tab...")
                    time.sleep(5)
                    
                    # Close the browser tab
                    self.close_browser_tab()
                    
                    logger.info("Exception process completed")
                    return True
                else:
                    logger.error("Failed to open browser for exception handling")
                    return False
                
        except Exception as e:
            error_msg = f"Error processing exception for tracking number {tracking_number}: {str(e)}"
            logger.error(error_msg)
            return False
            
    def open_exceptions_page(self):
        """
        Open the exceptions page in the default browser
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Opening exceptions page")
            
            # Get the exceptions page URL from config or use default
            if hasattr(self.config_manager.settings, 'exceptions_page_url') and self.config_manager.settings.exceptions_page_url:
                url = self.config_manager.settings.exceptions_page_url
            else:
                # Default URL for exceptions page - replace with actual URL when known
                url = "https://iwms.us.jdlglobal.com/#/exceptions"
                # Save the URL to config for future use
                self.config_manager.settings.exceptions_page_url = url
                self.config_manager.save_settings()
                
            # Append tracking number to URL if available
            if hasattr(self, 'current_tracking') and self.current_tracking:
                # Format depends on the site's URL structure
                if '?' in url:
                    url += f"&tracking={self.current_tracking}"
                else:
                    url += f"?tracking={self.current_tracking}"
            
            # Open in a new browser tab
            success = webbrowser.open(url, new=2)
            
            # Alternative methods if standard method fails
            if not success and os.name == 'nt':
                logger.info("Trying alternative method to open browser")
                os.startfile(url)
                success = True
            
            if not success:
                logger.info("Trying subprocess method to open browser")
                import subprocess
                browsers = ['chrome', 'firefox', 'safari', 'opera', 'iexplore']
                for browser in browsers:
                    try:
                        subprocess.Popen([browser, url])
                        success = True
                        break
                    except Exception:
                        continue
            
            if success:
                logger.info("Successfully opened exceptions page")
                return True
            else:
                logger.error("All methods to open browser failed")
                return False
                
        except Exception as e:
            error_msg = f"Error opening exceptions page: {str(e)}"
            logger.error(error_msg)
            return False
    
    def close_browser_tab(self):
        """
        Close the current browser tab
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Closing browser tab")
            pyautogui.hotkey('ctrl', 'w')  # Close the tab
            time.sleep(1)  # Wait a moment for the tab to close
            return True
        except Exception as e:
            error_msg = f"Error closing browser tab: {str(e)}"
            logger.error(error_msg)
            return False
        
    def wait_for_page_load(self, exception_type=None, expected_elements=None, max_wait_time=15):
        """
        Wait for a page to fully load using the page_load_detector module
        
        Args:
            exception_type: Type of exception being processed (for logging)
            expected_elements: List of text elements expected on the page when loaded
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            bool: True if page is detected as loaded, False if timeout occurred
        """
        try:
            # Import the page load detector module
            from src.utils.page_load_detector import detect_page_load
            
            logger.info(f"Waiting for {exception_type or 'exception'} page to load...")
            
            # Default expected elements if none provided
            if not expected_elements:
                expected_elements = ["exception", "form", "submit"]
                
            # Use the page load detector with appropriate parameters
            screenshot_prefix = f"exception_{exception_type or 'page'}"
            
            # Call the page load detection function
            page_loaded = detect_page_load(
                max_wait_time=max_wait_time,
                check_interval=0.5,
                expected_elements=expected_elements,
                screenshot_prefix=screenshot_prefix
            )
            
            if page_loaded:
                logger.info(f"{exception_type or 'Exception'} page successfully loaded")
            else:
                logger.warning(f"{exception_type or 'Exception'} page load detection timed out after {max_wait_time} seconds")
                
            return page_loaded
            
        except Exception as e:
            error_msg = f"Error in wait_for_page_load: {str(e)}"
            logger.error(error_msg)
            # Fall back to a simple delay if detection fails
            logger.info(f"Falling back to simple delay of 5 seconds")
            time.sleep(5)
            return True  # Assume page loaded after delay
            
    # Track active exception dialogs to prevent duplicates
    _active_exception_dialogs = {}
    
    def register_exception_dialog(self, exception_type, tracking_number, hwnd):
        """
        Register an active exception dialog
        
        Args:
            exception_type: The type of exception
            tracking_number: The tracking number
            hwnd: Window handle of the dialog
        """
        dialog_key = f"{exception_type}_{tracking_number}"
        self._active_exception_dialogs[dialog_key] = hwnd
        logger.info(f"Registered exception dialog for {exception_type} with handle {hwnd}")
    
    def unregister_exception_dialog(self, exception_type, tracking_number):
        """
        Unregister an active exception dialog
        
        Args:
            exception_type: The type of exception
            tracking_number: The tracking number
        """
        dialog_key = f"{exception_type}_{tracking_number}"
        if dialog_key in self._active_exception_dialogs:
            del self._active_exception_dialogs[dialog_key]
            logger.info(f"Unregistered exception dialog for {exception_type} and tracking {tracking_number}")
    
    
    def handle_exception_type(self, exception_type, tracking_number, sku=None):
        """
        Handle a specific type of exception
        
        Args:
            exception_type: The type of exception to handle (e.g., 'sku mismatch', 'rma on label but not in system')
            tracking_number: The tracking number to process
            sku: Optional SKU number associated with the tracking number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Handling {exception_type} exception for tracking number: {tracking_number}")
            
            # Check if we already have an active dialog for this exception type
            dialog_key = f"{exception_type}_{tracking_number}"
            if dialog_key in self._active_exception_dialogs:
                logger.info(f"Exception dialog for {exception_type} and tracking {tracking_number} is already active")
                # Try to focus the existing dialog
                try:
                    import win32gui
                    hwnd = self._active_exception_dialogs[dialog_key]
                    if win32gui.IsWindow(hwnd):  # Check if window still exists
                        win32gui.SetForegroundWindow(hwnd)
                        logger.info(f"Focused existing dialog with handle {hwnd}")
                        return True
                    else:
                        # Window no longer exists, remove from tracking
                        del self._active_exception_dialogs[dialog_key]
                except Exception as e:
                    logger.error(f"Error focusing existing dialog: {str(e)}")
                    # Remove potentially invalid reference
                    if dialog_key in self._active_exception_dialogs:
                        del self._active_exception_dialogs[dialog_key]
            
            # Store the tracking number and exception type
            self.current_tracking = tracking_number
            self.current_sku = sku
            self.current_exception_type = exception_type
            
            # Log the exception event
            try:
                from src.utils.log_manager import log_shipping_event
                log_shipping_event(
                    tracking_number=tracking_number,
                    sku=sku,
                    action=f"exception_{exception_type}",
                    status="initiated",
                    details=f"{exception_type.capitalize()} exception handling initiated for tracking number: {tracking_number}"
                )
            except ImportError:
                logger.warning("Could not import log_shipping_event function")
            
            # Store the exception type in lowercase for easier comparison
            exception_type_lower = exception_type.lower()
            
            # Special handling for SKU mismatch - don't open browser tab yet
            if exception_type_lower == 'sku mismatch':
                logger.info("SKU mismatch requires Order Reference Number first, not opening browser yet")
                # Call the handler which will ask for RS number and then open browser
                return self._handle_sku_mismatch(tracking_number, sku)
            
            # For all other exception types, proceed with opening the browser
            url = self._get_exception_url(exception_type)
            logger.info(f"Opening exception URL for {exception_type}: {url}")
            
            # Open in a new browser tab
            success = webbrowser.open(url, new=2)
            
            if success:
                logger.info(f"Successfully opened exception URL for {exception_type}")
                
                # Wait for the page to load
                self.wait_for_page_load(exception_type)
                
                # Handle specific exception types with different behaviors
                if exception_type_lower == 'rma on label but not in system':
                    # Handle RMA missing exception
                    self._handle_rma_missing(tracking_number)
                elif exception_type_lower == 'fraudulent / suspicious package / e':
                    # Handle suspicious package exception
                    self._handle_suspicious_package(tracking_number)
                elif exception_type_lower == 'return to sender':
                    # Handle return to sender exception
                    self._handle_return_to_sender(tracking_number, sku)
                
                # Take a screenshot if configured
                if hasattr(self.config_manager.settings, 'take_exception_screenshots') and self.config_manager.settings.take_exception_screenshots:
                    self.take_exception_screenshot(exception_type)
                
                logger.info(f"{exception_type.capitalize()} exception process initiated successfully")
                return True
            else:
                logger.error(f"Failed to open browser for {exception_type} exception handling")
                return False
                
        except Exception as e:
            error_msg = f"Error handling {exception_type} exception for tracking number {tracking_number}: {str(e)}"
            logger.error(error_msg)
            return False
            
    def _get_exception_url(self, exception_type):
        """
        Get the URL for a specific exception type
        
        Args:
            exception_type: The type of exception
            
        Returns:
            str: The URL for the exception
        """
        # Use a single base URL for all exception types as per requirements
        base_url = self.config_manager.settings.exception_base_url
        
        # If no exception base URL is configured, use the default
        if not base_url:
            base_url = "https://jdl.iwms.com/exceptions"
            logger.info(f"Using default exception base URL: {base_url}")
        
        logger.info(f"Using exception base URL: {base_url} for exception type: {exception_type}")
        return base_url
        
    def _open_browser_tab(self, url):
        """
        Open a browser tab with multiple fallback methods
        
        Args:
            url: The URL to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Attempting to open URL: {url}")
        
        # Method 1: Use webbrowser module
        try:
            logger.info("Trying webbrowser.open method")
            success = webbrowser.open(url, new=2)
            if success:
                logger.info("Successfully opened browser using webbrowser.open")
                return True
            else:
                logger.warning("webbrowser.open returned False, trying alternative methods")
        except Exception as e:
            logger.error(f"Error using webbrowser.open: {str(e)}")
        
        # Method 2: Try using os.system with start command on Windows
        try:
            logger.info("Trying os.system method")
            import os
            os.system(f'start "" "{url}"')
            logger.info("Executed os.system command to open browser")
            return True
        except Exception as e:
            logger.error(f"Error using os.system: {str(e)}")
        
        # Method 3: Try using subprocess
        try:
            logger.info("Trying subprocess method")
            import subprocess
            subprocess.Popen(["cmd", "/c", "start", "", url], shell=True)
            logger.info("Executed subprocess command to open browser")
            return True
        except Exception as e:
            logger.error(f"Error using subprocess: {str(e)}")
            
        # Method 4: Try using the default browser path directly
        try:
            logger.info("Trying direct browser launch method")
            # Try common browser paths
            browser_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                r"C:\Program Files\Internet Explorer\iexplore.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            
            for browser_path in browser_paths:
                if os.path.exists(browser_path):
                    logger.info(f"Found browser at: {browser_path}")
                    os.system(f'"{browser_path}" "{url}"')
                    logger.info(f"Launched browser directly using: {browser_path}")
                    return True
        except Exception as e:
            logger.error(f"Error launching browser directly: {str(e)}")
        
        logger.error("All methods to open browser failed")
        return False
        
    # This section was cleaned up
        
    def _open_specific_url(self, url):
        """
        Open a specific URL in the browser
        
        Args:
            url: The URL to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Opening specific URL: {url}")
            
            # Append tracking number to URL if available
            if hasattr(self, 'current_tracking') and self.current_tracking:
                # Format depends on the site's URL structure
                if '?' in url:
                    url += f"&tracking={self.current_tracking}"
                else:
                    url += f"?tracking={self.current_tracking}"
            
            # Open in a new browser tab
            success = webbrowser.open(url, new=2)
            
            # Alternative methods if standard method fails
            if not success and os.name == 'nt':
                logger.info("Trying alternative method to open browser")
                os.startfile(url)
                success = True
            
            if not success:
                logger.info("Trying subprocess method to open browser")
                import subprocess
                browsers = ['chrome', 'firefox', 'safari', 'opera', 'iexplore']
                for browser in browsers:
                    try:
                        subprocess.Popen([browser, url])
                        success = True
                        break
                    except Exception:
                        continue
            
            if success:
                logger.info(f"Successfully opened URL: {url}")
                return True
            else:
                logger.error(f"All methods to open URL failed: {url}")
                return False
                
        except Exception as e:
            error_msg = f"Error opening specific URL {url}: {str(e)}"
            logger.error(error_msg)
            return False
            
    def _handle_sku_mismatch(self, tracking_number, sku=None, url=None):
        """
        Handle SKU mismatch exception - requires Order Reference Number / Picking Route number (RS number)
        
        Args:
            tracking_number: The tracking number to process
            sku: Optional SKU number associated with the tracking number
            url: The URL to open for the SKU mismatch exception
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Handling SKU mismatch for tracking number: {tracking_number}, SKU: {sku or 'N/A'}")
            
            # FIRST: Prompt for Order Reference Number / Picking Route number (RS number)
            # Use a simpler approach with tkinter.simpledialog that's more reliable
            import tkinter as tk
            from tkinter import simpledialog
            
            # Create a root window but keep it hidden
            root = tk.Tk()
            root.withdraw()
            
            # Make sure the window is properly initialized and visible
            root.update()
            
            # Show a dialog to get the RS number
            rs_number = simpledialog.askstring(
                "Order Reference Number", 
                "Enter the Order Reference Number / Picking Route (RS number):",
                parent=root
            )
            
            # Destroy the root window
            root.destroy()
            
            if not rs_number:
                logger.warning("No RS number provided, aborting SKU mismatch handling")
                return False
            
            logger.info(f"RS number provided: {rs_number}")
            
            # SECOND: Now open the browser tab with the exception URL
            if not url:
                # If URL wasn't provided, get it
                url = self._get_exception_url('sku mismatch')
                
            logger.info(f"Opening SKU mismatch exception URL: {url}")
            
            # Use a very direct approach to open the browser - try multiple methods
            try:
                # For testing, use a well-known URL that's guaranteed to work
                test_url = "https://www.google.com"
                logger.info(f"Using test URL for debugging: {test_url}")
                
                # Method 1: Direct system command
                import os
                logger.info("Trying direct system command to open browser")
                os.system(f'start "" "{test_url}"')
                
                # Method 2: Also try subprocess as a backup
                import subprocess
                logger.info("Also trying subprocess to open browser")
                subprocess.Popen(["cmd.exe", "/c", "start", "", test_url], shell=True)
                
                # Method 3: Try using a direct browser path
                browser_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                ]
                
                for browser_path in browser_paths:
                    if os.path.exists(browser_path):
                        logger.info(f"Found browser at: {browser_path}")
                        os.system(f'"{browser_path}" "{test_url}"')
                        break
                
                # Assume success if no exceptions
                success = True
                logger.info("Browser opening commands executed successfully")
            except Exception as e:
                logger.error(f"Error opening browser: {str(e)}")
                success = False
            
            if not success:
                logger.error("Failed to open browser for SKU mismatch exception handling")
                return False
                
            logger.info("Waiting for SKU mismatch page to load...")
            self.wait_for_page_load(
                exception_type='sku_mismatch',
                expected_elements=['exception', 'form', 'submit'],
                max_wait_time=15
            )
            
            # Store original clipboard content to restore later if needed
            original_clipboard = pyperclip.paste()
            
            # Use pyautogui to fill in the form fields
            try:
                # Wait a moment for the page to be fully loaded and interactive
                time.sleep(1)
                
                # STEP 1: Tab - Enter - up arrow key +2 - Enter (First dropdown selection)
                logger.info("Step 1: First dropdown selection")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.3)
                pyautogui.press('up')
                time.sleep(0.3)
                pyautogui.press('up')  # Second up arrow press
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # STEP 2: Tab - Paste Tracking number
                logger.info(f"Step 2: Entering tracking number: {tracking_number}")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyperclip.copy(tracking_number)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                
                # STEP 3: Tab - Enter - up arrow key - Enter (Second dropdown selection)
                logger.info("Step 3: Second dropdown selection")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.3)
                pyautogui.press('up')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # STEP 4: Tab - Enter - down arrow key - Enter (Third dropdown selection)
                logger.info("Step 4: Third dropdown selection")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.3)
                pyautogui.press('down')  # Down arrow key
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # STEP 5: Tab - Paste SKU
                if sku:
                    logger.info(f"Step 5: Entering SKU: {sku}")
                    pyautogui.press('tab')
                    time.sleep(0.3)
                    pyperclip.copy(sku)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.5)
                else:
                    logger.info("Step 5: No SKU provided, skipping")
                    pyautogui.press('tab')
                    time.sleep(0.3)
                
                # STEP 6: Tab - Enter 1 (quantity)
                logger.info("Step 6: Entering quantity: 1")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyperclip.copy("1")
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                
                # STEP 7: Tab - Paste Order Reference Number / Picking Route number
                logger.info(f"Step 7: Entering RS number: {rs_number}")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyperclip.copy(rs_number)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                
                # STEP 8: Final Tab
                logger.info("Step 8: Final Tab")
                pyautogui.press('tab')
                time.sleep(0.3)
                
                # STEP 9: Press Enter to submit the form
                logger.info("Step 9: Pressing Enter to submit the form")
                pyautogui.press('enter')
                time.sleep(2.5)  # Increased wait time to ensure dialog appears
                
                # STEP 10: Press Delete key
                logger.info("Step 10: Pressing Delete key")
                pyautogui.press('delete')
                time.sleep(0.5)  # Short wait after pressing Delete
                
                # Restore original clipboard content
                pyperclip.copy(original_clipboard)
                
                # Wait a moment for the form to process and the Process Exception window to appear
                time.sleep(3)  # Increased wait time to ensure dialog appears
                
                # Try a more direct approach to focus the window
                try:
                    # Import necessary modules
                    import win32gui
                    import win32con
                    import win32api
                    import ctypes
                    from ctypes import wintypes
                    
                    # Define Windows API functions for more direct window manipulation
                    user32 = ctypes.WinDLL('user32', use_last_error=True)
                    
                    # Define necessary Windows API functions
                    user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
                    user32.AttachThreadInput.restype = wintypes.BOOL
                    user32.BringWindowToTop.argtypes = [wintypes.HWND]
                    user32.BringWindowToTop.restype = wintypes.BOOL
                    user32.GetForegroundWindow.argtypes = []
                    user32.GetForegroundWindow.restype = wintypes.HWND
                    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
                    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
                    user32.GetCurrentThreadId.argtypes = []
                    user32.GetCurrentThreadId.restype = wintypes.DWORD
                    
                    logger.info("Using direct Windows API approach to focus window")
                    
                    # Function to forcefully set focus to a window
                    def force_focus_window(hwnd):
                        # Get thread IDs
                        remote_thread = user32.GetWindowThreadProcessId(hwnd, None)
                        current_thread = user32.GetCurrentThreadId()
                        
                        # Attach threads to synchronize input processing
                        attached = False
                        if current_thread != remote_thread:
                            attached = user32.AttachThreadInput(current_thread, remote_thread, True)
                            logger.info(f"Attached threads: {attached}")
                        
                        # Forcefully bring window to top and set focus
                        user32.BringWindowToTop(hwnd)
                        user32.SetForegroundWindow(hwnd)
                        win32gui.SetActiveWindow(hwnd)
                        
                        # Detach threads if they were attached
                        if attached:
                            user32.AttachThreadInput(current_thread, remote_thread, False)
                        
                        # Get window rect to find center and title bar for mouse clicks
                        rect = wintypes.RECT()
                        user32.GetWindowRect(hwnd, ctypes.byref(rect))
                        center_x = (rect.left + rect.right) // 2
                        center_y = (rect.top + rect.bottom) // 2
                        
                        # Calculate title bar position (typically near the top of the window)
                        title_bar_x = center_x
                        title_bar_y = rect.top + 10  # 10 pixels down from the top
                        
                        # First click on the title bar to ensure window activation
                        logger.info(f"Clicking on title bar at ({title_bar_x}, {title_bar_y})")
                        pyautogui.click(title_bar_x, title_bar_y)
                        time.sleep(0.3)
                        
                        # Then click in the center of the window
                        logger.info(f"Clicking in center at ({center_x}, {center_y})")
                        pyautogui.click(center_x, center_y)
                        time.sleep(0.3)
                        
                        # Try one more focus attempt
                        user32.SetForegroundWindow(hwnd)
                        
                        return True
                    
                    # Find all windows
                    def find_all_windows():
                        result = []
                        def winEnumHandler(hwnd, ctx):
                            if win32gui.IsWindowVisible(hwnd):
                                title = win32gui.GetWindowText(hwnd)
                                # Log all visible windows to help with debugging
                                if title:  # Only log windows with titles
                                    logger.info(f"Found window: '{title}' with handle {hwnd}")
                                    result.append((hwnd, title))
                        win32gui.EnumWindows(winEnumHandler, None)
                        return result
                    
                    # Find all windows and log them
                    all_windows = find_all_windows()
                    logger.info(f"Found {len(all_windows)} total windows")
                    
                    # First, try Alt+Tab to switch to the most recent window
                    logger.info("Trying Alt+Tab to switch to most recent window")
                    pyautogui.hotkey('alt', 'tab')
                    time.sleep(0.5)
                    
                    # Then try to find and focus specific windows - prioritize exact match first
                    exact_match = None
                    for hwnd, title in all_windows:
                        # Look for exact match first
                        if title == 'Process Exception':
                            exact_match = (hwnd, title)
                            break
                    
                    # If we found an exact match, focus it
                    if exact_match:
                        hwnd, title = exact_match
                        logger.info(f"Found exact match window: '{title}'")
                        try:
                            if force_focus_window(hwnd):
                                logger.info(f"Successfully forced focus on exact match window: '{title}'")
                        except Exception as e:
                            logger.error(f"Error forcing focus on exact match window '{title}': {str(e)}")
                    # Otherwise try partial matches
                    else:
                        for hwnd, title in all_windows:
                            if any(text in title for text in ['Process Exception', 'Exception', 'SKU Mismatch', 'JDL Global']):
                                logger.info(f"Attempting to force focus on window: '{title}'")
                                try:
                                    if force_focus_window(hwnd):
                                        logger.info(f"Successfully forced focus on window: '{title}'")
                                        break
                                except Exception as e:
                                    logger.error(f"Error forcing focus on window '{title}': {str(e)}")
                    
                    # As a last resort, try clicking in the center of the screen
                    logger.info("Clicking center of screen as last resort")
                    screen_width, screen_height = pyautogui.size()
                    pyautogui.click(screen_width // 2, screen_height // 2)
                    
                except Exception as e:
                    logger.error(f"Error trying to focus Process Exception window: {str(e)}")
                
                logger.info(f"Successfully filled in SKU mismatch form for tracking number: {tracking_number}")
                return True
            except Exception as e:
                logger.error(f"Error filling in SKU mismatch form: {str(e)}")
                # Restore original clipboard content
                pyperclip.copy(original_clipboard)
                return False
                
        except Exception as e:
            error_msg = f"Error handling SKU mismatch for tracking number {tracking_number}: {str(e)}"
            logger.error(error_msg)
            return False
    
    def _handle_rma_missing(self, tracking_number):
        """
        Handle RMA missing exception
        
        Args:
            tracking_number: The tracking number to process
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Handling RMA missing for tracking number: {tracking_number}")
            
            # Wait for the page to load completely using the new page load detection
            self.wait_for_page_load(
                exception_type='rma_missing',
                expected_elements=['exception', 'form', 'tracking'],
                max_wait_time=10
            )
            
            # Use pyautogui to fill in the form fields
            try:
                # Wait a moment for the page to be fully loaded and interactive
                time.sleep(1)
                
                # Copy the tracking number to clipboard
                pyperclip.copy(tracking_number)
                
                # Tab to the tracking number field and paste
                pyautogui.press('tab')
                pyautogui.hotkey('ctrl', 'v')
                
                logger.info(f"Successfully filled in RMA missing form for tracking number: {tracking_number}")
                return True
            except Exception as e:
                logger.error(f"Error filling in RMA missing form: {str(e)}")
                return False
                
        except Exception as e:
            error_msg = f"Error handling RMA missing for tracking number {tracking_number}: {str(e)}"
            logger.error(error_msg)
            return False
    
    def _handle_suspicious_package(self, tracking_number):
        """
        Handle suspicious package exception
        
        Args:
            tracking_number: The tracking number to process
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Handling suspicious package for tracking number: {tracking_number}")
            
            # Wait for the page to load completely
            time.sleep(2)
            
            # Use pyautogui to fill in the form fields
            try:
                # Wait a moment for the page to be fully loaded and interactive
                time.sleep(1)
                
                # Copy the tracking number to clipboard
                pyperclip.copy(tracking_number)
                
                # Tab to the tracking number field and paste
                pyautogui.press('tab')
                pyautogui.hotkey('ctrl', 'v')
                
                logger.info(f"Successfully filled in suspicious package form for tracking number: {tracking_number}")
                return True
            except Exception as e:
                logger.error(f"Error filling in suspicious package form: {str(e)}")
                return False
                
        except Exception as e:
            error_msg = f"Error handling suspicious package for tracking number {tracking_number}: {str(e)}"
            logger.error(error_msg)
            return False
    
    def _handle_return_to_sender(self, tracking_number, sku=None):
        """
        Handle return to sender exception
        
        Args:
            tracking_number: The tracking number to process
            sku: Optional SKU number associated with the tracking number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Handling return to sender for tracking number: {tracking_number}")
            
            # Wait for the page to load completely
            time.sleep(2)
            
            # Store original clipboard content to restore later if needed
            original_clipboard = pyperclip.paste()
            
            # Use pyautogui to fill in the form fields
            try:
                # Wait a moment for the page to be fully loaded and interactive
                time.sleep(1)
                
                # STEP 1: Tab - Enter - up arrow key +2 - Enter
                logger.info("Step 1: First dropdown selection")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.3)
                pyautogui.press('up')
                time.sleep(0.3)
                pyautogui.press('up')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # STEP 2: Tab - Paste Tracking number
                logger.info(f"Step 2: Entering tracking number: {tracking_number}")
                pyautogui.press('tab')
                time.sleep(0.3)
                # Copy the tracking number to clipboard
                pyperclip.copy(tracking_number)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                
                # STEP 3: Tab - Enter - up arrow key - Enter
                logger.info("Step 3: Second dropdown selection")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.3)
                pyautogui.press('up')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # STEP 4: Tab - Enter - up arrow key - Enter
                logger.info("Step 4: Third dropdown selection")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.3)
                pyautogui.press('up')
                time.sleep(0.3)
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # STEP 5: Tab - N/A
                logger.info("Step 5: Entering N/A")
                pyautogui.press('tab')
                time.sleep(0.3)
                pyperclip.copy("N/A")
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                
                # STEP 6: Tab - SKU
                logger.info(f"Step 6: Entering SKU: {sku if sku else 'N/A'}")
                pyautogui.press('tab')
                time.sleep(0.3)
                # Use provided SKU or N/A if none provided
                pyperclip.copy(sku if sku else "N/A")
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                
                # STEP 7: Press Enter to submit the form
                logger.info("Step 7: Pressing Enter to submit the form")
                pyautogui.press('enter')
                time.sleep(2.5)  # Increased wait time to ensure dialog appears
                
                # STEP 8: Press Delete key
                logger.info("Step 8: Pressing Delete key")
                pyautogui.press('delete')
                time.sleep(0.5)  # Short wait after pressing Delete
                
                # Restore original clipboard content
                pyperclip.copy(original_clipboard)
                
                # Wait a moment for the form to process and the Process Exception window to appear
                time.sleep(3)  # Increased wait time to ensure dialog appears
                
                # Try a more direct approach to focus the window
                try:
                    # Import necessary modules
                    import win32gui
                    import win32con
                    import win32api
                    import ctypes
                    from ctypes import wintypes
                    
                    # Define Windows API functions for more direct window manipulation
                    user32 = ctypes.WinDLL('user32', use_last_error=True)
                    
                    # Define necessary Windows API functions
                    user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
                    user32.AttachThreadInput.restype = wintypes.BOOL
                    user32.BringWindowToTop.argtypes = [wintypes.HWND]
                    user32.BringWindowToTop.restype = wintypes.BOOL
                    user32.GetForegroundWindow.argtypes = []
                    user32.GetForegroundWindow.restype = wintypes.HWND
                    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
                    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
                    user32.GetCurrentThreadId.argtypes = []
                    user32.GetCurrentThreadId.restype = wintypes.DWORD
                    
                    logger.info("Using direct Windows API approach to focus window")
                    
                    # Function to forcefully set focus to a window
                    def force_focus_window(hwnd):
                        # Get thread IDs
                        remote_thread = user32.GetWindowThreadProcessId(hwnd, None)
                        current_thread = user32.GetCurrentThreadId()
                        
                        # Attach threads to synchronize input processing
                        attached = False
                        if current_thread != remote_thread:
                            attached = user32.AttachThreadInput(current_thread, remote_thread, True)
                            logger.info(f"Attached threads: {attached}")
                        
                        # Forcefully bring window to top and set focus
                        user32.BringWindowToTop(hwnd)
                        user32.SetForegroundWindow(hwnd)
                        win32gui.SetActiveWindow(hwnd)
                        
                        # Detach threads if they were attached
                        if attached:
                            user32.AttachThreadInput(current_thread, remote_thread, False)
                        
                        # Get window rect to find center and title bar for mouse clicks
                        rect = wintypes.RECT()
                        user32.GetWindowRect(hwnd, ctypes.byref(rect))
                        center_x = (rect.left + rect.right) // 2
                        center_y = (rect.top + rect.bottom) // 2
                        
                        # Calculate title bar position (typically near the top of the window)
                        title_bar_x = center_x
                        title_bar_y = rect.top + 10  # 10 pixels down from the top
                        
                        # First click on the title bar to ensure window activation
                        logger.info(f"Clicking on title bar at ({title_bar_x}, {title_bar_y})")
                        pyautogui.click(title_bar_x, title_bar_y)
                        time.sleep(0.3)
                        
                        # Then click in the center of the window
                        logger.info(f"Clicking in center at ({center_x}, {center_y})")
                        pyautogui.click(center_x, center_y)
                        time.sleep(0.3)
                        
                        # Try one more focus attempt
                        user32.SetForegroundWindow(hwnd)
                        
                        return True
                    
                    # Find all windows
                    def find_all_windows():
                        result = []
                        def winEnumHandler(hwnd, ctx):
                            if win32gui.IsWindowVisible(hwnd):
                                title = win32gui.GetWindowText(hwnd)
                                # Log all visible windows to help with debugging
                                if title:  # Only log windows with titles
                                    logger.info(f"Found window: '{title}' with handle {hwnd}")
                                    result.append((hwnd, title))
                        win32gui.EnumWindows(winEnumHandler, None)
                        return result
                    
                    # Find all windows and log them
                    all_windows = find_all_windows()
                    logger.info(f"Found {len(all_windows)} total windows")
                    
                    # First, try Alt+Tab to switch to the most recent window
                    logger.info("Trying Alt+Tab to switch to most recent window")
                    pyautogui.hotkey('alt', 'tab')
                    time.sleep(0.5)
                    
                    # Then try to find and focus specific windows - prioritize exact match first
                    exact_match = None
                    for hwnd, title in all_windows:
                        # Look for exact match first
                        if title == 'Process Exception':
                            exact_match = (hwnd, title)
                            break
                    
                    # If we found an exact match, focus it
                    if exact_match:
                        hwnd, title = exact_match
                        logger.info(f"Found exact match window: '{title}'")
                        try:
                            if force_focus_window(hwnd):
                                logger.info(f"Successfully forced focus on exact match window: '{title}'")
                        except Exception as e:
                            logger.error(f"Error forcing focus on exact match window '{title}': {str(e)}")
                    # Otherwise try partial matches
                    else:
                        for hwnd, title in all_windows:
                            if any(text in title for text in ['Process Exception', 'Exception', 'Return to Sender', 'JDL Global']):
                                logger.info(f"Attempting to force focus on window: '{title}'")
                                try:
                                    if force_focus_window(hwnd):
                                        logger.info(f"Successfully forced focus on window: '{title}'")
                                        break
                                except Exception as e:
                                    logger.error(f"Error forcing focus on window '{title}': {str(e)}")
                    
                    # As a last resort, try clicking in the center of the screen
                    logger.info("Clicking center of screen as last resort")
                    screen_width, screen_height = pyautogui.size()
                    pyautogui.click(screen_width // 2, screen_height // 2)
                    
                except Exception as e:
                    logger.error(f"Error trying to focus Process Exception window: {str(e)}")
                
                logger.info(f"Successfully filled in return to sender form for tracking number: {tracking_number}")
                return True
            except Exception as e:
                logger.error(f"Error filling in return to sender form: {str(e)}")
                # Restore original clipboard content
                pyperclip.copy(original_clipboard)
                return False
                
        except Exception as e:
            error_msg = f"Error handling return to sender for tracking number {tracking_number}: {str(e)}"
            logger.error(error_msg)
            return False
    
    def take_exception_screenshot(self, exception_type=None):
        """
        Take a screenshot of the current exception page for documentation
        
        Args:
            exception_type: Optional type of exception for naming the screenshot
            
        Returns:
            str: Path to the saved screenshot or None if failed
        """
        try:
            # Create screenshots directory if it doesn't exist
            screenshots_dir = os.path.join(logs_dir, 'exception_screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Generate filename with timestamp and exception type
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            exception_name = exception_type or getattr(self, 'current_exception_type', 'general')
            tracking = getattr(self, 'current_tracking', 'unknown')
            filename = f"exception_{exception_name}_{tracking}_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            # Take the screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            logger.info(f"Saved exception screenshot to {filepath}")
            return filepath
        except Exception as e:
            error_msg = f"Error taking exception screenshot: {str(e)}"
            logger.error(error_msg)
            return None

def process_exception_operation(config_manager, tracking_number, sku=None):
    """
    Process an exception operation for a tracking number.
    
    Args:
        config_manager: The application's configuration manager
        tracking_number: The tracking number to process
        sku: Optional SKU number associated with the tracking number
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get the singleton instance
    exceptions_manager = ExceptionsManager.get_instance(config_manager)
    
    try:
        logger.info(f"Starting exception process for tracking number: {tracking_number}, SKU: {sku or 'N/A'}")
        result = exceptions_manager.process_exception(tracking_number, sku)
        
        if result:
            logger.info(f"Successfully processed exception for tracking number: {tracking_number}")
        else:
            logger.warning(f"Failed to process exception for tracking number: {tracking_number}")
        
        return result
    except Exception as e:
        error_msg = f"Error in process_exception_operation: {str(e)}"
        logger.error(error_msg)
        return False

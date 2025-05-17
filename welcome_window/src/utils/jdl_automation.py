"""
JDL Global IWMS automation utilities.
This module handles interactions with the JDL Global IWMS site for creating after-sales orders.
"""
import time
import logging
import threading
import os
import webbrowser
import pyautogui
import pyperclip
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime, timedelta
import subprocess
import platform

# Set up logging
logger = logging.getLogger(__name__)

# Create a visual logger class
class JDLVisualLogger:
    """A visual logging window to track JDL automation activities."""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of JDLVisualLogger"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
    
    def __init__(self):
        """Initialize the visual logger window."""
        self.window = None
        self.log_text = None
        self.is_visible = False
        self.log_entries = []
        self.max_entries = 100  # Maximum number of log entries to keep
    
    def show(self):
        """Show or create the visual logger window."""
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            self.is_visible = True
            return
        
        # Create a new window
        self.window = tk.Toplevel()
        self.window.title("JDL Automation Activity Log")
        self.window.geometry("700x400")
        self.window.minsize(500, 300)
        
        # Create a frame for the log
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add a title label
        title_label = tk.Label(
            frame, 
            text="JDL Global IWMS Automation Activity Log", 
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Create the scrolled text widget for logs
        self.log_text = scrolledtext.ScrolledText(
            frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20, 
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)  # Make it read-only
        
        # Add a clear button
        clear_button = tk.Button(
            frame, 
            text="Clear Log", 
            command=self.clear_log,
            bg="#f44336",
            fg="white",
            padx=10
        )
        clear_button.pack(pady=10)
        
        # Set up window close handler
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Restore any existing log entries
        self.refresh_log()
        
        self.is_visible = True
    
    def hide(self):
        """Hide the visual logger window."""
        if self.window and self.window.winfo_exists():
            self.window.withdraw()
            self.is_visible = False
    
    def clear_log(self):
        """Clear the log entries."""
        self.log_entries = []
        if self.log_text and self.window and self.window.winfo_exists():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    def log(self, message, level="INFO"):
        """Add a log entry to the visual logger."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine color based on level
        if level == "ERROR":
            color = "#f44336"  # Red
        elif level == "WARNING":
            color = "#ff9800"  # Orange
        elif level == "SUCCESS":
            color = "#4caf50"  # Green
        else:  # INFO
            color = "#2196f3"  # Blue
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "color": color
        }
        
        # Add to log entries
        self.log_entries.append(log_entry)
        
        # Trim log entries if needed
        if len(self.log_entries) > self.max_entries:
            self.log_entries = self.log_entries[-self.max_entries:]
        
        # Update the visual log if it's visible
        if self.is_visible and self.log_text and self.window and self.window.winfo_exists():
            self.log_text.config(state=tk.NORMAL)
            
            # Add the new entry
            self.log_text.insert(tk.END, f"[{timestamp}] [{level}] ")
            self.log_text.insert(tk.END, f"{message}\n", (f"tag_{len(self.log_entries)}"))
            
            # Configure the tag for this entry
            self.log_text.tag_config(f"tag_{len(self.log_entries)}", foreground=color)
            
            # Scroll to the end
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    def refresh_log(self):
        """Refresh the log display with all stored entries."""
        if not self.log_text or not self.window or not self.window.winfo_exists():
            return
            
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        for i, entry in enumerate(self.log_entries):
            self.log_text.insert(tk.END, f"[{entry['timestamp']}] [{entry['level']}] ")
            self.log_text.insert(tk.END, f"{entry['message']}\n", (f"tag_{i}"))
            self.log_text.tag_config(f"tag_{i}", foreground=entry['color'])
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

# Create a global instance of the visual logger
visual_logger = JDLVisualLogger.get_instance()

# Function to activate browser window
def activate_browser_window():
    """
    Attempt to bring the browser window to the foreground.
    Different approaches based on the operating system.
    Will try multiple Alt+Tab attempts if needed.
    """
    try:
        visual_logger.log("Attempting to activate browser window", "INFO")
        
        if platform.system() == "Windows":
            # For Windows, use PowerShell to activate Chrome window
            browser_activated = False
            try:
                # First try Chrome
                chrome_result = subprocess.run([
                    'powershell', '-Command',
                    '(New-Object -ComObject WScript.Shell).AppActivate("Google Chrome")'                    
                ], capture_output=True, text=True, check=False)
                
                if "True" in chrome_result.stdout:
                    visual_logger.log("Activated Chrome browser window", "SUCCESS")
                    browser_activated = True
                else:
                    # Then try Edge
                    edge_result = subprocess.run([
                        'powershell', '-Command',
                        '(New-Object -ComObject WScript.Shell).AppActivate("Microsoft Edge")'                    
                    ], capture_output=True, text=True, check=False)
                    
                    if "True" in edge_result.stdout:
                        visual_logger.log("Activated Edge browser window", "SUCCESS")
                        browser_activated = True
                    else:
                        # Then try Firefox
                        firefox_result = subprocess.run([
                            'powershell', '-Command',
                            '(New-Object -ComObject WScript.Shell).AppActivate("Mozilla Firefox")'                    
                        ], capture_output=True, text=True, check=False)
                        
                        if "True" in firefox_result.stdout:
                            visual_logger.log("Activated Firefox browser window", "SUCCESS")
                            browser_activated = True
                
                if browser_activated:
                    visual_logger.log("Successfully activated browser window using PowerShell", "SUCCESS")
                else:
                    visual_logger.log("Could not activate browser with direct method, trying Alt+Tab sequence", "WARNING")
                    # Fallback to multiple Alt+Tab attempts
                    _try_multiple_alt_tabs()
            except Exception as e:
                visual_logger.log(f"PowerShell activation failed: {str(e)}", "WARNING")
                # Fallback to multiple Alt+Tab attempts
                _try_multiple_alt_tabs()
        else:
            # For other OS, try multiple Alt+Tab attempts
            _try_multiple_alt_tabs()
            
        # Give the window time to activate
        time.sleep(1)
        return True
    except Exception as e:
        visual_logger.log(f"Failed to activate browser window: {str(e)}", "ERROR")
        return False
        
def _try_multiple_alt_tabs(max_attempts=5):
    """
    Try multiple Alt+Tab attempts to find the browser window.
    
    Args:
        max_attempts: Maximum number of Alt+Tab attempts
    """
    visual_logger.log(f"Trying up to {max_attempts} Alt+Tab attempts to find browser", "INFO")
    
    if platform.system() == "Windows":
        # Use PowerShell for more reliable Alt+Tab on Windows
        for i in range(max_attempts):
            visual_logger.log(f"Alt+Tab attempt {i+1}/{max_attempts}", "INFO")
            subprocess.run([
                'powershell', '-Command',
                '(New-Object -ComObject WScript.Shell).SendKeys("%{TAB}")'                    
            ], check=False)
            time.sleep(0.5)  # Short delay between Alt+Tab attempts
    else:
        # Use pyautogui for other platforms
        for i in range(max_attempts):
            visual_logger.log(f"Alt+Tab attempt {i+1}/{max_attempts}", "INFO")
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)  # Short delay between Alt+Tab attempts

class JDLAutomation:
    """Class for automating interactions with the JDL Global IWMS site using the user's default browser."""
    
    # Class variable to store the singleton instance
    _instance = None
    _lock = threading.Lock()
    
    # Class variables to track browser state
    browser_tab_open = False
    browser_used = None  # Will store the browser name that was used (e.g., 'chrome', 'edge', etc.)
    just_opened_browser = False  # Flag to indicate if we just opened the browser
    
    @classmethod
    def get_instance(cls, config_manager=None):
        """Get the singleton instance of JDLAutomation"""
        with cls._lock:
            if cls._instance is None:
                if config_manager is None:
                    raise ValueError("config_manager must be provided when creating a new instance")
                cls._instance = cls(config_manager)
            return cls._instance
    
    def __init__(self, config_manager):
        """
        Initialize the JDL automation.
        
        Args:
            config_manager: The application's configuration manager
        """
        self.config_manager = config_manager
        
        # Get URLs from settings if available, otherwise use defaults
        self.jdl_url = "https://iwms.us.jdlglobal.com/"
        
        # Use the SCAN URL from settings if available
        if hasattr(self.config_manager.settings, 'scan_url') and self.config_manager.settings.scan_url:
            self.after_sales_url = self.config_manager.settings.scan_url
            logger.info(f"Using SCAN URL from settings: {self.after_sales_url}")
        else:
            # Default URL for creating after-sales orders
            self.after_sales_url = "https://iwms.us.jdlglobal.com/#/createAfterSalesOrder"
            logger.info("Using default SCAN URL")
    
    def open_jdl_site(self):
        """
        Open the JDL Global IWMS site in the default browser.
        If a tab is already open, it won't open a new one.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Make sure visual logger is visible
            visual_logger.show()
            
            # Check if we already have a tab open
            if JDLAutomation.browser_tab_open:
                visual_logger.log("Browser tab is already open - using existing tab", "INFO")
                return True
                
            visual_logger.log(f"Attempting to open JDL site: {self.jdl_url}", "INFO")
            
            # Detect the default browser before opening the URL
            self._detect_default_browser()
            
            result = webbrowser.open(self.jdl_url)
            
            if result:
                visual_logger.log(f"Successfully opened JDL site", "SUCCESS")
                if JDLAutomation.browser_used:
                    visual_logger.log(f"Using browser: {JDLAutomation.browser_used}", "INFO")
                # Mark that we have a tab open now
                JDLAutomation.browser_tab_open = True
                return True
            else:
                error_msg = "Could not open the JDL site"
                logger.error(error_msg)
                visual_logger.log(error_msg, "ERROR")
                return False
                
        except Exception as e:
            error_msg = f"Error opening JDL site: {str(e)}"
            logger.error(error_msg)
            visual_logger.log(error_msg, "ERROR")
            return False
            
    def _detect_default_browser(self):
        """
        Detect the default browser on the system and store it in the class variable.
        """
        try:
            # For Windows, try to detect the default browser
            if platform.system() == "Windows":
                # Use PowerShell to query the default browser from the registry
                ps_command = [
                    'powershell', '-Command',
                    r'''
                    # Try to get the default browser from the registry
                    $browserPath = (Get-ItemProperty "HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice").ProgId
                    
                    # Map registry values to browser names
                    $browserName = switch -Wildcard ($browserPath) {
                        "*Chrome*"  { "chrome" }
                        "*Edge*"    { "msedge" }
                        "*Firefox*" { "firefox" }
                        "*IE*"      { "iexplore" }
                        "*Opera*"   { "opera" }
                        "*Safari*"  { "safari" }
                        default     { "unknown" }
                    }
                    
                    # Return the browser name
                    $browserName
                    '''
                ]
                
                result = subprocess.run(ps_command, capture_output=True, text=True, check=False)
                browser_name = result.stdout.strip().lower()
                
                if browser_name and browser_name != "unknown":
                    JDLAutomation.browser_used = browser_name
                    return
                    
                # If registry method failed, try to check running processes after a short delay
                # (since opening the URL will start the browser process)
                time.sleep(1)
                
                # Check common browser processes
                browsers = ["chrome", "msedge", "firefox", "iexplore", "opera", "safari"]
                for browser in browsers:
                    check_cmd = ['powershell', '-Command', f'Get-Process -Name {browser} -ErrorAction SilentlyContinue']
                    result = subprocess.run(check_cmd, capture_output=True, text=True, check=False)
                    if result.stdout.strip():
                        JDLAutomation.browser_used = browser
                        return
            
            # If we couldn't detect the browser, set it to unknown
            JDLAutomation.browser_used = "unknown"
            
        except Exception as e:
            logger.warning(f"Could not detect default browser: {str(e)}")
            JDLAutomation.browser_used = "unknown"
    
    def open_after_sales_order_page(self):
        """
        Open the After Sales Order creation page in the default browser.
        If a tab is already open, it won't open a new one.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Make sure visual logger is visible
            visual_logger.show()
            
            # Check if we already have a tab open
            if JDLAutomation.browser_tab_open:
                visual_logger.log("Browser tab is already open - using existing tab", "INFO")
                visual_logger.log("Please navigate to the After Sales Order page if needed", "INFO")
                return True
                
            visual_logger.log(f"Attempting to open After Sales Order page: {self.after_sales_url}", "INFO")
            
            # Detect the default browser before opening the URL
            self._detect_default_browser()
            
            # Try different URL formats since the exact format might vary
            # First try the standard format
            result = webbrowser.open(self.after_sales_url)
            
            # If that doesn't work, try alternative formats
            if not result:
                visual_logger.log("Primary URL failed, trying alternative URLs", "WARNING")
                # Try alternative URLs if the main one fails
                alt_urls = [
                    # First try the configured URL without the hash
                    self.after_sales_url.replace("#/", ""),
                    # Then try default URLs
                    "https://iwms.us.jdlglobal.com/#/createAfterSalesOrder",
                    "https://iwms.us.jdlglobal.com/createAfterSalesOrder",
                    "https://iwms.us.jdlglobal.com/#/after-sales-order/create"
                ]
                
                for url in alt_urls:
                    if url != self.after_sales_url:
                        visual_logger.log(f"Trying alternative URL: {url}", "INFO")
                        if webbrowser.open(url):
                            # Update the URL if this one works
                            self.after_sales_url = url
                            success_msg = f"Found working URL: {url}"
                            logger.info(success_msg)
                            visual_logger.log(success_msg, "SUCCESS")
                            # Mark that we have a tab open now
                            JDLAutomation.browser_tab_open = True
                            if JDLAutomation.browser_used:
                                visual_logger.log(f"Using browser: {JDLAutomation.browser_used}", "INFO")
                            # Set a flag to indicate we just opened the browser
                            JDLAutomation.just_opened_browser = True
                            return True
            
            # If we got here with result=True, the original URL worked
            if result:
                visual_logger.log(f"Successfully opened After Sales Order page", "SUCCESS")
                # Mark that we have a tab open now
                JDLAutomation.browser_tab_open = True
                if JDLAutomation.browser_used:
                    visual_logger.log(f"Using browser: {JDLAutomation.browser_used}", "INFO")
                # Set a flag to indicate we just opened the browser
                JDLAutomation.just_opened_browser = True
                return True
                
            # If we've tried all URLs and none worked, return False
            error_msg = "Could not open the After Sales Order page with any known URL format"
            logger.error(error_msg)
            visual_logger.log(error_msg, "ERROR")
            return False
            
        except Exception as e:
            error_msg = f"Error opening After Sales Order page: {str(e)}"
            logger.error(error_msg)
            visual_logger.log(error_msg, "ERROR")
            return False
    
    def process_tracking_number(self, tracking_number):
        """
        Process a single tracking number by opening the After Sales Order page,
        copying the tracking number to clipboard, pasting it, pressing Enter,
        and closing the tab after a delay.
        
        Args:
            tracking_number: The tracking number to process
            
        Returns:
            bool: True if page was opened successfully, False otherwise
        """
        try:
            # Make sure visual logger is visible
            visual_logger.show()
            visual_logger.log(f"Processing tracking number: {tracking_number}", "INFO")
            
            # Copy the tracking number to clipboard first (this always works)
            pyperclip.copy(tracking_number)
            visual_logger.log(f"Copied tracking number to clipboard: {tracking_number}", "SUCCESS")
            
            # Try to open the After Sales Order page directly
            visual_logger.log("Opening After Sales Order page", "INFO")
            page_opened = self.open_after_sales_order_page()
            
            if not page_opened:
                # If that fails, try opening the main site first, then the After Sales page
                visual_logger.log("Direct page open failed, trying main site first", "WARNING")
                main_opened = webbrowser.open(self.jdl_url)
                time.sleep(1)  # Give a moment for the browser to respond
                
                if not main_opened:
                    error_msg = "Could not open the web browser. Please check your internet connection."
                    visual_logger.log(error_msg, "ERROR")
                    return False
                    
                # Try again with the After Sales Order page
                visual_logger.log("Attempting to open After Sales Order page (second try)", "INFO")
                page_opened = self.open_after_sales_order_page()
                if not page_opened:
                    error_msg = "Could not open the After Sales Order page. Please manually navigate to the Create After Sales Order page."
                    visual_logger.log(error_msg, "ERROR")
                    return False
            
            # Give the page time to load
            visual_logger.log("Waiting for page to load completely...", "INFO")
            time.sleep(3)  # Wait for page to fully load
            
            # The browser should already be active since we just opened it
            # No need to activate it again unless we're having focus issues
            if not JDLAutomation.browser_used:
                # If we don't know which browser was used, activate to be safe
                visual_logger.log("Activating browser window as a precaution", "INFO")
                activate_browser_window()
                time.sleep(1)  # Wait for the browser to be fully active
            else:
                visual_logger.log(f"Browser {JDLAutomation.browser_used} should already be active", "INFO")
            
            # Paste the tracking number (Ctrl+V)
            visual_logger.log("Pasting tracking number", "INFO")
            if platform.system() == "Windows":
                # Use pyautogui instead of PowerShell to avoid Num Lock issues
                pyautogui.hotkey('ctrl', 'v')
            else:
                pyautogui.hotkey('ctrl', 'v')
        
            # Wait a moment after pasting
            time.sleep(0.5)
            
            # Press Enter to submit the form
            visual_logger.log("Pressing Enter to submit", "INFO")
            if platform.system() == "Windows":
                # Use pyautogui instead of PowerShell to avoid Num Lock issues
                pyautogui.press('enter')
            else:
                pyautogui.press('enter')
            
            # Wait for the form to process (adjust time as needed)
            visual_logger.log("Waiting for form submission to complete...", "INFO")
            time.sleep(5)  # Wait for form submission and page reload
            
            # Close the tab after processing
            visual_logger.log("Closing the browser tab", "INFO")
            # Use pyautogui for all platforms to avoid Num Lock issues
            pyautogui.hotkey('ctrl', 'w')
            
            # Reset the browser tab flag
            JDLAutomation.browser_tab_open = False
            
            # Notify the UI that the tab has been closed
            try:
                # Find the UI instance to notify
                # We need to find the root Tk window and then the CreateLabelFrame instance
                import tkinter as tk
                
                def find_and_notify_widget(parent):
                    """Recursively search for the CreateLabelFrame widget and notify it"""
                    # Check if this widget has the method we're looking for
                    if hasattr(parent, 'simulate_close_tab_button_click'):
                        visual_logger.log(f"Found UI widget of type {type(parent).__name__}, simulating Close Tab button click", "INFO")
                        parent.simulate_close_tab_button_click()
                        return True
                    
                    # Check if this widget has the close_tab_button attribute directly
                    if hasattr(parent, 'close_tab_button'):
                        visual_logger.log(f"Found widget with close_tab_button, hiding it directly", "INFO")
                        # Use after to ensure it runs on the main thread
                        parent.after(0, lambda: parent.close_tab_button.pack_forget())
                        # Also try to enable and focus the SKU field
                        if hasattr(parent, 'field_widgets') and "SKU:" in parent.field_widgets:
                            parent.after(0, lambda: parent.field_widgets["SKU:"]["widget"].config(state="normal"))
                            parent.after(0, lambda: parent.field_widgets["SKU:"]["widget"].focus_set())
                        # Update status message if possible
                        if hasattr(parent, '_update_status'):
                            parent.after(0, lambda: parent._update_status("Browser tab automatically closed. Continue with SKU entry.", 'green'))
                        return True
                    
                    # Search all children
                    for child in parent.winfo_children():
                        if find_and_notify_widget(child):
                            return True
                    
                    return False
                
                # Start the search from the root window
                if hasattr(tk, '_default_root') and tk._default_root is not None:
                    visual_logger.log("Searching for CreateLabelFrame in widget hierarchy", "INFO")
                    if not find_and_notify_widget(tk._default_root):
                        visual_logger.log("Could not find CreateLabelFrame widget in main hierarchy", "WARNING")
                        
                        # As a fallback, try to directly find and hide any close_tab_button in the UI
                        def find_close_tab_button(parent):
                            """Find any widget named close_tab_button"""
                            for child in parent.winfo_children():
                                if child.winfo_name() == 'close_tab_button':
                                    visual_logger.log(f"Found close_tab_button by name, hiding it", "INFO")
                                    child.pack_forget()
                                    return True
                                if find_close_tab_button(child):
                                    return True
                            return False
                        
                        find_close_tab_button(tk._default_root)
            except Exception as e:
                visual_logger.log(f"Could not notify UI of tab closure: {str(e)}", "WARNING")
                # This is not critical, so we can continue even if it fails
            
            visual_logger.log(f"Successfully processed tracking number: {tracking_number}", "SUCCESS")
            return True
                
        except Exception as e:
            error_msg = f"Error processing tracking number {tracking_number}: {str(e)}"
            logger.error(error_msg)
            visual_logger.log(error_msg, "ERROR")
            return False
    
    def process_tracking_numbers(self, tracking_numbers):
        """
        Process a list of tracking numbers.
        
        Args:
            tracking_numbers: List of tracking numbers to process
            
        Returns:
            tuple: (Number of successful tracking numbers, List of failed tracking numbers)
        """
        if len(tracking_numbers) > 1:
            # Multiple tracking numbers
            visual_logger.log(f"Processing {len(tracking_numbers)} tracking numbers", "INFO")
            
            # Ask user if they want to process them one by one or all at once
            import tkinter.messagebox as messagebox
            result = messagebox.askyesno(
                "Process Multiple Tracking Numbers", 
                f"You have {len(tracking_numbers)} tracking numbers to process.\n\n"
                f"Do you want to process them one by one?\n\n"
                f"Click 'Yes' to process one by one.\n"
                f"Click 'No' to copy all to clipboard and process manually."
            )
            
            if result:  # Process one by one
                visual_logger.log("Processing tracking numbers one by one", "INFO")
                
                success_count = 0
                failed_tracking_numbers = []
                
                for tracking_number in tracking_numbers:
                    visual_logger.log(f"Processing tracking number: {tracking_number}", "INFO")
                    
                    if self.process_tracking_number(tracking_number):
                        success_count += 1
                    else:
                        failed_tracking_numbers.append(tracking_number)
                        
                    # Ask if user wants to continue after each one (except the last one)
                    if tracking_number != tracking_numbers[-1]:
                        continue_result = messagebox.askyesno(
                            "Continue Processing", 
                            f"Processed {success_count} of {len(tracking_numbers)} tracking numbers.\n"
                            f"{len(failed_tracking_numbers)} have failed.\n\n"
                            f"Do you want to continue with the next tracking number?"
                        )
                        
                        if not continue_result:
                            visual_logger.log("User chose to stop processing tracking numbers", "INFO")
                            break
                
                visual_logger.log(f"Finished processing tracking numbers. Success: {success_count}, Failed: {len(failed_tracking_numbers)}", "INFO")
                return success_count, failed_tracking_numbers
            else:  # Copy all to clipboard
                try:
                    if not self.open_after_sales_order_page():
                        visual_logger.log("Failed to open After Sales Order page", "ERROR")
                        return 0, tracking_numbers
                        
                    # Join tracking numbers with newlines for easy copying
                    tracking_list = "\n".join(tracking_numbers)
                    pyperclip.copy(tracking_list)
                    visual_logger.log("Copied all tracking numbers to clipboard", "SUCCESS")
                    
                    import tkinter.messagebox as messagebox
                    messagebox.showinfo(
                        "Process Multiple Tracking Numbers", 
                        f"The following tracking numbers have been copied to your clipboard:\n\n"
                        f"{tracking_list}\n\n"
                        f"Please paste each one into the 'Tracking Number' field on the JDL website and click 'Create'."
                    )
                    
                    visual_logger.log("Ready for user to paste multiple tracking numbers", "SUCCESS")
                    
                    # We can't know for sure which ones succeeded, so return all as potential failures
                    return 0, tracking_numbers
                    
                except Exception as e:
                    error_msg = f"Error processing multiple tracking numbers: {str(e)}"
                    logger.error(error_msg)
                    visual_logger.log(error_msg, "ERROR")
                    return 0, tracking_numbers
        else:
            # Just one tracking number
            visual_logger.log(f"Processing single tracking number: {tracking_numbers[0]}", "INFO")
            if self.process_tracking_number(tracking_numbers[0]):
                # The success message is now logged in the process_tracking_number method
                return 1, []
            else:
                visual_logger.log(f"Failed to process tracking number: {tracking_numbers[0]}", "ERROR")
                return 0, tracking_numbers
            
def close(self):
    """
    Close the browser tab and reset the browser_tab_open flag.
    This allows the next tracking number to open a fresh tab.
    
    Returns:
        bool: True if the tab was successfully closed, False otherwise
    """
    try:
        # Get the browser that was used to open the tab
        browser_name = JDLAutomation.browser_used
        visual_logger.log(f"Detected browser: {browser_name if browser_name else 'unknown'}", "INFO")
        
        # Only attempt to close if we believe a tab is open
        if not JDLAutomation.browser_tab_open:
            visual_logger.log("No browser tab is currently tracked as open", "INFO")
            return True
        
        # Automatically close the browser tab without asking
        visual_logger.log("Attempting to close browser tab...", "INFO")
        
        close_success = False
        try:
            # For Windows, use browser-specific approach when possible
            if platform.system() == "Windows":
                # First, try to focus the specific browser if we know which one was used
                browser_focused = False
                
                if browser_name and browser_name != "unknown":
                    # Try to focus the specific browser process
                    ps_focus_browser = [
                        'powershell', '-Command',
                        r'''
                        $browserName = "''' + browser_name + r'''"
                        $processes = Get-Process -Name $browserName -ErrorAction SilentlyContinue
                        
                        if ($processes) {
                            # Try to focus the browser window
                            Add-Type @"
                                using System;
                                using System.Runtime.InteropServices;
                                public class WindowHelper {
                                    [DllImport("user32.dll")]
                                    [return: MarshalAs(UnmanagedType.Bool)]
                                    public static extern bool SetForegroundWindow(IntPtr hWnd);
                                }
"@
                            
                            # Focus the main window of the first process
                            [WindowHelper]::SetForegroundWindow($processes[0].MainWindowHandle)
                            $true
                        } else {
                            $false
                        }
                        '''
                    ]
                    
                    result = subprocess.run(ps_focus_browser, capture_output=True, text=True, check=False)
                    browser_focused = result.stdout.strip().lower() == 'true'
                    
                    if browser_focused:
                        visual_logger.log(f"Successfully focused {browser_name} browser", "SUCCESS")
                    else:
                        visual_logger.log(f"Could not focus {browser_name} browser, trying alternative method", "WARNING")
                
                # If we couldn't focus the specific browser, try Alt+Tab as a fallback
                if not browser_focused:
                    visual_logger.log("Using Alt+Tab to switch to the browser", "INFO")
                    # Use Alt+Tab to switch to the previous window (likely the browser)
                    subprocess.run([
                        'powershell', '-Command',
                        '(New-Object -ComObject WScript.Shell).SendKeys("%{TAB}")'
                    ], check=False)
                
                # Give a small delay for the window to get focus
                time.sleep(0.5)
                
                # Now try to close the tab with the appropriate shortcut
                # Ctrl+W works in all major browsers
                subprocess.run([
                    'powershell', '-Command',
                    '(New-Object -ComObject WScript.Shell).SendKeys("^w")'
                ], check=False)
                
                visual_logger.log("Sent command to close the browser tab", "SUCCESS")
                close_success = True
                
                # Wait a moment, then Alt+Tab back to our application if we used Alt+Tab before
                if not browser_focused:
                    time.sleep(0.5)
                    subprocess.run([
                        'powershell', '-Command',
                        '(New-Object -ComObject WScript.Shell).SendKeys("%{TAB}")'
                    ], check=False)
            else:
                # For other platforms, just inform the user
                visual_logger.log("Please close the browser tab manually", "INFO")
                close_success = True  # Assume success on non-Windows platforms
                
        except Exception as e:
            visual_logger.log(f"Could not automatically close tab: {str(e)}", "WARNING")
            visual_logger.log("Please close the browser tab manually", "INFO")
            close_success = False
        
        # Reset the browser tab tracking flag regardless of success
        # This ensures the UI will update properly even if the tab close was not perfect
        JDLAutomation.browser_tab_open = False
        visual_logger.log("Browser tab tracking reset - next tracking number will open a new tab", "INFO")
        
        # Notify any UI components that might be waiting for tab closure
        # This is important for ensuring buttons are properly hidden
        try:
            # Import tkinter here to avoid circular imports
            import tkinter as tk
            from tkinter import Event
            
            # Find all CreateLabelFrame instances and directly update them
            def find_create_label_frames(widget):
                frames = []
                if widget.__class__.__name__ == "CreateLabelFrame":
                    frames.append(widget)
                for child in widget.winfo_children():
                    frames.extend(find_create_label_frames(child))
                return frames
            
            if tk._default_root:
                # Find all CreateLabelFrame instances
                create_label_frames = find_create_label_frames(tk._default_root)
                
                for frame in create_label_frames:
                    # Directly hide the Close Tab button
                    if hasattr(frame, 'close_tab_button'):
                        visual_logger.log(f"Directly hiding Close Tab button in {frame.__class__.__name__}", "INFO")
                        frame.after(0, lambda f=frame: f.close_tab_button.pack_forget())
                        frame.after(100, lambda f=frame: f.close_tab_button.pack_forget())
                        frame.after(500, lambda f=frame: f.close_tab_button.pack_forget())
                        
                        # Enable the SKU field
                        if hasattr(frame, 'field_widgets') and "SKU:" in frame.field_widgets:
                            frame.after(0, lambda f=frame: f.field_widgets["SKU:"]["widget"].config(state="normal"))
                            frame.after(100, lambda f=frame: f.field_widgets["SKU:"]["widget"].focus_set())
                
                # Also send the event for backward compatibility
                for widget in tk._default_root.winfo_children():
                    widget.event_generate("<<BrowserTabClosed>>", when="tail")
                
                visual_logger.log("Directly updated UI components and notified about tab closure", "INFO")
        except Exception as notify_error:
            visual_logger.log(f"Could not update UI about tab closure: {str(notify_error)}", "WARNING")
            
        # Also simulate a click on the Close Tab button if it exists
        try:
            # Search for CreateLabelFrame in widget hierarchy
            visual_logger.log("Searching for CreateLabelFrame in widget hierarchy", "INFO")
            import tkinter as tk
            
            def find_create_label_frame(widget):
                if widget.__class__.__name__ == "CreateLabelFrame":
                    return widget
                for child in widget.winfo_children():
                    result = find_create_label_frame(child)
                    if result:
                        return result
                return None
            
            if tk._default_root:
                frame = find_create_label_frame(tk._default_root)
                if frame and hasattr(frame, 'simulate_close_tab_button_click'):
                    visual_logger.log(f"Found UI widget of type {frame.__class__.__name__}, simulating Close Tab button click", "INFO")
                    frame.after(0, frame.simulate_close_tab_button_click)
        except Exception as e:
            visual_logger.log(f"Error simulating Close Tab button click: {str(e)}", "WARNING")
            
        return close_success
            
    except Exception as e:
        error_msg = f"Error in close method: {str(e)}"
        logger.error(error_msg)
        visual_logger.log(error_msg, "ERROR")
        return False

def create_after_sales_orders(config_manager, tracking_numbers, username=None, password=None):
    """
    Create after-sales orders for a list of tracking numbers.
    
    Args:
        config_manager: The application's configuration manager
        tracking_numbers: List of tracking numbers to process
        username: Username for JDL Global IWMS (not used in browser-based approach)
        password: Password for JDL Global IWMS (not used in browser-based approach)
        
    Returns:
        tuple: (success_count, failed_tracking_numbers)
    """
    # Get the visual logger instance and show it
    visual_logger.show()
    visual_logger.log("Starting JDL Global IWMS automation process", "INFO")
    visual_logger.log(f"Received {len(tracking_numbers)} tracking number(s) to process", "INFO")
    
    # Check if we should process in reverse order
    if hasattr(config_manager.settings, 'reverseinbound_creation') and config_manager.settings.reverseinbound_creation:
        visual_logger.log("Reverse inbound creation setting is enabled", "INFO")
        tracking_numbers = list(reversed(tracking_numbers))
        visual_logger.log("Tracking numbers will be processed in reverse order", "INFO")
    else:
        visual_logger.log("Tracking numbers will be processed in standard order", "INFO")
    
    # Get the singleton instance
    automation = JDLAutomation.get_instance(config_manager)
    
    try:
        visual_logger.log("Beginning tracking number processing", "INFO")
        result = automation.process_tracking_numbers(tracking_numbers)
        success_count, failed_numbers = result
        
        # Log the final results
        if success_count == len(tracking_numbers):
            visual_logger.log(f"Successfully processed all {success_count} tracking numbers", "SUCCESS")
        elif success_count > 0:
            visual_logger.log(f"Partially successful: processed {success_count} of {len(tracking_numbers)} tracking numbers", "WARNING")
            visual_logger.log(f"Failed tracking numbers: {', '.join(failed_numbers)}", "WARNING")
        else:
            visual_logger.log(f"Failed to process any tracking numbers", "ERROR")
        
        return result
    except Exception as e:
        error_msg = f"Error in create_after_sales_orders: {str(e)}"
        logger.error(error_msg)
        visual_logger.log(error_msg, "ERROR")
        return 0, tracking_numbers

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
    def get_instance(cls, config_manager=None):
        """Get the singleton instance of JDLVisualLogger"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(config_manager=config_manager)
            elif config_manager and cls._instance.config_manager is None:
                # If instance exists but didn't have config_manager, update it
                cls._instance.config_manager = config_manager
            return cls._instance
    
    def __init__(self, config_manager=None):
        """Initialize the visual logger window."""
        self.window = None
        self.log_text = None
        self.is_visible = False
        self.log_entries = []
        self.max_entries = 100  # Maximum number of log entries to keep
        self.config_manager = config_manager
    
    def show(self):
        """Show or create the visual logger window."""
        # Check setting for logger mode
        logger_mode = "show" # Default to show
        if self.config_manager and hasattr(self.config_manager.settings, 'jdl_visual_logger_mode'):
            logger_mode = self.config_manager.settings.jdl_visual_logger_mode.lower()

        if logger_mode == "disabled":
            self.is_visible = False # Ensure correct state
            if self.window and self.window.winfo_exists():
                self.window.withdraw() # Hide if it already exists
            return

        # If mode is not 'disabled' (e.g., 'show', or any other value, or setting not present), proceed to show
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
    """
    try:
        visual_logger.log("Attempting to activate browser window", "INFO")
        
        if platform.system() == "Windows":
            # For Windows, use PowerShell to activate Chrome window
            try:
                # First try Chrome
                subprocess.run([
                    'powershell', '-Command',
                    '(New-Object -ComObject WScript.Shell).AppActivate("Google Chrome")'                    
                ], check=False)
                
                # Then try Edge
                subprocess.run([
                    'powershell', '-Command',
                    '(New-Object -ComObject WScript.Shell).AppActivate("Microsoft Edge")'                    
                ], check=False)
                
                # Then try Firefox
                subprocess.run([
                    'powershell', '-Command',
                    '(New-Object -ComObject WScript.Shell).AppActivate("Mozilla Firefox")'                    
                ], check=False)
                
                visual_logger.log("Activated browser window using PowerShell", "SUCCESS")
            except Exception as e:
                visual_logger.log(f"PowerShell activation failed: {str(e)}", "WARNING")
                # Fallback to Alt+Tab
                pyautogui.hotkey('alt', 'tab')
                visual_logger.log("Used Alt+Tab to switch windows", "INFO")
        else:
            # For other OS, try Alt+Tab
            pyautogui.hotkey('alt', 'tab')
            visual_logger.log("Used Alt+Tab to switch windows", "INFO")
            
        # Give the window time to activate
        time.sleep(1)
        return True
    except Exception as e:
        visual_logger.log(f"Failed to activate browser window: {str(e)}", "ERROR")
        return False

class JDLAutomation:
    """Class for automating interactions with the JDL Global IWMS site using the user's default browser."""
    
    # Class variable to store the singleton instance
    _instance = None
    _lock = threading.Lock()
    
    # Class variables to track browser state
    browser_tab_open = False
    browser_used = None  # Will store the browser name that was used (e.g., 'chrome', 'edge', etc.)
    
    @classmethod
    def get_instance(cls, config_manager=None):
        """Get the singleton instance of JDLAutomation"""
        with cls._lock:
            if cls._instance is None:
                if config_manager is None:
                    # Optionally raise an error or handle if config_manager is essential
                    # For now, proceeding will mean visual logger might not get config
                    pass 
                cls._instance = cls(config_manager)
            elif config_manager and cls._instance.config_manager is None:
                # This case might be relevant if get_instance could be called with and without config_manager
                cls._instance.config_manager = config_manager
                # Ensure visual logger also gets updated config_manager if needed
                JDLVisualLogger.get_instance(config_manager)
        return cls._instance

    def __init__(self, config_manager):
        """
        Initialize the JDL automation.

        Args:
            config_manager: The application's configuration manager
        """
        self.config_manager = config_manager

        # Use the configurable URLs from settings, or fall back to defaults if not set
        if hasattr(config_manager.settings, 'jdl_main_url') and config_manager.settings.jdl_main_url:
            self.jdl_url = config_manager.settings.jdl_main_url
        else:
            self.jdl_url = "https://iwms.us.jdlglobal.com/"

        # Update the URL to the correct path for creating after-sales orders
        if hasattr(config_manager.settings, 'jdl_after_sales_url') and config_manager.settings.jdl_after_sales_url:
            self.after_sales_url = config_manager.settings.jdl_after_sales_url
        else:
            self.after_sales_url = "https://iwms.us.jdlglobal.com/#/createAfterSalesOrder"

        # Ensure URLs have proper format
        if not self.jdl_url.startswith("http"):
            self.jdl_url = "https://" + self.jdl_url

        if not self.after_sales_url.startswith("http"):
            self.after_sales_url = "https://" + self.after_sales_url

        # Ensure the JDLVisualLogger singleton instance has access to config_manager
        JDLVisualLogger.get_instance(config_manager)

        # Detect default browser on initialization
        self._detect_default_browser()
    
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
                alt_urls = [
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
                            return True
            
            # If we got here with result=True, the original URL worked
            if result:
                visual_logger.log(f"Successfully opened After Sales Order page", "SUCCESS")
                # Mark that we have a tab open now
                JDLAutomation.browser_tab_open = True
                if JDLAutomation.browser_used:
                    visual_logger.log(f"Using browser: {JDLAutomation.browser_used}", "INFO")
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
        Process a single tracking number by opening the After Sales Order page
        and copying the tracking number to clipboard for easy pasting.
        
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
            
            # Let the user know what to do next
            visual_logger.log("Browser page opened - tracking number is copied to clipboard", "SUCCESS")
            visual_logger.log("Please paste the tracking number in the browser and press Enter", "INFO")
            
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
            tuple: (success_count, failed_tracking_numbers)
        """
        # Never show the visual logger automatically when scanning a tracking number
        # Just log the activity in the background
        # The user can open the log manually from the settings dialog if needed
        
        if not tracking_numbers:
            visual_logger.log("No tracking numbers to process", "WARNING")
            return 0, []
            
        visual_logger.log(f"Processing {len(tracking_numbers)} tracking number(s)", "INFO")
        
        # For multiple tracking numbers, just open the page and show instructions
        if len(tracking_numbers) > 1:
            try:
                visual_logger.log(f"Multiple tracking numbers detected: {len(tracking_numbers)}", "INFO")
                
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
                visual_logger.log(f"Successfully processed tracking number: {tracking_numbers[0]}", "SUCCESS")
                
                # Don't automatically close the tab - let the user do it with the Close Tab button
                # The browser_tab_open flag will remain true until the user clicks the Close Tab button
                
                return 1, []
            else:
                visual_logger.log(f"Failed to process tracking number: {tracking_numbers[0]}", "ERROR")
                return 0, tracking_numbers
                
    def close(self):
        """
        Close the browser tab and reset the browser_tab_open flag.
        This allows the next tracking number to open a fresh tab.
        """
        try:
            # Get the browser that was used to open the tab
            browser_name = JDLAutomation.browser_used
            visual_logger.log(f"Detected browser: {browser_name if browser_name else 'unknown'}", "INFO")
            
            # Reset the browser tab tracking flag
            JDLAutomation.browser_tab_open = False
            visual_logger.log("Browser tab tracking reset - next tracking number will open a new tab", "INFO")
            
            # Automatically close the browser tab without asking
            visual_logger.log("Attempting to close browser tab...", "INFO")
            
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
                    
            except Exception as e:
                visual_logger.log(f"Could not automatically close tab: {str(e)}", "WARNING")
                visual_logger.log("Please close the browser tab manually", "INFO")
                
        except Exception as e:
            error_msg = f"Error in close method: {str(e)}"
            logger.error(error_msg)
            visual_logger.log(error_msg, "ERROR")


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
    # Log in the background without showing the visual logger
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

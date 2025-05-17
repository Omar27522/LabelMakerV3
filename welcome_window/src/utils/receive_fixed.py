"""
Receive module for handling incoming shipments.
This module provides functionality for receiving and processing incoming packages.
"""
import os
import sys
import time
import logging
import webbrowser
import subprocess
import threading
import pyautogui
import pyperclip

# Import the macro system
from src.utils.macro_integrator import execute_jdl_scan_macro, execute_macro

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

class ReceiveManager:
    """Class for managing receive operations."""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, config_manager=None):
        """Get the singleton instance of ReceiveManager"""
        with cls._lock:
            if cls._instance is None:
                if config_manager is None:
                    raise ValueError("config_manager must be provided when creating a new instance")
                cls._instance = cls(config_manager)
            return cls._instance
    
    def __init__(self, config_manager):
        """
        Initialize the receive manager.
        
        Args:
            config_manager: The application's configuration manager
        """
        self.config_manager = config_manager
        logger.info("ReceiveManager initialized")
    
    def process_receive(self, tracking_number):
        """
        Process a receive operation for a tracking number.
        
        Args:
            tracking_number: The tracking number to process
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Processing receive for tracking number: {tracking_number}")
            # Placeholder for actual receive processing logic
            return True
        except Exception as e:
            error_msg = f"Error processing receive for tracking number {tracking_number}: {str(e)}"
            logger.error(error_msg)
            return False
            
    def open_jdl_scan_page(self):
        """
        Open the JDL Global IWMS scan page in the default browser
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Opening JDL Global IWMS scan page")
            
            # Get the scan URL from settings or use default
            url = self.config_manager.settings.scan_url
            
            # Use default URL if not configured
            if not url:
                url = "https://iwms.us.jdlglobal.com/#/scan"
                logger.info(f"Using default scan URL: {url}")
            
            # Track that we're opening a browser tab
            # This is important for proper UI state management
            from src.utils.jdl_automation import JDLAutomation
            JDLAutomation.browser_tab_open = True
            JDLAutomation.browser_used = "chrome"  # Default to Chrome
            logger.info("Set browser_tab_open flag to True for UI state tracking")
            
            # Method 1: Standard webbrowser module
            success = webbrowser.open(url, new=2)
            
            # Method 2: If standard method fails, try with os.startfile on Windows
            if not success and os.name == 'nt':
                logger.info("Trying alternative method to open browser")
                os.startfile(url)
                success = True
            
            # Method 3: If both fail, try with subprocess
            if not success:
                logger.info("Trying subprocess method to open browser")
                import subprocess
                browsers = ['chrome', 'firefox', 'safari', 'opera', 'iexplore']
                for browser in browsers:
                    try:
                        subprocess.Popen([browser, url])
                        success = True
                        logger.info(f"Successfully opened URL with {browser}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to open with {browser}: {str(e)}")
            
            if success:
                logger.info("Successfully opened JDL Global IWMS scan page")
                # Give the browser time to open
                time.sleep(2)
                return True
            else:
                logger.error("Failed to open JDL Global IWMS scan page")
                return False
                
        except Exception as e:
            error_msg = f"Error opening JDL Global IWMS scan page: {str(e)}"
            logger.error(error_msg)
            return False
            
    def automate_jdl_scan_process(self, tracking_number, container_card, sku, error_callback=None):
        """
        Automate the JDL scan process with the specified sequence
        
        Args:
            tracking_number: The tracking number to process
            container_card: The container card number
            sku: The SKU number
            error_callback: Optional callback function to call when specific errors are detected
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Store original clipboard content to restore later if needed
            original_clipboard = pyperclip.paste()
            
            # Create a context with all the necessary data for the macro
            context = {
                'tracking_number': tracking_number,
                'container_card': container_card,
                'sku': sku
            }
            
            # Log the start of the process
            logger.info("Starting JDL scan automation process using macro system")
            logger.info(f"Processing: Tracking={tracking_number}, Container={container_card}, SKU={sku}")
            
            # Execute the jdl_scan macro with the context
            success = execute_macro('jdl_scan', context)
            
            # Restore original clipboard content
            pyperclip.copy(original_clipboard)
            
            # Reset browser tab state after macro execution
            try:
                from src.utils.jdl_automation import JDLAutomation
                JDLAutomation.browser_tab_open = False
                
                # Notify UI components that the browser tab is now closed
                import tkinter as tk
                if tk._default_root:
                    for widget in tk._default_root.winfo_children():
                        widget.event_generate("<<BrowserTabClosed>>", when="tail")
                logger.info("Reset browser tab state and notified UI components")
            except Exception as state_error:
                logger.warning(f"Could not reset browser tab state: {str(state_error)}")
            
            if success:
                logger.info("JDL scan macro executed successfully")
                return True
            else:
                logger.error("JDL scan macro execution failed")
                return False
                
        except Exception as e:
            error_msg = f"Error in JDL scan automation: {str(e)}"
            logger.error(error_msg)
            
            # Even in case of error, reset the browser tab state
            try:
                from src.utils.jdl_automation import JDLAutomation
                JDLAutomation.browser_tab_open = False
                
                # Notify UI components that the browser tab is now closed
                import tkinter as tk
                if tk._default_root:
                    for widget in tk._default_root.winfo_children():
                        widget.event_generate("<<BrowserTabClosed>>", when="tail")
                logger.info("Reset browser tab state after error")
            except Exception as state_error:
                logger.warning(f"Could not reset browser tab state after error: {str(state_error)}")
                
            return False

def process_receive_operation(config_manager, tracking_number):
    """
    Process a receive operation for a tracking number.
    
    Args:
        config_manager: The application's configuration manager
        tracking_number: The tracking number to process
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get the singleton instance
    receive_manager = ReceiveManager.get_instance(config_manager)
    
    try:
        logger.info(f"Starting receive process for tracking number: {tracking_number}")
        result = receive_manager.process_receive(tracking_number)
        
        if result:
            logger.info(f"Successfully processed receive for tracking number: {tracking_number}")
        else:
            logger.warning(f"Failed to process receive for tracking number: {tracking_number}")
        
        return result
    except Exception as e:
        error_msg = f"Error in process_receive_operation: {str(e)}"
        logger.error(error_msg)
        return False

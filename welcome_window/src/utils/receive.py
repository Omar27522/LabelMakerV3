"""
Receive module for handling incoming shipments.
This module provides functionality for receiving and processing incoming packages.
"""
import os
import sys
import logging
import threading
import webbrowser
import time
import pyautogui
import pyperclip

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
            webbrowser.open("https://iwms.us.jdlglobal.com/#/scan", new=2)
            return True
        except Exception as e:
            error_msg = f"Error opening JDL Global IWMS scan page: {str(e)}"
            logger.error(error_msg)
            return False
            
    def automate_jdl_scan_process(self, tracking_number, container_card, sku):
        """
        Automate the JDL scan process with the specified sequence
        
        Args:
            tracking_number: The tracking number to process
            container_card: The container card number
            sku: The SKU number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open the scan page
            logger.info("Starting JDL scan automation process")
            self.open_jdl_scan_page()
            
            # Wait for page to load
            time.sleep(3)
            
            # Paste tracking number and wait
            logger.info(f"Pasting tracking number: {tracking_number}")
            pyautogui.hotkey('ctrl', 'v')  # Paste tracking number (should be in clipboard)
            time.sleep(2)  # Wait for page to process
            
            # Paste container card and wait
            logger.info(f"Pasting container card: {container_card}")
            pyperclip.copy(container_card)  # Copy container card to clipboard
            pyautogui.hotkey('ctrl', 'v')  # Paste container card
            time.sleep(2)  # Wait for page to process
            
            # Paste SKU and wait
            logger.info(f"Pasting SKU: {sku}")
            pyperclip.copy(sku)  # Copy SKU to clipboard
            pyautogui.hotkey('ctrl', 'v')  # Paste SKU
            time.sleep(2)  # Wait for page to process
            
            # Enter number of items (always 1) and wait
            logger.info("Entering quantity: 1")
            pyperclip.copy("1")  # Copy "1" to clipboard
            pyautogui.hotkey('ctrl', 'v')  # Paste "1"
            time.sleep(2)  # Wait for page to process
            
            # Press SHIFT+Tab 3 times
            logger.info("Navigating to previous fields")
            for _ in range(3):
                pyautogui.hotkey('shift', 'tab')
                time.sleep(0.5)
            
            # Press ENTER twice
            logger.info("Confirming entries")
            pyautogui.press('enter')
            time.sleep(0.5)
            pyautogui.press('enter')
            
            # Wait for user to click "Order Complete"
            logger.info("Waiting for user to click 'Order Complete'...")
            # This step requires user interaction, so we'll just log it
            
            # After user clicks, press Tab twice and Enter
            logger.info("Finalizing order")
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.press('enter')
            
            # Wait for browser and close the tab
            time.sleep(3)
            logger.info("Closing browser tab")
            pyautogui.hotkey('ctrl', 'w')  # Close the tab
            
            logger.info("JDL scan automation process completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Error in JDL scan automation: {str(e)}"
            logger.error(error_msg)
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

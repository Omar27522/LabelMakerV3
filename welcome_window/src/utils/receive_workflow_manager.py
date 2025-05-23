"""
Receive Workflow Manager for handling the R toggle state workflow.
This module extends the tab workflow manager to handle receive mode toggle state.
"""
import os
import sys
import time
import logging
import threading
import tkinter as tk

# Import the tab workflow manager
from src.utils.tab_workflow_manager import TabWorkflowManager, tab_workflow_manager

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

class ReceiveWorkflowManager:
    """Class for managing the receive mode toggle workflow."""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of ReceiveWorkflowManager"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
    
    def __init__(self):
        """Initialize the receive workflow manager."""
        self.active_workflows = {}
        self.workflow_count = 0
        logger.info("ReceiveWorkflowManager initialized")
    
    def handle_receive_toggle(self, frame, current_state):
        """
        Handle the receive mode toggle state change
        
        Args:
            frame: The CreateLabelFrame instance
            current_state: The current state of the receive mode toggle (True or False)
            
        Returns:
            bool: True if handled successfully, False otherwise
        """
        try:
            logger.info(f"Handling receive toggle state change to {current_state}")
            
            # Generate a unique workflow ID
            workflow_id = f"receive_workflow_{self.workflow_count}"
            self.workflow_count += 1
            
            # Store workflow information
            self.active_workflows[workflow_id] = {
                "frame": frame,
                "current_state": current_state,
                "start_time": time.time(),
                "status": "starting"
            }
            
            # Update UI based on receive mode
            if current_state:
                frame._update_status("Receive mode activated", 'blue')
            else:
                frame._update_status("Receive mode deactivated", 'black')
            
            # If exceptions mode is being turned on, turn off receive mode
            if current_state and frame.exceptions_mode_var.get():
                # Update exceptions button state
                frame.exceptions_mode_var.set(False)
                frame.exceptions_btn.config(
                    bg='#D3D3D3',  # Light Gray if off
                    relief='raised'
                )
                
                # Save the setting
                frame.config_manager.settings.exceptions_mode = False
                frame.config_manager.save_settings()
                
                frame._update_status("Exceptions mode deactivated", 'black')
            
            # If a browser tab is open, check if we need to close it
            try:
                from src.utils.jdl_automation import JDLAutomation
                browser_tab_open = getattr(JDLAutomation, 'browser_tab_open', False)
                
                if browser_tab_open:
                    # Close the browser tab if it's open
                    logger.info("Browser tab is open, closing it first")
                    self._close_browser_tab(frame)
                    # Wait a moment for the tab to close before proceeding
                    time.sleep(0.5)
                    # Update workflow status
                    self.active_workflows[workflow_id]["status"] = "tab_closed"
            except (ImportError, AttributeError) as e:
                logger.warning(f"Error checking browser tab state: {str(e)}")
            
            # Reset field states based on new mode
            self._reset_field_states(frame, current_state)
            
            # Return focus to tracking field
            self._focus_tracking_field(frame)
            
            # Schedule a delayed update to ensure the UI is properly refreshed
            frame.after(100, lambda: self._delayed_update(frame, current_state, workflow_id))
            
            return True
        except Exception as e:
            error_msg = f"Error handling receive toggle: {str(e)}"
            logger.error(error_msg)
            return False
    
    def _reset_field_states(self, frame, receive_mode_enabled):
        """
        Reset field states based on receive mode
        
        Args:
            frame: The CreateLabelFrame instance
            receive_mode_enabled: Whether receive mode is enabled
        """
        try:
            # Check if exceptions mode is enabled
            exceptions_mode_enabled = frame.exceptions_mode_var.get()
            
            # Check for JDL automation browser tab state
            try:
                from src.utils.jdl_automation import JDLAutomation
                browser_tab_open = getattr(JDLAutomation, 'browser_tab_open', False)
            except (ImportError, AttributeError):
                browser_tab_open = False
            
            # If a browser tab is open, keep the SKU field disabled
            if browser_tab_open:
                frame.field_widgets["SKU:"]["widget"].config(state="disabled")
                # Show the Close Tab button if it exists
                if hasattr(frame, 'close_tab_button'):
                    frame.close_tab_button.pack(side=tk.RIGHT, padx=(5, 0))
                # Don't return here, continue to ensure SKU field stays disabled
            
            # By default, disable the SKU field until tracking number is entered
            frame.field_widgets["SKU:"]["widget"].config(state="disabled")
            
            # Only enable the SKU field if a valid tracking number is entered
            # This prevents enabling the SKU field without a tracking number
            if frame.tracking_var.get().strip() and len(frame.tracking_var.get().strip()) > 12:
                frame.field_widgets["SKU:"]["widget"].config(state="normal")
            else:
                frame.field_widgets["SKU:"]["widget"].config(state="disabled")
            
            # Hide the Close Tab button if it exists
            if hasattr(frame, 'close_tab_button'):
                frame.close_tab_button.pack_forget()
                
        except Exception as e:
            error_msg = f"Error resetting field states: {str(e)}"
            logger.error(error_msg)
    
    def _focus_tracking_field(self, frame):
        """
        Set focus to the tracking number field
        
        Args:
            frame: The CreateLabelFrame instance
        """
        try:
            # Always focus the tracking field regardless of content
            tracking_field = frame.field_widgets["Tracking Number:"]["widget"]
            tracking_field.focus_set()
            
            # If the field is not empty, select all text to make it easy to replace
            if frame.tracking_var.get().strip():
                tracking_field.select_range(0, 'end')
                tracking_field.icursor('end')
        except Exception as e:
            logger.error(f"Error focusing tracking field: {str(e)}")
    
    def _close_browser_tab(self, frame):
        """
        Close browser tab
        
        Args:
            frame: The CreateLabelFrame instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Closing browser tab")
            
            # Use JDLAutomation to close the tab
            from src.utils.jdl_automation import JDLAutomation
            
            # Get the JDLAutomation instance
            automation = JDLAutomation.get_instance(frame.config_manager)
            
            # Close the tab
            success = automation.close()
            
            # Reset browser tab state
            JDLAutomation.browser_tab_open = False
            
            # Hide the Close Tab button
            if hasattr(frame, 'close_tab_button'):
                frame.after(0, lambda: frame.close_tab_button.pack_forget())
            
            # Enable the SKU field
            frame.after(0, lambda: frame.field_widgets["SKU:"]["widget"].config(state="normal"))
            frame.after(0, lambda: frame.field_widgets["SKU:"]["widget"].focus_set())
            
            # Update UI status
            frame.after(0, lambda: frame._update_status("Ready for SKU input", 'blue'))
            
            # Notify UI components that the browser tab is now closed
            frame.after(0, lambda: frame.event_generate("<<BrowserTabClosed>>", when="tail"))
            
            return success
        except Exception as e:
            error_msg = f"Error closing browser tab: {str(e)}"
            logger.error(error_msg)
            return False

# Create a global instance of the receive workflow manager
receive_workflow_manager = ReceiveWorkflowManager.get_instance()

def handle_receive_toggle(frame, current_state):
    """
    Handle the receive mode toggle state change
    
    Args:
        frame: The CreateLabelFrame instance
        current_state: The current state of the receive mode toggle (True or False)
        
    Returns:
        bool: True if handled successfully, False otherwise
    """
    try:
        logger.info(f"Handling receive toggle state change to {current_state}")
        return receive_workflow_manager.handle_receive_toggle(frame, current_state)
    except Exception as e:
        error_msg = f"Error handling receive toggle: {str(e)}"
        logger.error(error_msg)
        return False


def _delayed_update(frame, current_state, workflow_id):
    """
    Perform a delayed update to ensure the UI is properly refreshed
    
    Args:
        frame: The CreateLabelFrame instance
        current_state: The current state of the receive mode toggle
        workflow_id: The workflow ID
    """
    try:
        # Update UI based on receive mode
        if current_state:
            frame._update_status("Receive mode activated - ready for input", 'blue')
        else:
            frame._update_status("Receive mode deactivated - ready for input", 'black')
            
        # Make sure the SKU field is properly enabled/disabled
        if frame.tracking_var.get().strip() or (current_state and not frame.exceptions_mode_var.get()):
            frame.field_widgets["SKU:"]["widget"].config(state="normal")
        else:
            frame.field_widgets["SKU:"]["widget"].config(state="disabled")
            
        # Make sure the Close Tab button is hidden
        if hasattr(frame, 'close_tab_button'):
            frame.close_tab_button.pack_forget()
            
        # Return focus to tracking field
        tracking_field = frame.field_widgets["Tracking Number:"]["widget"]
        tracking_field.focus_set()
        
        # Update workflow status
        receive_workflow_manager.active_workflows[workflow_id]["status"] = "completed"
        
        logger.info(f"Delayed update completed for workflow {workflow_id}")
    except Exception as e:
        error_msg = f"Error in delayed update: {str(e)}"
        logger.error(error_msg)

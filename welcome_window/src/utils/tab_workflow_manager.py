"""
Tab Workflow Manager for handling the complete tracking number scanning workflow.
This module manages the sequence of:
1. Scanning tracking number
2. Opening browser tab
3. Running automation macro
4. Closing tab
5. Updating dialog state
"""
import os
import sys
import time
import logging
import threading
import tkinter as tk
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

class TabWorkflowManager:
    """Class for managing the complete tab workflow sequence."""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of TabWorkflowManager"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
    
    def __init__(self):
        """Initialize the tab workflow manager."""
        self.active_workflows = {}
        self.workflow_count = 0
        logger.info("TabWorkflowManager initialized")
    
    def start_workflow(self, frame, tracking_number):
        """
        Start a new tab workflow sequence
        
        Args:
            frame: The CreateLabelFrame instance
            tracking_number: The tracking number to process
            
        Returns:
            str: Workflow ID for tracking this workflow
        """
        try:
            # Generate a unique workflow ID
            workflow_id = f"workflow_{self.workflow_count}"
            self.workflow_count += 1
            
            logger.info(f"Starting new tab workflow {workflow_id} for tracking number: {tracking_number}")
            
            # Store workflow information
            self.active_workflows[workflow_id] = {
                "frame": frame,
                "tracking_number": tracking_number,
                "start_time": time.time(),
                "status": "starting",
                "tab_opened": False,
                "macro_run": False,
                "tab_closed": False
            }
            
            # Create and start a new thread for this workflow
            workflow_thread = threading.Thread(
                target=self._execute_workflow,
                args=(workflow_id,),
                daemon=True
            )
            workflow_thread.start()
            
            return workflow_id
        except Exception as e:
            error_msg = f"Error starting tab workflow: {str(e)}"
            logger.error(error_msg)
            return None
    
    def _execute_workflow(self, workflow_id):
        """
        Execute the complete tab workflow sequence
        
        Args:
            workflow_id: The workflow ID to execute
        """
        try:
            if workflow_id not in self.active_workflows:
                logger.error(f"Workflow {workflow_id} not found")
                return
            
            workflow = self.active_workflows[workflow_id]
            frame = workflow["frame"]
            tracking_number = workflow["tracking_number"]
            
            logger.info(f"Executing workflow {workflow_id} for tracking number: {tracking_number}")
            
            # Step 1: Update workflow status
            workflow["status"] = "opening_tab"
            
            # Step 2: Open browser tab
            tab_opened = self._open_browser_tab(workflow_id)
            if not tab_opened:
                logger.error(f"Failed to open browser tab for workflow {workflow_id}")
                self._cleanup_workflow(workflow_id, success=False)
                return
            
            # Step 3: Run automation macro
            workflow["status"] = "running_macro"
            macro_success = self._run_automation_macro(workflow_id)
            if not macro_success:
                logger.error(f"Failed to run automation macro for workflow {workflow_id}")
                self._cleanup_workflow(workflow_id, success=False)
                return
            
            # Step 4: Close tab
            workflow["status"] = "closing_tab"
            tab_closed = self._close_browser_tab(workflow_id)
            if not tab_closed:
                logger.warning(f"Failed to close browser tab for workflow {workflow_id}")
                # Continue anyway, as this is not a critical failure
            
            # Step 5: Update dialog state
            workflow["status"] = "updating_dialog"
            self._update_dialog_state(workflow_id)
            
            # Step 6: Cleanup
            self._cleanup_workflow(workflow_id, success=True)
            
        except Exception as e:
            error_msg = f"Error executing tab workflow {workflow_id}: {str(e)}"
            logger.error(error_msg)
            self._cleanup_workflow(workflow_id, success=False)
    
    def _open_browser_tab(self, workflow_id):
        """
        Open browser tab for the workflow
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            workflow = self.active_workflows[workflow_id]
            frame = workflow["frame"]
            tracking_number = workflow["tracking_number"]
            
            logger.info(f"Opening browser tab for workflow {workflow_id}")
            
            # Use JDLAutomation to open the tab
            from src.utils.jdl_automation import JDLAutomation
            
            # Get the JDLAutomation instance
            automation = JDLAutomation.get_instance(frame.config_manager)
            
            # Set the browser tab state
            JDLAutomation.browser_tab_open = True
            
            # Show the Close Tab button on the UI
            if hasattr(frame, 'close_tab_button'):
                frame.after(0, lambda: frame.close_tab_button.pack(side=tk.RIGHT, padx=(5, 0)))
            
            # Update UI status
            frame.after(0, lambda: frame._update_status("Opening JDL Global IWMS page...", 'blue'))
            
            # Open the JDL site
            success = automation.open_jdl_site()
            if not success:
                logger.error(f"Failed to open JDL site for workflow {workflow_id}")
                return False
            
            # Update workflow status
            workflow["tab_opened"] = True
            
            # Wait for the page to load
            time.sleep(2)
            
            return True
        except Exception as e:
            error_msg = f"Error opening browser tab for workflow {workflow_id}: {str(e)}"
            logger.error(error_msg)
            return False
    
    def _run_automation_macro(self, workflow_id):
        """
        Run automation macro for the workflow
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            workflow = self.active_workflows[workflow_id]
            frame = workflow["frame"]
            tracking_number = workflow["tracking_number"]
            
            logger.info(f"Running automation macro for workflow {workflow_id}")
            
            # Update UI status
            frame.after(0, lambda: frame._update_status("Processing tracking number...", 'blue'))
            
            # Use JDLAutomation to process the tracking number
            from src.utils.jdl_automation import JDLAutomation
            
            # Get the JDLAutomation instance
            automation = JDLAutomation.get_instance(frame.config_manager)
            
            # Process the tracking number
            success = automation.process_tracking_number(tracking_number)
            
            # Update workflow status
            workflow["macro_run"] = True
            
            return success
        except Exception as e:
            error_msg = f"Error running automation macro for workflow {workflow_id}: {str(e)}"
            logger.error(error_msg)
            return False
    
    def _close_browser_tab(self, workflow_id):
        """
        Close browser tab for the workflow
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            workflow = self.active_workflows[workflow_id]
            frame = workflow["frame"]
            
            logger.info(f"Closing browser tab for workflow {workflow_id}")
            
            # Update UI status
            frame.after(0, lambda: frame._update_status("Closing browser tab...", 'blue'))
            
            # Use JDLAutomation to close the tab
            from src.utils.jdl_automation import JDLAutomation
            
            # Get the JDLAutomation instance
            automation = JDLAutomation.get_instance(frame.config_manager)
            
            # Close the tab
            success = automation.close()
            
            # Update workflow status
            workflow["tab_closed"] = True
            
            return success
        except Exception as e:
            error_msg = f"Error closing browser tab for workflow {workflow_id}: {str(e)}"
            logger.error(error_msg)
            return False
    
    def _update_dialog_state(self, workflow_id):
        """
        Update dialog state for the workflow
        
        Args:
            workflow_id: The workflow ID
        """
        try:
            workflow = self.active_workflows[workflow_id]
            frame = workflow["frame"]
            
            logger.info(f"Updating dialog state for workflow {workflow_id}")
            
            # Update UI status
            frame.after(0, lambda: frame._update_status("Ready for SKU input", 'blue'))
            
            # Hide the Close Tab button
            if hasattr(frame, 'close_tab_button'):
                frame.after(0, lambda: frame.close_tab_button.pack_forget())
            
            # Enable the SKU field
            frame.after(0, lambda: frame.field_widgets["SKU:"]["widget"].config(state="normal"))
            frame.after(0, lambda: frame.field_widgets["SKU:"]["widget"].focus_set())
            
            # Reset browser tab state
            from src.utils.jdl_automation import JDLAutomation
            JDLAutomation.browser_tab_open = False
            
            # Notify UI components that the browser tab is now closed
            frame.after(0, lambda: frame.event_generate("<<BrowserTabClosed>>", when="tail"))
            
        except Exception as e:
            error_msg = f"Error updating dialog state for workflow {workflow_id}: {str(e)}"
            logger.error(error_msg)
    
    def _cleanup_workflow(self, workflow_id, success=True):
        """
        Clean up workflow resources
        
        Args:
            workflow_id: The workflow ID
            success: Whether the workflow completed successfully
        """
        try:
            if workflow_id not in self.active_workflows:
                return
            
            workflow = self.active_workflows[workflow_id]
            frame = workflow["frame"]
            
            logger.info(f"Cleaning up workflow {workflow_id} (success={success})")
            
            # If workflow failed, make sure the UI is in a usable state
            if not success:
                # Update UI status
                frame.after(0, lambda: frame._update_status("Automation failed, please try again", 'red'))
                
                # Reset browser tab state
                from src.utils.jdl_automation import JDLAutomation
                JDLAutomation.browser_tab_open = False
                
                # Hide the Close Tab button
                if hasattr(frame, 'close_tab_button'):
                    frame.after(0, lambda: frame.close_tab_button.pack_forget())
                
                # Enable the SKU field
                frame.after(0, lambda: frame.field_widgets["SKU:"]["widget"].config(state="normal"))
                frame.after(0, lambda: frame.field_widgets["SKU:"]["widget"].focus_set())
            
            # Remove the workflow from active workflows
            del self.active_workflows[workflow_id]
            
        except Exception as e:
            error_msg = f"Error cleaning up workflow {workflow_id}: {str(e)}"
            logger.error(error_msg)
    
    def handle_close_tab_button_click(self, frame):
        """
        Handle Close Tab button click
        
        Args:
            frame: The CreateLabelFrame instance
        """
        try:
            logger.info("Close Tab button clicked")
            
            # Find the workflow for this frame
            workflow_id = None
            for wid, workflow in self.active_workflows.items():
                if workflow["frame"] == frame:
                    workflow_id = wid
                    break
            
            if workflow_id:
                logger.info(f"Found workflow {workflow_id} for Close Tab button click")
                
                # Close the browser tab
                self._close_browser_tab(workflow_id)
                
                # Update dialog state
                self._update_dialog_state(workflow_id)
                
                # Cleanup workflow
                self._cleanup_workflow(workflow_id, success=True)
            else:
                logger.warning("No active workflow found for Close Tab button click")
                
                # Reset browser tab state
                from src.utils.jdl_automation import JDLAutomation
                JDLAutomation.browser_tab_open = False
                
                # Hide the Close Tab button
                if hasattr(frame, 'close_tab_button'):
                    frame.close_tab_button.pack_forget()
                
                # Enable the SKU field
                frame.field_widgets["SKU:"]["widget"].config(state="normal")
                frame.field_widgets["SKU:"]["widget"].focus_set()
                
                # Update UI status
                frame._update_status("Ready for SKU input", 'blue')
            
        except Exception as e:
            error_msg = f"Error handling Close Tab button click: {str(e)}"
            logger.error(error_msg)

# Create a global instance of the tab workflow manager
tab_workflow_manager = TabWorkflowManager.get_instance()

def process_tracking_with_tab_workflow(frame, tracking_number):
    """
    Process a tracking number using the tab workflow manager
    
    Args:
        frame: The CreateLabelFrame instance
        tracking_number: The tracking number to process
        
    Returns:
        bool: True if workflow started successfully, False otherwise
    """
    try:
        logger.info(f"Processing tracking number with tab workflow: {tracking_number}")
        
        # Start a new workflow
        workflow_id = tab_workflow_manager.start_workflow(frame, tracking_number)
        
        if workflow_id:
            logger.info(f"Started workflow {workflow_id} for tracking number: {tracking_number}")
            return True
        else:
            logger.error(f"Failed to start workflow for tracking number: {tracking_number}")
            return False
    except Exception as e:
        error_msg = f"Error processing tracking with tab workflow: {str(e)}"
        logger.error(error_msg)
        return False

def handle_close_tab_button_click(frame):
    """
    Handle Close Tab button click
    
    Args:
        frame: The CreateLabelFrame instance
    """
    try:
        logger.info("Handling Close Tab button click")
        tab_workflow_manager.handle_close_tab_button_click(frame)
        return True
    except Exception as e:
        error_msg = f"Error handling Close Tab button click: {str(e)}"
        logger.error(error_msg)
        return False

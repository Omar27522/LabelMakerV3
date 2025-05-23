"""
UI State Manager for handling state transitions between different toggle modes.
This module provides functionality to manage UI state when toggling between modes
and ensures proper tracking number scanning in different states.
"""
import os
import sys
import logging
import tkinter as tk
import pyperclip
from src.utils.tab_workflow_manager import process_tracking_with_tab_workflow, handle_close_tab_button_click
from src.utils.receive_workflow_manager import handle_receive_toggle

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

class UIStateManager:
    """Class for managing UI state transitions and field behavior."""
    
    @staticmethod
    def handle_toggle_mode(frame, toggle_type, current_state):
        """
        Handle toggling between different modes (receive, exceptions)
        
        Args:
            frame: The CreateLabelFrame instance
            toggle_type: The type of toggle ('receive' or 'exceptions')
            current_state: The current state of the toggle (True or False)
            
        Returns:
            None
        """
        try:
            logger.info(f"Toggling {toggle_type} mode to {current_state}")
            
            # Handle receive mode toggle using the receive workflow manager
            if toggle_type == 'receive':
                success = handle_receive_toggle(frame, current_state)
                if not success:
                    # Fallback to basic handling if receive workflow manager fails
                    logger.warning("Receive workflow manager failed, using fallback method")
                    if current_state:
                        frame._update_status("Receive mode activated", 'blue')
                    else:
                        frame._update_status("Receive mode deactivated", 'black')
                    # Reset field states based on new mode
                    UIStateManager.reset_field_states(frame)
                    # Return focus to tracking field
                    UIStateManager.focus_tracking_field(frame)
            # Handle exceptions mode toggle
            elif toggle_type == 'exceptions':
                if current_state:
                    frame._update_status("Exceptions mode activated", 'blue')
                else:
                    frame._update_status("Exceptions mode deactivated", 'black')
                # Reset field states based on new mode
                UIStateManager.reset_field_states(frame)
                # Return focus to tracking field
                UIStateManager.focus_tracking_field(frame)
            
        except Exception as e:
            error_msg = f"Error handling toggle mode: {str(e)}"
            logger.error(error_msg)
            frame._update_status(error_msg, 'red')
    
    @staticmethod
    def handle_tracking_enter(frame, event):
        """
        Handle tracking number field enter key press
        
        Args:
            frame: The CreateLabelFrame instance
            event: The event object
            
        Returns:
            str: "break" to prevent default Enter behavior
        """
        try:
            # Get the tracking number
            tracking_number = frame.tracking_var.get().strip()
            
            # Check if receive mode is enabled
            receive_mode_enabled = frame.receive_mode_var.get()
            
            # Check if exceptions mode is enabled
            exceptions_mode_enabled = frame.exceptions_mode_var.get()
            
            # Check for JDL automation browser tab state
            try:
                from src.utils.jdl_automation import JDLAutomation
                browser_tab_open = getattr(JDLAutomation, 'browser_tab_open', False)
            except (ImportError, AttributeError):
                browser_tab_open = False
            
            # If a browser tab is already open, show a warning and focus the Close Tab button
            if browser_tab_open:
                frame._update_status("Please close the current browser tab before continuing", 'orange')
                try:
                    frame.close_tab_button.focus_set()
                except:
                    pass
                return "break"
            
            # Validate tracking number - always required
            if not tracking_number:
                frame._update_status("Please enter a tracking number", 'red')
                tk.messagebox.showerror("Missing Tracking Number", "A tracking number is required.\n\nPlease enter a valid tracking number.")
                return "break"  # Prevent default Enter behavior
            
            # Validate tracking number length (skip if blank in receive mode)
            if tracking_number and len(tracking_number) <= 12:
                frame._update_status("Tracking number must be longer than 12 characters", 'red')
                tk.messagebox.showerror("Invalid Tracking Number", "Tracking number must be longer than 12 characters.\n\nPlease enter a valid tracking number.")
                # Clear the invalid tracking number
                frame.tracking_var.set("")
                return "break"  # Prevent default Enter behavior
            
            # Copy to clipboard
            if tracking_number:
                # Save original clipboard content
                try:
                    original_clipboard = pyperclip.paste()
                except:
                    original_clipboard = ""
                    
                try:
                    frame.clipboard_clear()
                    frame.clipboard_append(tracking_number)
                    pyperclip.copy(tracking_number)  # Use pyperclip as a backup method
                except Exception as e:
                    logger.error(f"Error copying to clipboard: {str(e)}")
                
                # Process the tracking number with JDL automation if enabled and exceptions mode is not enabled
                if (hasattr(frame.config_manager.settings, 'jdl_automation_enabled') and 
                    frame.config_manager.settings.jdl_automation_enabled and 
                    not exceptions_mode_enabled):
                    # Use the new tab workflow manager to process the tracking number
                    success = process_tracking_with_tab_workflow(frame, tracking_number)
                    
                    if success:
                        # Keep the SKU field disabled until the workflow completes
                        frame._update_status("Processing tracking number...", 'blue')
                    else:
                        # If workflow failed to start, enable the SKU field
                        frame._update_status("Failed to start automation workflow", 'red')
                        frame.field_widgets["SKU:"]["widget"].config(state="normal")
                        frame.field_widgets["SKU:"]["widget"].focus_set()
                else:
                    # If JDL automation is not enabled, enable the SKU field immediately
                    frame.field_widgets["SKU:"]["widget"].config(state="normal")
                    frame.field_widgets["SKU:"]["widget"].focus_set()
                    
                # Clear any previous error messages if not using JDL
                if not (hasattr(frame.config_manager.settings, 'jdl_automation_enabled') and frame.config_manager.settings.jdl_automation_enabled):
                    frame._update_status("", 'black')
            
            return "break"  # Prevent default Enter behavior
            
        except Exception as e:
            error_msg = f"Error handling tracking enter: {str(e)}"
            logger.error(error_msg)
            frame._update_status(error_msg, 'red')
            return "break"
    
    @staticmethod
    def reset_field_states(frame):
        """
        Reset field states based on current mode
        
        Args:
            frame: The CreateLabelFrame instance
            
        Returns:
            None
        """
        try:
            # Check if receive mode is enabled
            receive_mode_enabled = frame.receive_mode_var.get()
            
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
    
    @staticmethod
    def focus_tracking_field(frame):
        """
        Set focus to the tracking number field
        
        Args:
            frame: The CreateLabelFrame instance
            
        Returns:
            None
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
    
    @staticmethod
    def reset_browser_tab_state(frame):
        """
        Reset the browser tab state
        
        Args:
            frame: The CreateLabelFrame instance
            
        Returns:
            None
        """
        try:
            from src.utils.jdl_automation import JDLAutomation
            JDLAutomation.browser_tab_open = False
            logger.info("Reset browser tab state")
            
            # Hide the Close Tab button if it exists
            if hasattr(frame, 'close_tab_button'):
                frame.close_tab_button.pack_forget()
            
            # Reset field states based on current mode
            UIStateManager.reset_field_states(frame)
            
            # Notify UI components that the browser tab is now closed
            if tk._default_root:
                for widget in tk._default_root.winfo_children():
                    widget.event_generate("<<BrowserTabClosed>>", when="tail")
        except Exception as e:
            logger.error(f"Error resetting browser tab state: {str(e)}")
    
    @staticmethod
    def handle_close_tab_click(frame):
        """
        Handle close tab button click
        
        Args:
            frame: The CreateLabelFrame instance
            
        Returns:
            None
        """
        try:
            # Use the tab workflow manager to handle the close tab button click
            success = handle_close_tab_button_click(frame)
            
            if not success:
                # Fallback to the old method if tab workflow manager fails
                logger.warning("Tab workflow manager failed, using fallback method")
                
                # Reset browser tab state
                UIStateManager.reset_browser_tab_state(frame)
                
                # Enable the SKU field
                frame.field_widgets["SKU:"]["widget"].config(state="normal")
                frame.field_widgets["SKU:"]["widget"].focus_set()
                
                # Update status
                frame._update_status("Tab closed, please enter SKU", 'blue')
            
        except Exception as e:
            error_msg = f"Error handling close tab click: {str(e)}"
            logger.error(error_msg)
            frame._update_status(error_msg, 'red')

# Function to patch the CreateLabelFrame class with our improved handlers
def patch_create_label_frame(frame):
    """
    Patch the CreateLabelFrame instance with our improved handlers
    
    Args:
        frame: The CreateLabelFrame instance to patch
        
    Returns:
        None
    """
    try:
        logger.info("Patching CreateLabelFrame with improved handlers")
        
        # Store original methods for reference
        original_toggle_receive = frame._create_ui.toggle_receive_mode
        original_toggle_exceptions = frame._create_ui.toggle_exceptions_mode
        original_on_tracking_enter = frame._create_ui.on_tracking_enter
        
        # Create wrapper functions that call our improved handlers
        def toggle_receive_mode_wrapper():
            # Call original method first
            original_toggle_receive()
            # Then call our improved handler
            UIStateManager.handle_toggle_mode(frame, 'receive', frame.receive_mode_var.get())
        
        def toggle_exceptions_mode_wrapper():
            # Call original method first
            original_toggle_exceptions()
            # Then call our improved handler
            UIStateManager.handle_toggle_mode(frame, 'exceptions', frame.exceptions_mode_var.get())
        
        def on_tracking_enter_wrapper(event):
            # Call our improved handler directly
            return UIStateManager.handle_tracking_enter(frame, event)
        
        # Replace original methods with our wrappers
        frame._create_ui.toggle_receive_mode = toggle_receive_mode_wrapper
        frame._create_ui.toggle_exceptions_mode = toggle_exceptions_mode_wrapper
        frame._create_ui.on_tracking_enter = on_tracking_enter_wrapper
        
        # Add our reset_field_states method to the frame
        frame._reset_field_states = lambda: UIStateManager.reset_field_states(frame)
        
        # Add our focus_tracking_field method to the frame
        original_focus_tracking = frame._focus_tracking_field
        frame._focus_tracking_field = lambda: UIStateManager.focus_tracking_field(frame)
        
        # Add our reset_browser_tab_state method to the frame
        if hasattr(frame, '_reset_browser_tab_state'):
            original_reset_browser = frame._reset_browser_tab_state
            frame._reset_browser_tab_state = lambda: UIStateManager.reset_browser_tab_state(frame)
        else:
            frame._reset_browser_tab_state = lambda: UIStateManager.reset_browser_tab_state(frame)
        
        # Create a Close Tab button if it doesn't exist
        if not hasattr(frame, 'close_tab_button'):
            # Find the button frame (assuming it's the first frame in the frame)
            button_frame = None
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    button_frame = child
                    break
            
            if button_frame:
                # Create the Close Tab button
                frame.close_tab_button = tk.Button(
                    button_frame,
                    text="Close Tab",
                    bg="#FF5722",  # Orange
                    fg="white",
                    command=lambda: UIStateManager.handle_close_tab_click(frame)
                )
                # Don't pack it yet, it will be packed when needed
            else:
                logger.warning("Could not find button frame to add Close Tab button")
        else:
            # If the frame already has a close_tab_button, update its command
            frame.close_tab_button.config(command=lambda: UIStateManager.handle_close_tab_click(frame))
        
        # Add a method to simulate Close Tab button click
        frame.simulate_close_tab_button_click = lambda: UIStateManager.handle_close_tab_click(frame)
        
        # Initialize field states
        UIStateManager.reset_field_states(frame)
        
        logger.info("Successfully patched CreateLabelFrame with improved handlers")
        return True
    except Exception as e:
        error_msg = f"Error patching CreateLabelFrame: {str(e)}"
        logger.error(error_msg)
        return False

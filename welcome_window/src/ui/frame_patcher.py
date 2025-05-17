"""
Frame Patcher module for applying fixes to the CreateLabelFrame.
This module integrates with the WelcomeWindow to patch the CreateLabelFrame
without modifying the original code.
"""
import os
import sys
import logging
import tkinter as tk

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

def patch_welcome_window(welcome_window):
    """
    Patch the WelcomeWindow to apply UI patches to CreateLabelFrame instances
    
    Args:
        welcome_window: The WelcomeWindow instance to patch
        
    Returns:
        bool: True if the patch was applied successfully, False otherwise
    """
    try:
        logger.info("Patching WelcomeWindow to apply UI patches to CreateLabelFrame instances")
        
        # Store the original user_action method
        original_user_action = welcome_window.user_action
        
        # Create a wrapper function that calls our patched version
        def user_action_wrapper():
            # Call the original method
            original_user_action()
            
            # Apply our patch to the CreateLabelFrame instance
            if welcome_window.open_dialogs['create_label'] is not None:
                from src.utils.ui_patch import patch_frame
                create_label_frame = welcome_window.open_dialogs['create_label']
                success = patch_frame(create_label_frame)
                if success:
                    logger.info("Successfully patched CreateLabelFrame instance")
                else:
                    logger.warning("Failed to patch CreateLabelFrame instance")
        
        # Replace the original method with our wrapper
        welcome_window.user_action = user_action_wrapper
        
        logger.info("Successfully patched WelcomeWindow")
        return True
    except Exception as e:
        error_msg = f"Error patching WelcomeWindow: {str(e)}"
        logger.error(error_msg)
        return False

# Function to apply all UI patches
def apply_all_patches():
    """
    Apply all UI patches to fix tracking number scanning issues
    
    Returns:
        bool: True if all patches were applied successfully, False otherwise
    """
    try:
        logger.info("Applying all UI patches")
        
        # Find the WelcomeWindow instance
        import tkinter as tk
        if not tk._default_root:
            logger.warning("No tkinter root window found, patches will be applied when frames are created")
            return False
        
        # Check if the root window is a WelcomeWindow
        from src.ui.welcome_window import WelcomeWindow
        if isinstance(tk._default_root, WelcomeWindow):
            success = patch_welcome_window(tk._default_root)
            if success:
                logger.info("Successfully applied all UI patches")
                return True
            else:
                logger.warning("Failed to apply UI patches to WelcomeWindow")
                return False
        else:
            logger.warning("Root window is not a WelcomeWindow, cannot apply patches")
            return False
    
    except Exception as e:
        error_msg = f"Error applying all UI patches: {str(e)}"
        logger.error(error_msg)
        return False

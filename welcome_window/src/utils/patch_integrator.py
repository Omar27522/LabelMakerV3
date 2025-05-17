"""
Patch Integrator module for applying UI patches to fix tracking number scanning issues.
This module is imported in the main application to apply patches without modifying original files.
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

def integrate_patches():
    """
    Integrate UI patches to fix tracking number scanning issues
    This function should be called after the main application window is created
    
    Returns:
        bool: True if patches were integrated successfully, False otherwise
    """
    try:
        logger.info("Integrating UI patches")
        
        # Import the frame patcher
        from src.ui.frame_patcher import apply_all_patches
        
        # Apply all patches
        success = apply_all_patches()
        
        if success:
            logger.info("Successfully integrated UI patches")
        else:
            logger.warning("Failed to integrate UI patches")
        
        return success
    except Exception as e:
        error_msg = f"Error integrating UI patches: {str(e)}"
        logger.error(error_msg)
        return False

# Function to be called after the application window is created
def setup_patch_integration(root_window=None):
    """
    Set up patch integration to be applied after the application window is created
    
    Args:
        root_window: Optional root window to patch directly
        
    Returns:
        None
    """
    try:
        logger.info("Setting up patch integration")
        
        if root_window:
            # If a root window is provided, apply patches directly
            from src.ui.frame_patcher import patch_welcome_window
            from src.ui.welcome_window import WelcomeWindow
            
            if isinstance(root_window, WelcomeWindow):
                success = patch_welcome_window(root_window)
                if success:
                    logger.info("Successfully applied patches to provided root window")
                else:
                    logger.warning("Failed to apply patches to provided root window")
            else:
                logger.warning("Provided root window is not a WelcomeWindow, cannot apply patches")
        else:
            # Otherwise, schedule the integration to happen after the main loop starts
            import tkinter as tk
            
            def delayed_integration():
                integrate_patches()
                
            # Schedule the integration to happen after the main loop starts
            if tk._default_root:
                tk._default_root.after(1000, delayed_integration)
                logger.info("Scheduled patch integration to happen after main loop starts")
            else:
                logger.warning("No tkinter root window found, cannot schedule patch integration")
    
    except Exception as e:
        error_msg = f"Error setting up patch integration: {str(e)}"
        logger.error(error_msg)

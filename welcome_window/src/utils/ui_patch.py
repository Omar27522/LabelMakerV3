"""
UI Patch module for applying fixes to the CreateLabelFrame.
This module patches the existing CreateLabelFrame class to fix tracking number scanning issues
in different toggle states without modifying the original code.
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

def apply_ui_patches():
    """
    Apply UI patches to fix tracking number scanning issues in different toggle states.
    This function should be called after the main application window is created.
    
    Returns:
        bool: True if patches were applied successfully, False otherwise
    """
    try:
        logger.info("Applying UI patches")
        
        # Import the UI state manager
        from src.utils.ui_state_manager import patch_create_label_frame
        
        # Find all instances of CreateLabelFrame in the application
        import tkinter as tk
        if not tk._default_root:
            logger.warning("No tkinter root window found, patches will be applied when frames are created")
            return False
        
        # Find all CreateLabelFrame instances
        from src.ui.create_label_frame import CreateLabelFrame
        frames_patched = 0
        
        # Recursive function to find CreateLabelFrame instances in widget hierarchy
        def find_and_patch_frames(widget):
            nonlocal frames_patched
            if isinstance(widget, CreateLabelFrame):
                success = patch_create_label_frame(widget)
                if success:
                    frames_patched += 1
                    logger.info(f"Patched CreateLabelFrame instance: {widget}")
            
            # Check children widgets
            for child in widget.winfo_children():
                find_and_patch_frames(child)
        
        # Start searching from the root window
        find_and_patch_frames(tk._default_root)
        
        if frames_patched > 0:
            logger.info(f"Successfully patched {frames_patched} CreateLabelFrame instances")
            return True
        else:
            logger.warning("No CreateLabelFrame instances found to patch")
            
            # Set up a binding to patch frames when they are created
            def patch_new_frames(event):
                widget = event.widget
                if isinstance(widget, CreateLabelFrame):
                    success = patch_create_label_frame(widget)
                    if success:
                        logger.info(f"Patched newly created CreateLabelFrame: {widget}")
            
            # Bind to the <<FrameCreated>> event that should be generated when frames are created
            tk._default_root.bind_all("<<FrameCreated>>", patch_new_frames)
            logger.info("Set up binding to patch frames when they are created")
            
            return False
    
    except Exception as e:
        error_msg = f"Error applying UI patches: {str(e)}"
        logger.error(error_msg)
        return False

# Function to patch a specific CreateLabelFrame instance
def patch_frame(frame):
    """
    Patch a specific CreateLabelFrame instance
    
    Args:
        frame: The CreateLabelFrame instance to patch
        
    Returns:
        bool: True if the patch was applied successfully, False otherwise
    """
    try:
        from src.utils.ui_state_manager import patch_create_label_frame
        success = patch_create_label_frame(frame)
        if success:
            logger.info(f"Manually patched CreateLabelFrame instance: {frame}")
        return success
    except Exception as e:
        error_msg = f"Error manually patching frame: {str(e)}"
        logger.error(error_msg)
        return False

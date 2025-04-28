"""
Window management utility functions for the Label Maker application.
"""
import os
import sys
import subprocess
import time
import pyautogui
from .file_utils import get_project_root, file_exists

def open_file_explorer(directory):
    """
    Open the file explorer at the specified directory.
    
    Args:
        directory (str): Directory to open
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if sys.platform == 'win32':
            os.startfile(directory)
        elif sys.platform == 'darwin':  # macOS
            subprocess.call(['open', directory])
        else:  # Linux
            subprocess.call(['xdg-open', directory])
        return True
    except Exception as e:
        print(f"Error opening file explorer: {e}")
        return False

def view_files_in_directory(directory):
    """
    Open the file explorer at the specified directory and handle window focus.
    
    This function checks if the --view-files command-line argument was passed,
    which indicates that the application should open the file explorer and
    then bring the main window back to the front.
    
    Args:
        directory (str): Directory to open
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if the directory exists
    if not os.path.exists(directory):
        return False
    
    # Check if the --view-files argument was passed
    if '--view-files' in sys.argv:
        # Open the file explorer
        open_file_explorer(directory)
        
        # Wait for the file explorer to open
        time.sleep(0.5)
        
        # Move the mouse to the top of the screen to avoid hovering over buttons
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width // 2, 10)
        
        return True
    else:
        # Open the file explorer normally
        return open_file_explorer(directory)

def restart_application():
    """
    Restart the application.
    
    Returns:
        None: The application will exit and restart
    """
    python = sys.executable
    script = os.path.join(get_project_root(), 'main.py')
    
    if file_exists(script):
        os.execl(python, python, script)
    else:
        # Fallback to the current script
        os.execl(python, python, *sys.argv)

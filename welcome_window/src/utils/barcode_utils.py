"""
Barcode utility functions for the Label Maker application.
"""
import os
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageOps
from .file_utils import ensure_directory_exists

def get_temp_directory():
    """
    Get the temporary directory for barcode images.
    
    Returns:
        str: Path to the temporary directory
    """
    temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
    ensure_directory_exists(temp_dir)
    return temp_dir

def generate_barcode(tracking_number, barcode_width, barcode_height, mirror_print=False):
    """
    Generate a barcode image for a tracking number.
    
    Args:
        tracking_number (str): The tracking number to encode
        barcode_width (int): Width of the barcode image
        barcode_height (int): Height of the barcode image
        mirror_print (bool): Whether to mirror the barcode image
        
    Returns:
        tuple: (success, barcode_path or error_message)
    """
    try:
        # Create barcode
        code128 = barcode.get_barcode_class('code128')
        barcode_image = code128(tracking_number, writer=ImageWriter())
        
        # Save barcode to temporary file
        temp_dir = get_temp_directory()
        barcode_path = os.path.join(temp_dir, f'barcode_{tracking_number}.png')
        barcode_image.save(barcode_path)
        
        # Load and resize barcode image
        img = Image.open(barcode_path)
        img = img.resize((barcode_width, barcode_height), Image.LANCZOS)
        
        # Mirror image if needed
        if mirror_print:
            img = ImageOps.mirror(img)
            
        # Save the modified image
        img.save(barcode_path)
        
        return True, barcode_path
    except Exception as e:
        return False, f"Error generating barcode: {str(e)}"

def print_barcode(barcode_path):
    """
    Print a barcode image.
    
    Args:
        barcode_path (str): Path to the barcode image
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Check if the file exists
        if not os.path.exists(barcode_path):
            return False, "Barcode image not found"
        
        # Use ShellExecute to open the print dialog
        try:
            import win32api
            win32api.ShellExecute(
                0,          # Handle to parent window
                "print",    # Operation to perform
                barcode_path, # File to print
                None,       # Parameters
                ".",        # Working directory
                0           # Show command
            )
            return True, "Label sent to printer"
        except ImportError:
            # Fallback to os.startfile for printing if win32api is not available
            os.startfile(barcode_path, "print")
            return True, "Label sent to printer"
    except Exception as e:
        return False, f"Error printing label: {str(e)}"

def get_barcode_path(tracking_number):
    """
    Get the path to a barcode image for a tracking number.
    
    Args:
        tracking_number (str): The tracking number
        
    Returns:
        str: Path to the barcode image
    """
    temp_dir = get_temp_directory()
    return os.path.join(temp_dir, f'barcode_{tracking_number}.png')

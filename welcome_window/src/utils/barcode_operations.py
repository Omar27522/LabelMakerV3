"""
Utility functions for barcode operations specific to the Label Maker application.
"""

import os
import datetime
from PIL import Image
import barcode
from barcode.writer import ImageWriter
from src.utils.file_utils import ensure_directory_exists, file_exists, find_files_by_sku, log_shipping_record, directory_exists

def create_barcode_for_tracking(tracking_number, directory, mirror_print=False, status_callback=None):
    """
    This function is disabled - no longer creates new barcodes.
    
    Args:
        tracking_number: The tracking number to encode in the barcode
        directory: The directory to save the barcode image to
        mirror_print: Whether to create a mirrored version of the barcode
        status_callback: Optional callback function to update status messages
        
    Returns:
        tuple: (success, barcode_path, message)
    """
    if status_callback:
        status_callback("Label creation has been disabled by administrator", 'orange')
    return False, None, "Label creation has been disabled by administrator"

def print_barcode(barcode_path, mirror_print=False, status_callback=None):
    """
    Print a barcode image.
    
    Args:
        barcode_path: The path to the barcode image
        mirror_print: Whether to create a mirrored version of the barcode before printing
        status_callback: Optional callback function to update status messages
        
    Returns:
        tuple: (success, message)
    """
    try:
        # First verify the file exists before attempting any operations
        if not file_exists(barcode_path):
            error_msg = f"Label file not found: {barcode_path}"
            if status_callback:
                status_callback(error_msg, 'red')
            return False, error_msg
            
        # If mirror print is enabled, create a mirrored temporary copy
        print_path = barcode_path
        if mirror_print:
            try:
                # Use a cached temp directory path to avoid repeated calls
                temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
                ensure_directory_exists(temp_dir)
                
                # Use a simpler filename to reduce path complexity
                temp_path = os.path.join(temp_dir, f'mirror_{os.path.basename(barcode_path)}')
                
                # Only create mirrored image if it doesn't already exist or source has changed
                if not file_exists(temp_path) or os.path.getmtime(barcode_path) > os.path.getmtime(temp_path):
                    # Optimize image handling to reduce delay
                    img = Image.open(barcode_path)
                    mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                    
                    # Save with optimized settings
                    mirrored_img.save(temp_path, optimize=True)
                    
                # Use the mirrored path if it exists
                if file_exists(temp_path):
                    print_path = temp_path
                    if status_callback:
                        status_callback("Using mirrored label for printing", 'blue')
                else:
                    # Fall back to original if mirrored file wasn't created
                    if status_callback:
                        status_callback("Failed to create mirrored image, using original", 'orange')
                    print_path = barcode_path
            except Exception as e:
                if status_callback:
                    status_callback(f"Error creating mirrored image: {str(e)}", 'red')
                # Continue with original image if mirroring fails
                print_path = barcode_path
        
        # Update status before printing to provide immediate feedback
        if status_callback:
            status_callback("Sending label to printer...", 'blue')
        
        # Use a direct printing approach
        os.startfile(print_path, "print")
        
        # Return success immediately without waiting
        if status_callback:
            status_callback("Label sent to printer. Ready for next label.", 'green')
            
        return True, "Label sent to printer"
        
    except FileNotFoundError as e:
        # Specific handling for file not found errors
        error_msg = f"Label file not found: {barcode_path}"
        if status_callback:
            status_callback(error_msg, 'red')
        print(f"Error printing barcode: {error_msg}")
        return False, error_msg
        
    except Exception as e:
        error_msg = str(e)
        if status_callback:
            status_callback(f"Error printing barcode: {error_msg}", 'red')
        print(f"Error printing barcode: {error_msg}")
        
        # Fallback to opening the file if printing fails
        try:
            # Verify file exists before attempting to open
            if file_exists(barcode_path):
                os.startfile(barcode_path)
                if status_callback:
                    status_callback("Printing failed. Opened image for manual printing.", 'orange')
                return False, "Printing failed. Opened image for manual printing."
            else:
                if status_callback:
                    status_callback(f"Error: Label file not found: {barcode_path}", 'red')
                return False, f"Error: Label file not found: {barcode_path}"
        except Exception as e2:
            if status_callback:
                status_callback(f"Error opening barcode: {str(e2)}", 'red')
            return False, f"Error opening barcode: {str(e2)}"

def find_or_create_barcode(tracking_number, sku, directory, mirror_print=False, status_callback=None):
    """
    Find an existing barcode file for the given SKU (creation functionality disabled).
    
    Args:
        tracking_number: The tracking number to encode in the barcode
        sku: The SKU to search for existing barcodes
        directory: The directory to save the barcode image to
        mirror_print: Whether to create a mirrored version of the barcode
        status_callback: Optional callback function to update status messages
        
    Returns:
        tuple: (success, barcode_path, is_new, message)
    """
    # Check if a file with this SKU already exists
    existing_file = None
    if sku:
        # Search for files containing the SKU in the filename
        matching_files = find_files_by_sku(directory, sku)
        if matching_files:
            existing_file = matching_files[0]  # Use the first matching file
            if status_callback:
                status_callback(f"Found existing label file for SKU: {sku}", 'blue')
            print(f"Using existing label file: {existing_file}")
            return True, existing_file, False, f"Found existing label file for SKU: {sku}"
    
    # No existing file found and creation is disabled
    if status_callback:
        status_callback("Label creation has been disabled", 'orange')
    return False, None, False, "Label creation has been disabled"

def process_barcode(tracking_number, sku, directory, mirror_print=False, status_callback=None, after_print_callback=None):
    """
    Complete process for handling a barcode - find or create, log, and print.
    
    Args:
        tracking_number: The tracking number to encode in the barcode
        sku: The SKU to search for existing barcodes
        directory: The directory to save the barcode image to
        mirror_print: Whether to create a mirrored version of the barcode
        status_callback: Optional callback function to update status messages
        after_print_callback: Optional callback function to execute after successful printing
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Check if the directory exists - do this once at the beginning
        if not directory_exists(directory):
            if status_callback:
                status_callback(f"Error: Directory not found: {directory}", 'red')
            return False, f"Error: Directory not found: {directory}"
        
        # Find existing barcode (creation disabled)
        success, barcode_path, is_new, message = find_or_create_barcode(
            tracking_number, sku, directory, mirror_print, status_callback
        )
        
        if not success:
            return False, message
        
        # Print the barcode - we'll log shipping record only on successful print
        print_success, print_message = print_barcode(barcode_path, mirror_print, status_callback)
        
        # Execute the callback if printing was successful and a callback was provided
        if print_success and after_print_callback:
            # Execute callback which will handle logging and Google Sheets
            after_print_callback()
        
        return print_success, print_message
        
    except Exception as e:
        error_msg = str(e)
        if status_callback:
            status_callback(f"Error processing barcode: {error_msg}", 'red')
        return False, f"Error processing barcode: {error_msg}"

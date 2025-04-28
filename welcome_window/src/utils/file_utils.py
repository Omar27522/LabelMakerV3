"""
File utility functions for the Label Maker application.
"""
import os
import sys
import datetime

def get_project_root():
    """
    Get the absolute path to the project root directory.
    
    Returns:
        str: Absolute path to the project root directory
    """
    # Assuming this file is in src/utils
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def file_exists(file_path):
    """
    Check if a file exists.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if the file exists, False otherwise
    """
    return file_path and os.path.exists(file_path) and os.path.isfile(file_path)

def directory_exists(directory_path):
    """
    Check if a directory exists without creating it.
    
    Args:
        directory_path (str): Path to the directory to check
        
    Returns:
        bool: True if the directory exists, False otherwise
    """
    return directory_path and os.path.exists(directory_path) and os.path.isdir(directory_path)

def ensure_directory_exists(directory_path):
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path (str): Path to the directory to create
        
    Returns:
        bool: True if the directory exists or was created successfully, False otherwise
    """
    if not directory_exists(directory_path):
        try:
            os.makedirs(directory_path)
            return True
        except Exception as e:
            print(f"Error creating directory {directory_path}: {e}")
            return False
    return True

def count_files_in_directory(directory_path):
    """
    Count the number of files in a directory.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        int: Number of files in the directory, or 0 if the directory doesn't exist
    """
    if directory_path and os.path.exists(directory_path):
        return len([f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))])
    return 0

def find_files_with_extension(directory_path, extension):
    """
    Find all files with a specific extension in a directory.
    
    Args:
        directory_path (str): Path to the directory
        extension (str): File extension to search for (e.g., '.png')
        
    Returns:
        list: List of file paths matching the extension
    """
    if not directory_path or not os.path.exists(directory_path):
        return []
    
    return [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
            if os.path.isfile(os.path.join(directory_path, f)) and f.endswith(extension)]

def find_file_by_content(directory_path, content_str):
    """
    Find files containing a specific string in their filename.
    
    Args:
        directory_path (str): Path to the directory
        content_str (str): String to search for in filenames
        
    Returns:
        list: List of file paths containing the string
    """
    if not directory_path or not os.path.exists(directory_path):
        return []
    
    return [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
            if os.path.isfile(os.path.join(directory_path, f)) and content_str in f]

def normalize_filename_for_match(s):
    """Normalize a string for robust SKU/filename matching (remove dashes, underscores, spaces, lowercase)."""
    return s.replace('-', '').replace('_', '').replace(' ', '').lower()

def find_files_by_sku(directory_path, sku, extensions=('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
    """
    Find files containing a specific SKU in their filename, supporting multiple extensions and flexible matching.
    Args:
        directory_path (str): Path to the directory
        sku (str): SKU to search for in filenames
        extensions (tuple): File extensions to filter by (default: common image types)
    Returns:
        list: List of file paths containing the SKU (normalized) and matching the extension
    """
    if not directory_path or not directory_exists(directory_path) or not sku:
        return []
    norm_sku = normalize_filename_for_match(sku)
    files = []
    for f in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, f)):
            name, ext = os.path.splitext(f)
            if ext.lower() in extensions and norm_sku in normalize_filename_for_match(name):
                files.append(os.path.join(directory_path, f))
    return files


def get_central_log_file_path():
    """
    Get the path to the central log file.
    
    Returns:
        tuple: (log_directory, log_file_path)
    """
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Define the log directory
    log_directory = os.path.join(project_root, 'logs')
    
    # Ensure the log directory exists
    ensure_directory_exists(log_directory)
    
    # Define the log file path
    log_file_path = os.path.join(log_directory, 'shipping_records.txt')
    
    return log_directory, log_file_path

def get_credentials_file_path():
    """
    Get the path to the Google Sheets credentials file.
    
    Returns:
        str: Path to the credentials file
    """
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Define the credentials file path
    credentials_file_path = os.path.join(project_root, 'credentials.json')
    
    return credentials_file_path

def log_shipping_record(tracking_number, sku, label_filename):
    """
    Log a shipping record to the central log file.
    
    Args:
        tracking_number (str): Tracking number
        sku (str): SKU
        label_filename (str): Label filename
        
    Returns:
        bool: True if logging was successful, False otherwise
    """
    log_dir, log_file = get_central_log_file_path()
    
    # Create logs directory if it doesn't exist
    if not ensure_directory_exists(log_dir):
        return False
    
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} | Tracking: {tracking_number} | SKU: {sku} | Label: {label_filename}\n")
        return True
    except Exception as e:
        print(f"Error logging shipping record: {e}")
        return False

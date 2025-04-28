"""
Configuration utility functions for the Label Maker application.
"""
import os
import json
from .file_utils import ensure_directory_exists, file_exists, get_project_root

def get_config_directory():
    """
    Get the configuration directory for the application.
    
    Returns:
        str: Path to the configuration directory
    """
    project_root = get_project_root()
    config_dir = os.path.join(project_root, 'config')
    ensure_directory_exists(config_dir)
    return config_dir

def get_config_file_path(filename='label_maker_settings.json'):
    """
    Get the path to a configuration file.
    
    Args:
        filename (str): Name of the configuration file
        
    Returns:
        str: Path to the configuration file
    """
    config_dir = get_config_directory()
    return os.path.join(config_dir, filename)

def load_config(filename='label_maker_settings.json', default_config=None):
    """
    Load configuration from a file.
    
    Args:
        filename (str): Name of the configuration file
        default_config (dict): Default configuration to use if the file doesn't exist
        
    Returns:
        dict: Configuration dictionary
    """
    config_file = get_config_file_path(filename)
    
    if default_config is None:
        default_config = {}
    
    if file_exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return default_config
    else:
        return default_config

def save_config(config, filename='label_maker_settings.json'):
    """
    Save configuration to a file.
    
    Args:
        config (dict): Configuration dictionary
        filename (str): Name of the configuration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    config_file = get_config_file_path(filename)
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def update_config(key, value, filename='label_maker_settings.json'):
    """
    Update a specific configuration value.
    
    Args:
        key (str): Configuration key
        value: Configuration value
        filename (str): Name of the configuration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    config = load_config(filename)
    config[key] = value
    return save_config(config, filename)

"""
Centralized application logging configuration.
This module provides a unified approach to all application logging.
"""
import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

# Global logger instance
_app_logger = None

def configure_app_logging(app_name="LabelMaker", log_dir=None):
    """
    Configure application-wide logging.
    
    Args:
        app_name: Name of the application for the logger
        log_dir: Directory to store log files (defaults to project_root/logs)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    global _app_logger
    
    if _app_logger is not None:
        return _app_logger
    
    # Get the project root directory
    if log_dir is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        log_dir = os.path.join(project_root, 'logs')
    
    # Create the logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure the logger
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a file handler for the current month
    current_month = datetime.datetime.now().strftime('%Y%m')
    log_file = os.path.join(log_dir, f'{app_name.lower()}_{current_month}.log')
    
    # Create a rotating file handler (10 MB max size, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Store the logger
    _app_logger = logger
    
    return logger

def get_app_logger():
    """
    Get the application logger instance.
    
    Returns:
        logging.Logger: Application logger
    """
    global _app_logger
    
    if _app_logger is None:
        _app_logger = configure_app_logging()
    
    return _app_logger

# Configure the logger when the module is imported
logger = configure_app_logging()

# Convenience functions for logging
def debug(message):
    """Log a debug message"""
    logger.debug(message)

def info(message):
    """Log an info message"""
    logger.info(message)

def warning(message):
    """Log a warning message"""
    logger.warning(message)

def error(message):
    """Log an error message"""
    logger.error(message)

def critical(message):
    """Log a critical message"""
    logger.critical(message)

def exception(message):
    """Log an exception message with traceback"""
    logger.exception(message)

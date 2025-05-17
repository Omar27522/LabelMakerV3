"""
Macro Integrator for integrating the macro manager with existing exception handlers.
This module provides utility functions to integrate the macro manager with the application.
"""
import os
import sys
import logging
from src.utils.macro_manager import execute_macro

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

def execute_sku_mismatch_macro(tracking_number, sku, order_reference):
    """
    Execute the SKU mismatch macro with the provided context
    
    Args:
        tracking_number: The tracking number
        sku: The SKU
        order_reference: The order reference number
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        context = {
            'tracking_number': tracking_number,
            'sku': sku,
            'order_reference': order_reference
        }
        
        logger.info(f"Executing SKU mismatch macro for tracking number: {tracking_number}")
        return execute_macro('sku_mismatch', context)
    except Exception as e:
        error_msg = f"Error executing SKU mismatch macro: {str(e)}"
        logger.error(error_msg)
        return False

def execute_return_to_sender_macro(tracking_number, sku):
    """
    Execute the return to sender macro with the provided context
    
    Args:
        tracking_number: The tracking number
        sku: The SKU
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        context = {
            'tracking_number': tracking_number,
            'sku': sku
        }
        
        logger.info(f"Executing return to sender macro for tracking number: {tracking_number}")
        return execute_macro('return_to_sender', context)
    except Exception as e:
        error_msg = f"Error executing return to sender macro: {str(e)}"
        logger.error(error_msg)
        return False

def execute_receive_mode_macro(tracking_number, sku, container_card):
    """
    Execute the receive mode macro with the provided context
    
    Args:
        tracking_number: The tracking number
        sku: The SKU
        container_card: The container card number
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        context = {
            'tracking_number': tracking_number,
            'sku': sku,
            'container_card': container_card
        }
        
        logger.info(f"Executing receive mode macro for tracking number: {tracking_number}")
        return execute_macro('receive_mode', context)
    except Exception as e:
        error_msg = f"Error executing receive mode macro: {str(e)}"
        logger.error(error_msg)
        return False

def execute_jdl_scan_macro(tracking_number):
    """
    Execute the JDL scan macro with the provided context
    
    Args:
        tracking_number: The tracking number
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        context = {
            'tracking_number': tracking_number
        }
        
        logger.info(f"Executing JDL scan macro for tracking number: {tracking_number}")
        return execute_macro('jdl_scan', context)
    except Exception as e:
        error_msg = f"Error executing JDL scan macro: {str(e)}"
        logger.error(error_msg)
        return False

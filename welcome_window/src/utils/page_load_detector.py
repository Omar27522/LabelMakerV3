"""
Page load detection module.
This module provides functionality for detecting when a web page is fully loaded.
"""
import os
import time
import logging
import numpy as np
from PIL import ImageGrab
import pytesseract

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

def detect_page_load(max_wait_time=15, check_interval=0.5, expected_elements=None, screenshot_prefix=None):
    """
    Detect when a web page is fully loaded by monitoring screen changes.
    
    Args:
        max_wait_time: Maximum time to wait for page load in seconds
        check_interval: Time between checks in seconds
        expected_elements: List of text elements expected to be on the page when loaded
        screenshot_prefix: Optional prefix for saving debug screenshots
        
    Returns:
        bool: True if page is detected as loaded, False if timeout occurred
    """
    try:
        logger.info(f"Starting page load detection (max wait: {max_wait_time}s)")
        
        # Take initial screenshot
        initial_screen = np.array(ImageGrab.grab())
        
        # Save initial screenshot if prefix provided
        if screenshot_prefix:
            screenshot_path = os.path.join(logs_dir, f"{screenshot_prefix}_initial_{time.strftime('%Y%m%d_%H%M%S')}.png")
            ImageGrab.grab().save(screenshot_path)
            logger.info(f"Saved initial screenshot to {screenshot_path}")
        
        start_time = time.time()
        last_difference = 0
        stable_count = 0
        page_loaded = False
        
        # Monitor for page stability (indicating load complete)
        while (time.time() - start_time) < max_wait_time:
            # Wait before checking
            time.sleep(check_interval)
            
            # Take a new screenshot
            current_screen = np.array(ImageGrab.grab())
            
            # Compare with previous screenshot
            difference = np.sum(np.abs(current_screen - initial_screen))
            difference_percent = difference / (initial_screen.size * 255) * 100
            
            logger.info(f"Screen difference: {difference_percent:.2f}% (raw: {difference})")
            
            # Check if the difference is stable (indicating page has stopped changing)
            if abs(difference - last_difference) < (initial_screen.size * 0.01):  # Less than 1% change
                stable_count += 1
                logger.info(f"Stable frame detected ({stable_count}/3)")
                
                # If we have 3 consecutive stable frames, consider the page loaded
                if stable_count >= 3:
                    page_loaded = True
                    break
            else:
                stable_count = 0
                
            # Update reference for next comparison
            last_difference = difference
            initial_screen = current_screen
            
        # If we have expected elements, verify they're present using OCR
        if page_loaded and expected_elements:
            logger.info(f"Page appears stable, checking for expected elements: {expected_elements}")
            
            # Take a final screenshot for OCR
            final_screen = ImageGrab.grab()
            
            # Save final screenshot if prefix provided
            if screenshot_prefix:
                screenshot_path = os.path.join(logs_dir, f"{screenshot_prefix}_final_{time.strftime('%Y%m%d_%H%M%S')}.png")
                final_screen.save(screenshot_path)
                logger.info(f"Saved final screenshot to {screenshot_path}")
            
            # Convert image to text using OCR
            try:
                screen_text = pytesseract.image_to_string(final_screen)
                logger.info(f"OCR detected text: {screen_text[:200]}...")  # Log first 200 chars
                
                # Check if all expected elements are present
                elements_found = all(element.lower() in screen_text.lower() for element in expected_elements)
                
                if elements_found:
                    logger.info("All expected elements found on page")
                    page_loaded = True
                else:
                    logger.warning("Not all expected elements found on page")
                    page_loaded = False
            except Exception as e:
                logger.error(f"OCR error: {str(e)}")
                # Continue with page_loaded status from stability check
        
        elapsed_time = time.time() - start_time
        if page_loaded:
            logger.info(f"Page detected as loaded after {elapsed_time:.2f} seconds")
        else:
            logger.warning(f"Page load detection timed out after {elapsed_time:.2f} seconds")
            
            # Save timeout screenshot if prefix provided
            if screenshot_prefix:
                screenshot_path = os.path.join(logs_dir, f"{screenshot_prefix}_timeout_{time.strftime('%Y%m%d_%H%M%S')}.png")
                ImageGrab.grab().save(screenshot_path)
                logger.info(f"Saved timeout screenshot to {screenshot_path}")
        
        return page_loaded
        
    except Exception as e:
        logger.error(f"Error in page load detection: {str(e)}")
        return False

def detect_form_ready(form_elements=None, max_wait_time=10, screenshot_prefix=None):
    """
    Detect when a form is ready for input by checking for specific form elements.
    
    Args:
        form_elements: List of form element text to look for (labels, buttons, etc.)
        max_wait_time: Maximum time to wait in seconds
        screenshot_prefix: Optional prefix for saving debug screenshots
        
    Returns:
        bool: True if form is detected as ready, False otherwise
    """
    try:
        logger.info(f"Detecting if form is ready for input (max wait: {max_wait_time}s)")
        
        # Default form elements to look for if none provided
        if not form_elements:
            form_elements = ["submit", "enter", "input", "form", "field"]
            
        # Use the page load detection with form-specific elements
        return detect_page_load(
            max_wait_time=max_wait_time,
            check_interval=0.5,
            expected_elements=form_elements,
            screenshot_prefix=screenshot_prefix
        )
        
    except Exception as e:
        logger.error(f"Error in form ready detection: {str(e)}")
        return False

def wait_for_element_change(region=None, timeout=30, check_interval=0.5, screenshot_prefix=None):
    """
    Wait for a specific region of the screen to change (e.g., waiting for a button to appear).
    
    Args:
        region: Tuple of (left, top, right, bottom) coordinates to monitor, or None for full screen
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        screenshot_prefix: Optional prefix for saving debug screenshots
        
    Returns:
        bool: True if change detected, False if timeout occurred
    """
    try:
        logger.info(f"Waiting for element change in region {region if region else 'full screen'}")
        
        # Take initial screenshot of the region
        initial_screen = np.array(ImageGrab.grab(bbox=region))
        
        # Save initial screenshot if prefix provided
        if screenshot_prefix:
            screenshot_path = os.path.join(logs_dir, f"{screenshot_prefix}_initial_{time.strftime('%Y%m%d_%H%M%S')}.png")
            ImageGrab.grab(bbox=region).save(screenshot_path)
            logger.info(f"Saved initial region screenshot to {screenshot_path}")
        
        start_time = time.time()
        change_detected = False
        
        while (time.time() - start_time) < timeout:
            # Wait before checking
            time.sleep(check_interval)
            
            # Take a new screenshot
            current_screen = np.array(ImageGrab.grab(bbox=region))
            
            # Compare with initial screenshot
            if current_screen.shape == initial_screen.shape:
                difference = np.sum(np.abs(current_screen - initial_screen))
                difference_percent = difference / (initial_screen.size * 255) * 100
                
                logger.info(f"Region difference: {difference_percent:.2f}% (raw: {difference})")
                
                # If significant change detected
                if difference_percent > 5.0:  # More than 5% change
                    change_detected = True
                    
                    # Save change screenshot if prefix provided
                    if screenshot_prefix:
                        screenshot_path = os.path.join(logs_dir, f"{screenshot_prefix}_change_{time.strftime('%Y%m%d_%H%M%S')}.png")
                        ImageGrab.grab(bbox=region).save(screenshot_path)
                        logger.info(f"Saved change screenshot to {screenshot_path}")
                    
                    break
            else:
                logger.warning("Screenshot dimensions changed during monitoring")
                
        elapsed_time = time.time() - start_time
        if change_detected:
            logger.info(f"Element change detected after {elapsed_time:.2f} seconds")
        else:
            logger.warning(f"Element change detection timed out after {elapsed_time:.2f} seconds")
            
        return change_detected
        
    except Exception as e:
        logger.error(f"Error in element change detection: {str(e)}")
        return False

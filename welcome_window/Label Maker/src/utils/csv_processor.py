import pandas as pd
import os
from typing import Tuple
import re
from tkinter import messagebox
from ..barcode_generator import LabelData
from ..utils.logger import setup_logger

# Setup logger
logger = setup_logger()

def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename"""
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*\'"'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove any other non-printable characters
    name = ''.join(char for char in name if char.isprintable())
    return name

def process_product_name(full_name: str) -> Tuple[str, str, str]:
    """Process product name into name_line1, name_line2, and variant"""
    import re
    
    # Print the input for debugging
    print(f"Processing product name: '{full_name}'")
    
    # First process camelCase/PascalCase in the full name
    processed_name = full_name
    
    # Handle special case for names that are all uppercase
    if processed_name.isupper() and len(processed_name) > 3:
        # Don't process all uppercase names
        pass
    else:
        # Process camelCase (lowercase followed by uppercase)
        processed_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', processed_name)
        
        # Process PascalCase (capital letters at start of words)
        # This regex looks for capital letters that start a word and are followed by
        # at least one lowercase letter, then another capital
        processed_name = re.sub(r'(^|\s)([A-Z][a-z]+)([A-Z])', r'\1\2 \3', processed_name)
        
        # Handle consecutive capital letters (like "HTML") - don't split these
        # But do split if a capital is followed by lowercase (like "HTMLFile" -> "HTML File")
        processed_name = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', processed_name)
    
    # Print the processed name for debugging
    print(f"Processed to: '{processed_name}'")
    
    # Now continue with normal processing using the processed name
    # First try with spaces around double dash
    if ' -- ' in processed_name:
        name_parts = processed_name.split(' -- ', 1)
    # Then try without spaces
    elif '--' in processed_name:
        name_parts = processed_name.split('--', 1)
    # No fallback to single dash - if no double dash is found, there's no variant
    else:
        name_parts = [processed_name]
        
    base_name = name_parts[0].strip()
    variant = name_parts[1].strip() if len(name_parts) > 1 else ""
    
    # Split base name into lines, respecting max lengths
    words = base_name.split()
    line1 = []
    line2 = []
    current_line1 = ""
    
    # Build first line (max 18 chars)
    for word in words:
        test_line = (current_line1 + " " + word).strip()
        if len(test_line) <= 18:
            line1.append(word)
            current_line1 = test_line
        else:
            break
    
    # Remaining words go to second line (max 20 chars)
    remaining_words = words[len(line1):]
    current_line2 = ""
    for word in remaining_words:
        test_line = (current_line2 + " " + word).strip()
        if len(test_line) <= 20:
            line2.append(word)
            current_line2 = test_line
        else:
            break
    
    name_line1 = " ".join(line1)
    name_line2 = " ".join(line2)
    
    return name_line1, name_line2, variant

def clean_and_validate_barcode(barcode: str) -> str | None:
    """Return cleaned 12-digit barcode string, or None if invalid. Logs corrections and problems."""
    barcode = str(barcode).strip()
    # Remove .0 if present and preceding is 12 digits
    if barcode.endswith('.0') and barcode[:-2].isdigit() and len(barcode[:-2]) == 12:
        logger.warning(f"Barcode '{barcode}' had trailing '.0' (Excel float artifact); auto-corrected to '{barcode[:-2]}'")
        barcode = barcode[:-2]
    # Remove any decimal part if present (robust)
    if '.' in barcode:
        parts = barcode.split('.')
        if parts[0].isdigit() and len(parts[0]) == 12:
            logger.warning(f"Barcode '{barcode}' had decimal part; auto-corrected to '{parts[0]}'")
            barcode = parts[0]
    # Final validation
    if not barcode.isdigit() or len(barcode) != 12:
        logger.warning(f"Malformed or non-string barcode detected: '{barcode}' (should be a 12-digit string)")
        return None
    return barcode

# Backwards compatibility
is_valid_barcode = lambda barcode: clean_and_validate_barcode(barcode) is not None



def create_batch_labels(csv_path: str, main_window):
    """Create labels in batch from a CSV file"""
    try:
        # Read the CSV file with numeric columns as strings to preserve leading zeros and prevent float conversion
        df = pd.read_csv(csv_path, dtype={'Upc': str})
        
        # Get save directory from settings or use default
        save_dir = main_window.config_manager.settings.last_directory
        if not os.path.exists(save_dir):
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "Labels")
            os.makedirs(save_dir, exist_ok=True)
        
        labels_created = 0
        skipped_labels = 0
        
        # Process each row
        for _, row in df.iterrows():
            raw_barcode = str(row['Upc'])
            cleaned_barcode = clean_and_validate_barcode(raw_barcode)
            if not cleaned_barcode:
                skipped_labels += 1
                logger.warning(f"Skipping invalid barcode: {raw_barcode}")
                continue
            # Use only the cleaned barcode from here on
            barcode = cleaned_barcode

            full_name = str(row['Label Name'])

            # Process the product name
            name_line1, name_line2, variant = process_product_name(full_name)

            # Log the product name processing results
            logger.info(f"Full product name: {full_name}")
            logger.info(f"Extracted name_line1: {name_line1}")
            logger.info(f"Extracted name_line2: {name_line2}")
            logger.info(f"Extracted variant: {variant}")
            logger.info(f"Barcode used for label: {barcode}")

            # Create label data
            label_data = LabelData(
                name_line1=name_line1,
                name_line2=name_line2,
                variant=variant,
                upc_code=barcode
            )

            # Generate the label
            label_image = main_window.barcode_generator.generate_label(label_data)
            if label_image:
                # Create filename in same format as manual labels
                safe_name1 = sanitize_filename(name_line1)
                safe_name2 = sanitize_filename(name_line2) if name_line2 else ""
                safe_variant = sanitize_filename(variant)

                # For debugging
                logger.info(f"Original variant: {variant}")
                logger.info(f"Sanitized variant: {safe_variant}")
                logger.info(f"Barcode: {barcode}")

                if safe_name2:
                    filename = f"{safe_name1} {safe_name2} - {safe_variant}_label_{barcode}.png"
                else:
                    filename = f"{safe_name1} - {safe_variant}_label_{barcode}.png"

                logger.info(f"Generated filename: {filename}")

                filepath = os.path.join(save_dir, filename)
                label_image.save(filepath)
                labels_created += 1

                # Update label counter in settings
                main_window.config_manager.settings.label_counter += 1
                main_window.png_count.set(f"Labels: {main_window.config_manager.settings.label_counter}")
            
        # Save settings
        main_window.config_manager.save_settings()
        
        # Show completion message
        message = f"Created {labels_created} labels in:\n{save_dir}"
        if skipped_labels > 0:
            message += f"\n\nSkipped {skipped_labels} invalid barcodes. Check the logs for details."
        messagebox.showinfo("Complete", message)
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        messagebox.showerror("Error", f"Failed to process CSV file:\n\n{str(e)}")

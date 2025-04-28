"""
Utility functions for Google Sheets operations specific to the Label Maker application.
"""

import os
import re
from src.utils.file_utils import file_exists, get_credentials_file_path
from src.utils.sheets_utils import get_authorized_client, validate_sheet_url

def write_to_google_sheet(config_manager, tracking_number, sku, status_callback=None):
    """
    Write tracking number, SKU, and Steps value to Google Sheets.
    
    Args:
        config_manager: The application's configuration manager
        tracking_number: The tracking number to write
        sku: The SKU to write
        status_callback: Optional callback function to update status messages
        
    Returns:
        tuple: (success, message)
    """
    if not (config_manager.settings.google_sheet_url and 
            config_manager.settings.google_sheet_name):
        if status_callback:
            status_callback("Google Sheets not configured", 'red')
        return False, "Google Sheets not configured"
    
    try:
        # Check for credentials file
        creds_file = get_credentials_file_path()
        if not file_exists(creds_file):
            if status_callback:
                status_callback("Google Sheets credentials file not found", 'red')
            return False, "Google Sheets credentials file not found"
        
        # Validate the sheet URL
        is_valid, result = validate_sheet_url(config_manager.settings.google_sheet_url)
        if not is_valid:
            if status_callback:
                status_callback(f"Invalid Google Sheet URL: {result}", 'red')
            return False, f"Invalid Google Sheet URL: {result}"
        
        sheet_id = result
        
        # Get authorized client
        success, client_result = get_authorized_client()
        if not success:
            if status_callback:
                status_callback(f"Failed to authorize Google Sheets client: {client_result}", 'red')
            return False, f"Failed to authorize Google Sheets client: {client_result}"
        
        client = client_result
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        
        # Get the worksheet
        worksheet = spreadsheet.worksheet(config_manager.settings.google_sheet_name)
        
        # Get the configured row and column
        tracking_col = config_manager.settings.google_sheet_tracking_column
        tracking_row = config_manager.settings.google_sheet_tracking_row
        sku_col = config_manager.settings.google_sheet_sku_column
        sku_row = config_manager.settings.google_sheet_sku_row
        steps_col = config_manager.settings.google_sheet_steps_column
        steps_row = config_manager.settings.google_sheet_steps_row
        
        # Get the current date and time from Python
        import datetime
        now = datetime.datetime.now()
        
        # Try to detect the format of the target column by checking existing values
        try:
            # Check if there's any existing data in the column to determine format
            existing_format = "time"  # Default to time-only format
            
            # Try to get a sample value from the column (a few rows above current position)
            if steps_row > 3:  # Only check if we're not at the beginning
                sample_row = max(1, steps_row - 2)  # Look 2 rows above or at row 1
                sample_value = worksheet.acell(f"{steps_col}{sample_row}").value
                
                if sample_value and len(sample_value) > 0:
                    # If sample has date (contains /) and time, use full format
                    if "/" in sample_value and ":" in sample_value:
                        existing_format = "datetime"
                    # If sample only has time (no /), use time-only format
                    elif ":" in sample_value and "/" not in sample_value:
                        existing_format = "time"
        except Exception:
            # If any error occurs during format detection, use the default format
            existing_format = "time"
        
        # Get the date and time from cells Q1 and R1 in the Steps sheet
        try:
            # Try to get date from Q1 and time from R1
            date_from_sheet = None
            time_from_sheet = None
            
            try:
                # Get the Steps❗️ sheet specifically
                steps_sheet = None
                for sheet in worksheet.spreadsheet.worksheets():
                    if sheet.title == "Steps❗️":
                        steps_sheet = sheet
                        break
                
                if steps_sheet:
                    # Get the date from Q1 on the Steps❗️ sheet
                    date_cell = steps_sheet.acell("Q1").value
                    if date_cell and date_cell != "12/30/1899":
                        date_from_sheet = date_cell
                        if status_callback:
                            status_callback(f"Found date in Steps❗️!Q1: {date_from_sheet}", 'green')
                    
                    # Get the time from R1 on the Steps❗️ sheet
                    time_cell = steps_sheet.acell("R1").value
                    if time_cell:
                        time_from_sheet = time_cell
                        if status_callback:
                            status_callback(f"Found time in Steps❗️!R1: {time_from_sheet}", 'green')
                else:
                    if status_callback:
                        status_callback("Could not find Steps❗️ sheet", 'orange')
            except Exception as e:
                if status_callback:
                    status_callback(f"Error accessing Steps❗️ sheet: {str(e)}", 'orange')
            
            # Get the current time
            time_only = now.strftime("%H:%M:%S")
            
            # Check if we have a date from the sheet (not the default date)
            if date_from_sheet and date_from_sheet != "12/30/1899":
                # Use the date from the sheet with the current time
                steps_value = f"{date_from_sheet} {time_only}"
            else:
                # Use current date with current time
                date_only = now.strftime("%m/%d/%Y")
                steps_value = f"{date_only} {time_only}"
            
            # Only display the time in the status message
            if status_callback:
                status_callback(f"Using current time: {time_only}", 'green')
        except Exception as e:
            # If anything goes wrong, use current date and time
            date_only = now.strftime("%m/%d/%Y")
            time_only = now.strftime("%H:%M:%S")
            steps_value = f"{date_only} {time_only}"
            if status_callback:
                status_callback(f"Error reading from sheet, using current time: {time_only}", 'orange')
        
        # Write tracking number
        worksheet.update_acell(f"{tracking_col}{tracking_row}", tracking_number)
        
        # Write SKU
        worksheet.update_acell(f"{sku_col}{sku_row}", sku)
        
        # Write Steps value as a string
        worksheet.update_acell(f"{steps_col}{steps_row}", steps_value)
        
        if status_callback:
            status_callback(f"Time written to cell {steps_col}{steps_row}", 'green')
        
        # Increment row numbers for next entry
        config_manager.settings.google_sheet_tracking_row += 1
        config_manager.settings.google_sheet_sku_row += 1
        config_manager.settings.google_sheet_steps_row += 1
        config_manager.save_settings()
        
        if status_callback:
            status_callback("Data written to Google Sheets", 'green')
        
        return True, "Data written to Google Sheets"
        
    except ImportError:
        if status_callback:
            status_callback("Google Sheets libraries not installed", 'red')
        return False, "Google Sheets libraries not installed"
    except Exception as e:
        error_msg = str(e)
        if status_callback:
            status_callback(f"Error writing to Google Sheets: {error_msg}", 'red')
        return False, f"Error writing to Google Sheets: {error_msg}"

def create_google_sheets_dialog(parent, config_manager, update_callback=None):
    """
    Create a dialog for configuring Google Sheets integration.
    
    Args:
        parent: The parent window
        config_manager: The configuration manager
        update_callback: Optional callback to update the status display after dialog closes
        
    Returns:
        GoogleSheetsDialog: The created dialog
    """
    # Import here to avoid circular imports
    from src.ui.google_sheets_dialog import GoogleSheetsDialog
    
    # Create the dialog
    dialog = GoogleSheetsDialog(parent, config_manager, update_callback)
    
    return dialog

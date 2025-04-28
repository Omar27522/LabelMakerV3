"""
Google Sheets utility functions for the Label Maker application.
"""
import os
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from .file_utils import get_credentials_file_path, file_exists

def validate_sheet_url(url):
    """
    Validate a Google Sheet URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        tuple: (is_valid, sheet_id or error_message)
    """
    if not url:
        return False, "Please enter a Google Sheet URL"
    
    # Check if URL is valid
    sheet_id_pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.match(sheet_id_pattern, url)
    if not match:
        return False, "Invalid Google Sheet URL format.\n\nURL should be in the format:\nhttps://docs.google.com/spreadsheets/d/YOUR_SHEET_ID"
    
    return True, match.group(1)

def get_authorized_client():
    """
    Get an authorized Google Sheets client.
    
    Returns:
        tuple: (success, client or error_message)
    """
    # Check for credentials file
    creds_file = get_credentials_file_path()
    if not file_exists(creds_file):
        return False, f"Credentials file not found at:\n{creds_file}\n\nPlease create a service account and download the credentials file."
    
    try:
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Add credentials to the account
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        
        # Authorize the clientsheet
        client = gspread.authorize(creds)
        return True, client
    except Exception as e:
        return False, f"Failed to authorize Google Sheets client: {str(e)}"

def get_sheet_names(sheet_id):
    """
    Get the available sheet names from a Google Sheet.
    
    Args:
        sheet_id (str): Google Sheet ID
        
    Returns:
        tuple: (success, sheet_names or error_message)
    """
    success, client_or_error = get_authorized_client()
    if not success:
        return False, client_or_error
    
    try:
        # Get the sheet
        spreadsheet = client_or_error.open_by_key(sheet_id)
        
        # Get the available sheet names
        sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]
        return True, sheet_names
    except Exception as e:
        return False, f"Failed to fetch sheet names: {str(e)}"

def test_sheet_connection(sheet_id, sheet_name):
    """
    Test the connection to a Google Sheet.
    
    Args:
        sheet_id (str): Google Sheet ID
        sheet_name (str): Sheet name to test
        
    Returns:
        tuple: (success, message)
    """
    success, client_or_error = get_authorized_client()
    if not success:
        return False, client_or_error
    
    try:
        # Get the sheet
        spreadsheet = client_or_error.open_by_key(sheet_id)
        
        # Get all sheet names
        all_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
        
        # Check if the specified sheet exists
        if sheet_name in all_sheets:
            # Try to open the worksheet
            worksheet = spreadsheet.worksheet(sheet_name)
            return True, "Connected"
        else:
            # Sheet not found
            sheet_list = "\n".join(all_sheets)
            return False, f"Sheet '{sheet_name}' not found.\n\nAvailable sheets:\n{sheet_list}"
    except Exception as e:
        return False, f"Failed to connect to Google Sheet: {str(e)}"

def update_sheet_cell(sheet_id, sheet_name, cell, value):
    """
    Update a cell in a Google Sheet.
    
    Args:
        sheet_id (str): Google Sheet ID
        sheet_name (str): Sheet name
        cell (str): Cell reference (e.g., "A1")
        value (str): Value to set
        
    Returns:
        tuple: (success, message)
    """
    success, client_or_error = get_authorized_client()
    if not success:
        return False, client_or_error
    
    try:
        # Get the sheet
        spreadsheet = client_or_error.open_by_key(sheet_id)
        
        # Get the worksheet
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # Update the cell
        worksheet.update_acell(cell, value)
        return True, "Cell updated"
    except Exception as e:
        return False, f"Failed to update cell: {str(e)}"

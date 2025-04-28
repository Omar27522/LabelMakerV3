# Google Sheets Integration Documentation

## Overview

The Google Sheets integration allows the Label Maker application to connect to Google Sheets for tracking shipping information. This feature enables users to view and update tracking data directly from the application, providing a seamless workflow for managing labels and tracking information.

## Components

The Google Sheets integration consists of several components:

1. **GoogleSheetsDialog**: A dialog for configuring and testing the Google Sheets connection
2. **Sheets Operations**: Utility functions for interacting with Google Sheets
3. **Status Display**: A visual indicator of the connection status in the welcome window
4. **Configuration Management**: Settings for storing and retrieving Google Sheets configuration

## GoogleSheetsDialog

The `GoogleSheetsDialog` class provides a user interface for configuring the Google Sheets connection.

### Features

- URL input field for specifying the Google Sheet URL
- Sheet selection dropdown for choosing the specific sheet
- Cell selection for tracking and SKU information
- Test connection button to verify the configuration
- Save and cancel buttons for managing settings

### Implementation Details

- Validates the Google Sheet URL format
- Fetches available sheets from the specified spreadsheet
- Provides real-time feedback on connection status
- Saves configuration to the application settings file
- Handles authentication with Google Sheets API

## Sheets Operations

The `sheets_operations.py` module provides utility functions for interacting with Google Sheets.

### Key Functions

#### `write_to_google_sheet(tracking_number, sku)`

Writes tracking and SKU information to the configured Google Sheet.

##### Parameters
- `tracking_number`: The tracking number to write
- `sku`: The SKU to write

##### Returns
- `bool`: True if the write operation was successful, False otherwise

#### `create_google_sheets_dialog(parent, config_manager, callback=None)`

Creates a dialog for configuring Google Sheets integration.

##### Parameters
- `parent`: The parent window
- `config_manager`: The configuration manager instance
- `callback` (optional): Callback function to execute after the dialog is closed

##### Returns
- `GoogleSheetsDialog`: The created dialog instance

## Status Display

The welcome window includes a status display for the Google Sheets connection:

- Green "Connected" status when properly configured and connected
- Red "Not Connected" status when not configured or connection fails
- Displays the connected sheet name when connected

The status display is created using the `create_sheets_status_display()` function from the `ui_components` module and is updated whenever the configuration changes.

## Configuration Management

Google Sheets settings are stored in the `label_maker_settings.json` file:

```json
{
  "google_sheet_url": "https://docs.google.com/spreadsheets/d/...",
  "google_sheet_name": "Sheet1",
  "google_sheet_tracking_column": "A",
  "google_sheet_tracking_row": "2",
  "google_sheet_sku_column": "B",
  "google_sheet_sku_row": "2"
}
```

These settings are managed by the `ConfigManager` class and can be accessed and modified through the Google Sheets dialog.

## Authentication

The Google Sheets integration uses OAuth2 authentication with a service account:

1. Credentials are stored in a `credentials.json` file
2. The application uses the `gspread` library to authenticate and interact with Google Sheets
3. A template `credentials_template.json` file is provided for users to configure their own credentials

## Setup Instructions

Detailed setup instructions are provided in the `GOOGLE_SHEETS_SETUP.md` file, which includes:

1. Creating a Google Cloud project
2. Enabling the Google Sheets API
3. Creating a service account
4. Downloading credentials
5. Sharing the Google Sheet with the service account
6. Configuring the application to use the credentials

## Recent Improvements

Recent improvements to the Google Sheets integration include:

1. Fixed issues with the connection status display
2. Added proper status initialization in the GoogleSheetsDialog class
3. Updated the open_sheets_dialog method to reload the config manager after the dialog is closed
4. Added wait_window to ensure the dialog is fully closed before updating the status
5. Improved status label initialization based on the current configuration
6. Added error handling to the _update_status method
7. Added comprehensive try-except blocks to catch and handle exceptions
8. Restored URL validation and sheet selection logic
9. Created a test script (test_sheet_selection.py) to verify functionality

## Integration with Welcome Window

The Google Sheets integration is integrated with the welcome window:

1. The welcome window displays the connection status
2. The settings dialog provides access to the Google Sheets configuration
3. The status is updated whenever the configuration changes

## Error Handling

The Google Sheets integration includes comprehensive error handling:

- Validates the Google Sheet URL format
- Handles authentication errors
- Manages connection timeouts
- Provides user-friendly error messages
- Gracefully handles missing or invalid credentials

## Usage Example

```python
# Create a Google Sheets dialog
def on_sheets_dialog_closed():
    # Update the status display after the dialog is closed
    self._update_sheets_status_display()

sheets_dialog = create_google_sheets_dialog(
    self,
    self.config_manager,
    callback=on_sheets_dialog_closed
)

# Wait for the dialog to be closed
self.wait_window(sheets_dialog)
```

## Troubleshooting

Common issues and solutions:

1. **Connection Failed**: Verify your internet connection and credentials
2. **Authentication Error**: Ensure the credentials.json file is properly configured
3. **Sheet Not Found**: Verify the sheet URL and name
4. **Permission Denied**: Make sure the sheet is shared with the service account
5. **Invalid Cell Reference**: Check the column and row settings

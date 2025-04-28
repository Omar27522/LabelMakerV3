# Google Sheets Integration Setup

This document provides instructions on how to set up the Google Sheets integration for the Label Maker application.

## Prerequisites

1. A Google account
2. A Google Sheet that you want to write data to
3. Python libraries: `gspread` and `oauth2client`

## Installation

Install the required Python libraries:

```
pip install gspread oauth2client
```

## Setting Up Google Sheets API Access

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - In the sidebar, click on "APIs & Services" > "Library"
   - Search for "Google Sheets API" and click on it
   - Click "Enable"
4. Create a service account:
   - In the sidebar, click on "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Enter a name for the service account and click "Create"
   - Skip the optional steps and click "Done"
5. Create a key for the service account:
   - In the service accounts list, click on the email address of the service account you just created
   - Click on the "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Select "JSON" and click "Create"
   - The key file will be downloaded to your computer
6. Rename the downloaded file to `credentials.json` and place it in the root directory of the Label Maker application

## Setting Up Your Google Sheet

1. Create a new Google Sheet or use an existing one
2. Share the Google Sheet with the service account email address (found in the `client_email` field of your `credentials.json` file) with Editor permissions
3. Note the URL of your Google Sheet and the name of the worksheet you want to write to

## Configuring the Label Maker Application

1. Open the Label Maker application
2. Click the "Settings" button
3. In the "Google Sheets Integration" section, click "Configure Google Sheets"
4. Enter the URL of your Google Sheet and the name of the worksheet
5. Configure the columns and rows for tracking numbers and SKUs
6. Click "Test Connection" to verify that the connection works
7. Click "Save" to save your settings

## Connection Status Display

The welcome window displays the current Google Sheets connection status:

- **Green "Connected"**: Successfully connected to the configured Google Sheet
- **Orange "Configured (Not Tested)"**: Configuration exists but hasn't been tested
- **Red "Not Connected"**: Not configured or connection failed

The status indicator is clickable:
- Clicking on the "Configured (Not Tested)" status will test the connection without opening the full configuration dialog
- The text changes color and becomes underlined when hovered over, indicating it's clickable
- This provides a quick way to verify the connection status without navigating through the settings menu

## Persistent Connection Status

The Google Sheets connection status persists between application sessions:

1. The connection status is saved in the `label_maker_settings.json` file
2. When the application starts, it automatically verifies the connection using the saved settings
3. The status display is updated to reflect the current connection state
4. No need to reconnect or reconfigure when restarting the application

## Real-time Status Updates

The Google Sheets status updates immediately when changes are made:

1. When you save settings in the Google Sheets dialog, the status in the welcome window updates immediately
2. The application forces the UI to refresh using `update_idletasks()` to ensure the status is visible
3. Status changes are reflected without requiring the application to be restarted

## Using the Google Sheets Integration

Once configured, the Label Maker application will automatically write tracking numbers and SKUs to your Google Sheet when you create a new label.

The application will:
1. Write the tracking number to the specified column and row
2. Write the SKU to the specified column and row
3. Increment the row numbers for the next entry

## Troubleshooting

If you encounter issues with the Google Sheets integration, check the following:

1. Make sure the `credentials.json` file is in the root directory of the application
2. Verify that the Google Sheet is shared with the service account email address
3. Check that the worksheet name is correct
4. Ensure that the Google Sheets API is enabled for your project
5. Verify that the required Python libraries are installed
6. Try clicking the status indicator to test the connection
7. Check the application logs for detailed error messages

## 6. Google Sheets Integration

LabelMakerV3 offers powerful integration with Google Sheets, allowing you to track your shipments and inventory in the cloud. This section explains how to set up and use this integration.

### Benefits of Google Sheets Integration

Integrating LabelMakerV3 with Google Sheets provides several advantages:
- Access your inventory data from anywhere with internet access
- Share inventory information with team members
- Create automatic backups of your label data
- Generate reports and analytics using Google Sheets features
- Synchronize data across multiple devices

### Setting Up the Connection

To set up Google Sheets integration:

1. From the Welcome screen, click the gray **Settings** button
2. In the Settings screen, find the "Google Sheets Integration" section
3. Click the **Configure Google Sheets** button
4. The Google Sheets Configuration window will appear:

![Google Sheet Integration](/home/ubuntu/guide/images/Google Sheet Integration.jpg)

5. The configuration window includes:
   - A brief explanation of the integration purpose
   - A field for the Google Sheet URL
   - A dropdown for selecting the Sheet Name
   - Fields for specifying column mappings
   - Save and Cancel buttons

6. Enter the URL of your Google Sheet in the "Google Sheet URL" field
   - This should be the full URL of a Google Sheet you've already created
   - Make sure the sheet is accessible (shared with the appropriate permissions)

7. Select the specific sheet name from the dropdown
   - If your Google Sheets document has multiple sheets/tabs, select the one you want to use

8. Configure the column mappings:
   - **Tracking Number Column**: Specify which column will store tracking numbers (e.g., "D")
   - **SKU Column**: Specify which column will store SKU information (e.g., "E")
   - **Steps Value Column**: Specify which column will store steps values (e.g., "F")

9. For each column, specify the starting row (usually "3" if your sheet has headers)

10. Click **Save** to establish the connection

### Connected Status

Once successfully connected, the Google Sheets Configuration window will show the connected status:

![Google Sheet Integration Connected](/home/ubuntu/guide/images/Google Sheet Integration Connected.jpg)

The connection status will also be updated on the Welcome screen, changing from "Not Connected" to "Connected".

### Tracking Shipments and Inventory

After setting up the integration, LabelMakerV3 will:
- Automatically update your Google Sheet when new labels are created
- Read data from the specified columns when needed
- Write tracking information to the specified columns
- Synchronize data between the application and Google Sheets

You can view and edit the data directly in Google Sheets, and the changes will be reflected in LabelMakerV3 the next time you use the application.

### Troubleshooting Connection Issues

If you encounter problems with the Google Sheets integration:

1. Verify that the Google Sheet URL is correct and the sheet exists
2. Check that you have the necessary permissions to access the sheet
3. Ensure your internet connection is working properly
4. Verify that the column mappings are correct
5. Try disconnecting and reconnecting the integration
6. Check if your Google account requires re-authentication

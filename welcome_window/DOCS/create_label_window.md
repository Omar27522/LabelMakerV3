# Create Label Window Documentation

## Overview

The Create Label window provides a user interface for creating and printing barcode labels. It allows users to enter tracking numbers and SKUs, configure printing options, and send labels directly to the printer.

## Implementation

The Create Label window is implemented as a modular frame in `src/ui/create_label_frame.py` via the `CreateLabelFrame` class. It is embedded directly in the main application window, providing a seamless, integrated experience (not a modal dialog).

### Key Features

1. **Input Fields**
   - Tracking Number field
   - SKU field
   - Auto-focus on the Tracking Number field when the window opens
   - Keyboard shortcuts: Enter copies tracking number and moves focus to SKU

2. **Automatic Copy and Focus**
   - Pressing Enter in the Tracking Number field copies it to clipboard and moves focus to SKU

3. **Printing Options**
   - Print toggle: Enable/disable physical label printing (logs only if disabled)
   - Mirror Print toggle: Print mirrored labels for special use cases
   - Status messages and error handling for print operations

4. **Google Sheets Integration**
   - Automatically logs successful label prints to Google Sheets if configured
   - Only logs successful prints (errors prevent logging)

5. **Transparency and Pin**
   - Window transparency control (optional)
   - Pin button to keep window on top

6. **Frame-Based Modular Design**
   - Embedded as a frame, not a modal dialog
   - Allows easy navigation and integration with the rest of the UI
   - Consistent look and feel with other application windows

7. **Enhanced Error Handling**
   - Detects and warns about missing label files or invalid SKUs
   - Provides clear user feedback for all operations

8. **Additional Features**
   - Auto-clear fields after successful print
   - Visual feedback for print state (toggle color, status text)
   - Integrated with application-wide configuration and logging
   - When the user presses Enter after typing a tracking number, it is automatically copied to the clipboard
   - Focus automatically moves to the SKU field
   - This streamlines the workflow when the tracking number needs to be pasted into the SKU field
   - Eliminates the need for manual copying and tabbing, reducing user effort and potential errors
   - Implemented in both the standard Create Label dialog and the User dialog variant

3. **Mirror Print Toggle**:
   - Button to toggle mirror printing on/off
   - Visual indication of the current state (green for on, pink for off)
   - State is saved in the configuration

4. **Status Display**:
   - Real-time feedback on operations
   - Color-coded status messages (green for success, red for errors)

5. **Google Sheets Integration**:
   - Automatically writes tracking numbers and SKUs to Google Sheets if configured
   - Updates row numbers for the next entry

6. **Auto-Print**:
   - Uses PyAutoGUI to automatically press Enter after sending to the printer
   - Fallback to opening the image if printing fails

## Enhanced Workflow with Auto-Copy and Tab

The auto-copy and tab functionality significantly improves the user experience by:

1. **Streamlining Data Entry**:
   - Automatically copies the tracking number to the clipboard when the user presses Enter
   - Automatically moves focus to the SKU field without requiring manual tabbing
   - Makes it easier to paste the tracking number into the SKU field if needed

2. **Implementation Details**:
   ```python
   def on_tracking_enter(event):
       # Get the tracking number
       tracking_number = tracking_var.get().strip()
       
       # Copy to clipboard
       root.clipboard_clear()
       root.clipboard_append(tracking_number)
       
       # Move focus to SKU field
       sku_entry.focus_set()
       
       return "break"  # Prevent default Enter behavior
   
   # Bind Enter key to the tracking entry field
   tracking_entry.bind("<Return>", on_tracking_enter)
   ```

3. **User Experience Benefits**:
   - Reduces the number of keystrokes and mouse clicks required
   - Minimizes the chance of transcription errors
   - Speeds up the label creation process
   - Particularly useful when the tracking number and SKU are identical or related

## Usage Flow

1. User opens the Create Label window from the welcome screen
2. User enters a tracking number and presses Enter
   - The tracking number is automatically copied to the clipboard
   - Focus moves to the SKU field
3. User enters an SKU (optionally pasting the tracking number)
4. User clicks "Print Label" or presses Enter
5. The application:
   - Validates inputs
   - Updates Google Sheets if configured
   - Creates and prints the barcode
   - Updates the label count
   - Clears the form for the next label

## Code Structure

```python
def create_label_dialog(parent, config_manager, update_label_count_callback):
    # Dialog creation and setup
    
    # Form fields creation
    
    # Enter key handler for tracking field
    def on_tracking_enter(event):
        # Copy tracking number to clipboard
        # Move focus to SKU field
    
    # Mirror print toggle functionality
    
    # Print label function
    def print_label():
        # Get and validate input
        # Update Google Sheets
        # Generate and print barcode
        # Update label count
    
    # Button creation and event binding
```

## Dependencies

- `tkinter`: For the GUI components
- `PIL` (Pillow): For image manipulation
- `barcode`: For barcode generation
- `pyautogui`: For auto-pressing Enter in the print dialog
- `gspread` and `oauth2client`: For Google Sheets integration

## Related Components

- **Welcome Window**: Entry point that opens the Create Label dialog
- **Barcode Operations**: Utility functions for barcode generation and printing
- **Google Sheets Integration**: Functions for writing data to Google Sheets
- **Configuration Manager**: For storing and retrieving settings

## Consolidated Functionality

The Label Maker application has consolidated the label printing functionality by:

1. Removing the redundant `create_user_dialog` function
2. Updating the `user_action` method to call `create_label_action`
3. Enhancing the `create_label_dialog` function to include SKU validation
4. Using the same dialog for both User and Create Label buttons

This simplification ensures there's only one way to print labels through the Create Label dialog, making the application more intuitive and the codebase more maintainable with less duplicate code.

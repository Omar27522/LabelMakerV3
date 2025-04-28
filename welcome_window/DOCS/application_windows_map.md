# Label Maker Application Windows Map

## Overview

This document provides a comprehensive map of all windows and dialogs in the Label Maker application, including their locations in the codebase, their purpose, and their relationships to each other.

## Main Windows

### 1. Welcome Window
**File Location:** `src/ui/welcome_window.py`
**Class:** `WelcomeWindow`
**Purpose:** Main entry point of the application; provides access to all features.

**Key Features:**
- Dynamic label count in title
- Google Sheets connection status (clickable for testing)
- Buttons for:
  - User / Create Label (opens Create Label Frame)
  - Management (opens file viewer)
  - Settings (opens configuration dialogs)
  - Returns Data (opens Returns Data dialog)
- Hidden feature: Click "Ver." for No Record Label window

---

### 2. Create Label Frame
**File Location:** `src/ui/create_label_frame.py`
**Class:** `CreateLabelFrame`
**Purpose:** Main interface for creating and printing labels with tracking number and SKU.

**Key Features:**
- Frame-based (not a popup dialog)
- Tracking number/SKU entry fields
- Print toggle, Mirror Print toggle
- Auto-copy tracking number, keyboard shortcuts
- Error handling, status messages

---

### 3. No Record Label Frame
**File Location:** `src/ui/no_record_label_frame.py`
**Class:** `NoRecordLabelFrame`
**Purpose:** Print labels for existing SKUs without logging (hidden/quick access window).

**Key Features:**
- SKU-only entry
- Mirror Print toggle
- No logging or Google Sheets integration
- Error/status messages

---

### 4. Returns Data Dialog
**File Location:** `src/ui/returns_data_dialog.py`
**Class:** `ReturnsDataDialog`
**Purpose:** Tabbed interface for managing shipping records and labels.

**Key Features:**
- Two tabs:
  - Records Tab: View/edit shipping records (scrollable, form validation)
  - Labels Tab: See below
- Modular design; easy to extend

---

### 5. Labels Tab
**File Location:** `src/ui/labels_tab.py`
**Class:** `LabelsTab`
**Purpose:** Advanced label management and search.

**Key Features:**
- SQLite-backed label database
- CSV import/export (threaded for UI responsiveness)
- Flexible search across all fields, pagination
- Double-click to view label details
- Delete/export label records

---

### 6. Label Details Dialog
**File Location:** `src/ui/label_details_dialog.py`
**Class:** `LabelDetailsDialog`
**Purpose:** Shows detailed label info and image preview.

**Key Features:**
- Image preview (auto-resize, multiple formats)
- Thin info panel, reorganized controls
- Robust error handling

---

### 7. Google Sheets Dialog
**File Location:** `src/ui/google_sheets_dialog.py`
**Class:** `GoogleSheetsDialog`
**Purpose:** Configure and test Google Sheets integration.

**Key Features:**
- Sheet selection, URL validation
- Connection status test
- Remembers last selected sheet

---

### 8. Labels Settings Dialog
**File Location:** `src/ui/labels_settings_dialog.py`
**Class:** `LabelsSettingsDialog`
**Purpose:** Configure label-related settings (directories, options).

---

### 9. Log Migration Dialog
**File Location:** `src/ui/log_migration_dialog.py`
**Class:** `LogMigrationDialog`
**Purpose:** Migrate or update log files as needed.

---

### 10. Window Transparency Dialog
**File Location:** `src/ui/window_transparency.py`
**Class:** `TransparencyManager`
**Purpose:** Manage window transparency settings.

---

## Relationships & Navigation
- The Welcome Window is always the entry point
- All major actions open new frames/dialogs from the welcome window
- Returns Data dialog is the hub for record/label management
- Labels Tab and dialogs are modular for easy future expansion

## Notes
- All windows use Tkinter for UI
- Modular design: each dialog/frame in its own file/class
- Hidden/advanced windows (like No Record Label) are accessible via UI shortcuts

  - Labels (Opens Returns Data dialog)
  - Settings

**Related Functions:**
- `_create_ui()`: Creates the user interface elements
- `_create_title_section()`: Creates the title section with label count
- `_create_button_section()`: Creates the button grid
- `_update_sheets_status_display()`: Updates the Google Sheets connection status display

## Dialog Windows

### 1. Create Label Dialog
**File Location:** `src/utils/dialog_handlers.py`
**Functions:** 
- `create_label_dialog()`: Called from the "Create Label" button
- `create_user_dialog()`: Called from the "User" button (creates an identical dialog with mandatory SKU validation)

**Purpose:** Dialog for creating a new label.

**Key Features:**
- Input fields for tracking number and SKU
- Auto-copy and tab functionality when pressing Enter after typing tracking number
- Mirror print toggle
- Print label button

**Related Functions:**
- `print_label()`: Processes the label creation and printing
- `on_tracking_enter()`: Handles Enter key in tracking field

### 2. Returns Data Dialog
**File Location:** `src/utils/returns_operations.py`
**Function:** `create_returns_dialog()`
**Purpose:** Dialog for viewing and editing returns data.

**Key Features:**
- Displays a table of all shipping records
- Allows editing and deleting records
- Provides search functionality

**Related Functions:**
- `load_returns_data()`: Loads data from the log file
- `update_log_file()`: Updates the log file with changes

### 3. Edit Record Dialog
**File Location:** `src/utils/returns_operations.py`
**Function:** `create_edit_dialog()`
**Purpose:** Dialog for editing a returns data record.

**Key Features:**
- Scrollable form with fields for all record data
- Save and Cancel buttons
- Validation for required fields

### 4. Settings Dialog
**File Location:** `src/utils/settings_operations.py`
**Function:** `create_settings_dialog()`
**Purpose:** Dialog for configuring application settings.

**Key Features:**
- Labels directory configuration with browse button
- Google Sheets integration status and configuration button
- Save and Cancel buttons

**Related Functions:**
- `update_sheets_status_display()`: Updates the Google Sheets status display

### 5. Google Sheets Dialog
**File Location:** `src/ui/google_sheets_dialog.py`
**Class:** `GoogleSheetsDialog`
**Purpose:** Dialog for configuring Google Sheets integration.

**Key Features:**
- Google Sheet URL input
- Sheet name selection dropdown
- Column and row configuration for tracking numbers and SKUs
- Test connection button
- Save and Cancel buttons

**Related Functions:**
- `_fetch_sheet_names()`: Fetches available sheet names from the URL
- `_test_connection()`: Tests the connection to Google Sheets
- `_save_settings()`: Saves the Google Sheets configuration

## Workflow Relationships

### Label Creation Workflow
1. User clicks "User" or "Create Label" button in the Welcome Window
2. `user_action()` or `create_label_action()` in Welcome Window calls either `create_user_dialog()` or `create_label_dialog()` from dialog_handlers.py (both create the same dialog with minor differences)
3. User enters tracking number and presses Enter:
   - Tracking number is copied to clipboard
   - Focus moves to SKU field
4. User enters SKU and clicks "Print Label"
5. `process_barcode()` in barcode_operations.py:
   - Creates barcode image
   - Updates Google Sheets if configured
   - Prints the label directly
   - Updates label count

### Returns Data Workflow
1. User clicks "Labels" button in the Welcome Window
2. `labels_action()` in Welcome Window calls `create_labels_dialog()` from dialog_handlers.py
3. Returns Data Dialog opens showing all shipping records
4. User can select a record and click "Edit" to open the Edit Record Dialog
5. User makes changes and clicks "Save" to update the record

### Settings Workflow
1. User clicks "Settings" button in the Welcome Window
2. `settings_action()` in Welcome Window calls `create_settings_dialog_handler()` from dialog_handlers.py
3. Settings Dialog opens showing current settings
4. User can change the labels directory or click "Configure Google Sheets" to open the Google Sheets Dialog
5. User configures Google Sheets and clicks "Save" to update the configuration
6. User clicks "Save" in the Settings Dialog to save all settings

## Recent Enhancements

1. **Auto-copy and Tab in Create Label Window**
   - When user presses Enter after typing tracking number:
     - Number is automatically copied to clipboard
     - Focus moves to SKU field
   - Implemented in dialog_handlers.py

2. **Scrollable Edit Record Window**
   - Made the Edit Record window vertically scrollable with a canvas and scrollbar
   - Improved button visibility and layout
   - Added validation for required fields

3. **Google Sheets Status Updates**
   - Real-time status updates without requiring app restart
   - Clickable status indicator for quick connection testing
   - Persistent connection status between application sessions

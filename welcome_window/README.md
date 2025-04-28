# Label Maker V3

## Overview
This application provides a modular interface for managing the Label Maker application. It has been designed with a focus on modularity, maintainability, and extensibility.

## Project Structure
```
welcome_window/
├── assets/                      # Application icons and images
│   ├── icon_64.png
│   ├── icon_642.png
│   ├── returnsdata_64.png
│   └── settings_64.png
├── database/                    # SQLite databases
│   ├── labels.db                # Label metadata
│   └── shipping_records.db      # Shipping records
├── DOCS/                        # Documentation and developer guides
│   ├── CODEBASE_MAP.md
│   ├── GOOGLE_SHEETS_SETUP.md
│   ├── application_windows_map.md
│   ├── create_label_window.md
│   ├── edit_record_window.md
│   ├── google_sheets_integration.md
│   ├── index.md
│   ├── project_cleanup_standards.md
│   ├── returns_operations.md
│   ├── single_instance_mechanism.md
│   ├── ui_components.md
│   └── welcome_window.md
├── logs/                         # Log files
├── src/                          # Source code
│   ├── config/
│   │   └── config_manager.py     # Settings and config management
│   ├── ui/                       # UI components
│   │   ├── welcome_window.py
│   │   ├── create_label_frame.py
│   │   ├── no_record_label_frame.py
│   │   ├── google_sheets_dialog.py
│   │   ├── label_details_dialog.py
│   │   ├── labels_settings_dialog.py
│   │   ├── labels_tab.py
│   │   ├── log_migration_dialog.py
│   │   ├── returns_data_dialog.py
│   │   ├── window_state.py
│   │   ├── window_transparency.py
│   │   └── __init__.py
│   ├── utils/                    # Utility modules
│   │    ├── app_logger.py
│   │    ├── barcode_operations.py
│   │    ├── barcode_utils.py
│   │    ├── config_utils.py
│   │    ├── database_operations.py
│   │    ├── dialog_handlers.py
│   │    ├── file_utils.py
│   │    ├── label_database.py
│   │    ├── log_manager.py
│   │    ├── logger.py
│   │    ├── returns_operations.py
│   │    ├── settings_operations.py
│   │    ├── sheets_operations.py
│   │    ├── sheets_utils.py
│   │    ├── text_context_menu.py
│   │    ├── ui_components.py
│   │    ├── ui_utils.py
│   │    └── window_utils.py
│   └── Requrements.txt
├── label_maker_settings.json     # Application settings
├── main.pyw                     # Application entry point
├── README.md
├── credentials.json
```

## Features

### Major Features
- **Modular application structure** with clear separation between UI, logic, and data
- **Single-instance mechanism** (prevents multiple app launches)
- **Centralized configuration management** and comprehensive logging
- **Returns Data dialog** with tabbed interface:
  - **Records Tab**: Manage shipping records
  - **Labels Tab**: Advanced label management (see below)
- **Google Sheets integration** for tracking and record-keeping
- **Dynamic label count** in welcome window
- **Auto-copy** for tracking numbers, keyboard shortcuts for efficiency
- **Print toggle** for logging-only mode, and **Mirror Print** option
- **Pin toggle** to keep windows on top
- **Hidden "No Record Label" mode** for printing labels without logging

### Labels Tab (New)
- **Dedicated Labels Tab** in Returns Data dialog
- **SQLite database** for label metadata
- **CSV import/export** with threading for UI responsiveness
- **Flexible search** across all label fields (partial info, e.g., color or website)
- **Pagination** for large datasets, adjustable records per page
- **Image preview** for label files (with auto-resize and multiple formats)
- **Double-click to view label files**; integrates with file search utilities
- **Export search results to CSV**
- **Delete label records** with status indicators
- **Status messages** for all operations

### Advanced Search & UI
- **Search labels** by partial SKU, color, or website name
- **Treeview results** with pagination
- **Improved error handling** and user feedback
- **UI enhancements**: thinner info panels, reorganized controls, modern look

### Architecture & Structure
- Modular design: each major feature in its own class/file (e.g., `LabelsTab`, `ReturnsDataDialog`)
- `src/ui/labels_tab.py`, `src/ui/returns_data_dialog.py` for UI logic
- `src/utils/label_database.py` for database operations
- `database/labels.db` for label metadata
- Follows best practices for maintainability and extensibility

## Dependencies
- Python 3.6+
- pywin32
- pyautogui
- gspread
- oauth2client
- Pillow
- pandas

### Core Functionality
- **Frame-based UI** with modular components
- **Single instance enforcement** prevents multiple launches
- **DPI-aware scaling** for high-resolution displays
- **Temporary file cleanup** on exit

### Label Management
- **No-record label printing** (hidden feature)
- **Advanced label search** with partial SKU matching
- **Label database** (SQLite) with CSV import/export
- **Image preview** for label files

### Recent Enhancements
1. **Labels Tab** in Returns Data dialog:
   - Database-backed label metadata storage
   - Threaded CSV import with progress indicators
   - Flexible search across all fields
   - Paginated results with configurable page sizes

2. **UI Improvements**:
   - Tabbed interface for Records/Labels management
   - Visual label preview with aspect ratio maintenance
   - Enhanced error handling with user-friendly messages

3. **System Reliability**:
   - Single instance enforcement using mutex/socket
   - Cross-platform DPI awareness
   - Automated temp file cleanup

## Installation

### Requirements
- Python 3.9+
- Windows OS (DPI awareness and single-instance features are Windows-specific)

### Steps
1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. For Google Sheets integration, follow the instructions in `GOOGLE_SHEETS_SETUP.md`
4. (Optional) Review and edit `label_maker_settings.json` for custom paths and options

## Usage

Run the application by executing `main.pyw`:
```bash
python main.pyw
```

- The welcome window provides access to all main features
- Use the Records/Labels tabs in Returns Data for managing records and labels
- Access hidden features (like No Record Label) by clicking the "Ver." text in the main window

### Main Functions
- **User/Create Label**: Create and print labels with tracking numbers and SKUs
- **Labels/Returns Data**: Access Returns Data and label management features
- **Management**: Open the Label Maker file viewer for the selected labels directory
- **Settings**: Configure application settings including Google Sheets integration

## Label Creation and Printing
The application includes a robust label creation system:
- Enter tracking numbers and SKUs to create labels
- Auto-copy tracking numbers to clipboard when Enter is pressed
- Print toggle to enable/disable physical printing while maintaining data records
- Mirror Print option for special printing configurations
- Enhanced error handling for missing label files
- Clear warning messages when label files cannot be found

## Returns Data Management
The application includes a robust Returns Data management system:
- View and edit shipping records
- Scrollable interface for editing records
- Form validation for required fields
- Success/error messages for user feedback

## Google Sheets Integration
The application can connect to Google Sheets for tracking:
- Configure connection in Settings
- Test connection status with clickable status indicator
- Real-time status updates without requiring app restart
- Remembers the last selected sheet name
- Automatically update tracking information

## Hidden Features
- **No Record Label Mode**: Access by clicking the "Ver." text in the bottom-right corner
  - Print labels without recording them in logs or Google Sheets
  - Only requires an SKU (no tracking number)
  - Includes error handling for missing label files

## Development
The application is designed to be easily extended with new features:
- Add new UI components in the `src/ui/` directory
- Extend configuration options in `src/config/config_manager.py`
- Add utility functions in `src/utils/`
- Use the standardized UI components in `src/utils/ui_components.py` for consistent UI design

## UI Components
The application uses standardized UI components for a consistent look and feel:
- Title sections
- Colored buttons with hover effects
- Button grids
- Form field groups
- Status displays

## Integration with Label Maker
The application integrates with the Label Maker application by:
1. Detecting the Label Maker installation directory
2. Launching Label Maker with appropriate parameters
3. Managing window focus between applications
4. Displaying the number of labels in the configured directory

## Recent Improvements
- Added comprehensive **Labels Tab** with CSV import, advanced search, and image preview
- Enhanced **Label Details dialog**: visual file preview, better layout, and robust error handling
- Improved **Returns Data dialog**: modular, tabbed interface for easier expansion
- Upgraded **single-instance mechanism** (mutex/socket fallback)
- Improved DPI awareness for high-res screens
- More robust error messages and user feedback throughout the app
- Dynamic label count and instant Google Sheets status updates
- Streamlined logging, configuration, and code organization

# Label Maker V3

## Overview
This application provides a modular interface for managing the Label Maker application. It has been designed with a focus on modularity, maintainability, and extensibility. The application integrates label creation, printing, database management, and Google Sheets integration into a cohesive and user-friendly interface.

## Project Structure
```
label-maker-v3/
├── assets/                      # Application icons and images
│   ├── icon_64.png              # Main application icon
│   └── settings_64.png          # Settings icon
├── database/                    # SQLite databases
│   ├── labels.db                # Label metadata storage
│   └── shipping_records.db      # Shipping records database
├── DOCS/                        # Documentation and developer guides
│   ├── CODEBASE_MAP.md          # Overview of codebase structure
│   ├── GOOGLE_SHEETS_SETUP.md   # Google Sheets integration guide
│   ├── application_windows_map.md # Map of application windows
│   ├── browser_tab_management.md # Browser automation documentation
│   ├── create_label_window.md   # Label creation UI documentation
│   ├── edit_record_window.md    # Record editing documentation
│   ├── google_sheets_integration.md # Sheets API integration details
│   ├── index.md                 # Documentation index
│   ├── project_cleanup_standards.md # Code maintenance standards
│   ├── returns_operations.md    # Returns processing documentation
│   ├── single_instance_mechanism.md # Single instance implementation
│   ├── ui_components.md         # UI component documentation
│   └── welcome_window.md        # Main window documentation
├── logs/                        # Application log files
├── src/                         # Source code
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── config_manager.py    # Settings and config management
│   ├── ui/                      # User interface components
│   │   ├── __init__.py
│   │   ├── create_label_frame.py # Label creation interface
│   │   ├── google_sheets_dialog.py # Sheets configuration dialog
│   │   ├── jdl_automation_frame.py # JDL automation interface
│   │   ├── label_details_dialog.py # Label details view
│   │   ├── labels_settings_dialog.py # Label settings configuration
│   │   ├── labels_tab.py        # Labels management tab
│   │   ├── log_migration_dialog.py # Log migration interface
│   │   ├── no_record_label_frame.py # Hidden label creation mode
│   │   ├── returns_data_dialog.py # Returns data management
│   │   ├── welcome_window.py    # Main application window
│   │   ├── window_state.py      # Window state management
│   │   └── window_transparency.py # Window transparency control
│   ├── utils/                   # Utility modules
│   │   ├── __init__.py
│   │   ├── app_logger.py        # Application logging
│   │   ├── barcode_operations.py # Barcode generation and printing
│   │   ├── barcode_utils.py     # Barcode helper functions
│   │   ├── config_utils.py      # Configuration utilities
│   │   ├── database_operations.py # Database interaction
│   │   ├── dialog_handlers.py   # Dialog management
│   │   ├── file_utils.py        # File system operations
│   │   ├── jdl_automation.py    # JDL system automation
│   │   ├── label_database.py    # Label database operations
│   │   ├── log_manager.py       # Log management
│   │   ├── logger.py            # Logging setup
│   │   ├── returns_operations.py # Returns processing
│   │   ├── settings_operations.py # Settings management
│   │   ├── sheets_operations.py # Google Sheets operations
│   │   ├── sheets_utils.py      # Google Sheets utilities
│   │   ├── text_context_menu.py # Text field context menus
│   │   ├── ui_components.py     # Reusable UI components
│   │   ├── ui_utils.py          # UI helper functions
│   │   └── window_utils.py      # Window management utilities
│   └── requirements.txt         # Package dependencies
├── chrome_user_data/            # Browser automation data
├── credentials.json             # Google API credentials
├── credentials_template.json    # Template for API credentials
├── label_maker_settings.json    # Application settings
├── main.pyw                     # Application entry point
└── README.md                    # Project documentation
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
- **Dedicated Labels Tab** in Returns Data dialog with intuitive UI
- **SQLite database** for label metadata with efficient indexing
- **CSV import/export** with threading for UI responsiveness and progress indicators
- **Flexible search** across all label fields (partial info, e.g., color or website)
- **Advanced filtering** by field type (UPC, SKU, color, department, etc.)
- **Pagination** for large datasets with adjustable records per page
- **Image preview** for label files with auto-resize and support for multiple formats
- **Double-click to view label files**; integrates with file search utilities
- **Export search results to CSV** for external processing
- **Delete label records** with confirmation and status indicators
- **Status messages** for all operations with color-coded feedback
- **Context menu** for quick actions on selected records
- **User notes** for labels with option to sync across related items

### Advanced Search & UI
- **Search labels** by partial SKU, color, or website name with instant results
- **Treeview results** with pagination and sortable columns
- **Improved error handling** with detailed user feedback
- **UI enhancements**: thinner info panels, reorganized controls, modern look
- **Responsive design** that adapts to window resizing
- **Keyboard shortcuts** for common operations
- **Tabbed interface** for easy navigation between features
- **Context-sensitive help** for complex operations

### Architecture & Structure
- **Modular design**: each major feature in its own class/file (e.g., `LabelsTab`, `ReturnsDataDialog`)
- **Clean separation** of UI, business logic, and data access layers
- **Frame-based UI components** for reusability and consistent look-and-feel
- **Standardized UI components** in `src/utils/ui_components.py`
- **Database abstraction** in `src/utils/label_database.py` for clean data operations
- **Configuration management** with `src/config/config_manager.py`
- **Comprehensive logging** with rotation and different log levels
- **Error handling** with user-friendly messages and detailed logging
- **Thread management** for non-blocking UI during long operations
- **Follows best practices** for maintainability and extensibility

## Dependencies
- Python 3.6+
- pywin32
- pyautogui
- gspread
- oauth2client
- Pillow
- pandas

### Core Functionality
- **Frame-based UI** with modular components and standardized styling
- **Single instance enforcement** with mutex/socket fallback mechanism
- **DPI-aware scaling** for high-resolution displays across Windows versions
- **Temporary file cleanup** on exit with proper error handling
- **Comprehensive logging** with configurable verbosity levels
- **Window state management** for consistent user experience
- **Centralized configuration** with JSON-based settings persistence

### Label Management
- **No-record label printing** (hidden feature)
- **Advanced label search** with partial SKU matching
- **Label database** (SQLite) with CSV import/export
- **Image preview** for label files

### Recent Enhancements
1. **Labels Tab** in Returns Data dialog:
   - SQLite database-backed label metadata storage with optimized indexing
   - Threaded CSV import/export with progress indicators for UI responsiveness
   - Advanced search with field-specific filtering and partial matching
   - Paginated results with configurable page sizes and sorting
   - Context menu for quick actions on selected records
   - User notes with synchronization across related items

2. **UI Improvements**:
   - Modern tabbed interface for Records/Labels management
   - Visual label preview with aspect ratio maintenance and zoom
   - Enhanced error handling with color-coded, user-friendly messages
   - Keyboard shortcuts for common operations
   - Responsive design that adapts to window resizing
   - Transparency controls for better multitasking
   - Stay-on-top functionality for key windows

3. **System Reliability**:
   - Robust single instance enforcement using mutex with socket fallback
   - Enhanced cross-platform DPI awareness for high-resolution displays
   - Automated temp file cleanup with proper error handling
   - Improved Google Sheets connection status monitoring
   - Thread management for non-blocking UI during long operations

## Installation

### Requirements
- Python 3.9+ (tested with Python 3.9.7 and 3.10.x)
- Windows OS (DPI awareness and single-instance features are Windows-specific)
- Internet connection for Google Sheets integration

### Steps
1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. For Google Sheets integration:
   - Follow the detailed instructions in `DOCS/GOOGLE_SHEETS_SETUP.md`
   - Create a Google Cloud Platform project and enable the Google Sheets API
   - Download credentials and save as `credentials.json` in the project root
   - A template file `credentials_template.json` is provided for reference
4. Configure application settings:
   - Review and edit `label_maker_settings.json` for custom paths and options
   - Set the labels directory path to where your label files are stored
   - Configure Google Sheets settings if using that integration
   - Adjust UI preferences like transparency and stay-on-top behavior

## Usage

### Starting the Application
Run the application by executing `main.pyw`:
```bash
python main.pyw
```

The application uses a single-instance mechanism to prevent multiple launches. If you try to start it while it's already running, you'll receive a notification.

### Welcome Window
- The welcome window provides access to all main features through a clean, intuitive interface
- Dynamic label count shows the number of labels in the configured directory
- Google Sheets connection status is displayed with clickable indicator for testing
- Stay-on-top toggle allows the window to remain visible while working with other applications

### Main Functions
- **User/Create Label**: Create and print labels with tracking numbers and SKUs
  - Auto-copy tracking numbers to clipboard
  - Print toggle for logging-only mode
  - Mirror Print option for special printing configurations
  - Enhanced error handling for missing label files
  - Transparency controls for better multitasking

- **Labels/Returns Data**: Access the tabbed interface for data management
  - **Records Tab**: View and edit shipping records with scrollable interface
  - **Labels Tab**: Search, filter, and manage label metadata with advanced features
  - Import/export CSV data with progress indicators
  - Image preview for label files

- **Management**: Open the Label Maker file viewer for the selected labels directory
  - Quick access to label files
  - Automatic directory detection

- **Settings**: Configure application settings
  - Google Sheets integration setup and testing
  - Labels directory selection
  - UI preferences and behavior options

### Hidden Features
- Access the No Record Label mode by clicking the "Ver." text in the bottom-right corner
- This allows printing labels without logging them in records or Google Sheets

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

### 1. Labels Management System
- Added comprehensive **Labels Tab** with SQLite database backend and optimized indexing
- Implemented threaded **CSV import/export** with progress indicators for UI responsiveness
- Developed advanced **search functionality** with field-specific filtering and partial matching
- Created **pagination system** with configurable page sizes and dynamic record counts
- Added **context menu** for quick actions on selected records
- Implemented **user notes** with synchronization across related items
- Added **image preview** for label files with auto-resize and format detection

### 2. UI/UX Enhancements
- Enhanced **Label Details dialog** with visual file preview, zoom capabilities, and improved layout
- Improved **Returns Data dialog** with modular, tabbed interface for easier expansion
- Added **transparency controls** for better multitasking and window management
- Implemented **stay-on-top functionality** for key windows with persistent state
- Added **keyboard shortcuts** for common operations to improve workflow efficiency
- Created **responsive design** that adapts to window resizing and different display configurations
- Improved **error handling** with color-coded, user-friendly messages and detailed logging

### 3. System Reliability & Performance
- Upgraded **single-instance mechanism** with mutex and socket fallback for robust application launching
- Enhanced **cross-platform DPI awareness** for high-resolution displays across Windows versions
- Implemented **thread management** for non-blocking UI during long operations
- Improved **Google Sheets connection status** monitoring with real-time updates
- Enhanced **database operations** with prepared statements and optimized queries
- Added **automated temp file cleanup** with proper error handling and logging
- Implemented **centralized configuration management** with JSON-based settings persistence

### 4. New Functionality
- Added **JDL Automation** for streamlined workflow integration
- Implemented **browser tab management** for external system interaction
- Created **No Record Label mode** for specialized printing scenarios
- Added **dynamic label count** display with automatic updates
- Implemented **Mirror Print option** for special printing configurations
- Enhanced **barcode operations** with improved error handling and format support

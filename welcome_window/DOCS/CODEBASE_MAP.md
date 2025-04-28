# Label Maker Codebase Map

## Core Architecture

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
│   ├── application_windows_map.md
│   ├── GOOGLE_SHEETS_SETUP.md
│   └── ...
├── logs/                        # Log files
├── src/                         # Source code
│   ├── config/
│   │   └── config_manager.py    # Settings/configuration
│   ├── ui/                      # User interface components
│   │   ├── welcome_window.py            # Main welcome window
│   │   ├── create_label_frame.py        # Frame-based label creation
│   │   ├── no_record_label_frame.py     # No-record label creation
│   │   ├── returns_data_dialog.py       # Returns Data (tabbed: Records, Labels)
│   │   ├── labels_tab.py                # Labels Tab (advanced label management)
│   │   ├── label_details_dialog.py      # Label Details dialog (image preview)
│   │   ├── labels_settings_dialog.py    # Label settings dialog
│   │   ├── google_sheets_dialog.py      # Google Sheets configuration dialog
│   │   ├── log_migration_dialog.py      # Log migration dialog
│   │   ├── window_state.py              # Window state management
│   │   ├── window_transparency.py       # Transparency controls
│   │   └── __init__.py
│   ├── utils/                   # Utility modules
│   │   ├── app_logger.py
│   │   ├── barcode_operations.py        # Barcode generation/printing
│   │   ├── barcode_utils.py
│   │   ├── config_utils.py
│   │   ├── database_operations.py
│   │   ├── dialog_handlers.py
│   │   ├── file_utils.py
│   │   ├── label_database.py           # Label metadata DB ops
│   │   ├── log_manager.py
│   │   ├── logger.py
│   │   ├── returns_operations.py
│   │   ├── settings_operations.py
│   │   ├── sheets_operations.py        # Google Sheets API
│   │   ├── sheets_utils.py
│   │   ├── text_context_menu.py
│   │   ├── ui_components.py            # Reusable UI widgets
│   │   ├── ui_utils.py
│   │   └── window_utils.py
├── label_maker_settings.json           # App settings
├── main.pyw                            # Application entry point
├── README.md
├── credentials.json
├── credentials_template.json
├── .gitignore
├── .windsurf
```

│       └── config_manager.py     # Settings handling
├── main.pyw               # Application entry point
└── start_label_maker.pyw  # Launcher script
```

## Key Workflows

### 1. Create Label Workflow

1. User clicks "User" or "Create Label" button in welcome_window.py
2. `create_label_action()` in welcome_window.py calls `create_label_frame()` from create_label_frame.py
3. User enters tracking number and presses Enter:
   - Tracking number is copied to clipboard
   - Focus moves to SKU field
4. User enters SKU and clicks "Print Label"
5. `process_barcode()` in barcode_operations.py:
   - Creates barcode image
   - Updates Google Sheets if configured
   - Prints the label
   - Updates label count

### 2. Google Sheets Integration

1. User configures Google Sheets in Settings
2. Connection status is displayed in welcome window
3. When labels are created, data is written to the configured sheet

## Important Classes and Functions

### WelcomeWindow (welcome_window.py)
- Main application window
- Provides access to all features
- Displays label count and Google Sheets status
- Manages stay-on-top window state

### CreateLabelFrame (create_label_frame.py)
- Frame-based implementation of label creation
- Includes Pin toggle for stay-on-top functionality
- Handles tracking number validation and auto-copy

### NoRecordLabelFrame (no_record_label_frame.py)
- Frame for creating labels without logging
- Includes Pin toggle for stay-on-top functionality

### LabelWindow (label_window.py)
- Displays label preview
- Handles label printing

### ConfigManager (config_manager.py)
- Manages application settings
- Persists configuration between sessions

### Key Functions

- `create_label_dialog()` - Creates the dialog for label creation
- `process_barcode()` - Handles barcode creation and printing
- `write_to_google_sheet()` - Updates Google Sheets with label data
- `update_label_count()` - Updates the label count display

## Recent Enhancements

1. **Auto-copy and Tab in Create Label Window**
   - When user presses Enter after typing tracking number:
     - Number is automatically copied to clipboard
     - Focus moves to SKU field
   - Implemented in dialog_handlers.py

2. **Single Instance Mechanism**
   - Prevents multiple instances of the application
   - Shows notification when another instance is detected

3. **Google Sheets Status Updates**
   - Real-time status updates without requiring app restart
   - Clickable status indicator for quick connection testing

4. **Frame-based UI Implementation**
   - Replaced dialog-based UI with embedded frames
   - Improved navigation between different views
   - Enhanced user experience with consistent styling

5. **Stay-on-Top Feature**
   - Pin toggle button in all frames (except welcome window)
   - Keeps application window on top of other programs
   - Remembers user preference in settings
   - Implemented using tkinter's topmost attribute with lift() and focus_force()

# MainWindow Class Documentation

## Overview
The `MainWindow` class is the main application window for the Label Maker application. It inherits from `tk.Tk` and provides functionality for creating, managing, and printing labels with barcodes.

## Class Structure

### Constructor
```python
def __init__(self)
```
Initializes the main application window and sets up:
- Window tracking for managing multiple windows
- Configuration and window management
- Barcode generator
- Last print tracking
- Auto-switch functionality
- Window transparency
- UI components and event bindings

### Key Components

#### Window Management
- `app_windows`: List tracking all application windows
- `window_manager`: Handles window positioning and state
- `config_manager`: Manages application settings
- `barcode_generator`: Generates barcodes for labels

#### Input Fields
The application has four main input fields:
- Product Name Line 1
- Line 2 (optional)
- Variant
- UPC Code (12 digits)

Each field has associated validation and event handling.

#### UI Controls
- Pin button: Toggles always-on-top state
- Magnifier: Adjusts list view text size
- Preview size control: Cycles through 3 preview sizes
- Mirror print toggle (🔄): For mirror printing
- Auto-switch toggle (⚡): Manages window behavior when searching SKU/UPC:
  - Closes View Files window when no match is found
  - Switches focus to main window when match is found
  - Selects next item after printing
- Print minimize toggle (📄): Minimizes View Files window after printing

### Key Methods

#### Window Setup and Configuration
- `_setup_fonts()`: Configures default fonts
- `_setup_variables()`: Initializes tkinter variables
- `_load_icons()`: Loads button icons
- `_create_main_window()`: Sets up the main UI

#### Input Field Management
- `_create_input_fields()`: Creates and configures input fields
- `_add_undo_support()`: Adds undo/redo functionality
- `validate_upc()`: Validates UPC code input
- `validate_variant()`: Validates variant field input

#### File Operations
- `view_directory_files()`: Updates file listing
- `open_selected_file()`: Opens selected file
- `print_selected_file()`: Prints selected file
- `save_label()`: Saves label to file

#### Preview and Display
- `show_preview()`: Shows preview of selected file
- `cycle_preview_size()`: Cycles through preview sizes
- `toggle_magnification()`: Toggles list magnification

#### Window State Management
- `toggle_window_on_top()`: Toggles always-on-top state
- `toggle_mirror_print()`: Toggles mirror printing
- `toggle_auto_switch()`: Toggles auto window switching and closing behavior
- `toggle_print_minimize()`: Toggles print minimize behavior
- `update_window_transparency()`: Updates window transparency

### Event Handling
- Focus management for input fields
- Mouse click handling
- Keyboard shortcuts (Ctrl+A, Ctrl+Z, Ctrl+Y)
- Context menu support
- Window focus tracking

### Settings Management
- Transparency control
- Font size settings
- Barcode width settings
- Label counter tracking
- Configuration saving/loading

## Usage Example
```python
app = MainWindow()
app.run()
```

## Dependencies
- tkinter: For GUI components
- PIL: For image handling
- ConfigManager: For settings management
- WindowManager: For window state management
- BarcodeGenerator: For barcode generation

## Notes
- The application uses a modern UI with clear visual feedback
- Supports undo/redo operations for text input
- Implements Windows-style keyboard shortcuts
- Provides validation for UPC codes and variant fields
- Maintains window state across sessions

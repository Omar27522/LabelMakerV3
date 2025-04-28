# Main Application Script Documentation (main.pyw)

## Overview
The `main.pyw` script serves as the entry point for the Label Maker application. It handles application initialization, single-instance enforcement, window management, and provides utility functions for label creation and file processing.

## Key Components

### 1. Application Initialization
```python
if __name__ == "__main__":
    # Single instance enforcement using Windows mutex
    # Exception handling setup
    # Window initialization
```
- Creates a global mutex to ensure only one instance runs
- Sets up system-wide exception handling
- Initializes the main application window

### 2. Core Functions

#### Window Management
```python
def bring_to_front()
```
- Finds existing application window
- Forces window to foreground
- Restores from minimized state if needed
- Flashes window to get user attention

```python
def setup_window()
```
- Registers cleanup function
- Creates and configures main window
- Sets taskbar icon
- Starts the application main loop
- Initializes window state management:
  - 🔄 Mirror print functionality
  - ⚡ Auto-switch behavior for SKU/UPC searches
  - 📄 Print minimize feature

```python
def set_taskbar_icon(root)
```
- Sets window and taskbar icons
- Handles both PNG and ICO formats
- Sets Windows-specific app user model ID

#### Label Processing

```python
def process_product_name(full_name: str) -> tuple[str, str, str]
```
- Splits product name into components:
  - name_line1 (max 18 chars)
  - name_line2 (max 20 chars)
  - variant
- Handles word wrapping and length limits

```python
def create_batch_labels(csv_path, main_window)
```
- Processes CSV files for batch label creation
- Validates barcodes
- Generates and saves label images
- Updates label counter
- Handles error reporting

#### Utility Functions

```python
def sanitize_filename(name: str) -> str
```
- Removes invalid characters from filenames
- Ensures filenames are safe for all operating systems

```python
def is_valid_barcode(barcode: str) -> bool
```
- Validates 12-digit barcode format
- Uses regex for precise matching

```python
def cleanup()
```
- Performs application cleanup
- Removes temporary files
- Logs shutdown process

### 3. Error Handling

```python
def handle_exception(exc_type, exc_value, exc_traceback)
```
- Global exception handler
- Logs all uncaught exceptions
- Shows user-friendly error messages
- Special handling for KeyboardInterrupt

## Features
### Window Management
- Single instance enforcement
- Window state persistence
- Taskbar integration
- Modern UI with tooltips

### Label Operations
- Mirror printing support
- Preview size control (3 sizes)
- Batch label processing
- UPC/SKU validation

### View Files Window
- File preview with zoom
- Search functionality
- Toggle controls:
  - 🔄 Mirror Print: For mirroring label output
  - ⚡ Auto Switch: 
    - Closes window when no SKU/UPC match
    - Switches focus on match
    - Selects next item after printing
  - 📄 Print Minimize: Minimizes window after printing

### User Experience
- Keyboard shortcuts
- Input validation
- Error reporting
- State persistence
- Tooltips for all controls

## Dependencies
- tkinter: GUI framework
- PIL (Pillow): Image processing
- win32api/win32gui: Windows-specific functionality
- pandas: CSV processing
- logging: Application logging

## System Requirements
- Windows operating system
- Python 3.x
- Required system permissions for:
  - File system access
  - Window management
  - Mutex creation

## Usage
The script is designed to run as a Windows application (`.pyw` extension):
```bash
pythonw main.pyw
```

## Error Handling and Logging
- All exceptions are caught and logged
- User-friendly error messages are displayed
- Detailed logs are saved for debugging
- Graceful shutdown on errors

## Security Features
- Single instance enforcement
- Safe file handling
- Input validation
- Secure temporary file cleanup

## Notes
- The `.pyw` extension prevents console window from appearing
- Windows-specific features require appropriate permissions
- Temporary files are cleaned up on exit
- Application state is preserved between sessions

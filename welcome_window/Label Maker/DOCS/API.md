# API Documentation

## Application Execution

The Label Maker application can be executed in two ways:

1. **Python Script**: Run the `main.pyw` file directly with Python:
   ```
   python main.pyw
   ```
   This requires Python 3.7+ and all dependencies installed.

2. **Executable File**: If the application has been compiled using PyInstaller (as described in [Deployment Guide](DEPLOYMENT.md)), you can run the generated `.exe` file:
   ```
   "Label Maker V3.exe"
   ```
   The executable contains all dependencies and doesn't require a separate Python installation.

## Table of Contents

- [Core Modules](#core-modules)
  - [BarcodeGenerator](#barcodegenerator)
  - [WindowManager](#windowmanager)
  - [ConfigManager](#configmanager)
- [UI Components](#ui-components)
  - [MainWindow](#mainwindow)
  - [ViewFilesWindow](#viewfileswindow)
- [Utility Functions](#utility-functions)
  - [CSV Processing](#csv-processing)
  - [File Management](#file-management)
- [Event System](#event-system)
  - [Custom Events](#custom-events)
  - [Event Handlers](#event-handlers)
- [Constants and Enums](#constants-and-enums)
  - [Window States](#window-states)
  - [Preview Sizes](#preview-sizes)
- [Error Handling](#error-handling)
  - [Custom Exceptions](#custom-exceptions)
- [Configuration Schema](#configuration-schema)
  - [Settings Structure](#settings-structure)

## Core Modules

### BarcodeGenerator

#### Class: `BarcodeGenerator`
Main class for generating and managing label barcodes.

```python
def generate_label(
    text: str, 
    barcode: str, 
    size: tuple = (600, 310)
) -> PIL.Image:
    """Generate a label with text and barcode."""
```

**Example Usage:**
```python
from src.barcode_generator import BarcodeGenerator

# Create a barcode generator instance
generator = BarcodeGenerator()

# Generate a label with product name and UPC code
product_name = "Sample Product"
upc_code = "123456789012"
label_image = generator.generate_label(product_name, upc_code)

# Save the label to a file
label_image.save("sample_label.png")
```

```python
def validate_barcode(
    barcode: str
) -> bool:
    """Validate barcode format and checksum."""
```

**Example Usage:**
```python
from src.barcode_generator import BarcodeGenerator

generator = BarcodeGenerator()

# Validate a UPC code
valid_upc = "123456789012"
invalid_upc = "12345"

print(f"Valid UPC: {generator.validate_barcode(valid_upc)}")  # True
print(f"Invalid UPC: {generator.validate_barcode(invalid_upc)}")  # False
```

### WindowManager

#### Class: `WindowManager`
Handles window creation and management.

```python
def create_window(
    title: str,
    size: tuple,
    position: str = "center"
) -> tk.Toplevel:
    """Create a new window with specified parameters."""
```

**Example Usage:**
```python
from src.window_manager import WindowManager

# Create a window manager instance
window_manager = WindowManager()

# Create a new window
new_window = window_manager.create_window(
    title="Label Preview",
    size=(800, 600),
    position="center"
)

# Configure the window
new_window.configure(bg="white")
```

```python
def make_draggable(
    window: tk.Toplevel
) -> None:
    """Add drag functionality to window."""
```

**Example Usage:**
```python
from src.window_manager import WindowManager

window_manager = WindowManager()
preview_window = window_manager.create_window("Preview", (400, 300))

# Make the window draggable by clicking anywhere on it
window_manager.make_draggable(preview_window)
```

### ConfigManager

#### Class: `ConfigManager`
Manages application configuration and settings.

```python
def load_config() -> dict:
    """Load configuration from file."""
```

**Example Usage:**
```python
from src.config import ConfigManager

# Create a config manager instance
config_manager = ConfigManager()

# Load the configuration
config = config_manager.load_config()

# Access configuration values
font_size = config["window_settings"]["font_size_large"]
barcode_width = config["label_settings"]["barcode_width"]
```

```python
def save_config(
    config: dict
) -> bool:
    """Save configuration to file."""
```

**Example Usage:**
```python
from src.config import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config()

# Update configuration values
config["window_settings"]["transparency_level"] = 0.9
config["view_files_settings"]["auto_switch"] = True

# Save the updated configuration
success = config_manager.save_config(config)
print(f"Configuration saved: {success}")
```

## UI Components

### MainWindow

#### Class: `MainWindow`
Primary application window implementation.

```python
def preview_label(
    size: int = 4
) -> None:
    """Generate and display label preview."""
```

**Example Usage:**
```python
from src.ui.main_window import MainWindow

# Create the main window
main_window = MainWindow()

# Generate and display a preview with size 4
main_window.preview_label(size=4)

# Update the preview with a different size
main_window.preview_label(size=5)
```

```python
def save_label(
    path: str = None
) -> bool:
    """Save current label to file."""
```

**Example Usage:**
```python
from src.ui.main_window import MainWindow

main_window = MainWindow()

# Fill in the label information
main_window.name_entry.insert(0, "Sample Product")
main_window.upc_entry.insert(0, "123456789012")

# Save the label to a specific path
success = main_window.save_label(path="C:/labels/sample_label.png")

# Or let the application choose the path based on settings
success = main_window.save_label()
```

### ViewFilesWindow

#### Class: `ViewFilesWindow`
File management and preview window.

```python
def refresh_list(
    directory: str = None
) -> None:
    """Refresh file list view."""
```

**Example Usage:**
```python
from src.ui.view_files_window import ViewFilesWindow

# Create the view files window
view_files = ViewFilesWindow(parent=main_window)

# Refresh the file list with the default directory
view_files.refresh_list()

# Refresh with a specific directory
view_files.refresh_list(directory="C:/labels")
```

```python
def toggle_preview(
    state: bool
) -> None:
    """Toggle preview panel visibility."""
```

**Example Usage:**
```python
from src.ui.view_files_window import ViewFilesWindow

view_files = ViewFilesWindow(parent=main_window)

# Show the preview panel
view_files.toggle_preview(True)

# Hide the preview panel
view_files.toggle_preview(False)
```

## Utility Functions

### CSV Processing

```python
def process_csv(
    file_path: str,
    callback: Callable = None
) -> List[Dict]:
    """Process CSV file and return label data."""
```

**Example Usage:**
```python
from src.utils.csv_processor import process_csv

def update_progress(percent):
    print(f"Processing: {percent}% complete")

# Process a CSV file with progress updates
label_data = process_csv(
    file_path="C:/data/labels.csv",
    callback=update_progress
)

# Use the label data
for item in label_data:
    print(f"Product: {item['name']}, UPC: {item['upc']}")
```

### File Management

```python
def sanitize_filename(
    name: str
) -> str:
    """Clean filename for safe saving."""
```

**Example Usage:**
```python
from src.utils.file_utils import sanitize_filename

# Clean a filename with invalid characters
original_name = "Product: Sample/Test*Item?"
safe_name = sanitize_filename(original_name)
print(f"Safe filename: {safe_name}")  # "Product Sample-Test-Item"
```

```python
def get_unique_filename(
    base_name: str,
    directory: str
) -> str:
    """Generate unique filename in directory."""
```

**Example Usage:**
```python
from src.utils.file_utils import get_unique_filename

# Get a unique filename for a new label
base_name = "product_label"
directory = "C:/labels"
unique_name = get_unique_filename(base_name, directory)
print(f"Unique filename: {unique_name}")  # e.g., "product_label_001.png"
```

## Event System

### Custom Events

```python
class LabelEvent:
    """Base class for label-related events."""
    PREVIEW_UPDATED = "<<PreviewUpdated>>"
    SAVE_COMPLETED = "<<SaveCompleted>>"
    PRINT_STARTED = "<<PrintStarted>>"
    PRINT_COMPLETED = "<<PrintCompleted>>"
```

**Example Usage:**
```python
from src.events import LabelEvent
import tkinter as tk

# Create a widget that will respond to label events
widget = tk.Frame()

# Define an event handler
def on_preview_updated(event):
    print("Preview has been updated")

# Bind the event to the handler
widget.bind(LabelEvent.PREVIEW_UPDATED, on_preview_updated)

# Generate the event
widget.event_generate(LabelEvent.PREVIEW_UPDATED)
```

### Event Handlers

```python
def bind_label_events(
    widget: tk.Widget,
    events: List[str],
    callback: Callable
) -> None:
    """Bind label events to callback."""
```

**Example Usage:**
```python
from src.events import bind_label_events, LabelEvent

def handle_label_event(event):
    if event.type == LabelEvent.PREVIEW_UPDATED:
        print("Preview updated")
    elif event.type == LabelEvent.SAVE_COMPLETED:
        print("Save completed")

# Bind multiple events to a single handler
bind_label_events(
    widget=main_window,
    events=[LabelEvent.PREVIEW_UPDATED, LabelEvent.SAVE_COMPLETED],
    callback=handle_label_event
)
```

## Constants and Enums

### Window States
```python
class WindowState(Enum):
    NORMAL = "normal"
    MINIMIZED = "iconic"
    MAXIMIZED = "zoomed"
    HIDDEN = "withdrawn"
```

**Example Usage:**
```python
from src.constants import WindowState

# Set a window state
def set_window_state(window, state):
    if state == WindowState.NORMAL:
        window.deiconify()
    elif state == WindowState.MINIMIZED:
        window.iconify()
    elif state == WindowState.MAXIMIZED:
        window.state('zoomed')
    elif state == WindowState.HIDDEN:
        window.withdraw()

# Use the enum values
set_window_state(main_window, WindowState.NORMAL)
```

### Preview Sizes
```python
PREVIEW_SIZES = {
    3: (300, 155),
    4: (400, 207),
    5: (500, 259)
}
```

**Example Usage:**
```python
from src.constants import PREVIEW_SIZES

# Get dimensions for a specific preview size
size_level = 4
width, height = PREVIEW_SIZES[size_level]
print(f"Preview size {size_level}: {width}x{height}")

# Cycle through available sizes
current_size = 3
next_size = 4 if current_size == 3 else 5 if current_size == 4 else 3
```

## Error Handling

### Custom Exceptions
```python
class LabelMakerError(Exception):
    """Base exception for Label Maker."""
    pass

class ConfigError(LabelMakerError):
    """Configuration related errors."""
    pass

class BarcodeError(LabelMakerError):
    """Barcode generation errors."""
    pass
```

**Example Usage:**
```python
from src.exceptions import ConfigError, BarcodeError

# Using custom exceptions for better error handling
def load_settings():
    try:
        # Attempt to load configuration
        if not os.path.exists("settings.json"):
            raise ConfigError("Settings file not found")
        
        # Configuration loaded successfully
        return True
    except ConfigError as e:
        print(f"Configuration error: {e}")
        return False

def generate_barcode(upc):
    try:
        if len(upc) != 12:
            raise BarcodeError("UPC must be 12 digits")
        
        # Generate barcode
        return True
    except BarcodeError as e:
        print(f"Barcode error: {e}")
        return False
```

## Configuration Schema

### Settings Structure
```json
{
    "window_settings": {
        "font_size_large": int,
        "font_size_medium": int,
        "transparency_level": float,
        "always_on_top": boolean
    },
    "label_settings": {
        "barcode_width": int,
        "barcode_height": int,
        "DPI": int
    },
    "view_files_settings": {
        "mirror_print": boolean,
        "pin_window": boolean,
        "auto_switch": boolean,
        "print_minimize": boolean
    }
}
```

**Example Usage:**
```python
from src.config import ConfigManager
import json

# Create a default configuration
default_config = {
    "window_settings": {
        "font_size_large": 45,
        "font_size_medium": 45,
        "transparency_level": 0.9,
        "always_on_top": False
    },
    "label_settings": {
        "barcode_width": 600,
        "barcode_height": 310,
        "DPI": 300
    },
    "view_files_settings": {
        "mirror_print": False,
        "pin_window": False,
        "auto_switch": True,
        "print_minimize": False
    }
}

# Save the configuration to a file
with open("default_settings.json", "w") as f:
    json.dump(default_config, f, indent=2)

# Load and use the configuration
config_manager = ConfigManager()
config = config_manager.load_config()

# Access nested settings
font_size = config["window_settings"]["font_size_large"]
is_auto_switch = config["view_files_settings"]["auto_switch"]

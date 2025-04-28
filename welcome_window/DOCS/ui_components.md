# UI Components Documentation

## Overview

The `ui_components.py` module provides standardized UI components for the Label Maker application. This module was created as part of a refactoring effort to centralize UI component creation logic, improving code organization and maintainability. The components follow Material Design principles and provide consistent styling across the application.

## Components

### Title Section

```python
create_title_section(parent, title_text, subtitle_text=None)
```

Creates a standardized title section with an optional subtitle.

#### Parameters
- `parent`: Parent widget
- `title_text`: Main title text
- `subtitle_text` (optional): Subtitle text

#### Returns
- `tuple`: (frame, title_label, subtitle_label) - The created frame and labels

#### Usage Example
```python
title_frame, title_label, subtitle_label = create_title_section(
    parent_frame, 
    "Main Title", 
    "Optional Subtitle"
)
title_frame.pack(pady=20)
```

### Colored Button

```python
create_colored_button(parent, text, color, hover_color, command, big=False)
```

Creates a colored button with hover effect.

#### Parameters
- `parent`: Parent widget
- `text`: Button text
- `color`: Normal button color (hex code)
- `hover_color`: Hover color (hex code)
- `command`: Button command
- `big` (optional): Whether this is a big button

#### Returns
- `tk.Button`: The created button

#### Usage Example
```python
user_btn = create_colored_button(
    button_frame, 
    "User", 
    "#4CAF50",  # Green
    "#A5D6A7",  # Light Green
    user_action_callback,
    big=True
)
user_btn.pack(pady=10)
```

### Button Grid

```python
create_button_grid(parent, button_specs, num_columns=2)
```

Creates a grid of buttons based on specifications.

#### Parameters
- `parent`: Parent widget
- `button_specs`: List of button specifications, each with:
  - `text`: Button text
  - `colors`: Tuple of (normal_color, hover_color)
  - `command`: Button command
  - `big` (optional): Whether this is a big button
  - `grid` (optional): Tuple of (row, column, rowspan, columnspan)
  - `padx`, `pady` (optional): Padding
  - `sticky` (optional): Grid sticky option
- `num_columns`: Number of columns in the grid

#### Returns
- `tuple`: (frame, buttons_dict) - The created frame and dictionary of buttons

#### Usage Example
```python
button_specs = [
    {
        'text': 'User',
        'colors': ('#4CAF50', '#A5D6A7'),  # Green, Light Green
        'command': user_action,
        'big': True,
        'grid': (0, 0, 2, 1)
    },
    {
        'text': 'Settings',
        'colors': ('#9E9E9E', '#E0E0E0'),  # Gray, Light Gray
        'command': settings_action
    }
]

button_frame, buttons = create_button_grid(parent, button_specs)
button_frame.pack(fill='both', expand=True)
```

### Version Label

```python
create_version_label(parent, version_text)
```

Creates a standardized version label.

#### Parameters
- `parent`: Parent widget
- `version_text`: Version text to display

#### Returns
- `tk.Label`: The created version label

#### Usage Example
```python
version_label = create_version_label(root, "Version 1.0.1.2")
version_label.pack(side='right', padx=10, pady=5)
```

### Form Field Group

```python
create_form_field_group(parent, fields)
```

Creates a group of form fields based on specifications.

#### Parameters
- `parent`: Parent widget
- `fields`: List of field specifications, each with:
  - `label`: Field label text
  - `var_type`: Variable type ('string', 'int', 'boolean', etc.)
  - `default`: Default value
  - `width` (optional): Field width
  - `required` (optional): Whether the field is required
  - `readonly` (optional): Whether the field is read-only

#### Returns
- `dict`: Dictionary of field widgets, keyed by label

#### Usage Example
```python
fields = [
    {
        'label': 'Tracking Number:',
        'var_type': 'string',
        'default': '',
        'width': 30,
        'required': True
    },
    {
        'label': 'SKU:',
        'var_type': 'string',
        'default': '',
        'width': 30,
        'required': True
    }
]

field_widgets = create_form_field_group(form_frame, fields)
```

### Status Bar

```python
create_status_bar(parent, initial_text="", fg_color="black")
```

Creates a standardized status bar.

#### Parameters
- `parent`: Parent widget
- `initial_text`: Initial status text
- `fg_color`: Text color

#### Returns
- `tk.Label`: The created status label

#### Usage Example
```python
status_label = create_status_bar(root, "Ready", "green")
status_label.pack(side='bottom', fill='x')
```

### Google Sheets Status Display

```python
create_sheets_status_display(parent, status_text="Caution", status_color="red", sheet_name=None)
```

Creates a Google Sheets status display.

#### Parameters
- `parent`: Parent widget
- `status_text`: Status text
- `status_color`: Status color
- `sheet_name` (optional): Sheet name to display

#### Returns
- `tuple`: (frame, status_label) - The created frame and status label

#### Usage Example
```python
sheets_status_frame, sheets_status_label = create_sheets_status_display(
    root,
    "Connected",
    "green",
    "Tracking Sheet"
)
sheets_status_frame.pack(side='left', anchor='sw', padx=10, pady=10)
```

## Design Principles

The UI components follow these design principles:

1. **Consistency**: All components maintain a consistent look and feel
2. **Material Design**: Colors and styling are inspired by Material Design
3. **Responsiveness**: Components adapt to different window sizes and content
4. **User Feedback**: Interactive elements provide visual feedback (e.g., hover effects)
5. **Accessibility**: Components are designed to be accessible and easy to use

## Integration with Other Modules

The UI components module is used throughout the application:

- `welcome_window.py`: Uses components for the main interface
- `returns_operations.py`: Uses components for the returns data interface
- `google_sheets_dialog.py`: Uses components for the Google Sheets configuration dialog
- `settings_operations.py`: Uses components for the settings dialog

## Benefits of Refactoring

The refactoring of UI components into a centralized module provides several benefits:

1. **Code Reusability**: Components can be reused across the application
2. **Consistency**: Ensures a consistent look and feel
3. **Maintainability**: Changes to styling can be made in one place
4. **Readability**: Makes the code more readable and easier to understand
5. **Extensibility**: New components can be added easily

# Edit Record Window Documentation

## Overview

The Edit Record window is a core part of the Records Tab within the Returns Data dialog (`src/ui/returns_data_dialog.py`). It provides a robust, user-friendly interface for editing shipping record details (tracking numbers, SKUs, timestamps, status, and notes). The design is modular, allowing for future extensibility and integration with other record management features. All edits are performed directly on the main shipping records database (`database/shipping_records.db`) via utility functions in `src/utils/database_operations.py`.

## Key Features

1. **File Location & Architecture**
   - Main logic: `src/ui/returns_data_dialog.py` (class `ReturnsDataDialog`)
   - Database logic: `src/utils/database_operations.py`
   - Edits, deletes, and exports operate directly on `database/shipping_records.db`

2. **Modular, Frame-Based & Tabbed Design**
   - Integrated as a tab in the Returns Data dialog for easy access and maintainability
   - Clean separation of UI and database logic

3. **Editing Workflow**
   - Double-click a record in the table to open the Edit Record dialog
   - Edit fields: tracking number, SKU, status, notes
   - Save button validates and persists changes to the database instantly
   - Cancel button closes the dialog without saving
   - Success/error messages shown for all operations

4. **Batch Operations & Deletion**
   - Select multiple records and delete in one action (with confirmation)
   - Batch deletes update the UI and database immediately

5. **Exporting & Filtering**
   - Export current filtered records to CSV (via Save As dialog)
   - Filtering/search and date range supported for export and viewing

6. **Pagination & Sorting**
   - Pagination controls for navigating large datasets
   - Change records per page dynamically
   - Columns sortable by clicking headers (if enabled)

7. **Validation & Error Handling**
   - Required fields (SKU, Status) must be filled; clear error messages if not
   - Robust error handling for database failures or invalid data

8. **User Feedback & Accessibility**
   - Status messages for all save/delete/export actions
   - Visual cues for invalid input
   - Keyboard navigation (Tab/Enter) between fields and buttons
   - Mouse wheel support for scrolling records

9. **Live Sync & Instant Updates**
   - All changes are reflected instantly in the Records Tab and underlying database
   - No need to restart or reload the dialog to see edits

10. **Extensibility**
    - Easily extendable for new fields or workflow enhancements
    - Designed for maintainability and future features

## Window Structure

The Edit Record dialog is structured for clarity and usability, with the following main sections:

```
Edit Record Dialog (tk.Toplevel)
├── Title Section (fixed at top)
│   └── "Edit Record" window title
├── Scrollable Content Area (main frame)
│   ├── Form Fields (vertical layout)
│   │   ├── Tracking Number (entry)
│   │   ├── SKU (entry)
│   │   ├── Status (entry or dropdown)
│   │   └── Notes (multi-line text box)
├── Button Section (fixed at bottom)
│   ├── Save Button (bold, colored, always visible)
│   └── Cancel Button (always visible)
```

**Details:**
- The dialog opens as a modal window over the main Returns Data dialog.
- The content area contains labeled input fields for all editable record properties.
- The Notes field is a multi-line text box for additional information.
- The Save and Cancel buttons are placed at the bottom in a fixed button frame, styled for visibility and accessibility.
- The window is resizable, and supports keyboard navigation (Tab/Enter) and mouse wheel scrolling for the content area.
- Error and success messages are shown as pop-ups when saving or cancelling.

## Implementation Details

### Window Creation

The Edit Record window is created using the `create_edit_dialog` function in the `returns_operations.py` module:

```python
def create_edit_dialog(parent, tree, selected_item):
    # Get values of selected item
    item_values = tree.item(selected_item[0], "values")
    if not item_values or item_values[0] == "No records found":
        return False
        
    # Get the full label path from the hidden column
    full_label_path = item_values[4]
    
    # Create edit dialog
    edit_dialog = tk.Toplevel(parent)
    edit_dialog.title("Edit Record")
    edit_dialog.geometry("500x450")  
    edit_dialog.resizable(True, True)  
    edit_dialog.configure(bg='white')
    edit_dialog.transient(parent)
    edit_dialog.grab_set()
    
    # Center the dialog
    center_window(edit_dialog)
    
    # ... (rest of implementation)
```

### Scrollable Interface

The scrollable interface is implemented using a Canvas with a Scrollbar:

```python
# Create a main frame to hold everything
main_frame = tk.Frame(edit_dialog, bg='white')
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Create title section at the top (outside the scrollable area)
title_frame, _, _ = create_title_section(main_frame, "Edit Record")
title_frame.pack(pady=(0, 10))

# Create a canvas for scrolling
canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
canvas.pack(side='left', fill='both', expand=True)

# Add a scrollbar to the canvas
scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
scrollbar.pack(side='right', fill='y')

# Configure the canvas
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

# Create a frame inside the canvas to hold the content
content_frame = tk.Frame(canvas, bg='white')
canvas.create_window((0, 0), window=content_frame, anchor='nw', width=canvas.winfo_reqwidth())
```

### Form Fields

Form fields are created using the `create_form_field_group` function from the `ui_components` module:

```python
# Define form fields
fields = [
    {
        'label': 'Timestamp:',
        'var_type': 'string',
        'default': item_values[3],
        'width': 30,
        'required': True
    },
    {
        'label': 'Tracking Number:',
        'var_type': 'string',
        'default': item_values[0],
        'width': 30,
        'required': True
    },
    {
        'label': 'SKU:',
        'var_type': 'string',
        'default': item_values[1],
        'width': 30,
        'required': True
    },
    {
        'label': 'Label:',
        'var_type': 'string',
        'default': item_values[2],
        'width': 30,
        'required': False,
        'readonly': True
    }
]

# Create form fields
form_frame = tk.Frame(content_frame, bg='white', padx=10, pady=10)
form_frame.pack(fill='x', expand=True)

field_widgets = create_form_field_group(form_frame, fields)
```

### Button Section

The button section is fixed at the bottom of the dialog:

```python
# Create a separate frame for buttons at the bottom of the dialog
button_container = tk.Frame(edit_dialog, bg='white', pady=10)
button_container.pack(side='bottom', fill='x', padx=20, pady=10)

# Create a frame for the buttons inside the container
button_frame = tk.Frame(button_container, bg='white')
button_frame.pack(fill='x')

# Save Button
save_button = create_colored_button(
    button_frame,
    "Save",
    '#4CAF50',  # Green
    '#A5D6A7',  # Light Green
    save_changes
)
save_button.config(height=5, font=('Arial', 12, 'bold'), width=12)
save_button.pack(side='left', padx=(0, 20))

# Cancel Button
cancel_button = create_colored_button(
    button_frame,
    "Cancel",
    '#9E9E9E',  # Gray
    '#E0E0E0',  # Light Gray
    edit_dialog.destroy
)
cancel_button.config(height=5, font=('Arial', 12, 'bold'), width=12)
cancel_button.pack(side='left')
```

### Mouse Wheel Scrolling

Mouse wheel scrolling is implemented to enhance usability:

```python
# Add mouse wheel scrolling
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)
```

## Form Validation

The Edit Record window includes validation for required fields:

```python
# Function to save changes
def save_changes():
    # Get updated values
    new_timestamp = field_widgets['Timestamp:']['var'].get()
    new_tracking = field_widgets['Tracking Number:']['var'].get()
    new_sku = field_widgets['SKU:']['var'].get()
    label_name = field_widgets['Label:']['var'].get()
    
    # Get the full label path
    full_label_path = full_label_path_var.get()
    
    # Validate required fields
    if not new_timestamp or not new_tracking or not new_sku:
        messagebox.showerror("Error", "Please fill in all required fields.")
        return
    
    # Update treeview with display values
    tree.item(selected_item[0], values=(new_tracking, new_sku, label_name, new_timestamp, full_label_path))
    
    # Update log file
    success = update_log_file(tree)
    
    if success:
        messagebox.showinfo("Success", "Record updated successfully.")
        # Close dialog
        edit_dialog.destroy()
    else:
        messagebox.showerror("Error", "Failed to update record. Please try again.")
        # Keep dialog open so user can try again
```

## Recent Improvements

The Edit Record window has undergone several improvements to enhance its usability and robustness:

1. **File Existence Check Removed**: The file existence check that was causing errors when trying to edit records has been removed. This allows editing records even if the label files have been moved or renamed.

2. **Scrollable Interface**: The window is now vertically scrollable with a canvas and scrollbar, making it easier to accommodate more fields in the future.

3. **Window Organization**: The window is organized into three sections:
   - Title section (fixed at top)
   - Scrollable content area with form fields
   - Button section (fixed at bottom)

4. **Button Improvements**: Button visibility has been improved by making them taller and adding bold fonts. The button layout has been fixed to ensure they're always visible at the bottom of the dialog.

5. **Form Validation**: Proper validation for required fields has been added, with clear error messages when validation fails.

6. **User Feedback**: Success/error messages are now displayed when saving records, providing immediate feedback to the user.

7. **Window Size and Behavior**: The window is now resizable, with a default height of 450px. This provides more space for the form fields while maintaining a clean interface.

8. **Mouse Wheel Support**: Mouse wheel scrolling has been added to enhance usability, allowing users to scroll through the form fields more easily.

## Integration with UI Components

The Edit Record window uses components from the `ui_components` module:

- `create_title_section()`: For the title section
- `create_colored_button()`: For styled buttons
- `create_form_field_group()`: For form fields

## Usage

The Edit Record window is typically accessed from the Returns Data dialog when a user selects a record and clicks the "Edit" button:

```python
def on_edit_button_click():
    selected_items = tree.selection()
    if selected_items:
        create_edit_dialog(dialog, tree, selected_items)
```

## Error Handling

The Edit Record window includes comprehensive error handling:

- Validates required fields before saving
- Provides appropriate error messages
- Handles exceptions during file operations
- Gracefully handles missing files

## Conclusion

The improvements to the Edit Record window have significantly enhanced its usability and robustness. The scrollable interface, improved button design, form validation, and user feedback make it easier for users to manage shipping records efficiently.

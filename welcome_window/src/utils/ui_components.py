"""
UI Components module for standardizing UI element creation across the application.
This module provides functions for creating common UI elements like title sections,
buttons, button grids, and status displays.
"""
import tkinter as tk
from tkinter import ttk

def create_title_section(parent, title_text, subtitle_text=None):
    """
    Create a standardized title section with optional subtitle.
    
    Args:
        parent: Parent widget
        title_text (str): Main title text
        subtitle_text (str, optional): Subtitle text
        
    Returns:
        tuple: (frame, title_label, subtitle_label) - The created frame and labels
    """
    # Create frame
    title_frame = tk.Frame(parent, bg='white')
    
    # Create title label
    title_label = tk.Label(
        title_frame, 
        text=title_text, 
        font=("Arial", 16, "bold"), 
        bg='white'
    )
    title_label.pack()
    
    # Create subtitle label if provided
    subtitle_label = None
    if subtitle_text:
        subtitle_label = tk.Label(
            title_frame, 
            text=subtitle_text, 
            font=("Arial", 14), 
            bg='white'
        )
        subtitle_label.pack()
    
    return title_frame, title_label, subtitle_label

def create_colored_button(parent, text, color, hover_color, command, big=False):
    """
    Create a colored button with hover effect.
    
    Args:
        parent: Parent widget
        text (str): Button text
        color (str): Normal button color (hex code)
        hover_color (str): Hover color (hex code)
        command: Button command
        big (bool): Whether this is a big button
        
    Returns:
        tk.Button: The created button
    """
    btn = tk.Button(
        parent, 
        text=text,
        font=('Arial', 18 if big else 12, 'bold' if big else 'normal'),
        fg='white',
        bg=color,
        activeforeground='black',
        activebackground='white',
        relief='flat',
        borderwidth=0,
        width=20 if big else 15,
        height=4 if big else 2,
        cursor='hand2',
        command=command
    )
    
    # Add hover effect with delay
    hover_timer = None
    
    def apply_hover():
        btn['bg'] = hover_color
        btn['fg'] = 'black'
    
    def remove_hover():
        btn['bg'] = color
        btn['fg'] = 'white'
    
    def on_enter(e):
        nonlocal hover_timer
        # Cancel any existing timer
        if hover_timer is not None:
            btn.after_cancel(hover_timer)
        # Start new timer for hover effect
        hover_timer = btn.after(25, apply_hover)  # 25ms delay
    
    def on_leave(e):
        nonlocal hover_timer
        # Cancel any pending hover effect
        if hover_timer is not None:
            btn.after_cancel(hover_timer)
            hover_timer = None
        remove_hover()
        
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

def create_button_grid(parent, button_specs, num_columns=2):
    """
    Create a grid of buttons based on specifications.
    
    Args:
        parent: Parent widget
        button_specs (list): List of button specifications, each with:
            - text: Button text
            - colors: Tuple of (normal_color, hover_color)
            - command: Button command
            - big: Whether this is a big button (optional)
            - grid: Tuple of (row, column, rowspan, columnspan) (optional)
            - padx, pady: Padding (optional)
            - sticky: Grid sticky option (optional)
        num_columns (int): Number of columns in the grid
        
    Returns:
        tuple: (frame, buttons_dict) - The created frame and dictionary of buttons
    """
    # Create frame
    button_frame = tk.Frame(parent, bg='white')
    
    # Configure grid
    for i in range(num_columns):
        button_frame.grid_columnconfigure(i, weight=1)
    
    # Create buttons
    buttons = {}
    
    for i, spec in enumerate(button_specs):
        # Extract button properties
        text = spec['text']
        colors = spec['colors']
        command = spec['command']
        big = spec.get('big', False)
        
        # Create button
        btn = create_colored_button(button_frame, text, colors[0], colors[1], command, big)
        
        # Store button in dictionary using lowercase text as key
        key = text.lower()
        buttons[key] = btn
        
        # Grid placement
        if 'grid' in spec:
            row, col, rowspan, columnspan = spec['grid']
            btn.grid(
                row=row, 
                column=col, 
                rowspan=rowspan, 
                columnspan=columnspan,
                padx=spec.get('padx', 5),
                pady=spec.get('pady', 5),
                sticky=spec.get('sticky', 'nsew')
            )
        else:
            # Default placement
            row = i // num_columns
            col = i % num_columns
            btn.grid(
                row=row, 
                column=col, 
                padx=spec.get('padx', 5),
                pady=spec.get('pady', 5),
                sticky=spec.get('sticky', 'nsew')
            )
    
    return button_frame, buttons

def create_version_label(parent, version_text):
    """
    Create a standardized version label.
    
    Args:
        parent: Parent widget
        version_text (str): Version text to display
        
    Returns:
        tk.Label: The created version label
    """
    version_label = tk.Label(
        parent,
        text=version_text,
        font=("Arial", 8),
        bg='white',
        fg='gray'
    )
    
    return version_label

def create_form_field_group(parent, fields):
    """
    Create a group of form fields based on specifications.
    
    Args:
        parent: Parent widget
        fields (list): List of field specifications, each with:
            - label: Field label text
            - var_type: Variable type ('string', 'int', 'boolean', etc.)
            - default: Default value
            - width: Entry width
            - required: Whether the field is required
            - readonly: Whether the field is read-only (optional)
            
    Returns:
        dict: Dictionary of field widgets and variables
    """
    field_widgets = {}
    
    for field in fields:
        # Extract field properties
        label_text = field['label']
        var_type = field['var_type']
        default = field.get('default', '')
        width = field.get('width', 30)
        required = field.get('required', False)
        readonly = field.get('readonly', False)
        
        # Create frame for this field
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(fill='x', pady=(0, 10))
        
        # Create label
        label = tk.Label(
            field_frame, 
            text=label_text, 
            font=("Arial", 10), 
            bg='white'
        )
        label.pack(anchor='w')
        
        # Create variable based on type
        var = None
        if var_type == 'string':
            var = tk.StringVar(value=default)
        elif var_type == 'int':
            var = tk.IntVar(value=default)
        elif var_type == 'boolean':
            var = tk.BooleanVar(value=default)
        else:
            var = tk.StringVar(value=default)
        
        # Create widget based on type
        widget = None
        if var_type == 'boolean':
            widget = tk.Checkbutton(
                field_frame,
                variable=var,
                bg='white'
            )
        else:
            widget = tk.Entry(
                field_frame, 
                textvariable=var, 
                font=("Arial", 10), 
                width=width
            )
            
            # Set readonly state if specified
            if readonly:
                widget.config(state='readonly')
        
        widget.pack(fill='x', pady=(5, 0))
        
        # Store widgets and variables
        field_widgets[label_text] = {
            'frame': field_frame,
            'label': label,
            'widget': widget,
            'var': var,
            'required': required
        }
    
    return field_widgets

def create_status_bar(parent, initial_text="", fg_color="black"):
    """
    Create a standardized status bar.
    
    Args:
        parent: Parent widget
        initial_text (str): Initial status text
        fg_color (str): Text color
        
    Returns:
        tk.Label: The created status label
    """
    status_frame = tk.Frame(parent, bg='white')
    status_frame.pack(fill='x', pady=(10, 0))
    
    status_label = tk.Label(
        status_frame, 
        text=initial_text, 
        font=("Arial", 10), 
        bg='white',
        fg=fg_color,
        anchor='w'
    )
    status_label.pack(fill='x')
    
    return status_frame, status_label

def create_sheets_status_display(parent, status_text="Not Connected", status_color="red", sheet_name=None):
    """
    Create a Google Sheets status display.
    
    Args:
        parent: Parent widget
        status_text (str): Status text
        status_color (str): Status color
        sheet_name (str, optional): Sheet name to display
        
    Returns:
        tuple: (frame, status_label) - The created frame and status label
    """
    # Create frame
    status_frame = tk.Frame(parent, bg='white')
    
    # Create status label
    status_label = tk.Label(
        status_frame,
        text=status_text,
        font=("Arial", 8),
        bg='white',
        fg=status_color
    )
    status_label.pack(side='left')
    
    # Add sheet name if provided
    sheet_name_label = None
    if sheet_name:
        sheet_name_label = tk.Label(
            status_frame,
            text=f" | {sheet_name}",
            font=("Arial", 8, "italic"),
            bg='white'
        )
        sheet_name_label.pack(side='left')
    
    return status_frame, status_label

"""
Text context menu utilities for the Label Maker application.
Provides right-click context menus for text widgets with copy, paste, and select all functionality.
"""

import tkinter as tk
import platform

def add_context_menu(entry_widget):
    """
    Add a right-click context menu to a text entry widget.
    
    Args:
        entry_widget: A tkinter Entry, Text, or similar widget
        
    The menu includes:
    - Copy
    - Paste
    - Select All
    """
    context_menu = tk.Menu(entry_widget, tearoff=0)
    
    # Add menu items
    context_menu.add_command(label="Copy", command=lambda: copy_text(entry_widget))
    context_menu.add_command(label="Paste", command=lambda: paste_text(entry_widget))
    context_menu.add_separator()
    context_menu.add_command(label="Select All", command=lambda: select_all_text(entry_widget))
    
    # Bind right-click event
    if platform.system() == "Darwin":  # macOS
        entry_widget.bind("<Button-2>", lambda event: show_menu(event, context_menu))
    else:  # Windows, Linux
        entry_widget.bind("<Button-3>", lambda event: show_menu(event, context_menu))
    
    return context_menu

def show_menu(event, menu):
    """Show the context menu at the current mouse position."""
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        # Make sure to release the grab
        menu.grab_release()

def copy_text(widget):
    """Copy selected text to clipboard."""
    try:
        # Handle both Entry and Text widgets
        if isinstance(widget, tk.Entry) or hasattr(widget, 'selection_get'):
            widget.event_generate("<<Copy>>")
        # For custom widgets that might not have built-in copy
        elif hasattr(widget, 'get') and hasattr(widget, 'selection_present'):
            if widget.selection_present():
                selected_text = widget.selection_get()
                widget.clipboard_clear()
                widget.clipboard_append(selected_text)
    except tk.TclError:
        # No selection
        pass

def paste_text(widget):
    """Paste text from clipboard."""
    try:
        widget.event_generate("<<Paste>>")
    except:
        # Handle any paste errors
        pass

def select_all_text(widget):
    """Select all text in the widget."""
    try:
        # Handle Entry widget
        if isinstance(widget, tk.Entry):
            widget.select_range(0, tk.END)
            widget.icursor(tk.END)  # Set insert cursor to end
        # Handle Text widget
        elif isinstance(widget, tk.Text):
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, tk.END)
            widget.see(tk.INSERT)
        # Handle other widgets with select_range method
        elif hasattr(widget, 'select_range'):
            widget.select_range(0, tk.END)
            if hasattr(widget, 'icursor'):
                widget.icursor(tk.END)
    except:
        # Handle any selection errors
        pass

"""
Macro Editor Dialog for editing automation macros.
This module provides a dialog for editing macros defined in the macros.json file.
"""
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.macro_manager import macro_manager

# Configure logging
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(logs_dir, 'label_maker.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set up logging
logger = logging.getLogger(__name__)

class MacroEditorDialog(tk.Toplevel):
    """Dialog for editing automation macros."""
    
    def __init__(self, parent):
        """
        Initialize the macro editor dialog.
        
        Args:
            parent: The parent window
        """
        super().__init__(parent)
        self.title("Macro Editor")
        self.geometry("800x600")
        self.minsize(600, 400)
        self.transient(parent)  # Set to be on top of the parent window
        self.grab_set()  # Modal dialog
        
        # Center the dialog on the parent window
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"+{x}+{y}")
        
        # Create the UI
        self._create_ui()
        
        # Load the macros
        self._load_macros()
        
        # Set up the protocol for when the window is closed
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        logger.info("MacroEditorDialog initialized")
    
    def _create_ui(self):
        """Create the user interface elements."""
        # Create a main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the macro list
        list_frame = ttk.LabelFrame(main_frame, text="Macros", padding=5)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Create a listbox for the macros
        self.macro_listbox = tk.Listbox(list_frame, width=20, exportselection=0)
        self.macro_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        # Add a scrollbar to the listbox
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.macro_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.macro_listbox.config(yscrollcommand=list_scrollbar.set)
        
        # Bind the listbox selection event
        self.macro_listbox.bind('<<ListboxSelect>>', self._on_macro_selected)
        
        # Create a frame for the macro details
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create a frame for the macro name and description
        name_frame = ttk.Frame(details_frame)
        name_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Create a label and entry for the macro name
        ttk.Label(name_frame, text="Name:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=30)
        self.name_entry.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        # Create a label and entry for the macro description
        ttk.Label(name_frame, text="Description:").pack(side=tk.LEFT)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(name_frame, textvariable=self.description_var, width=50)
        self.description_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Create a label for the sequence editor
        ttk.Label(details_frame, text="Sequence:").pack(anchor=tk.W)
        
        # Create a text editor for the sequence
        sequence_frame = ttk.LabelFrame(details_frame, text="Sequence", padding=5)
        sequence_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.sequence_editor = scrolledtext.ScrolledText(sequence_frame, wrap=tk.WORD, width=60, height=20)
        self.sequence_editor.pack(fill=tk.BOTH, expand=True)
        
        # Bind right-click event to the sequence editor
        self.sequence_editor.bind("<Button-3>", self._show_context_menu)
        
        # Create a help text label
        help_text = (
            "Format: Each line represents one action in the sequence.\n"
            "Syntax: action [count] [value]\n"
            "Examples:\n"
            "  tab 1       - Press Tab key once\n"
            "  enter 2     - Press Enter key twice\n"
            "  up 3        - Press Up arrow key three times\n"
            "  down 1      - Press Down arrow key once\n"
            "  paste       - Paste tracking number from clipboard\n"
            "  paste_sku   - Paste SKU from clipboard\n"
            "  paste_order - Paste order reference from clipboard\n"
            "  text N/A    - Type the text 'N/A'\n"
            "  wait 2      - Wait for 2 seconds\n"
            "  delete      - Press Delete key"
        )
        help_label = ttk.Label(details_frame, text=help_text, justify=tk.LEFT, background="#f0f0f0", padding=5)
        help_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create a frame for the buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill=tk.X)
        
        # Create the buttons
        ttk.Button(button_frame, text="New", command=self._on_new).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Save", command=self._on_save).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete", command=self._on_delete).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", command=self._on_close).pack(side=tk.RIGHT)
    
    def _load_macros(self):
        """Load the macros into the listbox."""
        # Clear the listbox
        self.macro_listbox.delete(0, tk.END)
        
        # Get the list of macros
        macro_list = macro_manager.list_macros()
        
        # Create a dictionary to map display names to macro names
        self.display_to_macro_map = {}
        
        # Add the macros to the listbox
        for macro_name in sorted(macro_list):
            # Get the display name from the macro
            macro = macro_manager.get_macro(macro_name)
            display_name = macro.get('name', macro_name)
            
            # Add to the listbox
            self.macro_listbox.insert(tk.END, display_name)
            
            # Store the mapping between display name and macro name
            self.display_to_macro_map[display_name] = macro_name
        
        # Select the first macro if available
        if self.macro_listbox.size() > 0:
            self.macro_listbox.selection_set(0)
            self._on_macro_selected(None)
    
    def _on_macro_selected(self, event):
        """
        Handle macro selection in the listbox.
        
        Args:
            event: The event object
        """
        # Get the selected index
        selection = self.macro_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        
        # Get the macro name from the item attribute
        macro_name = self.macro_listbox.itemcget(index, 'macro_name')
        if not macro_name:
            # Fall back to the display name
            macro_name = self.macro_listbox.get(index).lower().replace(' ', '_')
        
        # Get the macro
        macro = macro_manager.get_macro(macro_name)
        if not macro:
            return
        
        # Update the name and description
        self.name_var.set(macro.get('name', ''))
        self.description_var.set(macro.get('description', ''))
        
        # Update the sequence editor
        sequence = macro.get('sequence', [])
        sequence_text = self._format_sequence_for_display(sequence)
        self.sequence_editor.delete(1.0, tk.END)
        self.sequence_editor.insert(tk.END, sequence_text)
    
    def _format_sequence_for_display(self, sequence):
        """
        Format a sequence for display in the text editor.
        
        Args:
            sequence: The sequence to format
            
        Returns:
            str: The formatted sequence
        """
        lines = []
        
        for action in sequence:
            action_type = action.get('action', '')
            count = action.get('count', 1)
            value = action.get('value', '')
            
            if action_type in ['tab', 'enter', 'up', 'down', 'delete']:
                lines.append(f"{action_type} {count}")
            elif action_type in ['paste', 'paste_sku', 'paste_order', 'paste_container']:
                lines.append(action_type)
            elif action_type == 'text':
                lines.append(f"{action_type} {value}")
            elif action_type == 'wait':
                seconds = action.get('seconds', 1)
                lines.append(f"{action_type} {seconds}")
            else:
                lines.append(f"{action_type} {count} {value}")
        
        return '\n'.join(lines)
    
    def _parse_sequence_from_text(self, text):
        """
        Parse a sequence from text.
        
        Args:
            text: The text to parse
            
        Returns:
            list: The parsed sequence
        """
        sequence = []
        
        # Split the text into lines
        lines = text.strip().split('\n')
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Split the line into parts
            parts = line.strip().split()
            
            if not parts:
                continue
            
            action_type = parts[0].lower()
            
            if action_type in ['tab', 'enter', 'up', 'down', 'delete']:
                count = int(parts[1]) if len(parts) > 1 else 1
                sequence.append({
                    'action': action_type,
                    'count': count
                })
            elif action_type in ['paste', 'paste_sku', 'paste_order', 'paste_container']:
                sequence.append({
                    'action': action_type
                })
            elif action_type == 'text':
                value = ' '.join(parts[1:]) if len(parts) > 1 else ''
                sequence.append({
                    'action': action_type,
                    'value': value
                })
            elif action_type == 'wait':
                seconds = float(parts[1]) if len(parts) > 1 else 1
                sequence.append({
                    'action': action_type,
                    'seconds': seconds
                })
            else:
                # Unknown action type, add it anyway
                count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                value = ' '.join(parts[2:]) if len(parts) > 2 else ''
                sequence.append({
                    'action': action_type,
                    'count': count,
                    'value': value
                })
        
        return sequence
    
    def _on_new(self):
        """Handle the New button click."""
        # Clear the fields
        self.name_var.set('')
        self.description_var.set('')
        self.sequence_editor.delete(1.0, tk.END)
        
        # Set focus to the name entry
        self.name_entry.focus_set()
    
    def _on_save(self):
        """Handle the Save button click."""
        # Get the values
        name = self.name_var.get().strip()
        description = self.description_var.get().strip()
        sequence_text = self.sequence_editor.get(1.0, tk.END)
        
        # Validate the name
        if not name:
            messagebox.showerror("Error", "Please enter a name for the macro.")
            self.name_entry.focus_set()
            return
        
        # Parse the sequence
        try:
            sequence = self._parse_sequence_from_text(sequence_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing sequence: {str(e)}")
            self.sequence_editor.focus_set()
            return
        
        # Check if we're updating an existing macro or adding a new one
        selection = self.macro_listbox.curselection()
        if selection:
            # Get the macro name from the item attribute
            index = selection[0]
            macro_name = self.macro_listbox.itemcget(index, 'macro_name')
            if not macro_name:
                # Fall back to the display name
                macro_name = self.macro_listbox.get(index).lower().replace(' ', '_')
            
            # Update the macro
            success = macro_manager.update_macro(macro_name, description, sequence)
            if success:
                messagebox.showinfo("Success", f"Macro '{name}' updated successfully.")
                # Reload the macros
                self._load_macros()
            else:
                messagebox.showerror("Error", f"Error updating macro '{name}'.")
        else:
            # Add a new macro
            macro_name = name.lower().replace(' ', '_')
            success = macro_manager.add_macro(name, description, sequence)
            if success:
                messagebox.showinfo("Success", f"Macro '{name}' added successfully.")
                # Reload the macros
                self._load_macros()
                # Select the new macro
                for i in range(self.macro_listbox.size()):
                    if self.macro_listbox.itemcget(i, 'macro_name') == macro_name:
                        self.macro_listbox.selection_set(i)
                        self._on_macro_selected(None)
                        break
            else:
                messagebox.showerror("Error", f"Error adding macro '{name}'.")
    
    def _on_delete(self):
        """Handle the Delete button click."""
        # Get the selected macro
        selection = self.macro_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a macro to delete.")
            return
        
        index = selection[0]
        
        # Get the macro name from the item attribute
        macro_name = self.macro_listbox.itemcget(index, 'macro_name')
        if not macro_name:
            # Fall back to the display name
            macro_name = self.macro_listbox.get(index).lower().replace(' ', '_')
        
        # Get the display name
        display_name = self.macro_listbox.get(index)
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the macro '{display_name}'?"):
            return
        
        # Delete the macro
        success = macro_manager.delete_macro(macro_name)
        if success:
            messagebox.showinfo("Success", f"Macro '{display_name}' deleted successfully.")
            # Reload the macros
            self._load_macros()
        else:
            messagebox.showerror("Error", f"Error deleting macro '{display_name}'.")
    
    def _on_close(self):
        """Handle the Close button click."""
        # Release the grab and destroy the dialog
        self.grab_release()
        self.destroy()
        
    def _show_context_menu(self, event):
        """Show the context menu on right-click."""
        # Create a context menu
        context_menu = tk.Menu(self, tearoff=0)
        
        # Create submenus for different action types
        keyboard_menu = tk.Menu(context_menu, tearoff=0)
        clipboard_menu = tk.Menu(context_menu, tearoff=0)
        other_menu = tk.Menu(context_menu, tearoff=0)
        
        # Add keyboard actions
        for action in ["tab", "enter", "up", "down", "delete"]:
            keyboard_menu.add_command(
                label=action, 
                command=lambda a=action: self._insert_action_at_cursor(a, count=1)
            )
        
        # Add clipboard actions
        clipboard_menu.add_command(label="paste", command=lambda: self._insert_action_at_cursor("paste"))
        clipboard_menu.add_command(label="paste_sku", command=lambda: self._insert_action_at_cursor("paste_sku"))
        clipboard_menu.add_command(label="paste_order", command=lambda: self._insert_action_at_cursor("paste_order"))
        clipboard_menu.add_command(label="paste_container", command=lambda: self._insert_action_at_cursor("paste_container"))
        
        # Add other actions
        other_menu.add_command(label="text", command=lambda: self._insert_action_at_cursor("text", value=""))
        other_menu.add_command(label="wait", command=lambda: self._insert_action_at_cursor("wait", seconds=1))
        other_menu.add_command(label="open_tab", command=lambda: self._insert_action_at_cursor("open_tab"))
        other_menu.add_command(label="close_tab", command=lambda: self._insert_action_at_cursor("close_tab"))
        other_menu.add_command(label="enable_sku", command=lambda: self._insert_action_at_cursor("enable_sku"))
        
        # Add the submenus to the context menu
        context_menu.add_cascade(label="Insert Keyboard Action", menu=keyboard_menu)
        context_menu.add_cascade(label="Insert Clipboard Action", menu=clipboard_menu)
        context_menu.add_cascade(label="Insert Other Action", menu=other_menu)
        
        # Display the menu at the event position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Make sure to release the grab
            context_menu.grab_release()
            
    def _insert_action_at_cursor(self, action_type, **kwargs):
        """Insert an action at the current cursor position."""
        # Format the action based on its type and parameters
        if action_type in ["tab", "enter", "up", "down", "delete"]:
            count = kwargs.get("count", 1)
            action_text = f"{action_type} {count}\n"
        elif action_type == "text":
            value = kwargs.get("value", "")
            action_text = f"{action_type} {value}\n"
        elif action_type == "wait":
            seconds = kwargs.get("seconds", 1)
            action_text = f"{action_type} {seconds}\n"
        else:
            # Simple action with no parameters
            action_text = f"{action_type}\n"
        
        # Get current cursor position
        current_pos = self.sequence_editor.index(tk.INSERT)
        
        # Insert the action at the cursor position
        self.sequence_editor.insert(current_pos, action_text)
        
        # Highlight the inserted text temporarily
        line_start = self.sequence_editor.index(f"{current_pos} linestart")
        line_end = self.sequence_editor.index(f"{current_pos} + 1 lines linestart")
        
        # Configure a tag for highlighting
        self.sequence_editor.tag_configure("highlight", background="#e6ffe6")
        self.sequence_editor.tag_add("highlight", line_start, line_end)
        
        # Schedule the highlight to be removed after 2 seconds
        self.after(2000, lambda: self.sequence_editor.tag_remove("highlight", "1.0", tk.END))


def create_macro_editor_dialog(parent):
    """
    Create and show the macro editor dialog.
    
    Args:
        parent: The parent window
    """
    dialog = MacroEditorDialog(parent)
    return dialog

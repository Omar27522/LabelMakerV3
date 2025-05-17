"""
Enhanced Macro Editor Dialog for editing automation macros.
This module provides an intuitive dialog for editing macros defined in the macros.json file.
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
from src.ui.action_editor_frame import ActionEditorFrame

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

class MacroEditorEnhanced(tk.Toplevel):
    """Enhanced dialog for editing automation macros."""
    
    def __init__(self, parent):
        """
        Initialize the macro editor dialog.
        
        Args:
            parent: The parent window
        """
        super().__init__(parent)
        self.title("Macro Editor")
        self.geometry("1200x800")  # Set a fixed size for better layout
        self.minsize(1000, 700)  # Ensure minimum size
        self.transient(parent)  # Set to be on top of the parent window
        self.grab_set()  # Modal dialog
        
        # Initialize the mapping between display names and macro names
        self.display_to_macro_map = {}
        
        # Initialize the action editors list
        self.action_editors = []
        
        # Initialize the selected macro ID
        self.selected_macro_id = None
        
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
        
        logger.info("MacroEditorEnhanced initialized")
    
    def _create_ui(self):
        """Create the user interface elements."""
        # Configure style for better appearance
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("TLabelframe.Label", font=("Arial", 10, "bold"))
        self.style.configure("Action.TFrame", background="#f0f0f0", relief="raised")
        self.style.configure("NewAction.TFrame", background="#e6ffe6", relief="raised")  # Light green background for new actions
        self.style.configure("Header.TLabel", font=("Arial", 10, "bold"))
        self.style.configure("ActionNumber.TLabel", font=("Arial", 10, "bold"), foreground="#555555")
        
        # Create a main frame with padding that fills the entire window
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a paned window to allow resizing between sections
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the macro list with a clear title
        list_frame = ttk.LabelFrame(paned_window, text="Macro Library", padding=10)
        
        # Create buttons for macro management at the top of the list
        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(list_buttons_frame, text="New Macro", command=self._on_new).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_buttons_frame, text="Delete", command=self._on_delete).pack(side=tk.RIGHT, padx=2)
        
        # Create a listbox for the macros with better styling
        self.macro_listbox = tk.Listbox(
            list_frame, 
            width=25, 
            exportselection=0, 
            font=("Arial", 11),
            activestyle="dotbox",
            selectbackground="#0078D7",
            selectforeground="white",
            relief="flat",
            bd=1
        )
        self.macro_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add a scrollbar to the listbox
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.macro_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.macro_listbox.config(yscrollcommand=list_scrollbar.set)
        
        # Bind the listbox selection event
        self.macro_listbox.bind('<<ListboxSelect>>', self._on_macro_selected)
        
        # Add the list frame to the paned window
        paned_window.add(list_frame, weight=1)
        
        # Create a frame for the macro details
        details_frame = ttk.Frame(paned_window)
        
        # Create a frame for the macro name and description
        name_frame = ttk.LabelFrame(details_frame, text="Macro Properties", padding=10)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create a grid for the name and description
        name_grid = ttk.Frame(name_frame)
        name_grid.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a label and entry for the macro name
        ttk.Label(name_grid, text="Name:", style="Header.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(name_grid, textvariable=self.name_var, width=30, font=("Arial", 11))
        self.name_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Create a label and entry for the macro description
        ttk.Label(name_grid, text="Description:", style="Header.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(name_grid, textvariable=self.description_var, width=50, font=("Arial", 11))
        self.description_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Configure the grid
        name_grid.columnconfigure(1, weight=1)
        
        # Create a frame for the sequence editor with a clear title
        sequence_frame = ttk.LabelFrame(details_frame, text="Action Sequence", padding=10)
        sequence_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create a header for the action list
        header_frame = ttk.Frame(sequence_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(header_frame, text="#", width=3, style="Header.TLabel").pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(header_frame, text="Action Type", width=15, style="Header.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(header_frame, text="Parameters", width=20, style="Header.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(header_frame, text="Description", width=30, style="Header.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        
        # Create a frame for the action editors with fixed height
        self.actions_frame = ttk.Frame(sequence_frame, height=300)
        self.actions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.actions_frame.pack_propagate(False)  # Prevent the frame from resizing to fit its contents
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.actions_frame, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.actions_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Set a fixed width for the canvas window to prevent horizontal expansion
        canvas_width = 750  # Adjust this value as needed
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=canvas_width)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a frame for the action buttons
        action_buttons_frame = ttk.Frame(sequence_frame)
        action_buttons_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Create the add action button with a plus icon
        add_action_button = ttk.Button(
            action_buttons_frame, 
            text="Add New Action", 
            command=self._on_add_action
        )
        add_action_button.pack(side=tk.LEFT)
        
        # Add a button to test the macro
        test_button = ttk.Button(
            action_buttons_frame, 
            text="Test Sequence", 
            command=self._on_test_macro
        )
        test_button.pack(side=tk.RIGHT)
        
        # Create a help text frame with fixed height
        help_frame = ttk.LabelFrame(details_frame, text="Quick Reference", padding=10, height=150)
        help_frame.pack(fill=tk.X, pady=(0, 10))
        help_frame.pack_propagate(False)  # Prevent the frame from resizing to fit its contents
        
        # Create a help text with better formatting
        help_text = (
            "Keyboard Actions: tab, enter, up, down, delete - Press keyboard keys (with repeat count)\n\n"
            "Clipboard Actions:\n"
            "• paste - Insert TRACKING NUMBER from clipboard\n"
            "• paste_sku - Insert SKU from clipboard\n"
            "• paste_order - Insert ORDER REFERENCE NUMBER from clipboard\n"
            "• paste_container - Insert CONTAINER CARD from clipboard\n\n"
            "Other Actions: text - Type specific text | wait - Pause for specified seconds | "
            "open_tab, close_tab - Control browser tabs | enable_sku - Enable SKU input field"
        )
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT, font=("Arial", 10), wraplength=750)
        help_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for the main buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Create the buttons with better styling
        save_button = ttk.Button(button_frame, text="Save Changes", command=self._on_save)
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        close_button = ttk.Button(button_frame, text="Close Editor", command=self._on_close)
        close_button.pack(side=tk.RIGHT)
        
        # Add the details frame to the paned window with more weight
        paned_window.add(details_frame, weight=3)
    
    def _load_macros(self):
        """Load the macros into the listbox."""
        # Clear the listbox
        self.macro_listbox.delete(0, tk.END)
        
        # Clear the mapping
        self.display_to_macro_map = {}
        
        # Get the list of macros
        macro_list = macro_manager.list_macros()
        logger.info(f"Found {len(macro_list)} macros")
        
        # Add the macros to the listbox
        for macro_name in sorted(macro_list):
            # Get the display name from the macro
            macro = macro_manager.get_macro(macro_name)
            display_name = macro.get('name', macro_name)
            
            # Add to the listbox
            self.macro_listbox.insert(tk.END, display_name)
            
            # Store the mapping between display name and macro name
            self.display_to_macro_map[display_name] = macro_name
            
            # Log the macro and its action count
            sequence = macro.get('sequence', [])
            logger.info(f"Macro '{display_name}' has {len(sequence)} actions")
        
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
        
        # Get the display name from the listbox
        display_name = self.macro_listbox.get(index)
        logger.info(f"Selected macro: {display_name}")
        
        # Get the macro name from our mapping
        macro_name = self.display_to_macro_map.get(display_name)
        if not macro_name:
            # Fall back to converting the display name if mapping fails
            macro_name = display_name.lower().replace(' ', '_')
        
        # Get the macro
        macro = macro_manager.get_macro(macro_name)
        if not macro:
            logger.error(f"Macro '{macro_name}' not found")
            return
            
        # Store the selected macro ID
        self.selected_macro_id = macro_name
        
        # Update the name and description
        self.name_var.set(macro.get('name', ''))
        self.description_var.set(macro.get('description', ''))
        
        # Get the sequence of actions
        sequence = macro.get('sequence', [])
        logger.info(f"Macro '{macro_name}' has {len(sequence)} actions")
        
        # Update the action editors
        self._load_actions(sequence)
    
    def _load_actions(self, actions):
        """
        Load the actions into the editor.
        
        Args:
            actions: List of action dictionaries
        """
        # Clear existing action editors
        self._clear_action_editors()
        
        # Log the number of actions to load
        logger.info(f"Loading {len(actions)} actions")
        
        # Create new action editors
        for i, action in enumerate(actions):
            self._add_action_editor(action, action_number=i+1)
            
        # Log the number of action editors created
        logger.info(f"Created {len(self.action_editors)} action editors")
        
        # Update the canvas scroll region to ensure all actions are visible
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Ensure the scrollable frame has a fixed width to prevent horizontal expansion
        self.scrollable_frame.update_idletasks()
        width = self.canvas.winfo_width()
        if width > 10:  # Ensure we have a reasonable width
            self.scrollable_frame.configure(width=width)
    
    def _clear_action_editors(self):
        """Clear all action editors."""
        # Log the number of widgets being cleared
        logger.info(f"Clearing {len(self.scrollable_frame.winfo_children())} action editors")
        
        # Destroy all widgets in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Reset the action editors list
        self.action_editors = []
        
        # Update the canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _add_action_editor(self, action=None, action_number=None, is_new=False, insert_after=None):
        """
        Add a new action editor.
        
        Args:
            action: The action to edit (dict)
            action_number: The number to display for this action (int)
            is_new: Whether this is a newly created action (for highlighting)
            insert_after: The action editor to insert after (or None to append)
        """
        # Create a new action editor
        action_editor = ActionEditorFrame(
            self.scrollable_frame,
            action=action,
            on_update=self._on_action_updated,
            on_delete=self._on_action_deleted,
            on_move_up=self._on_action_move_up,
            on_move_down=self._on_action_move_down,
            on_insert_after=self._on_insert_action_after,
            is_new=is_new
        )
        
        # If we're inserting after a specific editor, find its position
        if insert_after is not None and insert_after in self.action_editors:
            # Find the index of the action to insert after
            index = self.action_editors.index(insert_after)
            # Insert the new action editor at the next position
            self.action_editors.insert(index + 1, action_editor)
            # Repack all action editors to update the UI
            self._repack_action_editors()
        else:
            # Just append to the end and pack normally
            action_editor.pack(fill=tk.X, pady=5, padx=5)
            # Add to the list of action editors
            self.action_editors.append(action_editor)
        
        # Set the action number if provided
        if action_number is not None:
            action_editor.number_label.configure(text=str(action_number))
        
        # Update the canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Ensure the scrollable frame width is maintained
        self.scrollable_frame.update_idletasks()
        
        # Return the action editor
        return action_editor
        
    def _on_insert_action_after(self, editor, action=None):
        """
        Handle inserting a new action after the specified editor.
        
        Args:
            editor: The action editor to insert after
            action: The specific action to insert (or None for default)
        """
        # Use the provided action or create a default one
        if action is None:
            # Default to tab action if none specified
            action = {'action': 'tab', 'count': 1}
        
        # Add a new action editor after the specified one
        new_editor = self._add_action_editor(action=action, is_new=True, insert_after=editor)
        
        # Scroll to make the new action visible
        self.canvas.update_idletasks()
        
        # Calculate the position to scroll to (to show the new action)
        if new_editor.winfo_y() > 0:
            # Get the position of the new editor relative to the canvas
            y_position = float(new_editor.winfo_y()) / self.scrollable_frame.winfo_height()
            # Scroll to show the new editor
            self.canvas.yview_moveto(y_position)
    
    def _on_action_updated(self, editor, action):
        """
        Handle action update.
        
        Args:
            editor: The action editor
            action: The updated action
        """
        # Nothing to do here, the action is already updated in the editor
        pass
    
    def _on_action_deleted(self, editor):
        """
        Handle action deletion.
        
        Args:
            editor: The action editor to delete
        """
        # Remove from the list of action editors
        if editor in self.action_editors:
            self.action_editors.remove(editor)
        
        # Destroy the editor
        editor.destroy()
        
        # Update the canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Ensure the scrollable frame width is maintained
        self.scrollable_frame.update_idletasks()
    
    def _on_action_move_up(self, editor):
        """
        Handle action move up.
        
        Args:
            editor: The action editor to move up
        """
        # Get the index of the editor
        index = self.action_editors.index(editor)
        
        # Check if it can be moved up
        if index > 0:
            # Swap with the previous editor
            self.action_editors[index], self.action_editors[index - 1] = self.action_editors[index - 1], self.action_editors[index]
            
            # Repack the editors
            self._repack_action_editors()
    
    def _on_action_move_down(self, editor):
        """
        Handle action move down.
        
        Args:
            editor: The action editor to move down
        """
        # Get the index of the editor
        index = self.action_editors.index(editor)
        
        # Check if it can be moved down
        if index < len(self.action_editors) - 1:
            # Swap with the next editor
            self.action_editors[index], self.action_editors[index + 1] = self.action_editors[index + 1], self.action_editors[index]
            
            # Repack the editors
            self._repack_action_editors()
    
    def _repack_action_editors(self):
        """Repack all action editors in the correct order."""
        # Unpack all action editors
        for editor in self.action_editors:
            editor.pack_forget()
        
        # Repack all action editors with updated numbers
        for i, editor in enumerate(self.action_editors):
            # Update the action number
            editor.number_label.configure(text=str(i+1))
            # Repack the editor
            editor.pack(fill=tk.X, pady=5, padx=5)
        
        # Update the canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Ensure the scrollable frame width is maintained
        self.scrollable_frame.update_idletasks()
        # Ensure the scrollable frame width is maintained
        self.scrollable_frame.update_idletasks()
        

    
    def _on_add_action(self):
        """Handle add action button click."""
        # Add a new action editor
        action_editor = self._add_action_editor()
        
        # Scroll to the bottom
        self.canvas.yview_moveto(1.0)
    
    def _on_new(self):
        """Handle the New button click."""
        # Clear the fields
        self.name_var.set('')
        self.description_var.set('')
        self._clear_action_editors()
        
        # Set focus to the name entry
        self.name_entry.focus_set()
    
    def _on_save(self):
        """Handle the Save button click."""
        # Get the values
        name = self.name_var.get().strip()
        description = self.description_var.get().strip()
        
        # Validate the name
        if not name:
            messagebox.showerror("Error", "Please enter a name for the macro.")
            self.name_entry.focus_set()
            return
        
        # Get the sequence from the action editors
        sequence = [editor.get_action() for editor in self.action_editors]
        
        # Check if we're updating an existing macro or adding a new one
        selection = self.macro_listbox.curselection()
        if selection:
            # Get the display name from the listbox
            index = selection[0]
            display_name = self.macro_listbox.get(index)
            
            # Get the macro name from our mapping
            macro_name = self.display_to_macro_map.get(display_name)
            if not macro_name:
                # Fall back to converting the display name if mapping fails
                macro_name = display_name.lower().replace(' ', '_')
            
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
            success = macro_manager.add_macro(name, description, sequence)
            if success:
                messagebox.showinfo("Success", f"Macro '{name}' added successfully.")
                # Reload the macros
                self._load_macros()
                
                # Find and select the new macro
                macro_name = name.lower().replace(' ', '_')
                for i in range(self.macro_listbox.size()):
                    if self.macro_listbox.get(i) == name:
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
        
        # Get the display name from the listbox
        display_name = self.macro_listbox.get(index)
        
        # Get the macro name from our mapping
        macro_name = self.display_to_macro_map.get(display_name)
        if not macro_name:
            # Fall back to converting the display name if mapping fails
            macro_name = display_name.lower().replace(' ', '_')
        
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
    
    def _on_test_macro(self):
        """Test the current macro sequence."""
        # Check if there's a macro selected
        if not self.selected_macro_id:
            messagebox.showinfo("Test Macro", "Please select a macro to test.")
            return
            
        # Get the current sequence from the action editors
        sequence = []
        for editor in self.action_editors:
            action = editor.get_action()
            if action:
                sequence.append(action)
                
        if not sequence:
            messagebox.showinfo("Test Macro", "This macro has no actions to test.")
            return
            
        # Ask for confirmation
        if not messagebox.askyesno("Test Macro", "This will execute the macro sequence. Continue?"):
            return
            
        # Create a temporary macro
        temp_macro = {
            "id": "temp_test_macro",
            "name": f"Test: {self.name_var.get()}",
            "description": "Temporary test macro",
            "sequence": sequence
        }
        
        # Execute the macro
        try:
            # Hide the dialog temporarily
            self.withdraw()
            messagebox.showinfo("Test Macro", "The macro will start in 3 seconds. Position your cursor where needed.")
            
            # Import and use the macro executor
            from src.utils.macro_executor import MacroExecutor
            executor = MacroExecutor()
            
            # Wait 3 seconds before starting
            import time
            time.sleep(3)
            
            # Execute the macro
            executor.execute_macro(temp_macro)
            
            # Show the dialog again
            self.deiconify()
            messagebox.showinfo("Test Complete", "Macro test completed successfully.")
        except Exception as e:
            # Show the dialog again
            self.deiconify()
            messagebox.showerror("Test Error", f"Error executing macro: {str(e)}")
            logger.error(f"Error testing macro: {e}", exc_info=True)
    
    def _on_close(self):
        """Handle the Close button click."""
        # Release the grab and destroy the dialog
        self.grab_release()
        self.destroy()


def create_macro_editor_enhanced(parent):
    """
    Create and show the enhanced macro editor dialog.
    
    Args:
        parent: The parent window
    """
    dialog = MacroEditorEnhanced(parent)
    return dialog

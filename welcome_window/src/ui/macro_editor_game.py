"""
Game-like Macro Editor for creating fun, interactive automation sequences.
This module provides a visual, drag-and-drop interface for editing macros.
"""
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from PIL import Image, ImageTk

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.macro_manager import macro_manager
import logging

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

# Define action icons and colors
ACTION_ICONS = {
    "tab": "⇥",
    "enter": "↵",
    "up": "↑",
    "down": "↓",
    "delete": "⌫",
    "paste": "📋",
    "paste_sku": "📦",
    "paste_order": "🧾",
    "paste_container": "📦",
    "text": "🔤",
    "wait": "⏱️",
    "open_tab": "📂",
    "close_tab": "❌",
    "enable_sku": "✅"
}

ACTION_COLORS = {
    "tab": "#FFD700",        # Gold
    "enter": "#FF6347",       # Tomato
    "up": "#98FB98",          # Pale Green
    "down": "#87CEFA",        # Light Sky Blue
    "delete": "#FF69B4",      # Hot Pink
    "paste": "#DDA0DD",       # Plum
    "paste_sku": "#20B2AA",   # Light Sea Green
    "paste_order": "#9370DB", # Medium Purple
    "paste_container": "#F0E68C", # Khaki
    "text": "#FFDAB9",        # Peach Puff
    "wait": "#D3D3D3",        # Light Gray
    "open_tab": "#90EE90",    # Light Green
    "close_tab": "#FFA07A",   # Light Salmon
    "enable_sku": "#ADD8E6"   # Light Blue
}

# Define action categories
ACTION_CATEGORIES = {
    "Keyboard Actions": ["tab", "enter", "up", "down", "delete"],
    "Clipboard Actions": ["paste", "paste_sku", "paste_order", "paste_container"],
    "Other Actions": ["text", "wait", "open_tab", "close_tab", "enable_sku"]
}

class ActionBlock(tk.Canvas):
    """Interactive block representing a single action in the sequence."""
    
    def __init__(self, parent, action_type, **kwargs):
        """
        Initialize an action block.
        
        Args:
            parent: The parent widget
            action_type: The type of action this block represents
            **kwargs: Additional parameters for the action
        """
        # Get the color for this action type
        bg_color = ACTION_COLORS.get(action_type, "#FFFFFF")
        
        # Create the canvas
        super().__init__(
            parent, 
            width=180, 
            height=60, 
            bg=bg_color, 
            highlightthickness=2,
            highlightbackground="#000000"
        )
        
        self.parent = parent
        self.action_type = action_type
        self.params = kwargs
        self.selected = False
        
        # Create the visual elements
        self._create_ui()
        
        # Bind events
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Double-Button-1>", self._on_double_click)
        
    def _create_ui(self):
        """Create the UI elements for this action block."""
        # Add the icon
        icon = ACTION_ICONS.get(self.action_type, "?")
        self.create_text(20, 30, text=icon, font=("Arial", 20), fill="#000000")
        
        # Add the action type
        self.create_text(100, 15, text=self.action_type, font=("Arial", 12, "bold"), fill="#000000")
        
        # Add the parameters based on action type
        if self.action_type in ["tab", "enter", "up", "down", "delete"]:
            count = self.params.get("count", 1)
            self.create_text(100, 40, text=f"Count: {count}", font=("Arial", 10), fill="#000000")
        elif self.action_type == "text":
            value = self.params.get("value", "")
            display_value = value if len(value) < 15 else value[:12] + "..."
            self.create_text(100, 40, text=f"Text: {display_value}", font=("Arial", 10), fill="#000000")
        elif self.action_type == "wait":
            seconds = self.params.get("seconds", 1)
            self.create_text(100, 40, text=f"Wait: {seconds}s", font=("Arial", 10), fill="#000000")
            
    def _on_click(self, event):
        """Handle click events."""
        # Select this block
        self.selected = True
        self.config(highlightbackground="#FF0000", highlightthickness=3)
        
        # Store the initial position for dragging
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
        # Bring to front
        self.lift()
        
        # Notify the parent
        if hasattr(self.parent, "on_action_selected"):
            self.parent.on_action_selected(self)
            
    def _on_drag(self, event):
        """Handle drag events."""
        if not self.selected:
            return
            
        # Calculate the movement
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        
        # Move the block
        self.move(tk.ALL, dx, dy)
        
        # Update the start position
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def _on_release(self, event):
        """Handle release events."""
        if not self.selected:
            return
            
        # Notify the parent
        if hasattr(self.parent, "on_action_moved"):
            self.parent.on_action_moved(self)
            
    def _on_double_click(self, event):
        """Handle double-click events."""
        # Open the edit dialog
        if hasattr(self.parent, "on_action_edit"):
            self.parent.on_action_edit(self)
            
    def deselect(self):
        """Deselect this block."""
        self.selected = False
        self.config(highlightbackground="#000000", highlightthickness=2)
        
    def get_action(self):
        """Get the action represented by this block."""
        action = {"action": self.action_type}
        action.update(self.params)
        return action
        
    def update_params(self, **kwargs):
        """Update the parameters for this action."""
        self.params.update(kwargs)
        
        # Redraw the UI
        self.delete(tk.ALL)
        self._create_ui()


class ActionPalette(tk.Frame):
    """Palette of available actions to drag into the sequence."""
    
    def __init__(self, parent, on_action_selected=None):
        """
        Initialize the action palette.
        
        Args:
            parent: The parent widget
            on_action_selected: Callback when an action is selected
        """
        super().__init__(parent, bg="#F0F0F0", width=200)
        
        self.parent = parent
        self.on_action_selected = on_action_selected
        
        # Create the UI
        self._create_ui()
        
    def _create_ui(self):
        """Create the UI elements for the palette."""
        # Add a title
        title = ttk.Label(self, text="Action Palette", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Create a canvas with scrollbar for the palette
        self.canvas = tk.Canvas(self, bg="#F0F0F0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Create a frame inside the canvas to hold the action categories
        self.palette_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.palette_frame, anchor="nw")
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add action categories
        for category, actions in ACTION_CATEGORIES.items():
            # Create a label for the category
            category_frame = ttk.LabelFrame(self.palette_frame, text=category)
            category_frame.pack(fill="x", padx=5, pady=5)
            
            # Add the actions
            for action in actions:
                # Create a button for the action
                action_btn = ttk.Button(
                    category_frame, 
                    text=f"{ACTION_ICONS.get(action, '?')} {action}",
                    command=lambda a=action: self._on_action_clicked(a)
                )
                action_btn.pack(fill="x", padx=5, pady=2)
                
    def _on_action_clicked(self, action_type):
        """Handle action button clicks."""
        # Create default parameters based on action type
        params = {}
        if action_type in ["tab", "enter", "up", "down", "delete"]:
            params["count"] = 1
        elif action_type == "text":
            params["value"] = ""
        elif action_type == "wait":
            params["seconds"] = 1
            
        # Notify the parent
        if self.on_action_selected:
            self.on_action_selected(action_type, params)


class ActionEditDialog(tk.Toplevel):
    """Dialog for editing action parameters."""
    
    def __init__(self, parent, action_type, params=None, on_save=None):
        """
        Initialize the action edit dialog.
        
        Args:
            parent: The parent widget
            action_type: The type of action to edit
            params: The current parameters for the action
            on_save: Callback when the action is saved
        """
        super().__init__(parent)
        self.title(f"Edit {action_type} Action")
        self.geometry("300x200")
        self.resizable(False, False)
        self.transient(parent)  # Set to be on top of the parent window
        self.grab_set()  # Modal dialog
        
        # Store the parameters
        self.action_type = action_type
        self.params = params or {}
        self.on_save = on_save
        
        # Create the UI
        self._create_ui()
        
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
        
        # Set up the protocol for when the window is closed
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
    def _create_ui(self):
        """Create the UI elements for the dialog."""
        # Create a main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a label for the action type
        ttk.Label(main_frame, text=f"Action Type: {self.action_type}", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Add fields based on action type
        self.param_vars = {}
        
        if self.action_type in ["tab", "enter", "up", "down", "delete"]:
            # Add a field for the count
            count_frame = ttk.Frame(main_frame)
            count_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(count_frame, text="Count:").pack(side=tk.LEFT)
            
            self.param_vars["count"] = tk.IntVar(value=self.params.get("count", 1))
            ttk.Spinbox(count_frame, from_=1, to=10, textvariable=self.param_vars["count"], width=5).pack(side=tk.LEFT, padx=5)
            
        elif self.action_type == "text":
            # Add a field for the text value
            value_frame = ttk.Frame(main_frame)
            value_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(value_frame, text="Text:").pack(side=tk.LEFT)
            
            self.param_vars["value"] = tk.StringVar(value=self.params.get("value", ""))
            ttk.Entry(value_frame, textvariable=self.param_vars["value"], width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
        elif self.action_type == "wait":
            # Add a field for the wait duration
            seconds_frame = ttk.Frame(main_frame)
            seconds_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(seconds_frame, text="Seconds:").pack(side=tk.LEFT)
            
            self.param_vars["seconds"] = tk.DoubleVar(value=self.params.get("seconds", 1.0))
            ttk.Spinbox(seconds_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.param_vars["seconds"], width=5).pack(side=tk.LEFT, padx=5)
        
        # Add buttons for save and cancel
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="Save", command=self._on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT, padx=5)
        
    def _on_save(self):
        """Handle the Save button click."""
        # Get the values from the UI
        new_params = {}
        for param, var in self.param_vars.items():
            new_params[param] = var.get()
            
        # Call the callback
        if self.on_save:
            self.on_save(new_params)
            
        # Close the dialog
        self.grab_release()
        self.destroy()
        
    def _on_cancel(self):
        """Handle the Cancel button click."""
        # Close the dialog
        self.grab_release()
        self.destroy()


class MacroEditorGame(tk.Toplevel):
    """Game-like interface for editing macros."""
    
    def __init__(self, parent):
        """
        Initialize the macro editor game.
        
        Args:
            parent: The parent window
        """
        super().__init__(parent)
        self.title("Macro Editor - Game Mode")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        self.transient(parent)  # Set to be on top of the parent window
        self.grab_set()  # Modal dialog
        
        # Initialize variables
        self.parent = parent
        self.selected_macro_id = None
        self.action_blocks = []
        self.selected_block = None
        
        # Create the UI
        self._create_ui()
        
        # Load the macros
        self._load_macros()
        
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
        
        # Set up the protocol for when the window is closed
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        logger.info("MacroEditorGame initialized")
        
    def _create_ui(self):
        """Create the user interface elements."""
        # Create a main frame with a dark background for the game-like feel
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the left panel (macro list and properties)
        left_panel = ttk.Frame(self.main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Create a frame for the macro list
        list_frame = ttk.LabelFrame(left_panel, text="Macro Library", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Add buttons for new and delete
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame, text="New Macro", command=self._on_new).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self._on_delete).pack(side=tk.RIGHT, padx=5)
        
        # Create a listbox for the macros
        self.macro_listbox = tk.Listbox(list_frame, width=20, height=10, exportselection=0)
        self.macro_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar to the listbox
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.macro_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.macro_listbox.config(yscrollcommand=list_scrollbar.set)
        
        # Bind the listbox selection event
        self.macro_listbox.bind('<<ListboxSelect>>', self._on_macro_selected)
        
        # Create a frame for the macro properties
        properties_frame = ttk.LabelFrame(left_panel, text="Macro Properties", padding=5)
        properties_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add fields for name and description
        ttk.Label(properties_frame, text="Name:").pack(anchor=tk.W, pady=(0, 2))
        self.name_var = tk.StringVar()
        ttk.Entry(properties_frame, textvariable=self.name_var).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(properties_frame, text="Description:").pack(anchor=tk.W, pady=(0, 2))
        self.description_var = tk.StringVar()
        ttk.Entry(properties_frame, textvariable=self.description_var).pack(fill=tk.X, pady=(0, 5))
        
        # Add the action palette
        self.action_palette = ActionPalette(left_panel, on_action_selected=self._on_palette_action_selected)
        self.action_palette.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the right panel (action sequence editor)
        right_panel = ttk.Frame(self.main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create a frame for the action sequence
        sequence_frame = ttk.LabelFrame(right_panel, text="Action Sequence", padding=5)
        sequence_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create a canvas for the action blocks
        self.sequence_canvas = tk.Canvas(sequence_frame, bg="#E0E0E0", highlightthickness=0)
        self.sequence_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add a scrollbar to the canvas
        sequence_scrollbar = ttk.Scrollbar(sequence_frame, orient=tk.VERTICAL, command=self.sequence_canvas.yview)
        sequence_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sequence_canvas.config(yscrollcommand=sequence_scrollbar.set)
        
        # Bind canvas events
        self.sequence_canvas.bind("<Button-1>", self._on_canvas_click)
        self.sequence_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Create a frame for the buttons
        button_frame = ttk.Frame(right_panel)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame, text="Save Changes", command=self._on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Sequence", command=self._on_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close Editor", command=self._on_close).pack(side=tk.RIGHT, padx=5)
        
        # Add a help text
        help_text = (
            "Drag actions from the palette to the sequence canvas.\n"
            "Double-click an action to edit its parameters.\n"
            "Click and drag actions to reorder them."
        )
        help_label = ttk.Label(right_panel, text=help_text, wraplength=400, justify=tk.LEFT)
        help_label.pack(fill=tk.X, pady=5)
        
    def _load_macros(self):
        """Load the macros into the listbox."""
        # Clear the listbox
        self.macro_listbox.delete(0, tk.END)
        
        # Get the macros
        macros = macro_manager.get_macros()
        
        # Add the macros to the listbox
        for macro_id, macro in macros.items():
            # Get the display name
            display_name = macro.get('name', macro_id)
            
            # Add the macro to the listbox
            self.macro_listbox.insert(tk.END, display_name)
            
            # Store the macro ID as an item attribute
            index = self.macro_listbox.size() - 1
            self.macro_listbox.itemconfig(index, macro_name=macro_id)
            
        logger.info(f"Loaded {len(macros)} macros")
        
    def _on_macro_selected(self, event):
        """Handle macro selection in the listbox."""
        # Get the selected macro
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
            messagebox.showerror("Error", f"Macro '{macro_name}' not found.")
            return
            
        # Store the selected macro ID
        self.selected_macro_id = macro_name
        
        # Update the UI
        self.name_var.set(macro.get('name', ''))
        self.description_var.set(macro.get('description', ''))
        
        # Clear the sequence canvas
        self._clear_sequence_canvas()
        
        # Add the actions to the sequence canvas
        sequence = macro.get('sequence', [])
        self._load_sequence(sequence)
        
        logger.info(f"Selected macro '{macro_name}'")
        
    def _clear_sequence_canvas(self):
        """Clear the sequence canvas."""
        # Remove all action blocks
        for block in self.action_blocks:
            block.destroy()
            
        self.action_blocks = []
        self.selected_block = None
        
        # Clear the canvas
        self.sequence_canvas.delete(tk.ALL)
        
    def _load_sequence(self, sequence):
        """Load a sequence into the canvas."""
        # Add each action as a block
        y_offset = 10
        for action in sequence:
            # Get the action type and parameters
            action_type = action.get('action')
            params = {k: v for k, v in action.items() if k != 'action'}
            
            # Create an action block
            block = ActionBlock(self.sequence_canvas, action_type, **params)
            
            # Add the block to the canvas
            self.sequence_canvas.create_window(100, y_offset, window=block, anchor=tk.NW)
            
            # Add the block to the list
            self.action_blocks.append(block)
            
            # Update the y offset
            y_offset += 70
            
        # Update the canvas scroll region
        self.sequence_canvas.configure(scrollregion=self.sequence_canvas.bbox(tk.ALL))
        
    def _on_canvas_click(self, event):
        """Handle clicks on the canvas."""
        # Deselect any selected block
        if self.selected_block:
            self.selected_block.deselect()
            self.selected_block = None
            
    def _on_canvas_configure(self, event):
        """Handle canvas resize events."""
        # Update the canvas scroll region
        self.sequence_canvas.configure(scrollregion=self.sequence_canvas.bbox(tk.ALL))
        
    def _on_palette_action_selected(self, action_type, params):
        """Handle action selection from the palette."""
        # Create a new action block
        block = ActionBlock(self.sequence_canvas, action_type, **params)
        
        # Add the block to the canvas at the end of the sequence
        y_offset = 10
        if self.action_blocks:
            # Get the position of the last block
            last_block = self.action_blocks[-1]
            last_block_id = self.sequence_canvas.find_withtag(last_block)
            if last_block_id:
                # Get the position of the last block
                x, y = self.sequence_canvas.coords(last_block_id[0])
                y_offset = y + 70
                
        # Add the block to the canvas
        self.sequence_canvas.create_window(100, y_offset, window=block, anchor=tk.NW)
        
        # Add the block to the list
        self.action_blocks.append(block)
        
        # Update the canvas scroll region
        self.sequence_canvas.configure(scrollregion=self.sequence_canvas.bbox(tk.ALL))
        
        # Scroll to show the new block
        self.sequence_canvas.yview_moveto(1.0)
        
        # Flash the block to indicate it was added
        self._flash_block(block)
        
        logger.info(f"Added {action_type} action to sequence")
        
    def _flash_block(self, block, times=3):
        """Flash a block to highlight it."""
        original_bg = block.cget('bg')
        
        def _flash_cycle(count):
            if count <= 0:
                block.configure(bg=original_bg)
                return
                
            # Toggle the background
            if count % 2 == 0:
                block.configure(bg="#FFFF00")  # Yellow
            else:
                block.configure(bg=original_bg)
                
            # Schedule the next cycle
            self.after(200, lambda: _flash_cycle(count - 1))
            
        # Start the flashing
        _flash_cycle(times * 2)
        
    def on_action_selected(self, block):
        """Handle action block selection."""
        # Deselect any previously selected block
        if self.selected_block and self.selected_block != block:
            self.selected_block.deselect()
            
        # Set the new selected block
        self.selected_block = block
        
    def on_action_moved(self, block):
        """Handle action block movement."""
        # Get the position of all blocks
        block_positions = []
        for b in self.action_blocks:
            # Get the position of the block
            block_id = self.sequence_canvas.find_withtag(b)
            if block_id:
                x, y = self.sequence_canvas.coords(block_id[0])
                block_positions.append((b, y))
                
        # Sort the blocks by y position
        block_positions.sort(key=lambda x: x[1])
        
        # Reorder the blocks in the list
        self.action_blocks = [b for b, _ in block_positions]
        
        # Reposition the blocks on the canvas
        y_offset = 10
        for b in self.action_blocks:
            # Get the block ID
            block_id = self.sequence_canvas.find_withtag(b)
            if block_id:
                # Move the block to the new position
                self.sequence_canvas.coords(block_id[0], 100, y_offset)
                
                # Update the y offset
                y_offset += 70
                
        # Update the canvas scroll region
        self.sequence_canvas.configure(scrollregion=self.sequence_canvas.bbox(tk.ALL))
        
    def on_action_edit(self, block):
        """Handle action block editing."""
        # Open the edit dialog
        dialog = ActionEditDialog(
            self,
            block.action_type,
            block.params,
            on_save=lambda params: self._on_action_updated(block, params)
        )
        
    def _on_action_updated(self, block, params):
        """Handle action parameter updates."""
        # Update the block parameters
        block.update_params(**params)
        
        # Flash the block to indicate it was updated
        self._flash_block(block, times=2)
        
        logger.info(f"Updated {block.action_type} action parameters")
        
    def _on_new(self):
        """Handle the New button click."""
        # Create a new macro
        name = "New Macro"
        description = "Description"
        sequence = []
        
        # Add the macro
        success = macro_manager.add_macro(name, description, sequence)
        if success:
            # Reload the macros
            self._load_macros()
            
            # Select the new macro
            for i in range(self.macro_listbox.size()):
                if self.macro_listbox.get(i) == name:
                    self.macro_listbox.selection_set(i)
                    self._on_macro_selected(None)
                    break
                    
            logger.info(f"Created new macro '{name}'")
        else:
            messagebox.showerror("Error", f"Error creating macro '{name}'.")
            
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
            # Clear the UI
            self.name_var.set("")
            self.description_var.set("")
            self._clear_sequence_canvas()
            
            # Reload the macros
            self._load_macros()
            
            logger.info(f"Deleted macro '{display_name}'")
        else:
            messagebox.showerror("Error", f"Error deleting macro '{display_name}'.")
            
    def _on_save(self):
        """Handle the Save button click."""
        # Check if a macro is selected
        if not self.selected_macro_id:
            messagebox.showerror("Error", "Please select a macro to save.")
            return
            
        # Get the values
        name = self.name_var.get().strip()
        description = self.description_var.get().strip()
        
        # Validate the name
        if not name:
            messagebox.showerror("Error", "Please enter a name for the macro.")
            return
            
        # Get the sequence from the action blocks
        sequence = [block.get_action() for block in self.action_blocks]
        
        # Update the macro
        success = macro_manager.update_macro(self.selected_macro_id, description, sequence, name=name)
        if success:
            messagebox.showinfo("Success", f"Macro '{name}' saved successfully.")
            
            # Reload the macros
            self._load_macros()
            
            # Reselect the macro
            for i in range(self.macro_listbox.size()):
                if self.macro_listbox.itemcget(i, 'macro_name') == self.selected_macro_id:
                    self.macro_listbox.selection_set(i)
                    break
                    
            logger.info(f"Saved macro '{name}'")
        else:
            messagebox.showerror("Error", f"Error saving macro '{name}'.")
            
    def _on_test(self):
        """Handle the Test button click."""
        # Check if a macro is selected
        if not self.selected_macro_id:
            messagebox.showerror("Error", "Please select a macro to test.")
            return
            
        # Get the sequence from the action blocks
        sequence = [block.get_action() for block in self.action_blocks]
        
        # Create a temporary macro for testing
        temp_macro = {
            'name': 'Test Macro',
            'description': 'Temporary macro for testing',
            'sequence': sequence
        }
        
        # Execute the macro
        try:
            macro_manager.execute_macro(temp_macro)
            logger.info(f"Tested macro '{self.selected_macro_id}'")
        except Exception as e:
            messagebox.showerror("Error", f"Error testing macro: {str(e)}")
            logger.error(f"Error testing macro: {str(e)}")
            
    def _on_close(self):
        """Handle the Close button click."""
        # Release the grab and destroy the dialog
        self.grab_release()
        self.destroy()
        
        logger.info("MacroEditorGame closed")


def create_macro_editor_game(parent):
    """
    Create and show the game-like macro editor dialog.
    
    Args:
        parent: The parent window
    """
    dialog = MacroEditorGame(parent)
    return dialog

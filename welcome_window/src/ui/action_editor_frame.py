"""
Action Editor Frame for the Macro Editor.
This module provides a frame for editing individual macro actions in a more intuitive way.
"""
import tkinter as tk
from tkinter import ttk

class ActionEditorFrame(ttk.Frame):
    """Frame for editing a single macro action."""
    
    def __init__(self, parent, action=None, on_update=None, on_delete=None, on_move_up=None, on_move_down=None, on_insert_after=None, is_new=False):
        """
        Initialize the action editor frame.
        
        Args:
            parent: The parent widget
            action: The action to edit (dict)
            on_update: Callback for when the action is updated
            on_delete: Callback for when the action is deleted
            on_move_up: Callback for when the action should be moved up
            on_move_down: Callback for when the action should be moved down
            on_insert_after: Callback for when a new action should be inserted after this one
            is_new: Whether this is a newly created action (for highlighting)
        """
        super().__init__(parent, padding=5)
        self.parent = parent
        self.action = action or {'action': 'tab', 'count': 1}
        self.on_update = on_update
        self.on_delete = on_delete
        self.on_move_up = on_move_up
        self.on_move_down = on_move_down
        self.on_insert_after = on_insert_after
        self.is_new = is_new
        
        # Create the UI
        self._create_ui()
        
        # Load the action data
        self._load_action()
        
        # Apply highlighting if this is a new action
        if self.is_new:
            self.configure(style="NewAction.TFrame")
            # Schedule the highlighting to be removed after 5 seconds
            self.after(5000, self._remove_highlight)
        
    def _create_ui(self):
        """Create the user interface elements."""
        # Configure the frame with a modern look
        self.configure(style="Action.TFrame", padding=10)
        
        # Create a main frame with better organization
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.X, expand=True)
        
        # Bind right-click event to the frame
        self.bind("<Button-3>", self._show_context_menu)
        
        # Add a number indicator for the action (will be set by the parent)
        self.number_label = ttk.Label(main_frame, text="#", width=3, style="ActionNumber.TLabel")
        self.number_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create the action type dropdown with better styling
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.action_var = tk.StringVar()
        action_types = [
            # Keyboard actions
            "tab", "enter", "up", "down", "delete", 
            # Clipboard actions
            "paste", "paste_sku", "paste_order", "paste_container",
            # Text and timing
            "text", "wait",
            # Browser control
            "open_tab", "close_tab", 
            # Other actions
            "enable_sku"
        ]
        
        # Create a frame for the action type
        action_type_frame = ttk.Frame(action_frame)
        action_type_frame.pack(side=tk.LEFT, fill=tk.X)
        
        ttk.Label(action_type_frame, text="Action Type:", style="Header.TLabel").pack(side=tk.TOP, anchor="w")
        
        self.action_dropdown = ttk.Combobox(
            action_type_frame, 
            textvariable=self.action_var, 
            values=action_types,
            width=15,
            state="readonly",
            font=("Arial", 10)
        )
        self.action_dropdown.pack(side=tk.TOP, pady=(2, 0), anchor="w")
        self.action_dropdown.bind("<<ComboboxSelected>>", self._on_action_changed)
        
        # Create the parameters frame
        self.params_frame = ttk.Frame(action_frame)
        self.params_frame.pack(side=tk.LEFT, padx=(20, 0), fill=tk.X)
        
        # Create the count frame (for tab, enter, up, down, delete)
        self.count_frame = ttk.Frame(self.params_frame)
        
        ttk.Label(self.count_frame, text="Repeat Count:", style="Header.TLabel").pack(side=tk.TOP, anchor="w")
        count_frame_inner = ttk.Frame(self.count_frame)
        count_frame_inner.pack(side=tk.TOP, pady=(2, 0), anchor="w")
        
        self.count_var = tk.StringVar(value="1")
        count_spinbox = ttk.Spinbox(
            count_frame_inner, 
            from_=1, 
            to=20, 
            width=5, 
            textvariable=self.count_var,
            font=("Arial", 10)
        )
        count_spinbox.pack(side=tk.LEFT)
        ttk.Label(count_frame_inner, text="times").pack(side=tk.LEFT, padx=(5, 0))
        
        # Create the value frame (for text)
        self.value_frame = ttk.Frame(self.params_frame)
        
        ttk.Label(self.value_frame, text="Text to Type:", style="Header.TLabel").pack(side=tk.TOP, anchor="w")
        self.value_var = tk.StringVar()
        value_entry = ttk.Entry(self.value_frame, textvariable=self.value_var, width=25, font=("Arial", 10))
        value_entry.pack(side=tk.TOP, pady=(2, 0), anchor="w")
        
        # Create the seconds frame (for wait)
        self.seconds_frame = ttk.Frame(self.params_frame)
        
        ttk.Label(self.seconds_frame, text="Wait Duration:", style="Header.TLabel").pack(side=tk.TOP, anchor="w")
        seconds_frame_inner = ttk.Frame(self.seconds_frame)
        seconds_frame_inner.pack(side=tk.TOP, pady=(2, 0), anchor="w")
        
        self.seconds_var = tk.StringVar(value="1")
        seconds_spinbox = ttk.Spinbox(
            seconds_frame_inner, 
            from_=0.1, 
            to=10.0, 
            increment=0.1,
            width=5, 
            textvariable=self.seconds_var,
            font=("Arial", 10)
        )
        seconds_spinbox.pack(side=tk.LEFT)
        ttk.Label(seconds_frame_inner, text="seconds").pack(side=tk.LEFT, padx=(5, 0))
        
        # Create the description frame (for special actions)
        self.description_frame = ttk.Frame(self.params_frame)
        
        ttk.Label(self.description_frame, text="Description:", style="Header.TLabel").pack(side=tk.TOP, anchor="w")
        self.description_label = ttk.Label(self.description_frame, text="", font=("Arial", 10, "italic"))
        self.description_label.pack(side=tk.TOP, pady=(2, 0), anchor="w")
        
        # Create the buttons frame with better styling
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        # Create a frame for the move buttons
        move_buttons = ttk.Frame(buttons_frame)
        move_buttons.pack(side=tk.TOP, pady=(0, 5))
        
        # Create the move up button with an arrow symbol
        move_up_button = ttk.Button(
            move_buttons, 
            text="▲", 
            command=self._on_move_up,
            width=3
        )
        move_up_button.pack(side=tk.LEFT, padx=2)
        
        # Create the move down button with an arrow symbol
        move_down_button = ttk.Button(
            move_buttons, 
            text="▼", 
            command=self._on_move_down,
            width=3
        )
        move_down_button.pack(side=tk.LEFT, padx=2)
        
        # Create the delete button
        delete_button = ttk.Button(
            buttons_frame, 
            text="Delete", 
            command=self._on_delete
        )
        delete_button.pack(side=tk.BOTTOM)
        
        # Bind events
        self.count_var.trace_add("write", lambda *args: self._update_action())
        self.value_var.trace_add("write", lambda *args: self._update_action())
        self.seconds_var.trace_add("write", lambda *args: self._update_action())
    
    def _load_action(self):
        """Load the action data into the UI."""
        action_type = self.action.get('action', 'tab')
        self.action_var.set(action_type)
        
        # Update UI based on action type
        self._update_ui_for_action_type(action_type)
        
        # Set values
        if action_type in ['tab', 'enter', 'up', 'down', 'delete']:
            self.count_var.set(str(self.action.get('count', 1)))
        elif action_type == 'text':
            self.value_var.set(self.action.get('value', ''))
        elif action_type == 'wait':
            self.seconds_var.set(str(self.action.get('seconds', 1)))
    
    def _update_ui_for_action_type(self, action_type):
        """Update the UI based on the action type."""
        # Hide all option frames
        self.count_frame.pack_forget()
        self.value_frame.pack_forget()
        self.seconds_frame.pack_forget()
        self.description_frame.pack_forget()
        
        # Show the appropriate option frame
        if action_type in ['tab', 'enter', 'up', 'down', 'delete']:
            self.count_frame.pack(fill=tk.X, anchor="w")
            # Update action description based on type
            action_descriptions = {
                'tab': "Press the Tab key to move between fields",
                'enter': "Press the Enter key to submit or confirm",
                'up': "Press the Up arrow key to navigate upward",
                'down': "Press the Down arrow key to navigate downward",
                'delete': "Press the Delete key to remove content"
            }
            # Set number label color based on action type
            self.number_label.configure(foreground="#0066cc")
            
        elif action_type == 'text':
            self.value_frame.pack(fill=tk.X, anchor="w")
            # Set number label color for text actions
            self.number_label.configure(foreground="#006600")
            
        elif action_type == 'wait':
            self.seconds_frame.pack(fill=tk.X, anchor="w")
            # Set number label color for wait actions
            self.number_label.configure(foreground="#990000")
            
        elif action_type in ['paste', 'paste_sku', 'paste_order', 'paste_container']:
            self.description_frame.pack(fill=tk.X, anchor="w")
            descriptions = {
                'paste': "Pastes TRACKING NUMBER from clipboard",
                'paste_sku': "Pastes SKU from clipboard",
                'paste_order': "Pastes ORDER REFERENCE NUMBER from clipboard",
                'paste_container': "Pastes CONTAINER CARD from clipboard"
            }
            self.description_label.config(text=descriptions.get(action_type, ""))
            # Set number label color for paste actions
            self.number_label.configure(foreground="#663399")
            
        elif action_type in ['open_tab', 'close_tab', 'enable_sku']:
            self.description_frame.pack(fill=tk.X, anchor="w")
            descriptions = {
                'open_tab': "Opens a browser tab with the JDL site",
                'close_tab': "Closes the current browser tab",
                'enable_sku': "Enables the SKU input field"
            }
            self.description_label.config(text=descriptions.get(action_type, ""))
            # Set number label color for special actions
            self.number_label.configure(foreground="#ff6600")
    
    def _on_action_changed(self, event):
        """Handle action type change."""
        action_type = self.action_var.get()
        self._update_ui_for_action_type(action_type)
        self._update_action()
    
    def _update_action(self):
        """Update the action data from the UI."""
        action_type = self.action_var.get()
        
        # Create a new action dict
        new_action = {'action': action_type}
        
        # Add the appropriate properties
        if action_type in ['tab', 'enter', 'up', 'down', 'delete']:
            try:
                count = int(self.count_var.get())
                new_action['count'] = count
            except ValueError:
                new_action['count'] = 1
        elif action_type == 'text':
            new_action['value'] = self.value_var.get()
        elif action_type == 'wait':
            try:
                seconds = float(self.seconds_var.get())
                new_action['seconds'] = seconds
            except ValueError:
                new_action['seconds'] = 1
        elif action_type in ['open_tab', 'close_tab', 'enable_sku']:
            # These actions don't need additional properties
            new_action['description'] = {
                'open_tab': 'Opens a browser tab with the JDL site',
                'close_tab': 'Closes the current browser tab',
                'enable_sku': 'Enables the SKU input field'
            }.get(action_type, '')
        
        # Update the action
        self.action = new_action
        
        # Call the update callback
        if self.on_update:
            self.on_update(self, new_action)
    
    def _on_delete(self):
        """Handle delete button click."""
        if self.on_delete:
            self.on_delete(self)
    
    def _on_move_up(self):
        """Handle move up button click."""
        if self.on_move_up:
            self.on_move_up(self)
    
    def _on_move_down(self):
        """Handle move down button click."""
        if self.on_move_down:
            self.on_move_down(self)
    
    def get_action(self):
        """Get the current action."""
        return self.action
        
    def _show_context_menu(self, event):
        """Show the context menu on right-click."""
        # Create a context menu
        context_menu = tk.Menu(self, tearoff=0)
        
        # Create a submenu for action types
        action_menu = tk.Menu(context_menu, tearoff=0)
        
        # Define action types grouped by category
        keyboard_actions = ["tab", "enter", "up", "down", "delete"]
        clipboard_actions = ["paste", "paste_sku", "paste_order", "paste_container"]
        other_actions = ["text", "wait", "open_tab", "close_tab", "enable_sku"]
        
        # Add keyboard actions to the submenu
        action_menu.add_command(label="--- Keyboard Actions ---", state="disabled")
        for action in keyboard_actions:
            action_menu.add_command(label=action, 
                                  command=lambda a=action: self._insert_action_after(action_type=a))
        
        # Add clipboard actions to the submenu
        action_menu.add_separator()
        action_menu.add_command(label="--- Clipboard Actions ---", state="disabled")
        for action in clipboard_actions:
            action_menu.add_command(label=action, 
                                  command=lambda a=action: self._insert_action_after(action_type=a))
        
        # Add other actions to the submenu
        action_menu.add_separator()
        action_menu.add_command(label="--- Other Actions ---", state="disabled")
        for action in other_actions:
            action_menu.add_command(label=action, 
                                  command=lambda a=action: self._insert_action_after(action_type=a))
        
        # Add the action submenu to the context menu
        context_menu.add_cascade(label="Insert Action Below", menu=action_menu)
        
        # Display the menu at the event position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Make sure to release the grab
            context_menu.grab_release()
    
    def _insert_action_after(self, action_type=None):
        """Insert a new action after this one."""
        if self.on_insert_after:
            # Create a default action based on the selected type
            if action_type:
                # Create appropriate default action based on type
                if action_type in ['tab', 'enter', 'up', 'down', 'delete']:
                    default_action = {'action': action_type, 'count': 1}
                elif action_type == 'text':
                    default_action = {'action': action_type, 'value': ''}
                elif action_type == 'wait':
                    default_action = {'action': action_type, 'seconds': 1}
                else:
                    # Simple action with no parameters
                    default_action = {'action': action_type}
                
                # Call the callback with the specific action
                self.on_insert_after(self, default_action)
            else:
                # Call the callback with no specific action (will use default)
                self.on_insert_after(self)
    
    def _remove_highlight(self):
        """Remove the highlighting from a new action."""
        self.configure(style="Action.TFrame")
        self.is_new = False

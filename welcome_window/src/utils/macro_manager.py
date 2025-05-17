"""
Macro Manager for handling configurable automation macros.
This module loads, parses, and executes macros defined in a JSON file.
"""
import os
import sys
import json
import time
import logging
import threading
import pyautogui
import pyperclip
import tkinter as tk
from datetime import datetime

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

class MacroManager:
    """Class for managing configurable automation macros."""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of MacroManager"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
    
    def __init__(self):
        """Initialize the macro manager."""
        self.macros = {}
        self.macro_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'macros.json')
        self.load_macros()
        logger.info("MacroManager initialized")
    
    def load_macros(self):
        """Load macros from the JSON file."""
        try:
            if os.path.exists(self.macro_file_path):
                with open(self.macro_file_path, 'r') as f:
                    data = json.load(f)
                    self.macros = data.get('macros', {})
                logger.info(f"Loaded {len(self.macros)} macros from {self.macro_file_path}")
            else:
                logger.warning(f"Macro file not found at {self.macro_file_path}")
                self.create_default_macros()
        except Exception as e:
            error_msg = f"Error loading macros: {str(e)}"
            logger.error(error_msg)
            self.create_default_macros()
    
    def create_default_macros(self):
        """Create default macros if the JSON file doesn't exist."""
        try:
            self.macros = {
                "sku_mismatch": {
                    "name": "SKU Mismatch",
                    "description": "Default automation sequence for handling SKU mismatch exceptions",
                    "sequence": [
                        {"action": "tab", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "up", "count": 2},
                        {"action": "enter", "count": 1},
                        {"action": "tab", "count": 1},
                        {"action": "paste"},
                        {"action": "tab", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "up", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "tab", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "down", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "tab", "count": 1},
                        {"action": "paste_sku"},
                        {"action": "tab", "count": 1},
                        {"action": "text", "value": "1"},
                        {"action": "tab", "count": 1},
                        {"action": "paste_order"},
                        {"action": "tab", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "delete", "count": 1}
                    ]
                },
                "return_to_sender": {
                    "name": "Return to Sender",
                    "description": "Default automation sequence for handling return to sender exceptions",
                    "sequence": [
                        {"action": "tab", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "up", "count": 2},
                        {"action": "enter", "count": 1},
                        {"action": "tab", "count": 1},
                        {"action": "paste"},
                        {"action": "tab", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "up", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "tab", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "up", "count": 1},
                        {"action": "enter", "count": 1},
                        {"action": "tab", "count": 1},
                        {"action": "text", "value": "N/A"},
                        {"action": "tab", "count": 1},
                        {"action": "paste_sku"},
                        {"action": "enter", "count": 1},
                        {"action": "delete", "count": 1}
                    ]
                }
            }
            
            # Save the default macros to the JSON file
            self.save_macros()
            logger.info("Created default macros")
        except Exception as e:
            error_msg = f"Error creating default macros: {str(e)}"
            logger.error(error_msg)
    
    def save_macros(self):
        """Save macros to the JSON file."""
        try:
            data = {
                "version": "1.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "macros": self.macros
            }
            
            with open(self.macro_file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved {len(self.macros)} macros to {self.macro_file_path}")
            return True
        except Exception as e:
            error_msg = f"Error saving macros: {str(e)}"
            logger.error(error_msg)
            return False
    
    def get_macro(self, macro_name):
        """
        Get a macro by name
        
        Args:
            macro_name: The name of the macro to get
            
        Returns:
            dict: The macro definition, or None if not found
        """
        return self.macros.get(macro_name)
    
    def execute_macro(self, macro_name, context=None):
        """
        Execute a macro by name
        
        Args:
            macro_name: The name of the macro to execute
            context: Optional context data for the macro (e.g., tracking number, SKU)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the macro exists
            if macro_name not in self.macros:
                logger.error(f"Macro '{macro_name}' not found")
                return False
            
            # Get the macro
            macro = self.macros[macro_name]
            sequence = macro.get('sequence', [])
            
            logger.info(f"Executing macro '{macro_name}' with {len(sequence)} actions")
            
            # Execute each action in the sequence
            for i, action in enumerate(sequence):
                action_type = action.get('action', 'unknown')
                description = action.get('description', '')
                logger.info(f"Executing action {i+1}/{len(sequence)}: {action_type} - {description}")
                self._execute_action(action, context)
            
            logger.info(f"Macro '{macro_name}' execution completed successfully")
            return True
        except Exception as e:
            error_msg = f"Error executing macro '{macro_name}': {str(e)}"
            logger.error(error_msg)
            return False
    
    def _execute_action(self, action, context=None):
        """
        Execute a single action in a macro
        
        Args:
            action: The action to execute
            context: Optional context data for the action
        """
        try:
            action_type = action.get('action')
            count = action.get('count', 1)
            
            if action_type == 'tab':
                for _ in range(count):
                    pyautogui.press('tab')
                    time.sleep(0.1)
            
            elif action_type == 'enter':
                for _ in range(count):
                    pyautogui.press('enter')
                    time.sleep(0.1)
            
            elif action_type == 'up':
                for _ in range(count):
                    pyautogui.press('up')
                    time.sleep(0.1)
            
            elif action_type == 'down':
                for _ in range(count):
                    pyautogui.press('down')
                    time.sleep(0.1)
            
            elif action_type == 'delete':
                for _ in range(count):
                    pyautogui.press('delete')
                    time.sleep(0.1)
            
            elif action_type == 'paste':
                # Paste the tracking number from context
                if context and 'tracking_number' in context:
                    original_clipboard = pyperclip.paste()
                    pyperclip.copy(context['tracking_number'])
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.1)
                    # Restore original clipboard content
                    pyperclip.copy(original_clipboard)
            
            elif action_type == 'paste_sku':
                # Paste the SKU from context
                if context and 'sku' in context:
                    original_clipboard = pyperclip.paste()
                    pyperclip.copy(context['sku'])
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.1)
                    # Restore original clipboard content
                    pyperclip.copy(original_clipboard)
            
            elif action_type == 'paste_order':
                # Paste the order reference from context
                if context and 'order_reference' in context:
                    original_clipboard = pyperclip.paste()
                    pyperclip.copy(context['order_reference'])
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.1)
                    # Restore original clipboard content
                    pyperclip.copy(original_clipboard)
            
            elif action_type == 'paste_container':
                # Paste the container card from context
                if context and 'container_card' in context:
                    original_clipboard = pyperclip.paste()
                    pyperclip.copy(context['container_card'])
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.1)
                    # Restore original clipboard content
                    pyperclip.copy(original_clipboard)
            
            elif action_type == 'text':
                # Type the specified text
                value = action.get('value', '')
                pyautogui.write(value)
                time.sleep(0.1)
            
            elif action_type == 'wait':
                # Wait for the specified number of seconds
                seconds = action.get('seconds', 1)
                time.sleep(seconds)
            
            elif action_type == 'open_tab':
                # Open a browser tab with the JDL site
                logger.info("Opening browser tab with JDL site")
                try:
                    # Import here to avoid circular imports
                    from src.utils.jdl_automation import JDLAutomation
                    automation = JDLAutomation.get_instance()
                    automation.open_after_sales_order_page()
                    # Set the browser tab open flag
                    JDLAutomation.browser_tab_open = True
                except Exception as tab_error:
                    logger.error(f"Error opening browser tab: {str(tab_error)}")
            
            elif action_type == 'close_tab':
                # Close the browser tab
                logger.info("Closing browser tab")
                try:
                    # Use pyautogui to close the tab with Ctrl+W
                    pyautogui.hotkey('ctrl', 'w')
                    time.sleep(0.5)
                    # Import here to avoid circular imports
                    from src.utils.jdl_automation import JDLAutomation
                    # Reset the browser tab flag
                    JDLAutomation.browser_tab_open = False
                except Exception as tab_error:
                    logger.error(f"Error closing browser tab: {str(tab_error)}")
            
            elif action_type == 'enable_sku':
                # Enable the SKU field in the UI
                logger.info("Enabling SKU field")
                try:
                    # Find the CreateLabelFrame in the widget hierarchy
                    if context and 'frame' in context:
                        frame = context['frame']
                        # Enable the SKU field
                        frame.after(0, lambda: frame.field_widgets["SKU:"]["widget"].config(state="normal"))
                        frame.after(0, lambda: frame.field_widgets["SKU:"]["widget"].focus_set())
                        # Update UI status
                        frame.after(0, lambda: frame._update_status("Ready for SKU input", 'blue'))
                    else:
                        logger.warning("No frame provided in context for enable_sku action")
                except Exception as ui_error:
                    logger.error(f"Error enabling SKU field: {str(ui_error)}")
            
            elif action_type == 'user_interaction':
                # Show a dialog that waits for user interaction with animated gradient background
                message = action.get('message', 'Please complete the action in the application, then click OK to continue.')
                title = action.get('title', 'User Action Required')
                logger.info(f"Waiting for user interaction: {message}")
                
                # Track if we already have a dialog open to prevent duplicates
                dialog_id = f"user_interaction_{int(time.time())}"
                
                # Check if we already have a dialog with this ID in the global namespace
                if hasattr(self, '_active_dialogs') and dialog_id in self._active_dialogs:
                    logger.warning(f"Dialog {dialog_id} already active, not creating a new one")
                    return
                
                # Initialize the active dialogs tracking dict if it doesn't exist
                if not hasattr(self, '_active_dialogs'):
                    self._active_dialogs = {}
                
                # Add this dialog to active dialogs
                self._active_dialogs[dialog_id] = True
                
                # Create a simple dialog that blocks until the user clicks OK
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                
                # Position the dialog in the center of the screen
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                
                dialog = tk.Toplevel(root)
                dialog.title(title)
                dialog.geometry(f"450x250+{int(screen_width/2 - 225)}+{int(screen_height/2 - 125)}")
                dialog.resizable(False, False)
                dialog.attributes('-topmost', True)  # Keep on top of other windows
                
                # Add an icon if available
                try:
                    dialog.iconbitmap(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icon.ico'))
                except:
                    pass
                
                # Create a canvas for the animated gradient background
                canvas = tk.Canvas(dialog, width=450, height=250, highlightthickness=0)
                canvas.pack(fill=tk.BOTH, expand=True)
                
                # Create gradient colors (yellow shades)
                gradient_colors = [
                    "#FFFACD",  # Lemon Chiffon
                    "#FFFFE0",  # Light Yellow
                    "#FFFF00",  # Yellow
                    "#FFD700",  # Gold
                    "#FFC125"   # Goldenrod
                ]
                
                # Create gradient rectangles
                gradient_rects = []
                rect_height = 250 // len(gradient_colors)
                for i in range(len(gradient_colors)):
                    rect = canvas.create_rectangle(0, i * rect_height, 450, (i + 1) * rect_height, 
                                                fill=gradient_colors[i], outline="")
                    gradient_rects.append(rect)
                
                # Add a semi-transparent overlay frame for content
                content_frame = tk.Frame(dialog, bg="#FFFFFF", padx=20, pady=20)
                content_frame.configure(bg="#FFFFCC")
                content_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=200)
                
                # Add a message label with a nicer font
                msg_label = tk.Label(content_frame, text=message, wraplength=360, justify=tk.CENTER,
                                    font=("Arial", 12), bg="#FFFFCC")
                msg_label.pack(pady=(10, 30))
                
                # Animation function for moving gradient
                animation_id = [None]  # Use a list to store the animation ID so it can be modified in nested functions
                offset = [0]  # Animation offset
                
                def animate_gradient():
                    # Move the gradient
                    offset[0] = (offset[0] + 1) % (rect_height * 2)
                    
                    for i, rect in enumerate(gradient_rects):
                        # Calculate the new y position with offset
                        y1 = (i * rect_height - offset[0]) % (rect_height * len(gradient_colors))
                        y2 = ((i + 1) * rect_height - offset[0]) % (rect_height * len(gradient_colors))
                        
                        # Handle wrap-around
                        if y1 > y2:
                            y2 += rect_height * len(gradient_colors)
                        
                        # Update rectangle position
                        canvas.coords(rect, 0, y1, 450, y2)
                    
                    # Schedule the next animation frame
                    animation_id[0] = dialog.after(50, animate_gradient)
                
                # Start the animation
                animate_gradient()
                
                # Add an OK button with a nicer style
                def on_ok():
                    try:
                        # Stop the animation if it's running
                        if animation_id[0] is not None:
                            dialog.after_cancel(animation_id[0])
                            animation_id[0] = None
                            
                        # Remove from active dialogs
                        if hasattr(self, '_active_dialogs') and dialog_id in self._active_dialogs:
                            del self._active_dialogs[dialog_id]
                            
                        # Destroy the dialog and quit the mainloop
                        dialog.destroy()
                        root.quit()
                        root.destroy()
                    except Exception as e:
                        logger.error(f"Error closing dialog: {str(e)}")
                
                ok_button = tk.Button(content_frame, text="OK", command=on_ok, width=10,
                                    relief=tk.RAISED, bg="#FFD700", activebackground="#FFFF00",
                                    font=("Arial", 10, "bold"))
                ok_button.pack()
                
                # Handle window close event
                dialog.protocol("WM_DELETE_WINDOW", on_ok)
                
                # Center the dialog on the screen
                dialog.update_idletasks()
                
                try:
                    # Run the dialog
                    root.mainloop()
                except Exception as e:
                    logger.error(f"Error in dialog mainloop: {str(e)}")
                finally:
                    # Ensure cleanup happens even if there's an exception
                    if hasattr(self, '_active_dialogs') and dialog_id in self._active_dialogs:
                        del self._active_dialogs[dialog_id]
                
                logger.info("User interaction completed")
            
            elif action_type == 'shift_tab':
                # Press Shift+Tab the specified number of times
                for _ in range(count):
                    pyautogui.hotkey('shift', 'tab')
                    time.sleep(0.1)
                    
            else:
                logger.warning(f"Unknown action type: {action_type}")
                
        except Exception as e:
            error_msg = f"Error executing action {action}: {str(e)}"
            logger.error(error_msg)
    
    def list_macros(self):
        """
        List all available macros
        
        Returns:
            list: List of macro names
        """
        return list(self.macros.keys())
    
    def add_macro(self, name, description, sequence):
        """
        Add a new macro
        
        Args:
            name: The name of the macro
            description: A description of the macro
            sequence: The sequence of actions
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a normalized macro name (lowercase, spaces replaced with underscores)
            macro_name = name.lower().replace(' ', '_')
            
            # Add the macro
            self.macros[macro_name] = {
                "name": name,
                "description": description,
                "sequence": sequence
            }
            
            # Save the macros
            success = self.save_macros()
            
            return success
        except Exception as e:
            error_msg = f"Error adding macro: {str(e)}"
            logger.error(error_msg)
            return False
    
    def update_macro(self, macro_name, description=None, sequence=None):
        """
        Update an existing macro
        
        Args:
            macro_name: The name of the macro to update
            description: Optional new description
            sequence: Optional new sequence of actions
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the macro exists
            if macro_name not in self.macros:
                logger.error(f"Macro '{macro_name}' not found")
                return False
            
            # Update the macro
            if description is not None:
                self.macros[macro_name]["description"] = description
            
            if sequence is not None:
                self.macros[macro_name]["sequence"] = sequence
            
            # Save the macros
            success = self.save_macros()
            
            return success
        except Exception as e:
            error_msg = f"Error updating macro: {str(e)}"
            logger.error(error_msg)
            return False
    
    def delete_macro(self, macro_name):
        """
        Delete a macro
        
        Args:
            macro_name: The name of the macro to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the macro exists
            if macro_name not in self.macros:
                logger.error(f"Macro '{macro_name}' not found")
                return False
            
            # Delete the macro
            del self.macros[macro_name]
            
            # Save the macros
            success = self.save_macros()
            
            return success
        except Exception as e:
            error_msg = f"Error deleting macro: {str(e)}"
            logger.error(error_msg)
            return False

# Create a global instance of the macro manager
macro_manager = MacroManager.get_instance()

def execute_macro(macro_name, context=None):
    """
    Execute a macro by name
    
    Args:
        macro_name: The name of the macro to execute
        context: Optional context data for the macro (e.g., tracking number, SKU)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        return macro_manager.execute_macro(macro_name, context)
    except Exception as e:
        error_msg = f"Error executing macro: {str(e)}"
        logger.error(error_msg)
        return False

def get_macro_list():
    """
    Get a list of all available macros
    
    Returns:
        list: List of macro names
    """
    try:
        return macro_manager.list_macros()
    except Exception as e:
        error_msg = f"Error getting macro list: {str(e)}"
        logger.error(error_msg)
        return []

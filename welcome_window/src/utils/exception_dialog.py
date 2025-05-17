"""
Custom exception dialog with enhanced navigation.
"""
import tkinter as tk
from tkinter import ttk
import time
import threading
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ExceptionSelectionDialog:
    """
    A custom dialog for selecting exception types with enhanced navigation.
    Features:
    - Mouse hover navigation
    - Enter key prompt after 5 seconds
    - Keyboard navigation with arrow keys
    """
    
    def __init__(self, parent=None, title="Select Exception Type", tracking_number=None, sku=None):
        """
        Initialize the exception selection dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            tracking_number: The tracking number being processed
            sku: The SKU being processed
        """
        self.tracking_number = tracking_number
        self.sku = sku
        self.result = None
        self.show_enter_prompt = False
        
        # Create a root window if none is provided
        if parent is None:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the root window
            self.dialog = tk.Toplevel(self.root)
        else:
            self.root = parent
            self.dialog = tk.Toplevel(parent)
        
        # Configure the dialog
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.root)  # Make dialog modal
        self.dialog.grab_set()  # Make dialog modal
        
        # Center the dialog on screen
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 400) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Make the dialog stay on top
        self.dialog.attributes("-topmost", True)
        
        # Create the UI elements
        self._create_widgets()
        
        # Start the timer for the Enter prompt
        self.prompt_timer = threading.Timer(5.0, self._show_enter_prompt)
        self.prompt_timer.daemon = True
        self.prompt_timer.start()
        
        # Bind keyboard events
        self.dialog.bind("<Up>", lambda e: self._select_previous())
        self.dialog.bind("<Down>", lambda e: self._select_next())
        self.dialog.bind("<Return>", lambda e: self._on_select())
        self.dialog.bind("<Escape>", lambda e: self._on_cancel())
        
        # Ensure proper cleanup when the dialog is closed
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Set focus to the listbox
        self.listbox.focus_set()
        
        # Wait for the dialog to be closed
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """Create the UI elements for the dialog."""
        # Create a frame for the content
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a label with instructions
        if self.tracking_number:
            tracking_info = f"Tracking: {self.tracking_number}"
            if self.sku:
                tracking_info += f" | SKU: {self.sku}"
            
            ttk.Label(main_frame, text=tracking_info, font=("Arial", 10, "bold")).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="Select an exception type:", font=("Arial", 12)).pack(pady=(0, 10))
        
        # Create a frame for the listbox and scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the listbox with exception types
        self.listbox = tk.Listbox(
            list_frame,
            font=("Arial", 11),
            selectbackground="#1a73e8",
            selectforeground="white",
            activestyle="none",
            height=10,
            width=50,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Add exception types to the listbox
        exception_types = [
            "SKU Mismatch",
            "RMA on Label but Not in System",
            "Fraudulent / Suspicious Package",
            "Return to Sender",
            "General Exception"
        ]
        
        for exception_type in exception_types:
            self.listbox.insert(tk.END, exception_type)
        
        # Select the first item
        self.listbox.selection_set(0)
        self.listbox.activate(0)
        
        # Bind events for mouse hover and selection
        self.listbox.bind("<Motion>", self._on_mouse_move)
        self.listbox.bind("<ButtonRelease-1>", self._on_select)
        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
        
        # Create a label for the Enter prompt (initially hidden)
        self.enter_prompt = ttk.Label(
            main_frame, 
            text="Press Enter to select", 
            font=("Arial", 10, "italic"),
            foreground="#666666"
        )
        self.enter_prompt.pack(pady=(0, 10))
        self.enter_prompt.pack_forget()  # Hide initially
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Add buttons
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        select_button = ttk.Button(button_frame, text="Select", command=self._on_select)
        select_button.pack(side=tk.RIGHT)
    
    def _on_mouse_move(self, event):
        """Handle mouse movement over the listbox."""
        # Get the index of the item under the mouse
        index = self.listbox.nearest(event.y)
        if index >= 0:
            # Clear current selection
            self.listbox.selection_clear(0, tk.END)
            # Select the item under the mouse
            self.listbox.selection_set(index)
            self.listbox.activate(index)
    
    def _on_listbox_select(self, event):
        """Handle listbox selection change."""
        # This is needed to ensure the selection is visible
        if self.listbox.curselection():
            self.listbox.see(self.listbox.curselection()[0])
    
    def _select_next(self):
        """Select the next item in the listbox."""
        if self.listbox.curselection():
            current = self.listbox.curselection()[0]
            if current < self.listbox.size() - 1:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(current + 1)
                self.listbox.activate(current + 1)
                self.listbox.see(current + 1)
    
    def _select_previous(self):
        """Select the previous item in the listbox."""
        if self.listbox.curselection():
            current = self.listbox.curselection()[0]
            if current > 0:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(current - 1)
                self.listbox.activate(current - 1)
                self.listbox.see(current - 1)
    
    def _show_enter_prompt(self):
        """Show the Enter prompt after the timer expires."""
        self.show_enter_prompt = True
        self.enter_prompt.pack(pady=(0, 10))
    
    def _on_select(self, event=None):
        """Handle selection of an exception type."""
        if self.listbox.curselection():
            # Get the selected exception type
            index = self.listbox.curselection()[0]
            self.result = self.listbox.get(index).lower()
            
            # Cancel the timer if it's still running
            if self.prompt_timer.is_alive():
                self.prompt_timer.cancel()
            
            # Close the dialog
            self.dialog.destroy()
    
    def _on_cancel(self, event=None):
        """Handle dialog cancellation."""
        # Cancel the timer if it's still running
        if self.prompt_timer.is_alive():
            self.prompt_timer.cancel()
        
        # Close the dialog
        self.dialog.destroy()
    
    def get_result(self):
        """Get the selected exception type."""
        return self.result


def show_exception_dialog(tracking_number=None, sku=None):
    """
    Show the exception selection dialog and return the selected exception type.
    
    Args:
        tracking_number: The tracking number being processed
        sku: The SKU being processed
        
    Returns:
        str: The selected exception type or None if cancelled
    """
    try:
        dialog = ExceptionSelectionDialog(
            title="Select Exception Type",
            tracking_number=tracking_number,
            sku=sku
        )
        return dialog.get_result()
    except Exception as e:
        logger.error(f"Error showing exception dialog: {str(e)}")
        return None

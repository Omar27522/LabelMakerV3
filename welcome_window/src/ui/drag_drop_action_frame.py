"""
Drag and Drop Action Frame for the Macro Editor.
This module provides a draggable and droppable frame for macro actions.
"""
import tkinter as tk
from tkinter import ttk
import logging

# Configure logging
logger = logging.getLogger(__name__)

class DragDropActionFrame(ttk.Frame):
    """A draggable and droppable frame for macro actions."""
    
    def __init__(self, parent, action_editor, on_drag_start=None, on_drag_drop=None):
        """
        Initialize the drag and drop action frame.
        
        Args:
            parent: The parent widget
            action_editor: The action editor frame to wrap
            on_drag_start: Callback for when drag starts
            on_drag_drop: Callback for when drop occurs
        """
        super().__init__(parent)
        
        self.action_editor = action_editor
        self.on_drag_start_callback = on_drag_start
        self.on_drag_drop_callback = on_drag_drop
        
        # Create a handle for dragging
        self.drag_handle = ttk.Label(self, text="☰", cursor="fleur")
        self.drag_handle.pack(side=tk.LEFT, padx=(0, 5))
        
        # Pack the action editor directly in this frame
        # This ensures the action editor is visible
        self.action_editor.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configure the drag handle for drag and drop
        self.drag_handle.bind("<ButtonPress-1>", self._on_drag_start)
        self.drag_handle.bind("<ButtonRelease-1>", self._on_drag_stop)
        self.drag_handle.bind("<B1-Motion>", self._on_drag_motion)
        
        # Track drag state
        self.dragging = False
        self.drag_start_y = 0
        self.drag_widget = None
        
        # Visual feedback for drag and drop
        self.drag_indicator = None
        
        # Configure style for visual feedback
        self.style = ttk.Style()
        self.style.configure("Dragging.TFrame", background="#CCE5FF")
        self.style.configure("DropTarget.TFrame", background="#E5FFCC")
        
        logger.debug("DragDropActionFrame initialized")
    
    def _on_drag_start(self, event):
        """
        Handle the start of a drag operation.
        
        Args:
            event: The event object
        """
        if not self.dragging:
            self.dragging = True
            self.drag_start_y = event.y_root
            self.drag_widget = event.widget
            
            # Change appearance to indicate dragging
            self.configure(style="Dragging.TFrame")
            
            # Call the callback if provided
            if self.on_drag_start_callback:
                self.on_drag_start_callback(self)
            
            logger.debug("Drag started")
    
    def _on_drag_stop(self, event):
        """
        Handle the end of a drag operation.
        
        Args:
            event: The event object
        """
        if self.dragging:
            self.dragging = False
            
            # Reset appearance
            self.configure(style="")
            
            # Find the drop target
            drop_target = self._find_drop_target(event.y_root)
            
            # Call the callback if provided and a valid drop target is found
            if drop_target and self.on_drag_drop_callback:
                self.on_drag_drop_callback(self, drop_target)
            
            # Remove any drag indicators
            self._remove_drag_indicator()
            
            logger.debug("Drag stopped")
    
    def _on_drag_motion(self, event):
        """
        Handle drag motion.
        
        Args:
            event: The event object
        """
        if self.dragging:
            # Find potential drop target
            drop_target = self._find_drop_target(event.y_root)
            
            # Show visual feedback for the drop target
            self._show_drop_indicator(drop_target)
            
            # Keep the drag within the vertical space (don't move horizontally)
            x = self.winfo_rootx()  # Keep the original x position
            self.master.update()
            
            logger.debug(f"Drag motion: y={event.y_root}")
    
    def _find_drop_target(self, y_position):
        """
        Find the drop target based on the current mouse position.
        
        Args:
            y_position: The current y position of the mouse
            
        Returns:
            The drop target frame or None if not found
        """
        # Get all sibling frames
        siblings = [w for w in self.master.winfo_children() 
                   if isinstance(w, DragDropActionFrame) and w != self]
        
        # Find the closest sibling based on y position
        closest = None
        min_distance = float('inf')
        
        for sibling in siblings:
            # Get the y coordinates of the sibling
            sibling_y1 = sibling.winfo_rooty()
            sibling_y2 = sibling_y1 + sibling.winfo_height()
            sibling_middle = (sibling_y1 + sibling_y2) / 2
            
            # Calculate distance to the middle of the sibling
            distance = abs(y_position - sibling_middle)
            
            # Only consider siblings that are within a reasonable distance (prevent far jumps)
            if distance < 50 and distance < min_distance:
                min_distance = distance
                closest = sibling
        
        return closest
    
    def _show_drop_indicator(self, drop_target):
        """
        Show a visual indicator for the drop target.
        
        Args:
            drop_target: The drop target frame
        """
        # Remove any existing indicator
        self._remove_drag_indicator()
        
        if drop_target:
            # Reset all siblings to normal style
            for sibling in self.master.winfo_children():
                if isinstance(sibling, DragDropActionFrame) and sibling != self:
                    sibling.configure(style="")
            
            # Highlight the drop target
            drop_target.configure(style="DropTarget.TFrame")
            
            logger.debug(f"Drop indicator shown for {drop_target}")
    
    def _remove_drag_indicator(self):
        """Remove any drag indicators."""
        # Reset all siblings to normal style
        for sibling in self.master.winfo_children():
            if isinstance(sibling, DragDropActionFrame) and sibling != self:
                sibling.configure(style="")
        
        logger.debug("Drop indicators removed")
    
    def get_action(self):
        """
        Get the action from the wrapped action editor.
        
        Returns:
            The action dictionary
        """
        return self.action_editor.get_action()
    
    def set_action(self, action):
        """
        Set the action in the wrapped action editor.
        
        Args:
            action: The action dictionary
        """
        self.action_editor.set_action(action)

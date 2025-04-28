import tkinter as tk
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class WindowPosition:
    x: int
    y: int

class WindowManager:
    def __init__(self):
        self._drag_data = {"x": 0, "y": 0, "item": None}
        self._windows: Dict[str, tk.Toplevel] = {}

    def create_window(self, title: str, parent: Optional[tk.Tk] = None) -> tk.Toplevel:
        """Create a new Toplevel window"""
        window = tk.Toplevel(parent)
        window.title(title)
        
        # Set window properties
        window.resizable(False, False)  # Make window non-resizable
        window.attributes('-toolwindow', True)  # Remove minimize/maximize buttons
        
        # Center window on screen
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')
        
        self._windows[title] = window
        return window

    def make_draggable(self, widget: tk.Widget) -> None:
        """Make a widget contribute to window dragging"""
        widget.bind('<Button-1>', self._start_drag)
        widget.bind('<B1-Motion>', self._drag)
        
        # Make all child widgets draggable too
        for child in widget.winfo_children():
            if isinstance(child, (tk.Frame, tk.LabelFrame)):
                self.make_draggable(child)
            else:
                child.bind('<Button-1>', self._start_drag)
                child.bind('<B1-Motion>', self._drag)

    def disable_dragging(self, widget: tk.Widget) -> None:
        """Remove dragging bindings from a widget"""
        widget.unbind('<Button-1>')
        widget.unbind('<B1-Motion>')
        
        # Remove from child widgets too
        for child in widget.winfo_children():
            child.unbind('<Button-1>')
            child.unbind('<B1-Motion>')

    def _start_drag(self, event: tk.Event) -> None:
        """Remember the starting position for the drag"""
        window = event.widget.winfo_toplevel()
        self._drag_data["x"] = event.x_root - window.winfo_x()
        self._drag_data["y"] = event.y_root - window.winfo_y()
        self._drag_data["item"] = window

    def _drag(self, event: tk.Event) -> None:
        """Handle the dragging motion"""
        if self._drag_data["item"] is None:
            return
            
        x = event.x_root - self._drag_data["x"]
        y = event.y_root - self._drag_data["y"]
        self._drag_data["item"].geometry(f"+{x}+{y}")

    def set_window_on_top(self, window: tk.Toplevel, on_top: bool) -> None:
        """Set window always-on-top state and apply transparency"""
        window.attributes('-topmost', on_top)
        if on_top:
            window.lift()
            # Use the configured transparency level instead of hardcoded value
            window.attributes('-alpha', window.master.config_manager.settings.transparency_level)
        else:
            window.attributes('-alpha', 1.0)  # Full opacity when not on top

    def focus_window(self, window: tk.Toplevel) -> None:
        """Focus and lift a window"""
        if window.winfo_exists():
            window.focus_force()
            window.lift()

    def close_window(self, title: str) -> None:
        """Close a specific window"""
        if title in self._windows and self._windows[title].winfo_exists():
            self._windows[title].destroy()
            del self._windows[title]

    def close_all_windows(self) -> None:
        """Close all managed windows"""
        for window in list(self._windows.values()):
            if window.winfo_exists():
                window.destroy()
        self._windows.clear()

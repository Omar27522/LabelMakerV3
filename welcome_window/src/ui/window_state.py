import tkinter as tk
from typing import List, Optional, Type, Any

class WindowState:
    """
    Manages the state of application windows
    Keeps track of open windows and provides methods to access them
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super(WindowState, cls).__new__(cls)
            cls._instance.windows = []
        return cls._instance
    
    def add_window(self, window: tk.Toplevel) -> None:
        """
        Add a window to the tracked windows list
        
        Args:
            window (tk.Toplevel): Window to track
        """
        if window not in self.windows:
            self.windows.append(window)
    
    def remove_window(self, window: tk.Toplevel) -> None:
        """
        Remove a window from the tracked windows list
        
        Args:
            window (tk.Toplevel): Window to remove
        """
        if window in self.windows:
            self.windows.remove(window)
    
    def get_window_by_type(self, window_type: Type) -> Optional[Any]:
        """
        Get the first window of the specified type
        
        Args:
            window_type (Type): Type of window to find
            
        Returns:
            Optional[Any]: Window instance if found, None otherwise
        """
        for window in self.windows:
            if isinstance(window, window_type):
                return window
        return None
    
    def get_windows_by_type(self, window_type: Type) -> List[Any]:
        """
        Get all windows of the specified type
        
        Args:
            window_type (Type): Type of window to find
            
        Returns:
            List[Any]: List of window instances
        """
        return [window for window in self.windows if isinstance(window, window_type)]
    
    def close_all_windows(self) -> None:
        """Close all tracked windows"""
        for window in self.windows[:]:  # Create a copy to avoid modification during iteration
            try:
                window.destroy()
            except:
                pass
            self.windows.remove(window)

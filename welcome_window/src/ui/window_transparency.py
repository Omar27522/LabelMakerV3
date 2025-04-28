"""
Window transparency management module for the Label Maker application.
This module provides functionality to make windows transparent when inactive.
"""

import tkinter as tk
import time

class TransparencyManager:
    """
    Manages window transparency for a tkinter window or frame.
    Makes the window transparent when inactive and opaque when active.
    """
    
    def __init__(self, window, opacity=0.7, enabled=True):
        """
        Initialize the transparency manager.
        
        Args:
            window: The tkinter window or frame to manage
            opacity: The opacity level when inactive (0.0 to 1.0)
            enabled: Whether transparency is enabled
        """
        self.window = window
        self.opacity = opacity
        self.enabled = enabled
        self.is_active = True
        
        # Store the original attributes
        self.original_attributes = {}
        
        # Bind focus events
        self.window.bind("<FocusIn>", self._on_focus_in)
        self.window.bind("<FocusOut>", self._on_focus_out)
        
        # Set initial state
        if self.enabled:
            self._make_opaque()
    
    def _on_focus_in(self, event=None):
        """Handle focus in event"""
        self.is_active = True
        if self.enabled:
            self._make_opaque()
    
    def _on_focus_out(self, event=None):
        """Handle focus out event"""
        self.is_active = False
        if self.enabled:
            self._make_transparent()
    
    def _make_transparent(self):
        """Make the window transparent"""
        try:
            # No need to save original attributes, just set transparency
            self.window.attributes("-alpha", self.opacity)
        except Exception as e:
            print(f"Error setting transparency: {str(e)}")
    
    def _make_opaque(self):
        """Make the window opaque"""
        try:
            # Restore full opacity
            self.window.attributes("-alpha", 1.0)
        except Exception as e:
            print(f"Error restoring opacity: {str(e)}")
    
    def set_enabled(self, enabled):
        """
        Enable or disable transparency.
        
        Args:
            enabled: Whether transparency should be enabled
        """
        self.enabled = enabled
        
        # Update the window state based on current focus
        if self.enabled:
            if self.is_active:
                self._make_opaque()
            else:
                self._make_transparent()
        else:
            # If disabled, ensure window is opaque
            self._make_opaque()
    
    def set_opacity(self, opacity):
        """
        Set the opacity level for inactive state.
        
        Args:
            opacity: Opacity level (0.0 to 1.0)
        """
        self.opacity = max(0.1, min(1.0, opacity))  # Clamp between 0.1 and 1.0
        
        # Update if currently transparent
        if self.enabled and not self.is_active:
            self._make_transparent()
            
        return self.opacity  # Return the actual (possibly clamped) value

def create_transparency_toggle_button(parent, variable, command=None):
    """
    Create a toggle button for transparency.
    
    Args:
        parent: Parent widget
        variable: BooleanVar to track the state
        command: Optional callback when toggled
        
    Returns:
        tk.Checkbutton: The created button
    """
    button = tk.Checkbutton(
        parent,
        text="Transparency",
        variable=variable,
        command=command,
        bg='white',
        activebackground='#f0f0f0',
        selectcolor='#e0e0e0'
    )
    
    return button

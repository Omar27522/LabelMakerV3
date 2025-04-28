"""
Sheet View module for Sheets Manager application.
"""
from ui.sheet_view_frame import SheetViewFrame

class SheetViewModule:
    """Sheet view module UI for Sheets Manager (logic wrapper)."""
    def __init__(self, parent, main_window=None, on_return=None):
        self.frame = SheetViewFrame(parent, main_window=main_window, on_return=on_return)

    def get_frame(self):
        return self.frame

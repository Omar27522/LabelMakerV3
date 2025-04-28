"""
Scripts Manager Module - Logic wrapper for Apps Script management UI.
"""

from ui.scripts_manager_frame import ScriptsManagerFrame

class ScriptsManagerModule:
    """
    Logic wrapper for the Scripts Manager UI.
    Handles Apps Script API integration, state, and provides the main frame.
    """
    def __init__(self, parent, on_back=None):
        self.frame = ScriptsManagerFrame(parent, on_back=on_back)

    def get_frame(self):
        return self.frame

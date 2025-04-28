from ui.google_sheets_connection_frame import GoogleSheetsConnectionFrame

class ConnectionModule:
    """Connection module UI for Sheets Manager (logic wrapper)."""
    def __init__(self, parent, on_connect=None):
        self.frame = GoogleSheetsConnectionFrame(parent, on_verified=on_connect)
    def get_frame(self):
        return self.frame

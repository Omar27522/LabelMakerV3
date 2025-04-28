from ui.welcome_frame import WelcomeFrame

class WelcomeModule:
    """Welcome module UI for Sheets Manager (logic wrapper)."""
    def __init__(self, parent, on_start=None):
        self.frame = WelcomeFrame(parent, on_start=on_start)
    def get_frame(self):
        return self.frame

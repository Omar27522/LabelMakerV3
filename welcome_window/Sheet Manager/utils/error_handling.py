import logging
import tkinter as tk


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for uncaught exceptions in the app."""
    if issubclass(exc_type, KeyboardInterrupt):
        return
    logging.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
    try:
        error_msg = f"An unexpected error occurred:\n\n{str(exc_value)}\n\nPlease check the logs for details."
        tk.messagebox.showerror("Error", error_msg)
    except Exception:
        pass

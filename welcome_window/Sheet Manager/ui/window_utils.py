import os
import tkinter as tk


def set_taskbar_icon(root):
    """Set the taskbar icon for the main window, searching multiple asset paths."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "..", "assets", "icon_64.png")
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)
            root._icon = icon
            print(f"Successfully set taskbar icon from {icon_path}")
            return
        # Try alternate path in Sheet Manager assets/icon/icon_64.png
        icon_path_alt = os.path.join(script_dir, "..", "assets", "icon", "icon_64.png")
        if os.path.exists(icon_path_alt):
            icon = tk.PhotoImage(file=icon_path_alt)
            root.iconphoto(True, icon)
            root._icon = icon
            print(f"Successfully set alternate taskbar icon from {icon_path_alt}")
            return
        global_icon_path = os.path.abspath(os.path.join(script_dir, "..", "..", "assets", "returnsdata_64.png"))
        if os.path.exists(global_icon_path):
            icon = tk.PhotoImage(file=global_icon_path)
            root.iconphoto(True, icon)
            root._icon = icon
            print(f"Successfully set global suite icon from {global_icon_path}")
            return
        # Only warn if all options are missing
        import logging
        logging.warning(f"No icon file found at {icon_path}, {icon_path_alt}, or {global_icon_path}")
    except Exception as e:
        import logging
        logging.error(f"Failed to set taskbar icon: {str(e)}")

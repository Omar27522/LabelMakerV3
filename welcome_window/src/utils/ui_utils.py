"""
UI utility functions for the Label Maker application.
"""
import tkinter as tk

def center_window(window):
    """
    Center a window on the screen.
    
    Args:
        window (tk.Toplevel or tk.Tk): The window to center
    """
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def create_button(parent, text, command, bg='#2196F3', fg='white', font=("Arial", 10), 
                 activebackground=None, activeforeground='white', padx=15, pady=5):
    """
    Create a styled button.
    
    Args:
        parent (tk.Widget): Parent widget
        text (str): Button text
        command (callable): Button command
        bg (str): Background color
        fg (str): Foreground color
        font (tuple): Font specification
        activebackground (str): Active background color
        activeforeground (str): Active foreground color
        padx (int): Horizontal padding
        pady (int): Vertical padding
        
    Returns:
        tk.Button: The created button
    """
    if activebackground is None:
        # Darken the background color by default
        r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
        r = max(0, r - 20)
        g = max(0, g - 20)
        b = max(0, b - 20)
        activebackground = f'#{r:02x}{g:02x}{b:02x}'
    
    button = tk.Button(
        parent,
        text=text,
        font=font,
        bg=bg,
        fg=fg,
        activebackground=activebackground,
        activeforeground=activeforeground,
        relief=tk.FLAT,
        padx=padx,
        pady=pady,
        command=command
    )
    return button

def make_window_modal(window, parent):
    """
    Make a window modal (blocks interaction with parent).
    
    Args:
        window (tk.Toplevel): The window to make modal
        parent (tk.Tk or tk.Toplevel): The parent window
    """
    window.transient(parent)  # Make dialog modal
    window.grab_set()  # Make dialog modal
    window.focus_force()  # Focus the window
    
    # Make sure window appears on top
    window.lift()
    window.attributes('-topmost', True)
    window.after_idle(window.attributes, '-topmost', False)

def create_modal_dialog(parent, title, width=400, height=300):
    """
    Create a modal dialog window
    
    Args:
        parent: Parent window
        title: Dialog title
        width: Dialog width
        height: Dialog height
        
    Returns:
        dialog: The created dialog
    """
    # Create dialog window
    window = tk.Toplevel(parent)
    window.title(title)
    window.geometry(f"{width}x{height}")
    window.resizable(False, False)
    window.configure(bg='white')
    
    # Center the dialog
    center_window(window)
    
    return window

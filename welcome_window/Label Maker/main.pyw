import os
import sys
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from PIL import Image, ImageTk
import ctypes
import traceback
import atexit
import win32event
import win32api
import win32con
import winerror
from win32com.client import GetObject
import win32gui
import win32process

# Set DPI awareness before creating any windows
# This prevents scaling issues when interacting with system dialogs
try:
    # Try the newer API first (Windows 10+)
    awareness = ctypes.c_int(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
except AttributeError:
    # Fall back to older API (Windows 8.1 and earlier)
    ctypes.windll.user32.SetProcessDPIAware()
except Exception as e:
    # If it fails, just log it and continue
    print(f"Failed to set DPI awareness: {e}")

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.utils.logger import setup_logger
from src.ui.main_window import MainWindow

# Setup logger
logger = setup_logger()

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default handler for KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

    # Show error message to user
    try:
        error_msg = f"An unexpected error occurred:\n\n{str(exc_value)}\n\nPlease check the logs for details."
        tk.messagebox.showerror("Error", error_msg)
    except:
        pass  # If showing the error dialog fails, at least we logged the error

def bring_to_front():
    """Find and bring the existing instance to front"""
    try:
        # Get all windows with our app ID
        def enum_windows_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                # Look for our main window title
                if "Label Maker" in window_text:  # Adjust this to match your window title
                    results.append(hwnd)
            return True

        results = []
        win32gui.EnumWindows(enum_windows_callback, results)
        
        if results:
            # Found our window
            hwnd = results[0]
            # Force the window to be redrawn
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            # Restore if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # Force to front
            win32gui.SetForegroundWindow(hwnd)
            # Additional force-focus techniques
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetActiveWindow(hwnd)
            # Flash window to get user's attention
            win32gui.FlashWindow(hwnd, True)
        else:
            logger.warning("Could not find existing window")
                
    except Exception as e:
        logger.error(f"Error bringing window to front: {e}")

def cleanup():
    """Cleanup resources before exit"""
    logger.info("Application shutting down")
    try:
        # Use system temp directory instead of relative path
        temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, file))
                except:
                    pass
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def set_taskbar_icon(root):
    """Set the taskbar icon and Windows taskbar icon"""
    try:
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the icon file
        icon_path = os.path.join(script_dir, "assets", "icon_64.png")

        if os.path.exists(icon_path):
            # Load and set the icon using PhotoImage for the window icon
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)

            # Convert PNG to ICO for the taskbar
            img = Image.open(icon_path)
            # Keep reference to prevent garbage collection
            root.icon_image = ImageTk.PhotoImage(img)

            # Set the Windows taskbar icon
            myappid = 'com.codeium.labelmaker.1.0'  # Arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        else:
            logger.warning(f"Icon file not found at {icon_path}")
    except Exception as e:
        logger.error(f"Failed to set taskbar icon: {str(e)}")

def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename"""
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*\'"'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove any other non-printable characters
    name = ''.join(char for char in name if char.isprintable())
    return name

def process_product_name(full_name: str) -> tuple[str, str, str]:
    """Process product name into name_line1, name_line2, and variant"""
    # Split by the last dash to separate variant
    name_parts = full_name.rsplit('-', 1)
    base_name = name_parts[0].strip()
    variant = name_parts[1].strip() if len(name_parts) > 1 else ""

    # Split base name into lines, respecting max lengths
    words = base_name.split()
    line1 = []
    line2 = []
    current_line1 = ""

    # Build first line (max 18 chars)
    for word in words:
        test_line = (current_line1 + " " + word).strip()
        if len(test_line) <= 18:
            line1.append(word)
            current_line1 = test_line
        else:
            break

    # Remaining words go to second line (max 20 chars)
    remaining_words = words[len(line1):]
    current_line2 = ""
    for word in remaining_words:
        test_line = (current_line2 + " " + word).strip()
        if len(test_line) <= 20:
            line2.append(word)
            current_line2 = test_line
        else:
            break

    name_line1 = " ".join(line1)
    name_line2 = " ".join(line2)

    return name_line1, name_line2, variant

def is_valid_barcode(barcode: str) -> bool:
    """Check if barcode consists of exactly 12 digits"""
    import re
    # Match only if the entire string is exactly 12 digits
    return bool(re.match(r'^\d{12}$', barcode))

def create_batch_labels(csv_path, main_window):
    """Create labels in batch from a CSV file"""
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)

        # Get save directory from settings or use default
        save_dir = main_window.config_manager.settings.last_directory
        if not os.path.exists(save_dir):
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "Labels")
            os.makedirs(save_dir, exist_ok=True)

        labels_created = 0
        skipped_labels = 0

        # Process each row
        for _, row in df.iterrows():
            barcode = str(row['Upc'])

            # Skip if barcode is invalid
            if not is_valid_barcode(barcode):
                skipped_labels += 1
                logger.warning(f"Skipping invalid barcode: {barcode}")
                continue

            full_name = str(row['Label Name'])

            # Process the product name
            name_line1, name_line2, variant = process_product_name(full_name)

            # Create label data
            from src.barcode_generator import LabelData
            label_data = LabelData(
                name_line1=name_line1,
                name_line2=name_line2,
                variant=variant,
                upc_code=barcode
            )

            # Generate the label
            label_image = main_window.barcode_generator.generate_label(label_data)
            if label_image:
                # Create filename in old format: NAME Second NAME_Variant_label_123456789123
                safe_name1 = sanitize_filename(name_line1)
                safe_name2 = sanitize_filename(name_line2) if name_line2 else ""
                safe_variant = sanitize_filename(variant)

                if safe_name2:
                    filename = f"{safe_name1} {safe_name2}_{safe_variant}_label_{barcode}.png"
                else:
                    filename = f"{safe_name1}_{safe_variant}_label_{barcode}.png"

                filepath = os.path.join(save_dir, filename)
                label_image.save(filepath)
                labels_created += 1

                # Update label counter in settings
                main_window.config_manager.settings.label_counter += 1
                main_window.png_count.set(f"Labels: {main_window.config_manager.settings.label_counter}")

        # Save settings
        main_window.config_manager.save_settings()

        message = f"Created {labels_created} labels in:\n{save_dir}"
        if skipped_labels > 0:
            message += f"\n\nSkipped {skipped_labels} items with invalid barcodes"

        messagebox.showinfo("Success", message)

    except Exception as e:
        logger.error(f"Error creating batch labels: {str(e)}")
        messagebox.showerror("Error", f"Failed to create batch labels: {str(e)}")

def setup_window():
    """Initialize and configure the main window"""
    try:
        # Register cleanup function
        atexit.register(cleanup)

        # Create and configure main window
        root = MainWindow()

        # Set taskbar icon
        set_taskbar_icon(root)

        # Return the root window
        return root

    except Exception as e:
        logger.error(f"Failed to setup window: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Create a mutex for single instance
        mutex_name = "Global\\label_maker_app_mutex"
        mutex = win32event.CreateMutex(None, False, mutex_name)
        last_error = win32api.GetLastError()
        
        if last_error == winerror.ERROR_ALREADY_EXISTS:
            # Another instance is running
            win32api.CloseHandle(mutex)
            # Try to bring the existing window to front
            bring_to_front()
            sys.exit(0)
            
        # Set the app ID for Windows taskbar
        try:
            myappid = 'labelmaker.app.ver3.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass  # Fail silently if Windows-specific call fails

        # Set up exception handling
        sys.excepthook = handle_exception

        # Initialize and configure the main window
        root = setup_window()
        
        # Check for command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--view-files":
            # Schedule the view_directory_files method to run after the main window is fully loaded
            root.after(500, root.view_directory_files)
            
        # Start the application
        root.mainloop()

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        # Show error dialog
        try:
            tk.messagebox.showerror(
                "Fatal Error",
                f"A fatal error occurred while starting the application:\n\n{str(e)}\n\n"
                "Please check the logs for details."
            )
        except:
            pass  # If showing the error dialog fails, at least we logged the error
        sys.exit(1)  # Exit with error code
    finally:
        # Clean up mutex when the program exits
        if 'mutex' in locals():
            win32api.CloseHandle(mutex)

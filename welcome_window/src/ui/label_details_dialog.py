"""
Label Details Dialog for the Label Maker application.
This module provides a dialog for viewing detailed information about a label.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import webbrowser
from PIL import Image, ImageTk
import threading
import tempfile
import pyautogui

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_colored_button
from src.utils.file_utils import find_files_by_sku
from src.utils.barcode_operations import print_barcode

class LabelDetailsDialog(tk.Toplevel):
    """Dialog for displaying label details"""
    
    def __init__(self, parent, record, config_manager):
        """
        Initialize the Label Details Dialog
        
        Args:
            parent: Parent widget
            record: Dictionary containing label record data
            config_manager: Configuration manager instance
        """
        super().__init__(parent)
        
        # Store references
        self.parent = parent
        self.record = record
        self.config_manager = config_manager
        self.label_files = []
        

        
        # Mirror print setting
        self.mirror_print = tk.BooleanVar(value=False)
        if hasattr(self.config_manager, 'settings') and hasattr(self.config_manager.settings, 'mirror_print'):
            self.mirror_print.set(self.config_manager.settings.mirror_print)
        
        # Configure dialog
        self.title(f"Label Details: {record.get('label_name', 'Unknown')}")
        self.geometry("800x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Set dialog position centered on parent
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
        
        # Status variable
        self.status_var = tk.StringVar(value="Loading label information...")
        
        # Create UI
        self._create_ui()
        
        # Load label files in background
        self._load_label_files()
        
        # Make dialog modal
        self.focus_set()
        self.wait_window()
    
    def _add_copy_menu(self, widget, value):
        """Attach a right-click menu to a label widget for copying its value."""
        def copy_to_clipboard(event=None):
            self.clipboard_clear()
            self.clipboard_append(value)
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Copy", command=copy_to_clipboard)
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        widget.bind("<Button-3>", show_menu)

    def _create_ui(self):
        """Create the user interface elements"""
        # Create main container with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title with label name
        title_label = ttk.Label(
            main_frame, 
            text=self.record.get('label_name', 'Unknown Label'),
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Create details frame
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill='both', expand=True)
        
        # Left column - Label information (make it thinner)
        info_frame = ttk.LabelFrame(details_frame, text="Label Information", width=300)
        info_frame.pack(side='left', fill='both', expand=False, padx=(0, 10))
        info_frame.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents
        
        # Create a canvas with scrollbar for the info frame
        canvas = tk.Canvas(info_frame, width=280)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add label information fields
        fields = [
            ("UPC", "upc"),
            ("Department", "department"),
            ("Category", "category"),
            ("Color", "color"),
            ("Website Color", "website_color"),
            ("Website Name", "website_name")
        ]
        
        # Add variant information with prefix highlighted (insert at the beginning)
        variant_value = self.record.get('item_variant_number', '')
        
        # Add prefix row
        prefix_frame = ttk.Frame(scrollable_frame)
        prefix_frame.pack(fill='x', padx=10, pady=5)
        
        prefix_label = ttk.Label(prefix_frame, text="Variant Prefix:", width=15, anchor='w')
        prefix_label.pack(side='left', padx=(0, 10))
        
        # Extract the first 6 digits as the prefix
        prefix = variant_value[:6] if len(variant_value) >= 6 else variant_value
        prefix_value_label = ttk.Label(prefix_frame, text=prefix, wraplength=150, font=('Arial', 10, 'bold'))
        prefix_value_label.pack(side='left', fill='x', expand=True)
        self._add_copy_menu(prefix_value_label, prefix)
        
        # Add variant row (remainder without prefix)
        variant_frame = ttk.Frame(scrollable_frame)
        variant_frame.pack(fill='x', padx=10, pady=5)
        
        variant_label = ttk.Label(variant_frame, text="Variant:", width=15, anchor='w')
        variant_label.pack(side='left', padx=(0, 10))
        
        # Extract the remainder of the variant without the prefix
        variant_remainder = variant_value[6:] if len(variant_value) >= 6 else ""
        variant_value_label = ttk.Label(variant_frame, text=variant_remainder, wraplength=150)
        variant_value_label.pack(side='left', fill='x', expand=True)
        self._add_copy_menu(variant_value_label, variant_remainder)
        
        # Add each field to the scrollable frame
        for i, (label_text, field_name) in enumerate(fields):
            # Create frame for this field
            field_frame = ttk.Frame(scrollable_frame)
            field_frame.pack(fill='x', padx=10, pady=5)
            
            # Label
            label = ttk.Label(field_frame, text=f"{label_text}:", width=15, anchor='w')
            label.pack(side='left', padx=(0, 10))
            
            # Value
            value = self.record.get(field_name, "")
            value_label = ttk.Label(field_frame, text=value, wraplength=150)
            value_label.pack(side='left', fill='x', expand=True)
            self._add_copy_menu(value_label, value)
        

        
        # Right column - Label Preview (replacing the files list)
        preview_frame = ttk.LabelFrame(details_frame, text="Label")
        preview_frame.pack(side='right', fill='both', expand=True)
        
        # Create a frame for the image preview
        self.image_frame = ttk.Frame(preview_frame)
        self.image_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create a label for the image
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(fill='both', expand=True)
        
        # Create a label for showing when no image is available
        self.no_image_label = ttk.Label(
            self.image_frame, 
            text="No label image available",
            font=("Arial", 12),
            foreground="gray"
        )
        
        # Add buttons for actions
        buttons_frame = ttk.Frame(preview_frame)
        buttons_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Open button
        open_button = create_colored_button(
            buttons_frame,
            text="Open",
            color="#4CAF50", 
            hover_color="#45a049",
            command=self._open_selected_file
        )
        open_button.pack(side='left', padx=(0, 5))
        
        # Print button
        print_button = create_colored_button(
            buttons_frame,
            text="Print",
            color="#2196F3", 
            hover_color="#0b7dda",
            command=self._print_selected_file
        )
        print_button.pack(side='left', padx=5)
        
        # Mirror print checkbox
        mirror_check = ttk.Checkbutton(
            buttons_frame,
            text="Mirror Print",
            variable=self.mirror_print,
            command=self._toggle_mirror_print
        )
        mirror_check.pack(side='right')
        
        # Separator
        ttk.Separator(main_frame).pack(fill='x', pady=15)
        
        # Bottom buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        # Close button
        close_button = ttk.Button(
            buttons_frame,
            text="Close",
            command=self.destroy
        )
        close_button.pack(side='right')
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', side='bottom', pady=(10, 0))
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side='left')
    
    def _load_label_files(self):
        """Load label files in a background thread and display the first one"""
        def find_files_thread():
            try:
                # Get SKU from record
                sku = self.record.get('sku') or self.record.get('item_variant_number')
                if not sku:
                    self.after(0, lambda: self._update_status("No SKU available to find label files"))
                    self.after(0, self._show_no_image)
                    return
                
                # Update status
                self.after(0, lambda: self._update_status(f"Searching for label files with SKU: {sku}"))
                
                # Find files by SKU
                label_dirs = []
                try:
                    # Try to get label directories from config
                    if hasattr(self.config_manager, 'settings') and hasattr(self.config_manager.settings, 'label_directories'):
                        label_dirs = self.config_manager.settings.label_directories
                    # Fallback to last_directory if label_directories is not available
                    elif hasattr(self.config_manager, 'settings') and hasattr(self.config_manager.settings, 'last_directory'):
                        last_dir = self.config_manager.settings.last_directory
                        if last_dir and os.path.exists(last_dir):
                            label_dirs = [last_dir]
                except Exception as e:
                    print(f"Error accessing config settings: {e}")
                
                if not label_dirs:
                    self.after(0, lambda: self._update_status("No label directories configured"))
                    self.after(0, self._show_no_image)
                    return
                
                # Search for label files
                found_files = []
                for directory in label_dirs:
                    if os.path.exists(directory):
                        files = find_files_by_sku(directory, sku)
                        found_files.extend(files)
                
                # Store the found files
                self.label_files = found_files
                
                # Update the UI
                if found_files:
                    self.after(0, lambda: self._display_label_image(found_files[0]))
                    self.after(0, lambda: self._update_status(f"Found {len(found_files)} label files"))
                else:
                    self.after(0, self._show_no_image)
                    self.after(0, lambda: self._update_status("No label files found for this SKU"))
                
            except Exception as e:
                print(f"Error finding label files: {e}")
                self.after(0, lambda: self._update_status(f"Error: {str(e)}"))
                self.after(0, self._show_no_image)
        
        # Start thread
        threading.Thread(target=find_files_thread).start()
    
    def _display_label_image(self, file_path):
        """Display the label image in the preview panel"""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                self._show_no_image()
                self._update_status(f"File not found: {file_path}")
                return
            
            # Check file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
                self._show_no_image()
                self._update_status(f"File is not a supported image format: {file_path}")
                return
                
            # Check if file is an image
            try:
                # Open the image file
                image = Image.open(file_path)
                
                # Calculate the size to fit in the frame while maintaining aspect ratio
                frame_width = self.image_frame.winfo_width() - 20  # Subtract padding
                frame_height = self.image_frame.winfo_height() - 20  # Subtract padding
                
                # If frame hasn't been drawn yet, use reasonable defaults
                if frame_width <= 0:
                    frame_width = 400
                if frame_height <= 0:
                    frame_height = 400
                
                # Calculate the resize ratio
                img_width, img_height = image.size
                width_ratio = frame_width / img_width
                height_ratio = frame_height / img_height
                ratio = min(width_ratio, height_ratio)
                
                # Calculate new dimensions
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                # Resize the image - handle different versions of PIL/Pillow
                try:
                    # For newer versions of Pillow
                    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
                except AttributeError:
                    try:
                        # For older versions of Pillow
                        resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
                    except AttributeError:
                        # Fallback for very old versions
                        resized_image = image.resize((new_width, new_height))
                
                # Convert to PhotoImage
                self.photo_image = ImageTk.PhotoImage(resized_image)
                
                # Hide the no image label if it's visible
                self.no_image_label.pack_forget()
                
                # Update the image label
                self.image_label.configure(image=self.photo_image)
                self.image_label.pack(fill='both', expand=True)
                
                # Update status
                self._update_status(f"Displaying label image: {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"Error loading image: {e}")
                self._show_no_image()
                self._update_status(f"Error loading image: {str(e)}")
                
        except Exception as e:
            print(f"Error displaying image: {e}")
            self._show_no_image()
            self._update_status(f"Error displaying image: {str(e)}")
    
    def _show_no_image(self):
        """Show the 'no image available' message"""
        try:
            # Hide the image label
            self.image_label.pack_forget()
            
            # Show the no image label
            self.no_image_label.pack(fill='both', expand=True)
        except Exception as e:
            print(f"Error showing no image message: {e}")
    
    def _open_selected_file(self, event=None):
        """Open the first label file"""
        if not self.label_files:
            messagebox.showinfo("No Files Found", "No label files were found for this SKU")
            return
        
        # Get the first file path
        file_path = self.label_files[0]
        
        try:
            # Open file with default application
            os.startfile(file_path)
            self._update_status(f"Opened file: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error Opening File", f"Could not open file: {str(e)}")
            
    def _print_selected_file(self):
        """Print the first label file"""
        if not self.label_files:
            messagebox.showinfo("No Files Found", "No label files were found for this SKU")
            return
        
        # Get the first file path
        file_path = self.label_files[0]
        
        try:
            # Print the file using the barcode_operations utility
            success, message = print_barcode(
                file_path, 
                mirror_print=self.mirror_print.get(),
                status_callback=lambda msg, color: self._update_status(msg)
            )
            
            if success:
                self._update_status(f"Sent to printer: {os.path.basename(file_path)}")
                # Wait for the print dialog to appear and press Enter
                print("Waiting for print dialog to appear...")
                self.after(1000, self._press_enter_for_print_dialog)
            else:
                messagebox.showerror("Error Printing File", message)
                self._update_status(f"Error printing: {message}")
        except Exception as e:
            messagebox.showerror("Error Printing File", f"Could not print file: {str(e)}")
            
    def _toggle_mirror_print(self):
        """Toggle the mirror print setting and save to config"""
        # Update the config if available
        if hasattr(self.config_manager, 'settings'):
            self.config_manager.settings.mirror_print = self.mirror_print.get()
            if hasattr(self.config_manager, 'save_settings'):
                self.config_manager.save_settings()
                
        # Update status
        if self.mirror_print.get():
            self._update_status("Mirror print enabled")
        else:
            self._update_status("Mirror print disabled")
    
    def _press_enter_for_print_dialog(self):
        """Press Enter key to confirm print dialog"""
        try:
            print("Pressing Enter to confirm print dialog...")
            pyautogui.press('enter')
            print("Enter key pressed")
        except Exception as e:
            print(f"Error pressing Enter: {str(e)}")
    
    def _update_status(self, message):
        """Update the status message"""
        self.status_var.set(message)
        


def create_label_details_dialog(parent, record, config_manager):
    """
    Create and return a Label Details Dialog
    
    Args:
        parent: Parent widget
        record: Dictionary containing label record data
        config_manager: Configuration manager instance
        
    Returns:
        LabelDetailsDialog: The created dialog
    """
    return LabelDetailsDialog(parent, record, config_manager)

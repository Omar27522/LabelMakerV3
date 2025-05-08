import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, Callable
import os
import sys
from PIL import Image, ImageTk
import pyautogui
import pandas as pd
from ..config import ConfigManager
from ..utils.logger import setup_logger
from .window_manager import WindowManager
from ..barcode_generator import BarcodeGenerator, LabelData
from ..utils.csv_processor import is_valid_barcode, process_product_name, sanitize_filename
import time
import re

# Get logger instance
logger = setup_logger()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize window tracking
        self.app_windows = []  # Track all windows
        self.app_windows.append(self)  # Include main window
        
        self.config_manager = ConfigManager()
        self.window_manager = WindowManager()
        self.barcode_generator = BarcodeGenerator(self.config_manager.settings)
        
        # Add tracking for last printed label
        self.last_print_time = None
        self.last_printed_upc = None
        
        # Add auto-switch state
        self.is_auto_switch = tk.BooleanVar(value=True)  # Default to auto-switch enabled
        
        # Set initial transparency
        self.attributes('-alpha', self.config_manager.settings.transparency_level)
        
        self._setup_fonts()
        self._setup_variables()
        self._load_icons()
        self._create_tooltip_class()
        self._create_main_window()
        
        # Bind focus event to main window
        self.bind("<FocusIn>", lambda e: self._on_window_focus(self))

    def view_directory_files(self):
        """View files in the current directory"""
        # If file window exists and is valid, focus it
        if hasattr(self, 'file_window') and self.file_window and self.file_window.winfo_exists():
            self.file_window.deiconify()  # Ensure window is not minimized
            self.file_window.lift()       # Bring to front
            self.file_window.focus_force() # Force focus
            return

        if not self.config_manager.settings.last_directory:
            messagebox.showinfo("Info", "Please select a directory first.")
            return

        # Create view files window
        self.file_window = tk.Toplevel(self)
        self.file_window.title("View Files")
        self.file_window.geometry("600x400")  # Default size
        self.file_window.minsize(375, 200)    # Minimum size
        
        # Add keyboard shortcuts
        self.file_window.bind('<Control-o>', lambda e: self.open_selected_file())
        self.file_window.bind('<Control-p>', lambda e: self.print_selected_file())
        
        # Enable window resizing and add maximize/minimize buttons
        self.file_window.resizable(True, True)
        
        # Set window icon using viewfiles-specific icon
        self._set_window_icon(self.file_window, '32', 'viewfiles')
        
        # Bind focus events
        self.file_window.bind("<FocusIn>", lambda e: self._on_window_focus(self.file_window))
        
        # Give initial focus
        self.file_window.focus_set()

        # Create main content frame
        main_content = tk.Frame(self.file_window)
        main_content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Create top frame for controls
        top_frame = tk.Frame(main_content)
        top_frame.pack(fill=tk.X, padx=0, pady=1)

        # Add Pin (Always on Top) button
        window_always_on_top = tk.BooleanVar(value=self.config_manager.settings.view_files_pin_window)
        window_top_btn = tk.Button(top_frame, text="📌", bg='#C71585', relief='raised', width=3,
                                font=('TkDefaultFont', 14))

        def toggle_window_on_top():
            current_state = window_always_on_top.get()
            self.file_window.attributes('-topmost', current_state)
            if current_state:
                self.file_window.lift()
                window_top_btn.config(
                    text="📌",
                    bg='#90EE90',  # Light green when active
                    relief='sunken'
                )
            else:
                window_top_btn.config(
                    text="📌",
                    bg='#C71585',  # Velvet color when inactive
                    relief='raised'
                )
            # Save the pin state
            self.config_manager.settings.view_files_pin_window = current_state
            self.config_manager.save_settings()

        window_top_btn.config(
            command=lambda: [window_always_on_top.set(not window_always_on_top.get()), 
                           toggle_window_on_top()]
        )
        window_top_btn.pack(side=tk.LEFT, padx=2)
        
        # Apply initial pin state
        if window_always_on_top.get():
            toggle_window_on_top()
        
        # Add tooltip after button is fully configured
        self.CreateToolTip(window_top_btn, "Keep window on top of other windows")

        # Add Label Count display
        label_count_label = tk.Label(
            top_frame,
            text="",  # Will be set by update_file_list
            font=('TkDefaultFont', 10, 'bold'),
            fg='#2ecc71'  # Green text
        )
        label_count_label.pack(side=tk.LEFT, padx=10)

        # Add Magnifier button
        is_magnified = tk.BooleanVar(value=False)
        magnifier_btn = tk.Button(top_frame, text="🔍", bg='#C71585', relief='raised', width=3,
                                font=('TkDefaultFont', 14))

        def toggle_magnification():
            current_state = is_magnified.get()
            new_size = 16 if current_state else 9
            self.listbox.configure(font=('TkDefaultFont', new_size))
            if current_state:
                h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            else:
                h_scrollbar.pack_forget()
            magnifier_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )

        magnifier_btn.config(
            command=lambda: [is_magnified.set(not is_magnified.get()), 
                           toggle_magnification()]
        )
        magnifier_btn.pack(side=tk.LEFT, padx=2)
        
        # Add tooltip after button is fully configured
        self.CreateToolTip(magnifier_btn, "Toggle list text size")

        # Add preview size control with cycling states
        preview_size = tk.IntVar(value=3)  # Default to largest size
        
        def cycle_preview_size():
            """Cycle through preview sizes: 1 -> 2 -> 3 -> 1"""
            current = preview_size.get()
            next_size = current + 1 if current < 3 else 1
            preview_size.set(next_size)
            # Update button appearance based on size
            colors = {1: '#C71585', 2: '#90EE90', 3: '#4169E1'}  # Different color for each state
            zoom_btn.config(bg=colors[next_size])
            # Refresh preview with new size
            show_preview(None)

        # Create and configure zoom button with plus icon
        zoom_btn = tk.Button(top_frame, text="➕", bg='#4169E1', relief='raised', width=3,  # Start with size 3 color
                          font=('TkDefaultFont', 14),
                          command=cycle_preview_size)
        zoom_btn.pack(side=tk.LEFT, padx=2)
        
        # Add tooltip after button is fully configured
        self.CreateToolTip(zoom_btn, "Cycle through preview sizes (1-3)")

        # Add mirror print toggle button
        self.is_mirror_print = tk.BooleanVar(value=self.config_manager.settings.view_files_mirror_print)
        mirror_btn = tk.Button(top_frame, text=" 🖨️ ", bg='#C71585', relief='raised', width=3,
                             font=('TkDefaultFont', 14), anchor='center')

        def toggle_mirror_print():
            current_state = self.is_mirror_print.get()
            mirror_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )
            # Save the mirror print state
            self.config_manager.settings.view_files_mirror_print = current_state
            self.config_manager.save_settings()

        mirror_btn.config(
            command=lambda: [self.is_mirror_print.set(not self.is_mirror_print.get()),
                           toggle_mirror_print()]
        )
        mirror_btn.pack(side=tk.LEFT, padx=2)
        
        # Apply initial mirror state
        if self.is_mirror_print.get():
            toggle_mirror_print()
        
        # Add tooltip after button is fully configured
        self.CreateToolTip(mirror_btn, "Toggle mirror printing")
        
        # Add auto-switch toggle button
        self.is_auto_switch = tk.BooleanVar(value=self.config_manager.settings.view_files_auto_switch)
        auto_switch_btn = tk.Button(top_frame, text=" ⚡ ", bg='#C71585', relief='raised', width=3,
                                  font=('TkDefaultFont', 14), anchor='center')
        
        def toggle_auto_switch():
            current_state = self.is_auto_switch.get()
            auto_switch_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )
            # Save the auto-switch state
            self.config_manager.settings.view_files_auto_switch = current_state
            self.config_manager.save_settings()

        auto_switch_btn.config(
            command=lambda: [self.is_auto_switch.set(not self.is_auto_switch.get()),
                           toggle_auto_switch()]
        )
        
        # Apply initial auto-switch state
        toggle_auto_switch()
        
        auto_switch_btn.pack(side=tk.LEFT, padx=2)
        
        # Add tooltip after button is fully configured
        self.CreateToolTip(auto_switch_btn, "Toggle auto-switch to next item after printing")

        # Add print minimize toggle button
        self.is_print_minimize = tk.BooleanVar(value=self.config_manager.settings.view_files_print_minimize)
        print_minimize_btn = tk.Button(top_frame, text=" 📄 ", bg='#C71585', relief='raised', width=3,
                                  font=('TkDefaultFont', 14), anchor='center')
        
        def toggle_print_minimize():
            current_state = self.is_print_minimize.get()
            print_minimize_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )
            # Save the print minimize state
            self.config_manager.settings.view_files_print_minimize = current_state
            self.config_manager.save_settings()

        print_minimize_btn.config(
            command=lambda: [self.is_print_minimize.set(not self.is_print_minimize.get()),
                           toggle_print_minimize()]
        )
        
        # Apply initial print minimize state
        toggle_print_minimize()
        
        print_minimize_btn.pack(side=tk.LEFT, padx=2)
        
        # Add tooltip after button is fully configured
        self.CreateToolTip(print_minimize_btn, "Toggle print minimize")

        # Create search frame
        search_frame = tk.Frame(main_content)
        search_frame.pack(fill=tk.X, padx=0, pady=6)

        tk.Label(search_frame, text="Find:", 
                font=('TkDefaultFont', 11, 'bold')).pack(side=tk.LEFT, padx=(4,2))
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, 
                              font=('TkDefaultFont', 11))
        
        # Add undo/redo support using our custom implementation
        self._add_undo_support(search_entry, search_var)
        
        # Auto-select contents when entry gets focus
        def select_all(event):
            # Store current selection before modifying the entry
            current_selection = self.listbox.curselection()
            
            # Select all text in the entry
            event.widget.select_range(0, tk.END)
            
            # Restore listbox selection if there was one
            if current_selection:
                self.listbox.selection_set(current_selection)
                
            return "break"  # Prevents default behavior
            
        search_entry.bind('<FocusIn>', select_all)
        
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=6)
        search_entry.focus_set()
        
        # Add context menu to search entry
        self._add_context_menu(search_entry)

        # Create list frame with preview side by side
        list_frame = tk.Frame(main_content)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=1)

        # Left side for file list
        left_frame = tk.Frame(list_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add listbox with scrollbars
        self.listbox = tk.Listbox(left_frame, height=4, font=('TkDefaultFont', 9))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = tk.Scrollbar(left_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = tk.Scrollbar(left_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.listbox.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.config(command=self.listbox.yview)
        h_scrollbar.config(command=self.listbox.xview)

        # Right side for preview
        preview_frame = tk.Frame(list_frame, bg='white')
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Preview label
        preview_label = tk.Label(preview_frame, bg='white')
        preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Store preview label reference
        self.file_window.preview_label = preview_label

        # Create bottom frame for buttons
        bottom_frame = tk.Frame(main_content)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create buttons for file operations
        open_btn = tk.Button(bottom_frame, text="Open", width=8, command=self.open_selected_file)
        open_btn.pack(side=tk.LEFT, padx=5)
        self.CreateToolTip(open_btn, "Open the selected file (Ctrl+O)")
        
        print_btn = tk.Button(bottom_frame, text="Print", width=8, command=self.print_selected_file)
        print_btn.pack(side=tk.LEFT, padx=5)
        self.CreateToolTip(print_btn, "Print the selected file (Ctrl+P)")
        
        # Create a compact frame for browser buttons in the bottom right
        browser_frame = tk.Frame(bottom_frame, width=250)
        browser_frame.pack(side=tk.RIGHT, padx=5)
        
        # Track browser tab states for this dialog
        self.view_files_reverse_tab_open = False
        self.view_files_receive_tab_open = False
        
        # Create a small status indicator
        self.view_files_status_indicator = tk.Canvas(browser_frame, width=8, height=8, bg='#f0f0f0', highlightthickness=0)
        self.view_files_status_indicator.pack(side=tk.RIGHT, padx=(0, 5), pady=5)
        
        # Create the buttons with a compact design
        button_style = {
            'font': ('TkDefaultFont', 8),
            'relief': 'flat',
            'width': 10,
            'height': 1,
            'padx': 3,
            'pady': 1,
            'borderwidth': 1
        }
        
        # Create the Receive button
        self.view_files_receive_button = tk.Button(
            browser_frame, 
            text="Receive", 
            bg='#27ae60',  # Green
            fg='white',
            activebackground='#2ecc71',  # Lighter green
            **button_style,
            command=lambda: self.toggle_view_files_tab('receive')
        )
        self.view_files_receive_button.pack(side=tk.RIGHT, padx=2)
        
        # Create the Reverse Inbound button with emoji
        self.view_files_reverse_button = tk.Button(
            browser_frame, 
            text="↩️Inbound", 
            bg='#4169E1',  # Royal Blue
            fg='white',
            activebackground='#1E90FF',  # Dodger Blue
            **button_style,
            command=lambda: self.toggle_view_files_tab('reverse')
        )
        self.view_files_reverse_button.pack(side=tk.RIGHT, padx=2)
        
        # Add tooltips for the buttons
        self.CreateToolTip(self.view_files_receive_button, "Open or close JDL Scan/Receive page")
        self.CreateToolTip(self.view_files_reverse_button, "Open or close JDL After Sales Order page")

        # Right side for last print info
        last_print_label = tk.Label(bottom_frame, text="", font=('TkDefaultFont', 9), fg='#666666')
        last_print_label.pack(side=tk.RIGHT, padx=(0, 10), pady=5)

        def update_file_list(*args):
            """Update the listbox based on search text"""
            search_text = search_var.get().lower()
            self.listbox.delete(0, tk.END)
            
            try:
                files = os.listdir(self.config_manager.settings.last_directory)
                png_files = [f for f in files if f.lower().endswith('.png')]
                matched_files = []
                
                # Check if search is a 12-digit UPC
                is_upc_search = search_text.isdigit() and len(search_text) == 12
                
                # Split search into terms
                search_terms = [] if is_upc_search else search_text.split()
                
                for file in sorted(png_files):
                    file_lower = file.lower()
                    
                    # UPC search takes precedence
                    if is_upc_search:
                        if search_text in file_lower:
                            matched_files.append(file)
                    # If no search terms, include all files
                    elif not search_terms:
                        matched_files.append(file)
                    # Check if ALL search terms are in the filename
                    elif all(term in file_lower for term in search_terms):
                        matched_files.append(file)
                
                for file in matched_files:
                    self.listbox.insert(tk.END, file)
                    
                if len(matched_files) == 0:
                    # If it's a UPC search with no matches, switch to main window
                    if is_upc_search and self.is_auto_switch.get():
                        self.listbox.insert(tk.END, "No matching files found")
                        self.listbox.selection_clear(0, tk.END)
                        self.listbox.select_set(0)
                        self.listbox.see(0)
                        label_count_label.config(text="No Labels", fg='#e74c3c')  # Red text for no labels
                        preview_label.config(image='')  # Clear the preview label
                        
                        # Add a delay before switching to main window
                        self.file_window.after(375, lambda: [
                            self.deiconify(),
                            self.state('normal'),  # Ensure window is not minimized
                            self.lift(),
                            self.focus_force(),
                            self.input_vars['upc_code'].set(search_text),
                            self.inputs["upc_code"].focus_set(),
                            self.inputs["upc_code"].select_range(0, tk.END)
                        ])
                        return
                    
                    self.listbox.insert(tk.END, "No matching files found")
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.select_set(0)  # Select the "No matching files found" text in the listbox
                    self.listbox.see(0)
                    label_count_label.config(text="No Labels", fg='#e74c3c')  # Red text for no labels
                    preview_label.config(image='')  # Clear the preview label
                else:
                    self.listbox.selection_clear(0, tk.END)
                    
                    # For UPC searches with matches, just select the first match but don't auto-switch
                    if is_upc_search:
                        self.listbox.select_set(0)
                        self.listbox.see(0)
                        # Show preview of the selected file
                        show_preview(None)
                    else:
                        # Select the first item by default
                        self.listbox.select_set(0)
                        self.listbox.see(0)
                    
                    label_count_label.config(text=f"Labels: {len(matched_files)}", fg='#2ecc71')  # Green text for label count
                    # Show preview of first item
                    show_preview(None)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read directory: {str(e)}")

        def show_preview(event):
            """Show preview of selected file in the preview frame"""
            selection = self.listbox.curselection()
            if not selection:
                preview_label.config(image='')
                return

            file_name = self.listbox.get(selection[0])
            # Clear preview if "No matching files found" is selected
            if file_name == "No matching files found":
                preview_label.config(image='')
                return
                
            file_path = os.path.join(self.config_manager.settings.last_directory, file_name)

            try:
                img = Image.open(file_path)
                # Calculate size to fit in preview frame while maintaining aspect ratio
                preview_width = preview_frame.winfo_width()
                preview_height = preview_frame.winfo_height()
                
                if preview_width > 1 and preview_height > 1:  # Only resize if frame has valid dimensions
                    # Adjust preview size based on selected size button (1 = 70%, 2 = 80%, 3 = 95%)
                    size_map = {1: 0.70, 2: 0.80, 3: 0.95}  # Map button numbers to size multipliers
                    size_multiplier = size_map[preview_size.get()]
                    preview_width = int(preview_width * size_multiplier)
                    preview_height = int(preview_height * size_multiplier)
                    
                    img_ratio = img.width / img.height
                    frame_ratio = preview_width / preview_height
                    
                    if img_ratio > frame_ratio:
                        # Image is wider than frame
                        display_width = preview_width
                        display_height = int(preview_width / img_ratio)
                    else:
                        # Image is taller than frame
                        display_height = preview_height
                        display_width = int(preview_height * img_ratio)
                    
                    img = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
                    
                img_tk = ImageTk.PhotoImage(img)
                preview_label.config(image=img_tk)
                preview_label.image = img_tk  # Keep reference
            except Exception as e:
                preview_label.config(image='')
                print(f"Failed to preview image: {str(e)}")

        # Connect the search variable to the update function
        search_var.trace('w', update_file_list)
        self.listbox.bind('<<ListboxSelect>>', show_preview)

        # Update preview when window is resized
        def on_resize(event):
            show_preview(None)
        preview_frame.bind('<Configure>', on_resize)

        # Initial file list update
        update_file_list()

        # Force initial preview to be size 3
        show_preview(None)
        
        # Create a compact frame for the browser buttons with fixed width
        browser_frame = tk.Frame(bottom_frame, width=320)
        browser_frame.pack(side=tk.RIGHT, padx=5)
        browser_frame.pack_propagate(False)  # Prevent the frame from resizing based on content
        
        # Track browser tab states
        self.reverse_tab_open = False
        self.receive_tab_open = False
        self.browser_used = None
        
        # Create a small status indicator instead of a full label
        self.browser_status_indicator = tk.Canvas(browser_frame, width=10, height=10, bg='#f0f0f0', highlightthickness=0)
        self.browser_status_indicator.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Create button container to keep buttons aligned
        button_container = tk.Frame(browser_frame)
        button_container.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the buttons with a more compact design
        button_style = {
            'font': ('TkDefaultFont', 8),
            'relief': 'flat',
            'width': 12,
            'height': 1,
            'padx': 5,
            'pady': 2,
            'borderwidth': 1
        }
        
        # Create the Receive button
        self.receive_button = tk.Button(
            button_container, 
            text="Receive", 
            bg='#27ae60',  # Green
            fg='white',
            activebackground='#2ecc71',  # Lighter green
            **button_style,
            command=self.toggle_receive_tab
        )
        self.receive_button.pack(side=tk.TOP, padx=2, pady=1, fill=tk.X)
        
        # Create the Reverse Inbound button with emoji
        self.browser_button = tk.Button(
            button_container, 
            text="↩️Inbound", 
            bg='#4169E1',  # Royal Blue
            fg='white',
            activebackground='#1E90FF',  # Dodger Blue
            **button_style,
            command=self.toggle_browser_tab
        )
        self.browser_button.pack(side=tk.TOP, padx=2, pady=1, fill=tk.X)
        
        # Add tooltips for the buttons
        self.CreateToolTip(self.receive_button, "Open or close JDL Scan/Receive page")
        self.CreateToolTip(self.browser_button, "Open or close JDL After Sales Order page")

    def toggle_browser_tab(self):
        """Open or close a browser tab for the JDL After Sales Order page"""
        import webbrowser
        import subprocess
        import os
        import time
        
        # Initialize state if needed
        if not hasattr(self, 'reverse_tab_open'):
            self.reverse_tab_open = False
        
        if not self.reverse_tab_open:
            # Open the tab using URL from settings
            jdl_url = self.config_manager.settings.jdl_reverse_inbound_url
            webbrowser.open(jdl_url, new=2)
            
            # Update button state
            self.browser_button.config(
                text="Close Reverse",
                bg='#e74c3c',  # Red
                activebackground='#c0392b'  # Darker red
            )
            self.reverse_tab_open = True
        else:
            # Only close the tab if auto_close_browser_tabs is enabled
            if self.config_manager.settings.auto_close_browser_tabs:
                # Use a more robust approach to close the tab
                try:
                    # Create a temporary PowerShell script to close the active tab
                    temp_dir = os.path.join(os.environ['TEMP'], 'label_maker')
                    os.makedirs(temp_dir, exist_ok=True)
                    ps_script_path = os.path.join(temp_dir, 'close_tab.ps1')
                    
                    # Write a PowerShell script that sends Alt+Tab and then Ctrl+W
                    with open(ps_script_path, 'w') as f:
                        f.write("""
                        Add-Type -AssemblyName System.Windows.Forms
                        
                        # Alt+Tab to switch to the browser window
                        [System.Windows.Forms.SendKeys]::SendWait("%{TAB}")
                        Start-Sleep -Milliseconds 300
                        
                        # Send Ctrl+W to close the tab
                        [System.Windows.Forms.SendKeys]::SendWait("^w")
                        """)
                    
                    # Execute the PowerShell script
                    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_script_path], 
                                  capture_output=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    # Give time for the tab to close
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error closing tab: {str(e)}")
            
            # Update button state
            self.browser_button.config(
                text="↩️Inbound",
                bg='#4169E1',  # Royal Blue
                activebackground='#1E90FF'  # Dodger Blue
            )
            self.reverse_tab_open = False
            
    def toggle_receive_tab(self):
        """Open or close a browser tab for the JDL Scan/Receive page"""
        import webbrowser
        import subprocess
        import os
        import time
        
        # Initialize state if needed
        if not hasattr(self, 'receive_tab_open'):
            self.receive_tab_open = False
        
        if not self.receive_tab_open:
            # Open the tab using URL from settings
            jdl_url = self.config_manager.settings.jdl_receive_url
            webbrowser.open(jdl_url, new=2)
            
            # Update button state
            self.receive_button.config(
                text="Close Receive",
                bg='#e74c3c',  # Red
                activebackground='#c0392b'  # Darker red
            )
            self.receive_tab_open = True
        else:
            # Only close the tab if auto_close_browser_tabs is enabled
            if self.config_manager.settings.auto_close_browser_tabs:
                # Use a more robust approach to close the tab
                try:
                    # Create a temporary PowerShell script to close the active tab
                    temp_dir = os.path.join(os.environ['TEMP'], 'label_maker')
                    os.makedirs(temp_dir, exist_ok=True)
                    ps_script_path = os.path.join(temp_dir, 'close_tab.ps1')
                    
                    # Write a PowerShell script that sends Alt+Tab and then Ctrl+W
                    with open(ps_script_path, 'w') as f:
                        f.write("""
                        Add-Type -AssemblyName System.Windows.Forms
                        
                        # Alt+Tab to switch to the browser window
                        [System.Windows.Forms.SendKeys]::SendWait("%{TAB}")
                        Start-Sleep -Milliseconds 300
                        
                        # Send Ctrl+W to close the tab
                        [System.Windows.Forms.SendKeys]::SendWait("^w")
                        """)
                    
                    # Execute the PowerShell script
                    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_script_path], 
                                  capture_output=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    # Give time for the tab to close
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error closing tab: {str(e)}")
            
            # Update button state
            self.receive_button.config(
                text="Receive",
                bg='#27ae60',  # Green
                activebackground='#2ecc71'  # Lighter green
            )
            self.receive_tab_open = False
            
    def create_diagnostic_window(self):
        """Create a diagnostic window to track browser tab operations"""
        import platform
        
        # Create the diagnostic window
        self.diagnostic_window = tk.Toplevel(self)
        self.diagnostic_window.title("Browser Tab Diagnostics")
        self.diagnostic_window.geometry("800x500")
        self.diagnostic_window.minsize(600, 400)
        
        # Make sure it stays on top
        self.diagnostic_window.attributes('-topmost', True)
        
        # Create a frame for the text widget and scrollbar
        text_frame = tk.Frame(self.diagnostic_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a text widget to display diagnostic information
        self.diagnostic_text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.diagnostic_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.diagnostic_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.diagnostic_text.yview)
        
        # Create a frame for buttons
        button_frame = tk.Frame(self.diagnostic_window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Add a clear button
        clear_button = tk.Button(button_frame, text="Clear Log", command=self.clear_diagnostic_log)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Add a test button to manually trigger Ctrl+W
        test_button = tk.Button(button_frame, text="Test Ctrl+W", command=lambda: pyautogui.hotkey('ctrl', 'w'))
        test_button.pack(side=tk.LEFT, padx=5)
        
        # Log initial information
        self.log_diagnostic("=== DIAGNOSTIC WINDOW CREATED ===")
        self.log_diagnostic(f"Python version: {sys.version}")
        self.log_diagnostic(f"Operating system: {platform.system()} {platform.release()}")
        self.log_diagnostic(f"Default browser detected: {self._detect_default_browser()}")
        self.log_diagnostic("Ready to monitor browser tab operations")
        self.log_diagnostic("=== INSTRUCTIONS ===")
        self.log_diagnostic("1. Click ↩️Inbound or Receive to open a tab")
        self.log_diagnostic("2. Click 'Close Reverse' or 'Close Receive' to attempt to close the tab")
        self.log_diagnostic("3. Watch this window for diagnostic information")
        self.log_diagnostic("============================")
        
    def log_diagnostic(self, message):
        """Log a diagnostic message with timestamp"""
        # Check if automation activity logging is enabled
        if hasattr(self.config_manager.settings, 'automation_activity_log_enabled') and not self.config_manager.settings.automation_activity_log_enabled:
            # If logging is disabled, only log critical system messages
            if message.startswith("===") or "Error" in message:
                pass  # Still log critical messages and errors
            else:
                return  # Skip non-critical messages when logging is disabled
        
        # Log the message if diagnostic text widget exists
        if hasattr(self, 'diagnostic_text'):
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            self.diagnostic_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.diagnostic_text.see(tk.END)  # Scroll to the end
            
    def clear_diagnostic_log(self):
        """Clear the diagnostic log"""
        if hasattr(self, 'diagnostic_text'):
            self.diagnostic_text.delete(1.0, tk.END)
            self.log_diagnostic("Log cleared")
            
    def close_tab_with_diagnostics(self, tab_type):
        """Close a browser tab with detailed diagnostics"""
        import webbrowser
        import subprocess
        import platform
        import time
        import sys
        import win32gui
        import win32con
        import win32process
        import psutil
        
        self.log_diagnostic(f"Starting tab close operation for {tab_type}")
        
        # Try multiple approaches and log results
        try:
            # 1. First, try to find the browser window
            self.log_diagnostic("Searching for browser window...")
            
            # Define browser window titles to look for
            browser_titles = {
                "chrome": "Google Chrome",
                "msedge": "Microsoft Edge",
                "firefox": "Mozilla Firefox"
            }
            
            # Function to find browser windows
            def find_browser_windows():
                browser_windows = []
                
                def enum_callback(hwnd, results):
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        # Look for browser windows with our JDL URLs
                        for browser in browser_titles:
                            if browser_titles[browser] in window_text:
                                if "jdlglobal" in window_text.lower() or "iwms" in window_text.lower():
                                    # Get process info
                                    try:
                                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                        process = psutil.Process(pid)
                                        process_name = process.name()
                                        results.append((hwnd, window_text, process_name, pid))
                                    except Exception as e:
                                        results.append((hwnd, window_text, "Unknown", 0))
                    return True
                
                win32gui.EnumWindows(enum_callback, browser_windows)
                return browser_windows
            
            # Find browser windows
            browser_windows = find_browser_windows()
            
            if browser_windows:
                for hwnd, title, process_name, pid in browser_windows:
                    self.log_diagnostic(f"Found browser window: '{title}' (Process: {process_name}, PID: {pid})")
                
                # Try to focus and send Ctrl+W to the first window
                hwnd, title, _, _ = browser_windows[0]
                self.log_diagnostic(f"Focusing window: '{title}'")
                
                # Restore window if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                
                # Set foreground window
                win32gui.SetForegroundWindow(hwnd)
                
                # Give time for window to get focus
                time.sleep(0.5)
                
                # Send Ctrl+W
                self.log_diagnostic("Sending Ctrl+W keystroke")
                pyautogui.hotkey('ctrl', 'w')
                
                # Check if window still exists after a short delay
                time.sleep(1)
                try:
                    new_title = win32gui.GetWindowText(hwnd)
                    self.log_diagnostic(f"After Ctrl+W, window title is now: '{new_title}'")
                except Exception as e:
                    self.log_diagnostic(f"Window no longer exists after Ctrl+W: {str(e)}")
            else:
                self.log_diagnostic("No matching browser windows found")
                
                # Try direct approach with pyautogui
                self.log_diagnostic("Trying direct Ctrl+W approach")
                pyautogui.hotkey('ctrl', 'w')
        except Exception as e:
            self.log_diagnostic(f"Error during tab close operation: {str(e)}")
            import traceback
            self.log_diagnostic(traceback.format_exc())
    
    def open_browser_tab(self, tab_type):
        """Open a browser tab with the specified JDL page
        
        Args:
            tab_type: Either 'reverse' for After Sales Order or 'receive' for Scan/Receive
        """
        import webbrowser
        
        try:
            # Set URL based on tab type
            if tab_type == 'reverse':
                jdl_url = "https://iwms.us.jdlglobal.com/#/createAfterSalesOrder"
                button = self.browser_button
            else:  # receive
                jdl_url = "https://iwms.us.jdlglobal.com/#/scan"
                button = self.receive_button
            
            # Simply open the URL - no state tracking or complex logic
            webbrowser.open(jdl_url, new=2)  # Open in a new tab
            
            # Update status indicator
            self.browser_status_indicator.config(bg='#27ae60')  # Green
        except Exception as e:
            print(f"Error opening browser: {str(e)}")
            # Don't show error message to avoid interrupting workflow
    
    def close_browser_tab(self, tab_type):
        """Close the browser tab using a direct approach without keyboard shortcuts
        
        Args:
            tab_type: Either 'reverse' for After Sales Order or 'receive' for Scan/Receive
        """
        import webbrowser
        import time
        
        try:
            # Set indicator to yellow during closing
            self.browser_status_indicator.config(bg='#f39c12')  # Yellow/orange
            
            # Set button and state based on tab type
            if tab_type == 'reverse':
                button = self.browser_button
                button_text = "↩️Inbound"
                button_color = '#4169E1'  # Royal Blue
                button_active_color = '#1E90FF'  # Dodger Blue
                # Reset tab state
                self.reverse_tab_open = False
            else:  # receive
                button = self.receive_button
                button_text = "Receive"
                button_color = '#27ae60'  # Green
                button_active_color = '#2ecc71'  # Lighter green
                # Reset tab state
                self.receive_tab_open = False
            
            # Use a more robust approach to close browser tabs
            try:
                # Import necessary modules
                import subprocess
                import win32gui
                import win32con
                
                # Get the browser name
                browser_name = self.browser_used
                
                # Define browser window titles to look for
                browser_titles = {
                    "chrome": "Google Chrome",
                    "msedge": "Microsoft Edge",
                    "firefox": "Mozilla Firefox"
                }
                
                # Function to find and focus browser window
                def find_browser_window():
                    def enum_windows_callback(hwnd, results):
                        if win32gui.IsWindowVisible(hwnd):
                            window_text = win32gui.GetWindowText(hwnd)
                            # Look for browser windows that might have our JDL page open
                            if browser_name in browser_titles and browser_titles[browser_name] in window_text:
                                if "jdlglobal" in window_text.lower() or "iwms" in window_text.lower():
                                    results.append(hwnd)
                        return True
                    
                    windows = []
                    win32gui.EnumWindows(enum_windows_callback, windows)
                    return windows
                
                # Find and focus the browser window
                browser_windows = find_browser_window()
                
                if browser_windows:
                    # Focus the first matching window
                    hwnd = browser_windows[0]
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    
                    # Give a short delay to ensure the browser is focused
                    time.sleep(0.5)
                    
                    # Use Ctrl+W to close the current tab
                    pyautogui.hotkey('ctrl', 'w')
                else:
                    # If we can't find the browser window, try the direct approach
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl', 'w')
            except Exception as e:
                # If there's any error with the browser automation,
                # just log it and continue - the tab has already been replaced
                # with a blank page, which is good enough
                print(f"Browser automation note: {str(e)}")
                # No need to show an error to the user
            
            # Update button and status
            button.config(
                text=button_text,
                bg=button_color,
                activebackground=button_active_color
            )
            # Reset status indicator to default gray
            self.browser_status_indicator.config(bg='#f0f0f0')
        except Exception as e:
            messagebox.showerror("Error", f"Error closing browser tab: {str(e)}")
    
    def toggle_view_files_tab(self, tab_type):
        """Open or close a browser tab for the View Files dialog
        
        Args:
            tab_type: Either 'reverse' for After Sales Order or 'receive' for Scan/Receive
        """
        import webbrowser
        import subprocess
        import os
        import time
        
        # Initialize state variables if needed
        if not hasattr(self, 'view_files_reverse_tab_open'):
            self.view_files_reverse_tab_open = False
        if not hasattr(self, 'view_files_receive_tab_open'):
            self.view_files_receive_tab_open = False
            
        if tab_type == 'reverse':
            if not self.view_files_reverse_tab_open:
                # Open the tab using URL from settings
                jdl_url = self.config_manager.settings.jdl_reverse_inbound_url
                webbrowser.open(jdl_url, new=2)
                
                # Update button state
                self.view_files_reverse_button.config(
                    text="Close Reverse",
                    bg='#e74c3c',  # Red
                    activebackground='#c0392b'  # Darker red
                )
                self.view_files_reverse_tab_open = True
            else:
                # Use a more robust approach to close the tab
                try:
                    # Create a temporary PowerShell script to close the active tab
                    temp_dir = os.path.join(os.environ['TEMP'], 'label_maker')
                    os.makedirs(temp_dir, exist_ok=True)
                    ps_script_path = os.path.join(temp_dir, 'close_tab.ps1')
                    
                    # Write a PowerShell script that sends Alt+Tab and then Ctrl+W
                    with open(ps_script_path, 'w') as f:
                        f.write("""
                        Add-Type -AssemblyName System.Windows.Forms
                        
                        # Alt+Tab to switch to the browser window
                        [System.Windows.Forms.SendKeys]::SendWait("%{TAB}")
                        Start-Sleep -Milliseconds 300
                        
                        # Send Ctrl+W to close the tab
                        [System.Windows.Forms.SendKeys]::SendWait("^w")
                        """)
                    
                    # Execute the PowerShell script
                    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_script_path], 
                                  capture_output=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    # Give time for the tab to close
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error closing tab: {str(e)}")
                
                # Update button state
                self.view_files_reverse_button.config(
                    text="↩️Inbound",
                    bg='#4169E1',  # Royal Blue
                    activebackground='#1E90FF'  # Dodger Blue
                )
                self.view_files_reverse_tab_open = False
        else:  # receive
            if not self.view_files_receive_tab_open:
                # Open the tab using URL from settings
                jdl_url = self.config_manager.settings.jdl_receive_url
                webbrowser.open(jdl_url, new=2)
                
                # Update button state
                self.view_files_receive_button.config(
                    text="Close Receive",
                    bg='#e74c3c',  # Red
                    activebackground='#c0392b'  # Darker red
                )
                self.view_files_receive_tab_open = True
            else:
                # Use a more robust approach to close the tab
                try:
                    # Create a temporary PowerShell script to close the active tab
                    temp_dir = os.path.join(os.environ['TEMP'], 'label_maker')
                    os.makedirs(temp_dir, exist_ok=True)
                    ps_script_path = os.path.join(temp_dir, 'close_tab.ps1')
                    
                    # Write a PowerShell script that sends Alt+Tab and then Ctrl+W
                    with open(ps_script_path, 'w') as f:
                        f.write("""
                        Add-Type -AssemblyName System.Windows.Forms
                        
                        # Alt+Tab to switch to the browser window
                        [System.Windows.Forms.SendKeys]::SendWait("%{TAB}")
                        Start-Sleep -Milliseconds 300
                        
                        # Send Ctrl+W to close the tab
                        [System.Windows.Forms.SendKeys]::SendWait("^w")
                        """)
                    
                    # Execute the PowerShell script
                    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_script_path], 
                                  capture_output=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    # Give time for the tab to close
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error closing tab: {str(e)}")
                
                # Update button state
                self.view_files_receive_button.config(
                    text="Receive",
                    bg='#27ae60',  # Green
                    activebackground='#2ecc71'  # Lighter green
                )
                self.view_files_receive_tab_open = False
    
    def open_view_files_tab(self, tab_type):
        """Open a browser tab with the specified JDL page for the View Files dialog
        
        Args:
            tab_type: Either 'reverse' for After Sales Order or 'receive' for Scan/Receive
        """
        import webbrowser
        
        # Set URL based on tab type and open it directly
        if tab_type == 'reverse':
            jdl_url = "https://iwms.us.jdlglobal.com/#/createAfterSalesOrder"
        else:  # receive
            jdl_url = "https://iwms.us.jdlglobal.com/#/scan"
        
        # Simply open the URL in a new tab
        webbrowser.open(jdl_url, new=2)
    
    def close_view_files_tab(self, tab_type):
        """Close the browser tab for the View Files dialog using a direct approach without keyboard shortcuts
        
        Args:
            tab_type: Either 'reverse' for After Sales Order or 'receive' for Scan/Receive
        """
        import webbrowser
        import time
        
        try:
            # Set indicator to yellow during closing
            self.view_files_status_indicator.config(bg='#f39c12')  # Yellow/orange
            
            # Set button and state based on tab type
            if tab_type == 'reverse':
                button = self.view_files_reverse_button
                button_text = "↩️Inbound"
                button_color = '#4169E1'  # Royal Blue
                button_active_color = '#1E90FF'  # Dodger Blue
                # Reset tab state
                self.view_files_reverse_tab_open = False
            else:  # receive
                button = self.view_files_receive_button
                button_text = "Receive"
                button_color = '#27ae60'  # Green
                button_active_color = '#2ecc71'  # Lighter green
                # Reset tab state
                self.view_files_receive_tab_open = False
            
            # Use a more robust approach to close browser tabs
            try:
                # Import necessary modules
                import subprocess
                import win32gui
                import win32con
                
                # Get the browser name
                browser_name = self.browser_used
                
                # Define browser window titles to look for
                browser_titles = {
                    "chrome": "Google Chrome",
                    "msedge": "Microsoft Edge",
                    "firefox": "Mozilla Firefox"
                }
                
                # Function to find and focus browser window
                def find_browser_window():
                    def enum_windows_callback(hwnd, results):
                        if win32gui.IsWindowVisible(hwnd):
                            window_text = win32gui.GetWindowText(hwnd)
                            # Look for browser windows that might have our JDL page open
                            if browser_name in browser_titles and browser_titles[browser_name] in window_text:
                                if "jdlglobal" in window_text.lower() or "iwms" in window_text.lower():
                                    results.append(hwnd)
                        return True
                    
                    windows = []
                    win32gui.EnumWindows(enum_windows_callback, windows)
                    return windows
                
                # Find and focus the browser window
                browser_windows = find_browser_window()
                
                if browser_windows:
                    # Focus the first matching window
                    hwnd = browser_windows[0]
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    
                    # Give a short delay to ensure the browser is focused
                    time.sleep(0.5)
                    
                    # Use Ctrl+W to close the current tab
                    pyautogui.hotkey('ctrl', 'w')
                else:
                    # If we can't find the browser window, try the direct approach
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl', 'w')
            except Exception as e:
                # If there's any error with the browser automation,
                # just log it and continue - the tab has already been replaced
                # with a blank page, which is good enough
                print(f"Browser automation note: {str(e)}")
                # No need to show an error to the user
            
            # Update button and status
            button.config(
                text=button_text,
                bg=button_color,
                activebackground=button_active_color
            )
            # Reset status indicator to default gray
            self.view_files_status_indicator.config(bg='#f0f0f0')
        except Exception as e:
            messagebox.showerror("Error", f"Error closing browser tab: {str(e)}")
    
    def _detect_default_browser(self):
        """Detect the default browser on the system"""
        import subprocess
        import platform
        import re
        
        try:
            if platform.system() == "Windows":
                # Try to detect the default browser using PowerShell
                ps_command = [
                    'powershell', '-Command',
                    r'''
                    $browserPath = (Get-ItemProperty HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice).ProgId
                    $browserName = switch -Regex ($browserPath) {
                        "ChromeHTML|Chrome" { "chrome" }
                        "FirefoxURL|Firefox" { "firefox" }
                        "MSEdgeHTM|Edge" { "msedge" }
                        "IE.HTTP|InternetExplorer" { "iexplore" }
                        "OperaStable" { "opera" }
                        "BraveHTML" { "brave" }
                        default { "unknown" }
                    }
                    $browserName
                    '''
                ]
                
                result = subprocess.run(ps_command, capture_output=True, text=True, check=False)
                browser_name = result.stdout.strip().lower()
                
                if browser_name == "unknown" or not browser_name:
                    # Try another method - check running processes
                    browsers = ["chrome", "firefox", "msedge", "iexplore", "opera", "brave"]
                    for browser in browsers:
                        check_cmd = ['powershell', '-Command', f'Get-Process -Name {browser} -ErrorAction SilentlyContinue']
                        result = subprocess.run(check_cmd, capture_output=True, text=True, check=False)
                        if result.stdout.strip():
                            browser_name = browser
                            break
                
                self.browser_used = browser_name if browser_name else "unknown"
            else:
                # For non-Windows platforms, we'll just use a generic approach
                self.browser_used = "unknown"
        except Exception as e:
            # If detection fails, just set to unknown
            self.browser_used = "unknown"
            print(f"Error detecting browser: {str(e)}")
    
    def _setup_fonts(self):
        """Configure default fonts"""
        self.default_font = ('TkDefaultFont', 11)
        self.button_font = ('TkDefaultFont', 11, 'normal')
        self.entry_font = ('TkDefaultFont', 11)
        self.label_font = ('TkDefaultFont', 11)
        self.view_files_font = ('TkDefaultFont', 12, 'bold')

        self.option_add('*Font', self.default_font)
        self.option_add('*Button*Font', self.button_font)
        self.option_add('*Entry*Font', self.entry_font)
        self.option_add('*Label*Font', self.label_font)

    def _setup_variables(self):
        """Initialize tkinter variables"""
        # Initialize variables for each input field
        self.input_vars = {
            'name_line1': tk.StringVar(),
            'name_line2': tk.StringVar(),
            'variant': tk.StringVar(),
            'upc_code': tk.StringVar()
        }
        
        # Initialize undo stacks for each entry
        self.undo_stacks = {}
        self.redo_stacks = {}

        self.font_size_large = tk.IntVar(value=self.config_manager.settings.font_size_large)
        self.font_size_medium = tk.IntVar(value=self.config_manager.settings.font_size_medium)
        self.barcode_width = tk.IntVar(value=self.config_manager.settings.barcode_width)
        self.barcode_height = tk.IntVar(value=self.config_manager.settings.barcode_height)
        self.always_on_top = tk.BooleanVar(value=self.config_manager.settings.always_on_top)
        self.transparency_level = tk.DoubleVar(value=self.config_manager.settings.transparency_level)
        self.png_count = tk.StringVar(value=f"Labels: {self.config_manager.settings.label_counter}")
        
    def _load_icons(self):
        """Load icons for buttons"""
        # Create a simple batch icon using a PhotoImage
        self.batch_icon = tk.PhotoImage(width=16, height=16)
        # Create a simple spreadsheet-like icon using pixels
        data = """
        ................
        .##############.
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .##############.
        ................
        ................
        """
        # Put the data into the image
        for y, line in enumerate(data.split()):
            for x, c in enumerate(line):
                if c == '#':
                    self.batch_icon.put('#666666', (x, y))

    def _create_tooltip_class(self):
        """Create a tooltip class for button hints"""
        class ToolTip(object):
            def __init__(self, widget, text):
                self.widget = widget
                self.text = text
                self.tooltip = None
                self.widget.bind('<Enter>', self.enter)
                self.widget.bind('<Leave>', self.leave)
                self.widget.bind('<ButtonPress>', self.leave)

            def enter(self, event=None):
                x, y, _, _ = self.widget.bbox("insert")
                x += self.widget.winfo_rootx() + 25
                y += self.widget.winfo_rooty() + 20
                self.tooltip = tk.Toplevel(self.widget)
                self.tooltip.wm_overrideredirect(True)
                # Make tooltip always on top of its parent window
                parent_window = self.widget.winfo_toplevel()
                if parent_window.attributes('-topmost'):
                    self.tooltip.attributes('-topmost', True)
                self.tooltip.wm_geometry(f"+{x}+{y}")
                label = tk.Label(self.tooltip, text=self.text, 
                               justify='left',
                               background="#ffffe0", 
                               relief='solid', 
                               borderwidth=1,
                               font=("TkDefaultFont", "8", "normal"))
                label.pack()

            def leave(self, event=None):
                if self.tooltip:
                    self.tooltip.destroy()
                    self.tooltip = None

        self.CreateToolTip = ToolTip

    def _set_window_icon(self, window, icon_size='64', icon_type='icon'):
        """Set the window icon for any window in the application
        Args:
            window: The window to set the icon for
            icon_size: Size of the icon to use ('16', '32', '64')
            icon_type: Type of icon to use ('icon' for main icon, 'settings' for settings window)
        """
        import ctypes
        from PIL import Image, ImageTk
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'assets', f'{icon_type}_{icon_size}.png')
        
        if os.path.exists(icon_path):
            try:
                # Load the icon using PIL
                img = Image.open(icon_path)
                # Convert to PhotoImage for the window icon
                photo = ImageTk.PhotoImage(img)
                window.iconphoto(False, photo)  # False means don't use as default
                # Keep a reference to prevent garbage collection
                if not hasattr(window, '_icon'):
                    window._icon = photo
                
                # Set unique taskbar icon for Windows
                if isinstance(window, tk.Toplevel):
                    try:
                        # Generate unique app ID based on window type
                        if icon_type == 'settings':
                            app_id = 'labelmaker.settings.window'
                        elif icon_type == 'viewfiles':
                            app_id = 'labelmaker.viewfiles.window'
                        else:
                            app_id = 'labelmaker.main.window'
                        
                        # Set the app user model ID
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                        
                        # Get the window handle
                        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
                        
                        # Associate the window with its unique app ID
                        from ctypes import wintypes
                        SetWindowAttribute = ctypes.windll.user32.SetPropW
                        SetWindowAttribute(hwnd, "AppUserModelID", app_id)
                        
                    except Exception as e:
                        print(f"Failed to set taskbar icon: {str(e)}")
            except Exception as e:
                print(f"Failed to set window icon: {str(e)}")


    def _create_main_window(self):
        """Create and setup the main application window"""
        # Configure main window
        self.title("Label Maker")
        self.minsize(450, 200)
        
        # Set window icon with unique app ID
        self._set_window_icon(self, '64', 'icon')
        
        try:
            # Set the main window app ID
            import ctypes
            app_id = 'labelmaker.main.window'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass  # Fail silently if Windows-specific call fails
        
        # Center window on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.winfo_width()) // 2
        y = (screen_height - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Prevent window resizing
        self.resizable(False, False)
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main frame with comfortable padding
        self.main_frame = tk.Frame(self, padx=8, pady=5, bg='SystemButtonFace')
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Create top control frame
        self._create_top_control_frame()
        
        # Create control buttons frame (Reset)
        self._create_control_frame()
        
        # Create input fields
        self._create_input_fields()
        
        # Create action buttons frame
        self._create_action_buttons()
        
        # Add separator
        ttk.Separator(self.main_frame, orient='horizontal').grid(
            row=8, column=0, columnspan=2, sticky=tk.EW, pady=10
        )

    def on_close(self):
        """Handle window close event"""
        self.config_manager.save_settings()
        self.quit()

    def run(self):
        """Start the application"""
        try:
            self.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start application: {str(e)}")
            raise

    def _on_window_focus(self, focused_window):
        """Handle window focus to manage stacking order"""
        # Lower all windows
        for window in self.app_windows:
            if window.winfo_exists():  # Check if window still exists
                if isinstance(window, tk.Tk):  # Main window
                    window.attributes('-topmost', self.always_on_top.get())
                else:  # Child windows
                    window.attributes('-topmost', False)
        
        # Raise the focused window
        if focused_window != self or self.always_on_top.get():  # Don't set main window topmost unless Always on Top is enabled
            focused_window.attributes('-topmost', True)
        focused_window.lift()

    def _add_undo_support(self, entry, var):
        """Add undo/redo support to an entry widget"""
        # Initialize stacks for this entry
        self.undo_stacks[entry] = []
        self.redo_stacks[entry] = []
        
        def on_change(*args):
            current_value = var.get()
            # Only add to undo stack if the value actually changed
            if self.undo_stacks[entry] and self.undo_stacks[entry][-1] == current_value:
                return
            self.undo_stacks[entry].append(current_value)
            # Clear redo stack when new change is made
            self.redo_stacks[entry].clear()
        
        def undo(event):
            if len(self.undo_stacks[entry]) > 1:  # Keep the last state
                # Move current state to redo stack
                self.redo_stacks[entry].append(self.undo_stacks[entry].pop())
                # Restore previous state
                var.set(self.undo_stacks[entry][-1])
            return "break"
        
        def redo(event):
            if self.redo_stacks[entry]:
                # Get the state to redo
                value = self.redo_stacks[entry].pop()
                # Add it to undo stack
                self.undo_stacks[entry].append(value)
                # Restore the state
                var.set(value)
            return "break"
        
        def delete_word_before(event):
            # Get current cursor position
            cursor_pos = entry.index(tk.INSERT)
            # Get current text
            text = var.get()
            if cursor_pos == 0 or not text:  # Nothing to delete
                return "break"
            
            # Find the start of the word before cursor
            i = cursor_pos - 1
            # Skip spaces immediately before cursor
            while i >= 0 and text[i].isspace():
                i -= 1
            # Find start of word
            while i >= 0 and not text[i].isspace():
                i -= 1
            
            # Adjust index to keep the space before the word
            i += 1
                
            # Delete from start of word to cursor
            new_text = text[:i] + text[cursor_pos:]
            var.set(new_text)
            # Move cursor to deletion point
            entry.icursor(i)
            return "break"  # Prevents default behavior
            
        # Track changes
        var.trace_add('write', on_change)
        # Add initial state
        self.undo_stacks[entry].append(var.get())
        
        # Bind undo/redo shortcuts
        entry.bind("<Control-z>", undo)
        entry.bind("<Control-y>", redo)
        entry.bind("<Control-BackSpace>", delete_word_before)  # More standard shortcut for deleting word before

    def _create_input_fields(self):
        """Create input fields"""
        # Initialize inputs dictionary
        self.inputs = {}
        
        labels = [
            ("Product Name Line 1:", "name_line1"),
            ("Line 2 (optional):", "name_line2"),
            ("Variant:", "variant"),
            ("UPC Code(12 digits):", "upc_code")
        ]
        
        def on_input_focus(event):
            """Enable Always on Top when user focuses on any input field"""
            if not self.always_on_top.get():
                self.toggle_always_on_top()
        
        def on_input_click(event):
            """Handle mouse click in input field"""
            # Select all text when clicking into field
            event.widget.select_range(0, tk.END)
            event.widget.icursor(tk.END)
        
        def validate_upc(action, value_if_allowed):
            """Only allow integers in UPC field and ensure exactly 12 digits"""
            if action == '0':  # This is a delete action
                return True
            if not value_if_allowed:  # Empty value
                return True
            if not value_if_allowed.isdigit():  # Not a digit
                return False
            if len(value_if_allowed) > 12:  # Too many digits
                return False
            return True
        
        def validate_variant(action, value_if_allowed):
            """Validate variant field - now allowing numbers at the start"""
            if action == '0':  # This is a delete action
                return True
            if not value_if_allowed:  # Empty value
                return True
            return True
        
        for idx, (label_text, key) in enumerate(labels):
            # Label
            label = tk.Label(self.main_frame,
                text=label_text,
                anchor="e",
                width=20,
                bg='SystemButtonFace'
            )
            label.grid(row=idx+2, column=0, padx=5, pady=3, sticky="e")
            
            # Entry
            if key == "upc_code":
                vcmd = (self.register(validate_upc), '%d', '%P')
                entry = tk.Entry(self.main_frame,
                    width=25,
                    relief='sunken',
                    bg='white',
                    validate='key',
                    validatecommand=vcmd,
                    textvariable=self.input_vars[key]
                )
            elif key == "variant":
                vcmd = (self.register(validate_variant), '%d', '%P')
                entry = tk.Entry(self.main_frame,
                    width=25,
                    relief='sunken',
                    bg='white',
                    validate='key',
                    validatecommand=vcmd,
                    textvariable=self.input_vars[key]
                )
            else:
                entry = tk.Entry(self.main_frame,
                    width=25,
                    relief='sunken',
                    bg='white',
                    textvariable=self.input_vars[key]
                )
            
            entry.grid(row=idx+2, column=1, padx=5, pady=3, sticky="w")
            
            # Add undo/redo support
            self._add_undo_support(entry, self.input_vars[key])
            
            # Bind events
            entry.bind("<FocusIn>", on_input_focus)
            entry.bind("<Button-1>", on_input_click)  # Handle mouse click
            
            # Add context menu
            self._add_context_menu(entry)
            
            # Store entry widget in inputs dictionary
            self.inputs[key] = entry

    def _create_action_buttons(self):
        """Create action buttons frame"""
        button_frame = tk.Frame(self.main_frame, bg='SystemButtonFace')
        button_frame.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Preview button with vibrant blue theme
        preview_btn = self._create_styled_button(
            button_frame,
            text="Preview",
            command=self.preview_label,
            width=10,
        )
        preview_btn.pack(side=tk.LEFT, padx=2)
        
        # View Files button with vibrant purple theme
        view_files_btn = self._create_styled_button(
            button_frame,
            text="View Files",
            command=self.view_directory_files,
            width=10,
        )
        view_files_btn.pack(side=tk.LEFT, padx=2)

    def process_camel_case(self, text):
        """
        Process text to add spaces after capital letters that are followed by lowercase letters.
        Example: 'RedShirt' becomes 'Red Shirt'
        
        Args:
            text (str): The text to process
            
        Returns:
            str: Processed text with spaces added after capital letters
        """
        import re
        
        # Handle edge cases
        if not text or not isinstance(text, str):
            return text
            
        # Debug: Print what we're processing
        print(f"Processing: '{text}'")
        
        # This is a more comprehensive approach that handles multiple occurrences
        result = text
        
        # First pass: Add spaces between lowercase followed by uppercase
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', result)
        
        # Also handle PascalCase (first letter is capital)
        # This regex finds capital letters at the start of a word that are followed by
        # at least one lowercase letter, and then another capital
        result = re.sub(r'(^|\s)([A-Z][a-z]+)([A-Z])', r'\1\2 \3', result)
        
        # Debug: Print the result
        print(f"Result: '{result}'")
        
        return result
        
    def upload_csv(self):
        """Handle CSV file upload"""
        try:
            # Create file dialog
            file_path = filedialog.askopenfilename(
                title="Select CSV File",
                filetypes=[("CSV files", "*.csv")],
                parent=self.settings_window  # Make dialog modal to settings window
            )
            
            if not file_path:
                return
                
            # Create progress window
            progress_window = tk.Toplevel(self.settings_window)
            progress_window.title("Processing CSV")
            progress_window.geometry("300x150")
            progress_window.transient(self.settings_window)  # Make it modal
            progress_window.grab_set()  # Make it modal
            
            # Center the progress window
            progress_window.update_idletasks()
            x = self.settings_window.winfo_x() + (self.settings_window.winfo_width() - progress_window.winfo_width()) // 2
            y = self.settings_window.winfo_y() + (self.settings_window.winfo_height() - progress_window.winfo_height()) // 2
            progress_window.geometry(f"+{x}+{y}")
            
            # Add progress label
            progress_label = tk.Label(progress_window, text="Processing CSV file...\nPlease wait...", pady=10)
            progress_label.pack()
            
            # Add progress bar
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(
                progress_window, 
                variable=progress_var,
                maximum=100,
                mode='determinate',
                length=250
            )
            progress_bar.pack(pady=20)
            
            # Add cancel button
            cancel_button = ttk.Button(
                progress_window,
                text="Cancel",
                command=lambda: [progress_window.destroy(), setattr(self, '_cancel_process', True)]
            )
            cancel_button.pack(pady=10)
            
            # Initialize cancel flag
            self._cancel_process = False
            
            def process_csv():
                try:
                    # Read the CSV file
                    df = pd.read_csv(file_path)
                    
                    # Validate required columns
                    required_columns = ['Upc', 'Label Name']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        raise ValueError(f"Missing required columns in CSV: {', '.join(missing_columns)}\n"
                                      f"CSV must contain columns: {', '.join(required_columns)}")
                    
                    # Debug: Print the first few product names before processing
                    print("\nOriginal product names:")
                    for i, name in enumerate(df['Label Name'].head()):
                        print(f"  {i+1}: '{name}'")
                    
                    # We'll let process_product_name handle the camelCase processing
                    # Debug: Print the first few product names
                    print("\nProduct names from CSV:")
                    for i, name in enumerate(df['Label Name'].head()):
                        print(f"  {i+1}: '{name}'")
                    
                    total_rows = len(df)
                    
                    # Get save directory from settings or use default
                    save_dir = self.config_manager.settings.last_directory
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir, exist_ok=True)
                    
                    labels_created = 0
                    skipped_labels = 0
                    
                    # Process each row
                    for index, row in df.iterrows():
                        if self._cancel_process:
                            progress_window.destroy()
                            return
                            
                        # Update progress
                        progress = (index + 1) / total_rows * 100
                        progress_var.set(progress)
                        progress_label.config(text=f"Processing row {index + 1} of {total_rows}\n{labels_created} labels created")
                        progress_window.update()
                        
                        barcode = str(row['Upc'])
                        
                        # Skip if barcode is invalid
                        if not is_valid_barcode(barcode):
                            skipped_labels += 1
                            continue
                            
                        # Get the product name directly from CSV
                        # process_product_name will handle camelCase processing
                        full_name = str(row['Label Name'])
                        
                        # Process the product name
                        name_line1, name_line2, variant = process_product_name(full_name)
                        
                        # Create label data
                        label_data = LabelData(
                            name_line1=name_line1,
                            name_line2=name_line2,
                            variant=variant,
                            upc_code=barcode
                        )
                        
                        # Generate the label
                        label_image = self.barcode_generator.generate_label(label_data)
                        if label_image:
                            # Create safe filename
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
                            self.config_manager.settings.label_counter += 1
                            self.png_count.set(f"Labels: {self.config_manager.settings.label_counter}")
                    
                    # Save settings
                    self.config_manager.save_settings()
                    
                    # Show completion message
                    message = f"Created {labels_created} labels in:\n{save_dir}"
                    if skipped_labels > 0:
                        message += f"\n\nSkipped {skipped_labels} items with invalid barcodes"
                    
                    # Schedule UI updates on the main thread
                    progress_window.after(0, lambda: [
                        progress_window.destroy(),
                        self.settings_window.destroy(),
                        messagebox.showinfo("Success", message)
                    ])
                    
                except Exception as e:
                    # Schedule UI updates on the main thread
                    error_message = f"Failed to create batch labels: {str(e)}"
                    progress_window.after(0, lambda: [
                        progress_window.destroy(),
                        messagebox.showerror("Error", error_message)
                    ])
                    logger.error(f"Error creating batch labels: {str(e)}")
            
            # Start processing in a separate thread to keep UI responsive
            import threading
            thread = threading.Thread(target=process_csv)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error in upload_csv: {str(e)}")
            messagebox.showerror("Error", f"Failed to process CSV: {str(e)}")

    def _add_context_menu(self, widget):
        """Add right-click context menu to widget"""
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Cut", 
                        command=lambda: widget.event_generate('<<Cut>>'))
        menu.add_command(label="Copy", 
                        command=lambda: widget.event_generate('<<Copy>>'))
        menu.add_command(label="Paste", 
                        command=lambda: widget.event_generate('<<Paste>>'))
        menu.add_separator()
        menu.add_command(label="Select All", 
                        command=lambda: widget.select_range(0, tk.END))
        
        # Bind right-click to show menu
        widget.bind("<Button-3>", 
                   lambda e: menu.tk_popup(e.x_root, e.y_root))

    def toggle_always_on_top(self):
        """Toggle the always on top state"""
        self.always_on_top.set(not self.always_on_top.get())
        if self.always_on_top.get():
            self.always_on_top_btn.is_active = True
            self.always_on_top_btn.config(
                bg='#2ecc71',  # Bright green when active
                activebackground='#27ae60',  # Darker green when clicked
                relief='sunken'
            )
            self.attributes('-topmost', True)
            self.lift()
            self.focus_force()
        else:
            self.always_on_top_btn.is_active = False
            self.always_on_top_btn.config(
                bg='#e74c3c',  # Back to red
                activebackground='#c0392b',
                relief='raised'
            )
            self.attributes('-topmost', False)

    def clear_inputs(self):
        """Clear all input fields"""
        for entry in self.inputs.values():
            entry.delete(0, tk.END)

    def _select_output_directory(self):
        """Select output directory"""
        last_dir = self.config_manager.settings.last_directory
        directory = filedialog.askdirectory(
            title="Select where to save labels",
            initialdir=last_dir if last_dir and os.path.exists(last_dir) else None
        )
        if directory:
            self.config_manager.settings.last_directory = directory
            self.config_manager.save_settings()
            self._update_png_count()
            # Also open the directory viewer
            self.view_directory_files()

    def _update_png_count(self):
        """Update PNG count label"""
        if self.config_manager.settings.last_directory:
            count = len([f for f in os.listdir(self.config_manager.settings.last_directory)
                        if f.lower().endswith('.png')])
            self.config_manager.settings.label_counter = count
            self.png_count.set(f"Labels: {count}")
            self.config_manager.save_settings()

    def show_settings(self):
        """Show settings window"""
        # If settings window exists and is valid, focus it
        if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.deiconify()  # Show window if it exists
            self.settings_window.lift()       # Bring to front
            self.settings_window.focus_force() # Force focus
            return

        # Create settings window
        self.settings_window = tk.Toplevel(self)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x600")
        self.settings_window.minsize(400, 500)
        self.settings_window.resizable(True, True)  # Allow resizing
        
        # Set window icon using settings-specific icon
        self._set_window_icon(self.settings_window, '32', 'settings')
        
        # Add to window tracking
        self.app_windows.append(self.settings_window)
        
        # Bind focus event
        self.settings_window.bind("<FocusIn>", lambda e: self._on_window_focus(self.settings_window))
        
        # Center on parent
        self.settings_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - self.settings_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - self.settings_window.winfo_height()) // 2
        self.settings_window.geometry(f"+{x}+{y}")
        
        # Create settings content
        self._create_settings_content()

    def _create_settings_content(self):
        """Create settings window content"""
        # Create a container frame
        container = ttk.Frame(self.settings_window)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar for scrolling
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create a frame inside the canvas for the content
        main_frame = ttk.Frame(canvas)
        
        # Add the frame to the canvas
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Make the frame expand to the width of the canvas
        def configure_canvas(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas)
        
        # Update the scrollregion when the size of the frame changes
        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        main_frame.bind('<Configure>', update_scrollregion)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            # Scroll 2 lines at a time for better user experience
            canvas.yview_scroll(int(-1 * (event.delta / 60)), "units")
        
        # Bind mousewheel to canvas and all its children
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Add keyboard scrolling
        self.settings_window.bind("<Up>", lambda e: canvas.yview_scroll(-1, "units"))
        self.settings_window.bind("<Down>", lambda e: canvas.yview_scroll(1, "units"))
        self.settings_window.bind("<Prior>", lambda e: canvas.yview_scroll(-1, "pages"))
        self.settings_window.bind("<Next>", lambda e: canvas.yview_scroll(1, "pages"))
        
        # Unbind the mousewheel event when the window is destroyed
        def _on_destroy(event):
            canvas.unbind_all("<MouseWheel>")
        
        self.settings_window.bind("<Destroy>", _on_destroy)

        # JDL URL Settings - Moved to the top of the dialog
        jdl_frame = ttk.LabelFrame(main_frame, text="JDL URL Settings", padding="5")
        jdl_frame.pack(fill=tk.X, pady=5)
        
        # Reverse Inbound URL
        ttk.Label(jdl_frame, text="Reverse Inbound URL:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        reverse_url_var = tk.StringVar(value=self.config_manager.settings.jdl_reverse_inbound_url if hasattr(self.config_manager.settings, 'jdl_reverse_inbound_url') else "https://iwms.us.jdlglobal.com/#/createAfterSalesOrder")
        reverse_url_entry = ttk.Entry(jdl_frame, textvariable=reverse_url_var, width=40)
        reverse_url_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Receive URL
        ttk.Label(jdl_frame, text="Receive URL:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        receive_url_var = tk.StringVar(value=self.config_manager.settings.jdl_receive_url if hasattr(self.config_manager.settings, 'jdl_receive_url') else "https://iwms.us.jdlglobal.com/#/scan")
        receive_url_entry = ttk.Entry(jdl_frame, textvariable=receive_url_var, width=40)
        receive_url_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Reset URLs button
        def reset_urls():
            reverse_url_var.set("https://iwms.us.jdlglobal.com/#/createAfterSalesOrder")
            receive_url_var.set("https://iwms.us.jdlglobal.com/#/scan")
            messagebox.showinfo("URLs Reset", "The JDL URLs have been reset to their default values.")
            
        reset_urls_btn = ttk.Button(
            jdl_frame,
            text="Reset to Defaults",
            command=reset_urls
        )
        reset_urls_btn.grid(row=2, column=1, sticky="e", padx=5, pady=5)
        
        # Window Settings - Moved up in the dialog
        window_frame = ttk.LabelFrame(main_frame, text="Window Settings", padding="5")
        window_frame.pack(fill=tk.X, pady=5)

        # Always on Top checkbox
        always_on_top_var = tk.BooleanVar(value=self.config_manager.settings.always_on_top)
        always_on_top_cb = ttk.Checkbutton(
            window_frame, 
            text="Always on Top", 
            variable=always_on_top_var
        )
        always_on_top_cb.grid(row=0, column=0, sticky="w", columnspan=2)
        
        # Auto-close browser tabs checkbox
        auto_close_tabs_var = tk.BooleanVar(value=self.config_manager.settings.auto_close_browser_tabs if hasattr(self.config_manager.settings, 'auto_close_browser_tabs') else True)
        auto_close_tabs_cb = ttk.Checkbutton(
            window_frame, 
            text="Auto-close browser tabs", 
            variable=auto_close_tabs_var
        )
        auto_close_tabs_cb.grid(row=1, column=0, sticky="w", columnspan=2)

        # Add transparency level control
        ttk.Label(window_frame, text="Transparency:").grid(row=2, column=0, sticky="w")
        transparency_var = tk.DoubleVar(value=self.config_manager.settings.transparency_level)
        transparency_scale = ttk.Scale(
            window_frame,
            from_=0.1,
            to=1.0,
            orient="horizontal",
            variable=transparency_var
        )
        transparency_scale.grid(row=2, column=1, sticky="ew", padx=5)
        
        # Font Sizes
        font_frame = ttk.LabelFrame(main_frame, text="Font Settings", padding="5")
        font_frame.pack(fill=tk.X, pady=5)

        # Large Font Size
        ttk.Label(font_frame, text="Large Font Size:").grid(row=0, column=0, padx=5, pady=2)
        large_font_size = ttk.Entry(font_frame, width=10)
        large_font_size.insert(0, str(self.config_manager.settings.font_size_large))
        large_font_size.grid(row=0, column=1, padx=5, pady=2)

        # Medium Font Size
        ttk.Label(font_frame, text="Medium Font Size:").grid(row=1, column=0, padx=5, pady=2)
        medium_font_size = ttk.Entry(font_frame, width=10)
        medium_font_size.insert(0, str(self.config_manager.settings.font_size_medium))
        medium_font_size.grid(row=1, column=1, padx=5, pady=2)

        # Barcode Settings
        barcode_frame = ttk.LabelFrame(main_frame, text="Barcode Settings", padding="5")
        barcode_frame.pack(fill=tk.X, pady=5)
        
        # Create a notebook for barcode settings to organize them
        barcode_notebook = ttk.Notebook(barcode_frame)
        barcode_notebook.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Basic dimensions tab
        basic_tab = ttk.Frame(barcode_notebook, padding=5)
        barcode_notebook.add(basic_tab, text="Basic")
        
        # Barcode Width
        ttk.Label(basic_tab, text="Barcode Width:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        barcode_width = ttk.Entry(basic_tab, width=10)
        barcode_width.insert(0, str(self.config_manager.settings.barcode_width))
        barcode_width.grid(row=0, column=1, padx=5, pady=2)
        
        # Barcode Height
        ttk.Label(basic_tab, text="Barcode Height:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        barcode_height = ttk.Entry(basic_tab, width=10)
        barcode_height.insert(0, str(self.config_manager.settings.barcode_height))
        barcode_height.grid(row=1, column=1, padx=5, pady=2)
        
        # DPI Setting
        ttk.Label(basic_tab, text="DPI:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        dpi_entry = ttk.Entry(basic_tab, width=10)
        dpi_entry.insert(0, str(self.config_manager.settings.DPI))
        dpi_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Barcode DPI Setting
        ttk.Label(basic_tab, text="Barcode DPI:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        barcode_dpi_entry = ttk.Entry(basic_tab, width=10)
        barcode_dpi_entry.insert(0, str(self.config_manager.settings.barcode_dpi))
        barcode_dpi_entry.grid(row=3, column=1, padx=5, pady=2)
        
        # Advanced tab for barcode appearance
        advanced_tab = ttk.Frame(barcode_notebook, padding=5)
        barcode_notebook.add(advanced_tab, text="Advanced")
        
        # Module Height (bar height)
        ttk.Label(advanced_tab, text="Bar Height:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        module_height_entry = ttk.Entry(advanced_tab, width=10)
        module_height_entry.insert(0, str(self.config_manager.settings.barcode_module_height))
        module_height_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Module Width (bar width)
        ttk.Label(advanced_tab, text="Bar Width:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        module_width_entry = ttk.Entry(advanced_tab, width=10)
        module_width_entry.insert(0, str(self.config_manager.settings.barcode_module_width))
        module_width_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Quiet Zone
        ttk.Label(advanced_tab, text="Quiet Zone:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        quiet_zone_entry = ttk.Entry(advanced_tab, width=10)
        quiet_zone_entry.insert(0, str(self.config_manager.settings.barcode_quiet_zone))
        quiet_zone_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Text tab for text-related settings
        text_tab = ttk.Frame(barcode_notebook, padding=5)
        barcode_notebook.add(text_tab, text="Text")
        
        # UPC Font Size
        ttk.Label(text_tab, text="UPC Font Size:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        font_size_entry = ttk.Entry(text_tab, width=10)
        font_size_entry.insert(0, str(self.config_manager.settings.barcode_font_size))
        font_size_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Text Distance
        ttk.Label(text_tab, text="Text Distance:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        text_distance_entry = ttk.Entry(text_tab, width=10)
        text_distance_entry.insert(0, str(self.config_manager.settings.barcode_text_distance))
        text_distance_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Show UPC Number
        write_text_var = tk.BooleanVar(value=self.config_manager.settings.barcode_write_text)
        write_text_cb = ttk.Checkbutton(text_tab, text="Show UPC Number", variable=write_text_var)
        write_text_cb.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
        
        # Center UPC Text
        center_text_var = tk.BooleanVar(value=self.config_manager.settings.barcode_center_text)
        center_text_cb = ttk.Checkbutton(text_tab, text="Center UPC Text", variable=center_text_var)
        center_text_cb.grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
        
        # Colors tab
        colors_tab = ttk.Frame(barcode_notebook, padding=5)
        barcode_notebook.add(colors_tab, text="Colors")
        
        # Background Color
        ttk.Label(colors_tab, text="Background:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        background_entry = ttk.Entry(colors_tab, width=10)
        background_entry.insert(0, self.config_manager.settings.barcode_background)
        background_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Foreground Color
        ttk.Label(colors_tab, text="Foreground:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        foreground_entry = ttk.Entry(colors_tab, width=10)
        foreground_entry.insert(0, self.config_manager.settings.barcode_foreground)
        foreground_entry.grid(row=1, column=1, padx=5, pady=2)

        # CSV Import Frame
        csv_frame = ttk.LabelFrame(main_frame, text="Batch Import", padding="5")
        csv_frame.pack(fill=tk.X, pady=5)

        # CSV Import Description
        ttk.Label(csv_frame, text="Import multiple labels from a CSV file.\nRequired columns: 'Label Name', 'Upc'", 
                 justify=tk.LEFT).pack(padx=5, pady=2)

        # Upload CSV Button
        upload_csv_btn = ttk.Button(
            csv_frame,
            text="Upload CSV File",
            command=self.upload_csv,
            style="Accent.TButton"
        )
        upload_csv_btn.pack(pady=5)

        # Save settings function
        def save_settings():
            try:
                # Save window settings
                self.config_manager.settings.always_on_top = always_on_top_var.get()
                self.config_manager.settings.transparency_level = transparency_var.get()
                self.config_manager.settings.auto_close_browser_tabs = auto_close_tabs_var.get()
                
                # Save JDL URLs
                if hasattr(self.config_manager.settings, 'jdl_reverse_inbound_url'):
                    self.config_manager.settings.jdl_reverse_inbound_url = reverse_url_var.get()
                if hasattr(self.config_manager.settings, 'jdl_receive_url'):
                    self.config_manager.settings.jdl_receive_url = receive_url_var.get()
                
                # Save font sizes
                try:
                    self.config_manager.settings.font_size_large = int(large_font_size.get())
                    self.config_manager.settings.font_size_medium = int(medium_font_size.get())
                except ValueError:
                    raise ValueError("Font sizes must be integers")
                
                # Save barcode settings
                try:
                    self.config_manager.settings.barcode_width = int(barcode_width.get())
                    self.config_manager.settings.barcode_height = int(barcode_height.get())
                    self.config_manager.settings.DPI = int(dpi_entry.get())
                    self.config_manager.settings.barcode_dpi = int(barcode_dpi_entry.get())
                    self.config_manager.settings.barcode_module_height = float(module_height_entry.get())
                    self.config_manager.settings.barcode_module_width = float(module_width_entry.get())
                    self.config_manager.settings.barcode_quiet_zone = float(quiet_zone_entry.get())
                    self.config_manager.settings.barcode_font_size = int(font_size_entry.get())
                    self.config_manager.settings.barcode_text_distance = float(text_distance_entry.get())
                    self.config_manager.settings.barcode_write_text = write_text_var.get()
                    self.config_manager.settings.barcode_center_text = center_text_var.get()
                    self.config_manager.settings.barcode_background = background_entry.get()
                    self.config_manager.settings.barcode_foreground = foreground_entry.get()
                except ValueError:
                    raise ValueError("Invalid barcode settings. Please check your inputs.")
                
                # Save settings to file
                self.config_manager.save_settings()
                
                # Close the settings window
                self.settings_window.destroy()
                
                # Show success message
                messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")
                
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))
        
        # Auto-close browser tabs checkbox
        auto_close_tabs_var = tk.BooleanVar(value=self.config_manager.settings.auto_close_browser_tabs if hasattr(self.config_manager.settings, 'auto_close_browser_tabs') else True)
        auto_close_tabs_cb = ttk.Checkbutton(
            window_frame, 
            text="Auto-close browser tabs", 
            variable=auto_close_tabs_var
        )
        auto_close_tabs_cb.grid(row=1, column=0, sticky="w", columnspan=2)

        # Add transparency level control
        ttk.Label(window_frame, text="Transparency:").grid(row=2, column=0, sticky="w")
        transparency_var = tk.DoubleVar(value=self.config_manager.settings.transparency_level)
        transparency_scale = ttk.Scale(
            window_frame,
            from_=0.1,
            to=1.0,
            orient="horizontal",
            variable=transparency_var
        )
        transparency_scale.grid(row=2, column=1, sticky="ew", padx=5)
        
        # This section has been moved to the top of the dialog

        # Add callback for real-time transparency updates
        def update_transparency(*args):
            alpha = transparency_var.get()
            self.settings_window.attributes('-alpha', alpha)
            self.attributes('-alpha', alpha)
            # Update any other open windows
            for window in self.app_windows:
                if isinstance(window, tk.Toplevel):
                    window.attributes('-alpha', alpha)

        transparency_var.trace_add('write', update_transparency)

        def save_settings():
            try:
                # Validate and save font sizes
                new_font_large = int(large_font_size.get())
                new_font_medium = int(medium_font_size.get())
                new_barcode_width = int(barcode_width.get())
                new_barcode_height = int(barcode_height.get())
                new_transparency = transparency_var.get()
                
                # Validate and save DPI settings
                new_dpi = int(dpi_entry.get())
                new_barcode_dpi = int(barcode_dpi_entry.get())
                
                # Validate and save barcode appearance settings
                new_module_height = float(module_height_entry.get())
                new_module_width = float(module_width_entry.get())
                new_quiet_zone = float(quiet_zone_entry.get())
                new_font_size = int(font_size_entry.get())
                new_text_distance = float(text_distance_entry.get())
                new_background = background_entry.get()
                new_foreground = foreground_entry.get()

                if not (0.1 <= new_transparency <= 1.0):
                    raise ValueError("Transparency must be between 0.1 and 1.0")
                
                if new_dpi < 72:
                    raise ValueError("DPI must be at least 72")
                    
                if new_barcode_dpi < 72:
                    raise ValueError("Barcode DPI must be at least 72")

                # Save basic settings
                self.config_manager.settings.font_size_large = new_font_large
                self.config_manager.settings.font_size_medium = new_font_medium
                self.config_manager.settings.barcode_width = new_barcode_width
                self.config_manager.settings.barcode_height = new_barcode_height
                self.config_manager.settings.always_on_top = always_on_top_var.get()
                self.config_manager.settings.transparency_level = new_transparency
                
                # Save DPI settings
                self.config_manager.settings.DPI = new_dpi
                self.config_manager.settings.barcode_dpi = new_barcode_dpi
                
                # Save barcode appearance settings
                self.config_manager.settings.barcode_module_height = new_module_height
                self.config_manager.settings.barcode_module_width = new_module_width
                self.config_manager.settings.barcode_quiet_zone = new_quiet_zone
                self.config_manager.settings.barcode_font_size = new_font_size
                self.config_manager.settings.barcode_text_distance = new_text_distance
                self.config_manager.settings.barcode_write_text = write_text_var.get()
                self.config_manager.settings.barcode_center_text = center_text_var.get()
                self.config_manager.settings.barcode_background = new_background
                self.config_manager.settings.barcode_foreground = new_foreground
                
                # Save auto-close browser tabs setting
                self.config_manager.settings.auto_close_browser_tabs = auto_close_tabs_var.get()
                
                # Save JDL URL settings
                self.config_manager.settings.jdl_reverse_inbound_url = reverse_url_var.get()
                self.config_manager.settings.jdl_receive_url = receive_url_var.get()

                self.config_manager.save_settings()
                self.settings_window.destroy()
                
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))

        # Add a button frame at the bottom that stays visible
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        save_btn = ttk.Button(
            button_frame,
            text="Save Settings",
            command=save_settings,
            style="Accent.TButton"
        )
        save_btn.pack(pady=5, padx=10)

    def preview_label(self):
        """Show label preview window"""
        # Get input values
        name_line1 = self.inputs["name_line1"].get().strip()
        name_line2 = self.inputs["name_line2"].get().strip()
        variant = self.inputs["variant"].get().strip()
        upc_code = self.inputs["upc_code"].get().strip()
        
        # Validate inputs
        if not name_line1:
            messagebox.showwarning("Warning", "Product Name Line 1 is required.")
            self.inputs["name_line1"].focus_set()
            return
            
        if not upc_code or len(upc_code) != 12:
            messagebox.showwarning("Warning", "UPC Code must be exactly 12 digits.")
            self.inputs["upc_code"].focus_set()
            return
        
        # Create label data object
        label_data = LabelData(
            name_line1=name_line1,
            name_line2=name_line2,
            variant=variant,
            upc_code=upc_code
        )
        
        # Generate preview image
        try:
            preview_image = self.barcode_generator.generate_label(label_data)
            if not preview_image:
                raise Exception("Failed to generate label")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {str(e)}")
            return
        
        # Create or update preview window
        if not hasattr(self, 'preview_window') or not self.preview_window or not self.preview_window.winfo_exists():
            self.preview_window = tk.Toplevel(self)
            self.preview_window.title("Label Preview")
            
            # Set window icon
            self._set_window_icon(self.preview_window, '32')
            
            self.preview_window.resizable(False, False)
            self.preview_window.transient(self)
            
            # Add to window tracking
            self.app_windows.append(self.preview_window)
            
            # Bind focus event
            self.preview_window.bind("<FocusIn>", lambda e: self._on_window_focus(self.preview_window))
            
            # Create preview frame
            preview_frame = tk.Frame(self.preview_window)
            preview_frame.pack(padx=10, pady=10)
            
            # Create preview label
            self.preview_label = tk.Label(preview_frame)
            self.preview_label.pack()
            
            # Create save button with styling
            save_btn = tk.Button(preview_frame,
                text="Save Label",
                command=lambda: self.save_label(label_data),
                bg='#2ecc71',  # Green
                fg='white',
                activebackground='#27ae60',
                activeforeground='white',
                font=('TkDefaultFont', 10, 'bold'),
                relief='raised',
                width=15,
                height=2
            )
            save_btn.pack(pady=10)
        
        # Update preview image
        preview_photo = ImageTk.PhotoImage(preview_image)
        self.preview_label.config(image=preview_photo)
        self.preview_label.image = preview_photo  # Keep reference
        
        # Center on parent
        self.preview_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - self.preview_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - self.preview_window.winfo_height()) // 2
        self.preview_window.geometry(f"+{x}+{y}")
        
        # Show window
        self.preview_window.deiconify()
        self.preview_window.lift()
        self.preview_window.focus_force()

    def save_label(self, label_data):
        """Save the label to a file"""
        if not self.config_manager.settings.last_directory:
            directory = filedialog.askdirectory(
                title="Select where to save labels"
            )
            if not directory:
                return
            self.config_manager.settings.last_directory = directory
            self.config_manager.save_settings()
        
        try:
            # Generate and save the label
            self.barcode_generator.generate_and_save(
                label_data,
                self.config_manager.settings.last_directory
            )
            
            # Update PNG count
            self._update_png_count()
            
            # Close preview window
            if hasattr(self, 'preview_window') and self.preview_window:
                self.preview_window.destroy()
                self.preview_window = None
            
            # Show success message
            messagebox.showinfo("Success", "Label saved successfully!")
            
            # Clear inputs
            self.clear_inputs()
            
            # Focus on first input
            self.inputs["name_line1"].focus_set()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save label: {str(e)}")

    def _create_styled_button(self, parent, text, command, width=8, has_icon=False, icon=None, tooltip_text="", color_scheme=None):
        """Create a styled button with hover effect"""
        if color_scheme is None:
            color_scheme = {
                'bg': '#3498db',  # Default blue
                'fg': 'white',
                'hover_bg': '#2980b9',
                'active_bg': '#2473a6'
            }

        btn = tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            font=('TkDefaultFont', 10, 'bold'),  # Increased font size and made bold
            relief='raised',
            bg=color_scheme['bg'],
            fg=color_scheme['fg'],
            activebackground=color_scheme['active_bg'],
            activeforeground='white',
            bd=1,  # Border width
            padx=10,  # Horizontal padding
            pady=4,   # Vertical padding
        )
        
        if has_icon and icon:
            btn.config(image=icon, compound=tk.LEFT)

        # Add hover effect
        def on_enter(e):
            if not (hasattr(btn, 'is_active') and btn.is_active):
                btn['background'] = color_scheme['hover_bg']
                btn['cursor'] = 'hand2'

        def on_leave(e):
            if not (hasattr(btn, 'is_active') and btn.is_active):
                btn['background'] = color_scheme['bg']
                btn['cursor'] = ''

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        # Add tooltip
        if tooltip_text:
            self.CreateToolTip(btn, tooltip_text)

        return btn

    def _create_top_control_frame(self):
        """Create top control frame with Always on Top, Settings, and Labels Count buttons"""
        top_control_frame = tk.Frame(self.main_frame, bg='SystemButtonFace')
        top_control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)  # Increased padding
        
        # Create a sub-frame for the buttons to ensure proper horizontal alignment
        button_frame = tk.Frame(top_control_frame, bg='SystemButtonFace')
        button_frame.pack(side=tk.LEFT, padx=8)  # Increased padding
        
        # Color schemes for different buttons
        always_on_top_colors = {
            'bg': '#e74c3c',  # Red
            'fg': 'white',
            'hover_bg': '#c0392b',
            'active_bg': '#2ecc71'  # Green when active
        }
        
        settings_colors = {
            'bg': '#9b59b6',  # Purple
            'fg': 'white',
            'hover_bg': '#8e44ad',
            'active_bg': '#7d3c98'
        }
        
        labels_count_colors = {
            'bg': '#2ecc71',  # Green
            'fg': 'white',
            'hover_bg': '#27ae60',
            'active_bg': '#219a52'
        }
        
        # Always on Top button with toggle styling
        self.always_on_top_btn = self._create_styled_button(
            button_frame,
            text="Always on Top",
            command=self.toggle_always_on_top,
            width=12,
            color_scheme=always_on_top_colors
        )
        self.always_on_top_btn.is_active = False
        self.always_on_top_btn.pack(side=tk.LEFT, padx=3)  # Increased padding
        
        # Settings button with matching style
        settings_btn = self._create_styled_button(
            button_frame,
            text="Settings",
            command=self.show_settings,
            width=8,
            color_scheme=settings_colors
        )
        settings_btn.pack(side=tk.LEFT, padx=3)  # Increased padding
        
        # Labels count button
        self.png_count_btn = self._create_styled_button(
            button_frame,
            text="",  # Text will be set by textvariable
            command=self._select_output_directory,
            width=12,
            color_scheme=labels_count_colors
        )
        self.png_count_btn.config(textvariable=self.png_count)
        self.png_count_btn.pack(side=tk.LEFT, padx=3)  # Increased padding

    def _create_control_frame(self):
        """Create control buttons frame (Reset)"""
        control_frame = tk.Frame(self.main_frame, bg='SystemButtonFace')
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Reset button with vibrant red theme
        reset_btn = tk.Button(control_frame,
            text="Reset",
            width=8,
            bg='#e74c3c',  # Bright red
            activebackground='#c0392b',  # Darker red when clicked
            fg='white',
            command=self.clear_inputs
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

    def open_selected_file(self):
        """Open the selected file"""
        selection = self.listbox.curselection()
        if selection:
            file_name = self.listbox.get(selection[0])
            file_path = os.path.join(self.config_manager.settings.last_directory, 
                                   file_name)
            try:
                # Open the saved file with the default program
                os.startfile(file_path)
                
                # Close the view files window
                self.file_window.destroy()
                self.file_window = None
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def print_selected_file(self):
        """Print the selected file directly"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a file to print.")
            return

        file_name = self.listbox.get(selection[0])
        file_path = os.path.join(self.config_manager.settings.last_directory, 
                               file_name)
        try:
            # Extract UPC from filename (assuming it's in the filename)
            upc_match = re.search(r'\d{12}', file_name)
            if upc_match:
                self.last_printed_upc = upc_match.group(0)
                
            # Update last print time
            self.last_print_time = time.time()
            
            # If mirror print is enabled, create a mirrored temporary copy
            if self.is_mirror_print.get():
                img = Image.open(file_path)
                mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                temp_dir = os.path.join(os.environ['TEMP'], 'label_maker')
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, f'mirror_{file_name}')
                mirrored_img.save(temp_path)
                os.startfile(temp_path, "print")
            else:
                os.startfile(file_path, "print")
            self.file_window.after(1000, lambda: pyautogui.press('enter'))
            
            # If auto-switch is enabled, select the next item
            if self.is_auto_switch.get():
                self.select_next_item()
            
            # If print minimize is enabled, minimize the window after a delay
            if self.is_print_minimize.get():
                self.file_window.after(1500, lambda: self.file_window.iconify())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print: {str(e)}")

    def update_window_transparency(self):
        """Update the transparency of the main window"""
        self.attributes('-alpha', self.transparency_level.get())

    def toggle_new_feature(self):
        """Toggle the new feature state."""
        self.is_new_feature.set(not self.is_new_feature.get())
        self.config_manager.settings.view_files_new_feature = self.is_new_feature.get()
        self.config_manager.save_settings()

    def toggle_print_minimize(self):
        """Toggle the print minimize state."""
        self.is_print_minimize.set(not self.is_print_minimize.get())
        self.config_manager.settings.view_files_print_minimize = self.is_print_minimize.get()
        self.config_manager.save_settings()

    def toggle_auto_close(self):
        """Toggle the auto close state."""
        self.is_auto_close.set(not self.is_auto_close.get())
        self.config_manager.settings.view_files_auto_close = self.is_auto_close.get()
        self.config_manager.save_settings()

    def select_next_item(self):
        """Select the next item in the listbox"""
        current_index = self.listbox.curselection()
        if current_index:
            next_index = (current_index[0] + 1) % self.listbox.size()
            self.listbox.selection_clear(0, tk.END)
            self.listbox.select_set(next_index)
            self.listbox.see(next_index)

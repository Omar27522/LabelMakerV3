"""
JDL Global IWMS Automation Frame.
This module provides a UI for automating interactions with the JDL Global IWMS site.
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.jdl_automation import create_after_sales_orders
from src.utils.ui_components import (
    create_title_section, create_colored_button, create_button_grid, 
    create_form_field_group, create_status_bar
)
from src.utils.file_utils import get_project_root

# Set up logging
logger = logging.getLogger(__name__)

class JDLAutomationFrame(tk.Frame):
    """Frame for JDL Global IWMS automation."""
    
    def __init__(self, parent, config_manager, return_callback):
        """
        Initialize the JDL Automation Frame.
        
        Args:
            parent: Parent widget
            config_manager: Configuration manager
            return_callback: Callback to return to the previous screen
        """
        super().__init__(parent, bg='white')
        
        self.parent = parent
        self.config_manager = config_manager
        self.return_callback = return_callback
        
        # Create UI elements
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        # Main container with padding
        container = tk.Frame(self, bg='white', padx=20, pady=20)
        container.pack(fill='both', expand=True)
        
        # Title section
        title_frame = create_title_section(
            container, 
            "JDL Global IWMS Automation", 
            "Create after-sales orders automatically"
        )
        title_frame.pack(fill='x', pady=(0, 20))
        
        # Create a back button
        back_button = create_colored_button(
            title_frame,
            "← Back",
            '#f0f0f0',
            '#e0e0e0',
            self.return_callback
        )
        back_button.pack(side='right')
        
        # Create content frame
        content_frame = tk.Frame(container, bg='white')
        content_frame.pack(fill='both', expand=True)
        
        # Create credentials section
        credentials_frame = tk.LabelFrame(
            content_frame, 
            text="JDL Global IWMS Credentials", 
            font=("Arial", 12, "bold"), 
            bg='white', 
            padx=10, 
            pady=10
        )
        credentials_frame.pack(fill='x', pady=(0, 15))
        
        # Username field
        username_var = tk.StringVar()
        username_frame = tk.Frame(credentials_frame, bg='white')
        username_frame.pack(fill='x', pady=(5, 5))
        
        tk.Label(
            username_frame, 
            text="Username:", 
            font=("Arial", 10), 
            bg='white', 
            width=15, 
            anchor='w'
        ).pack(side='left')
        
        username_entry = tk.Entry(
            username_frame, 
            textvariable=username_var, 
            font=("Arial", 10), 
            width=30
        )
        username_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Password field
        password_var = tk.StringVar()
        password_frame = tk.Frame(credentials_frame, bg='white')
        password_frame.pack(fill='x', pady=(5, 5))
        
        tk.Label(
            password_frame, 
            text="Password:", 
            font=("Arial", 10), 
            bg='white', 
            width=15, 
            anchor='w'
        ).pack(side='left')
        
        password_entry = tk.Entry(
            password_frame, 
            textvariable=password_var, 
            font=("Arial", 10), 
            width=30, 
            show="*"
        )
        password_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Tracking numbers section
        tracking_frame = tk.LabelFrame(
            content_frame, 
            text="Tracking Numbers", 
            font=("Arial", 12, "bold"), 
            bg='white', 
            padx=10, 
            pady=10
        )
        tracking_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Tracking numbers text area
        tracking_text = tk.Text(
            tracking_frame, 
            font=("Arial", 10), 
            height=10, 
            width=50
        )
        tracking_text.pack(fill='both', expand=True, pady=(5, 5))
        
        # Add a scrollbar
        scrollbar = tk.Scrollbar(tracking_text)
        scrollbar.pack(side='right', fill='y')
        tracking_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=tracking_text.yview)
        
        # Instructions
        instructions = tk.Label(
            tracking_frame, 
            text="Enter one tracking number per line. Numbers will be processed in the order listed (or reverse order if enabled in settings).", 
            font=("Arial", 8, "italic"), 
            fg='gray', 
            bg='white', 
            wraplength=550, 
            justify='left'
        )
        instructions.pack(anchor='w', pady=(5, 0))
        
        # Display the current setting for reverse inbound creation
        reverse_status = "enabled" if self.config_manager.settings.reverseinbound_creation else "disabled"
        reverse_label = tk.Label(
            tracking_frame, 
            text=f"Reverse inbound creation is currently {reverse_status}.", 
            font=("Arial", 8, "italic"), 
            fg='gray', 
            bg='white'
        )
        reverse_label.pack(anchor='w')
        
        # Status section
        status_frame = tk.Frame(container, bg='white')
        status_frame.pack(fill='x', pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            status_frame, 
            textvariable=self.status_var, 
            font=("Arial", 10), 
            bg='white', 
            fg='black'
        )
        self.status_label.pack(side='left')
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            status_frame, 
            variable=self.progress_var, 
            length=300, 
            mode='determinate'
        )
        self.progress_bar.pack(side='right')
        
        # Button section
        button_frame = tk.Frame(container, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Process button
        self.process_button = create_colored_button(
            button_frame,
            "Process Tracking Numbers",
            '#4CAF50',
            '#45a049',
            self._process_tracking_numbers
        )
        self.process_button.pack(side='right', padx=(10, 0))
        
        # Clear button
        clear_button = create_colored_button(
            button_frame,
            "Clear",
            '#f44336',
            '#d32f2f',
            lambda: tracking_text.delete(1.0, tk.END)
        )
        clear_button.pack(side='right')
        
        # Store references to widgets
        self.username_entry = username_entry
        self.password_entry = password_entry
        self.tracking_text = tracking_text
    
    def _update_status(self, message, color='black'):
        """
        Update the status message.
        
        Args:
            message: Status message
            color: Text color
        """
        self.status_var.set(message)
        self.status_label.config(fg=color)
        self.update_idletasks()
    
    def _process_tracking_numbers(self):
        """Process the tracking numbers entered by the user."""
        # Get username and password
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Validate credentials
        if not username or not password:
            messagebox.showerror("Error", "Please enter your JDL Global IWMS username and password.")
            return
        
        # Get tracking numbers
        tracking_text = self.tracking_text.get(1.0, tk.END).strip()
        if not tracking_text:
            messagebox.showerror("Error", "Please enter at least one tracking number.")
            return
        
        # Parse tracking numbers (one per line)
        tracking_numbers = [line.strip() for line in tracking_text.split('\n') if line.strip()]
        
        # Disable UI elements during processing
        self._set_ui_state(False)
        
        # Update status
        self._update_status("Processing tracking numbers...", 'blue')
        
        # Start processing in a separate thread
        threading.Thread(
            target=self._process_in_thread,
            args=(username, password, tracking_numbers),
            daemon=True
        ).start()
    
    def _process_in_thread(self, username, password, tracking_numbers):
        """
        Process tracking numbers in a separate thread.
        
        Args:
            username: JDL Global IWMS username
            password: JDL Global IWMS password
            tracking_numbers: List of tracking numbers to process
        """
        try:
            # Initialize progress bar
            total = len(tracking_numbers)
            self.progress_var.set(0)
            
            # Process tracking numbers
            success_count, failed_tracking_numbers = create_after_sales_orders(
                self.config_manager,
                tracking_numbers,
                username,
                password
            )
            
            # Update progress bar to 100%
            self.progress_var.set(100)
            
            # Update status based on results
            if success_count == total:
                self._update_status(f"Successfully processed all {total} tracking numbers.", 'green')
            elif success_count > 0:
                self._update_status(
                    f"Processed {success_count} of {total} tracking numbers. {len(failed_tracking_numbers)} failed.", 
                    'orange'
                )
            else:
                self._update_status("Failed to process any tracking numbers.", 'red')
            
            # Show results
            if failed_tracking_numbers:
                failed_text = "\n".join(failed_tracking_numbers)
                messagebox.showwarning(
                    "Processing Results",
                    f"Successfully processed {success_count} of {total} tracking numbers.\n\n"
                    f"The following tracking numbers failed:\n{failed_text}"
                )
            else:
                messagebox.showinfo(
                    "Processing Complete",
                    f"Successfully processed all {total} tracking numbers."
                )
        except Exception as e:
            logger.error(f"Error in processing thread: {str(e)}")
            self._update_status(f"Error: {str(e)}", 'red')
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # Re-enable UI elements
            self.after(0, lambda: self._set_ui_state(True))
    
    def _set_ui_state(self, enabled):
        """
        Enable or disable UI elements.
        
        Args:
            enabled: Whether to enable or disable UI elements
        """
        state = 'normal' if enabled else 'disabled'
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)
        self.tracking_text.config(state=state)
        self.process_button.config(state=state)

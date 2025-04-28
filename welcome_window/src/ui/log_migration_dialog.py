"""
Dialog for migrating logs from old systems to the new centralized log database.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading

from src.utils.ui_utils import center_window, create_button
from src.utils.log_manager import run_migration_wizard, get_logs_db_path, get_shipping_logs

class LogMigrationDialog:
    def __init__(self, parent):
        """
        Initialize the log migration dialog.
        
        Args:
            parent: The parent window
        """
        self.parent = parent
        self.dialog = None
        
    def show(self):
        """
        Show the log migration dialog.
        """
        # Create the dialog
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Log Migration Utility")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg='white')
        
        # Make the dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        center_window(self.dialog)
        
        # Create the main frame
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Log Migration Utility", 
            font=("Arial", 16, "bold"), 
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Description
        description = (
            "This utility will migrate shipping logs from the old text file and database "
            "to the new centralized log database. This helps eliminate redundancy "
            "while maintaining a complete record of all shipping activities."
        )
        
        description_label = tk.Label(
            main_frame,
            text=description,
            font=("Arial", 10),
            bg='white',
            wraplength=450,
            justify='left'
        )
        description_label.pack(pady=(0, 20), fill='x')
        
        # Status frame
        status_frame = tk.LabelFrame(
            main_frame,
            text="Current Log Status",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=10,
            pady=10
        )
        status_frame.pack(fill='x', pady=(0, 20))
        
        # Check for existing logs
        logs_dir, db_path = get_logs_db_path()
        
        # Old text log
        old_text_log_path = os.path.join(logs_dir, 'shipping_records.txt')
        old_text_log_exists = os.path.exists(old_text_log_path)
        
        # Old database
        old_db_path = os.path.join(os.path.dirname(logs_dir), 'data', 'shipping_records.db')
        old_db_exists = os.path.exists(old_db_path)
        
        # New database
        new_db_exists = os.path.exists(db_path)
        
        # Status labels
        text_log_status = "Found" if old_text_log_exists else "Not found"
        text_log_color = "green" if old_text_log_exists else "red"
        
        old_db_status = "Found" if old_db_exists else "Not found"
        old_db_color = "green" if old_db_exists else "red"
        
        new_db_status = "Exists" if new_db_exists else "Will be created"
        new_db_color = "green" if new_db_exists else "blue"
        
        # Add status labels
        status_grid = tk.Frame(status_frame, bg='white')
        status_grid.pack(fill='x', pady=(5, 5))
        
        # Column headers
        tk.Label(status_grid, text="Log Source", font=("Arial", 10, "bold"), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=(0, 5))
        tk.Label(status_grid, text="Status", font=("Arial", 10, "bold"), bg='white').grid(row=0, column=1, sticky='w', padx=(0, 10), pady=(0, 5))
        
        # Text log status
        tk.Label(status_grid, text="Old Text Log:", font=("Arial", 10), bg='white').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(0, 5))
        tk.Label(status_grid, text=text_log_status, font=("Arial", 10), bg='white', fg=text_log_color).grid(row=1, column=1, sticky='w', padx=(0, 10), pady=(0, 5))
        
        # Old database status
        tk.Label(status_grid, text="Old Database:", font=("Arial", 10), bg='white').grid(row=2, column=0, sticky='w', padx=(0, 10), pady=(0, 5))
        tk.Label(status_grid, text=old_db_status, font=("Arial", 10), bg='white', fg=old_db_color).grid(row=2, column=1, sticky='w', padx=(0, 10), pady=(0, 5))
        
        # New database status
        tk.Label(status_grid, text="New Log Database:", font=("Arial", 10), bg='white').grid(row=3, column=0, sticky='w', padx=(0, 10), pady=(0, 5))
        tk.Label(status_grid, text=new_db_status, font=("Arial", 10), bg='white', fg=new_db_color).grid(row=3, column=1, sticky='w', padx=(0, 10), pady=(0, 5))
        
        # Current log count if new DB exists
        if new_db_exists:
            try:
                logs = get_shipping_logs(limit=1000000)  # Get all logs
                log_count = len(logs)
                
                tk.Label(status_grid, text="Current Log Count:", font=("Arial", 10), bg='white').grid(row=4, column=0, sticky='w', padx=(0, 10), pady=(0, 5))
                tk.Label(status_grid, text=str(log_count), font=("Arial", 10), bg='white').grid(row=4, column=1, sticky='w', padx=(0, 10), pady=(0, 5))
            except:
                pass
        
        # Action buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Migrate button
        migrate_button = create_button(
            button_frame,
            text="Migrate Logs",
            command=self._run_migration,
            bg='#2196F3',
            padx=15,
            pady=5
        )
        migrate_button.pack(side='left', padx=(0, 10))
        
        # View logs button
        view_logs_button = create_button(
            button_frame,
            text="View Logs",
            command=self._view_logs,
            bg='#4CAF50',
            padx=15,
            pady=5
        )
        view_logs_button.pack(side='left')
        
        # Close button
        close_button = create_button(
            button_frame,
            text="Close",
            command=self.dialog.destroy,
            bg='#F44336',
            padx=15,
            pady=5
        )
        close_button.pack(side='right')
    
    def _run_migration(self):
        """
        Run the migration wizard.
        """
        # Disable the dialog during migration
        self.dialog.config(cursor="wait")
        for widget in self.dialog.winfo_children():
            widget.config(state="disabled")
        
        # Run the migration
        run_migration_wizard(self.dialog)
        
        # Re-enable the dialog after migration starts
        def enable_dialog():
            self.dialog.config(cursor="")
            for widget in self.dialog.winfo_children():
                widget.config(state="normal")
        
        # Schedule re-enabling after a short delay
        self.dialog.after(1000, enable_dialog)
    
    def _view_logs(self):
        """
        Open a simple log viewer.
        """
        # Create the log viewer dialog
        log_viewer = tk.Toplevel(self.dialog)
        log_viewer.title("Log Viewer")
        log_viewer.geometry("800x500")
        log_viewer.configure(bg='white')
        
        # Make the dialog modal
        log_viewer.transient(self.dialog)
        log_viewer.grab_set()
        
        # Center the dialog
        center_window(log_viewer)
        
        # Create the main frame
        main_frame = tk.Frame(log_viewer, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Shipping Logs", 
            font=("Arial", 16, "bold"), 
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Create a frame for the treeview
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        # Create a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Create the treeview
        columns = ("timestamp", "tracking_number", "sku", "action", "status", "details")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        
        # Configure the scrollbar
        scrollbar.config(command=tree.yview)
        
        # Define column widths and headings
        tree.column("timestamp", width=150, anchor="w")
        tree.column("tracking_number", width=150, anchor="w")
        tree.column("sku", width=100, anchor="w")
        tree.column("action", width=80, anchor="w")
        tree.column("status", width=80, anchor="w")
        tree.column("details", width=200, anchor="w")
        
        tree.heading("timestamp", text="Timestamp")
        tree.heading("tracking_number", text="Tracking Number")
        tree.heading("sku", text="SKU")
        tree.heading("action", text="Action")
        tree.heading("status", text="Status")
        tree.heading("details", text="Details")
        
        # Pack the treeview
        tree.pack(fill='both', expand=True)
        
        # Load the logs
        try:
            logs = get_shipping_logs(limit=1000)  # Get the most recent 1000 logs
            
            # Add logs to the treeview
            for log in logs:
                tree.insert("", "end", values=(
                    log.get("timestamp", ""),
                    log.get("tracking_number", ""),
                    log.get("sku", ""),
                    log.get("action", ""),
                    log.get("status", ""),
                    log.get("details", "")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error loading logs: {str(e)}")
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Close button
        close_button = create_button(
            button_frame,
            text="Close",
            command=log_viewer.destroy,
            bg='#F44336',
            padx=15,
            pady=5
        )
        close_button.pack(side='right')


def show_log_migration_dialog(parent):
    """
    Show the log migration dialog.
    
    Args:
        parent: The parent window
    """
    dialog = LogMigrationDialog(parent)
    dialog.show()

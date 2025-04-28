"""
Returns Data dialog for the Label Maker application.
This module provides a dialog for viewing and managing shipping records
stored in the local SQLite database.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import datetime
from datetime import timedelta, date
from tkcalendar import DateEntry  # Make sure to install this: pip install tkcalendar

# Import the Labels tab
from src.ui.labels_tab import LabelsTab

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_title_section, create_colored_button
from src.utils.database_operations import (
    initialize_database, 
    get_shipping_records, 
    get_record_count,
    update_shipping_record,
    delete_shipping_record,
    export_to_csv
)

class ReturnsDataDialog(tk.Toplevel):
    """Dialog for viewing and managing shipping records"""
    
    def __init__(self, parent, config_manager):
        """
        Initialize the Returns Data dialog
        
        Args:
            parent: Parent widget
            config_manager: Configuration manager instance
        """
        super().__init__(parent)
        
        # Store references
        self.parent = parent
        self.config_manager = config_manager
        
        # Set window properties
        self.title("Returns Data")
        self.geometry("900x600")
        self.minsize(800, 500)
        self.configure(bg='white')
        
        # Enable standard window controls (minimize, maximize, close)
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Initialize database
        initialize_database()
        
        # Initialize variables
        self.search_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.status_var = tk.StringVar()
        
        # Pagination variables
        self.current_page = 1
        self.records_per_page = 20
        self.total_records = 0
        self.total_pages = 1
        
        # Create UI
        self._create_ui()
        
        # Load initial data
        self._load_data()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Create main container
        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create title section
        title_frame, _, _ = create_title_section(
            main_frame, 
            "Returns Data", 
            "View and manage shipping records"
        )
        title_frame.pack(fill='x', pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create Labels tab first (will be the default tab)
        self.labels_tab = LabelsTab(self.notebook, self.config_manager)
        self.notebook.add(self.labels_tab, text="Labels")
        
        # Create Records tab
        self.records_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.records_tab, text="Records")
        
        # Select the Labels tab by default
        self.notebook.select(0)
        
        # Create search and filter section
        filter_frame = tk.Frame(self.records_tab, bg='white')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        # Search box
        search_label = tk.Label(filter_frame, text="Search:", bg='white')
        search_label.pack(side='left', padx=(0, 5))
        
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind("<Return>", lambda e: self._load_data())
        
        # Date range
        date_label = tk.Label(filter_frame, text="Date Range:", bg='white')
        date_label.pack(side='left', padx=(0, 5))
        
        # Start date picker
        start_date_picker = DateEntry(
            filter_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        start_date_picker.pack(side='left', padx=(0, 5))
        start_date_picker.bind("<<DateEntrySelected>>", lambda e: self.start_date_var.set(start_date_picker.get()))
        
        # End date picker
        end_date_picker = DateEntry(
            filter_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        end_date_picker.pack(side='left', padx=(0, 5))
        end_date_picker.bind("<<DateEntrySelected>>", lambda e: self.end_date_var.set(end_date_picker.get()))
        
        # Clear dates button
        clear_dates_button = tk.Button(
            filter_frame,
            text="Clear Dates",
            command=lambda: [self.start_date_var.set(""), self.end_date_var.set(""), self._load_data()]
        )
        clear_dates_button.pack(side='left', padx=(0, 10))
        
        # Search button
        search_button = tk.Button(
            filter_frame,
            text="Search",
            command=self._load_data,
            bg="#4CAF50",
            fg="white",
            width=10
        )
        search_button.pack(side='left', padx=(0, 5))
        
        # Create treeview for data display
        tree_frame = tk.Frame(self.records_tab, bg='white')
        tree_frame.pack(fill='both', expand=True, pady=(10, 10))
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("Treeview", 
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white")
        style.map('Treeview', background=[('selected', '#4CAF50')])
        
        # Create treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "timestamp", "tracking_number", "sku", "status", "notes"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)
        
        # Define columns
        self.tree.heading("id", text="ID")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("tracking_number", text="Tracking Number")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("status", text="Status")
        self.tree.heading("notes", text="Notes")
        
        # Set column widths
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("timestamp", width=150, anchor="center")
        self.tree.column("tracking_number", width=200, anchor="center")
        self.tree.column("sku", width=150, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("notes", width=200, anchor="w")
        
        # Pack treeview
        self.tree.pack(fill='both', expand=True)
        
        # Add double-click event to edit record
        self.tree.bind("<Double-1>", self._edit_record)
        
        # Create pagination controls
        pagination_frame = tk.Frame(self.records_tab, bg='white')
        pagination_frame.pack(fill='x', pady=(10, 0))
        
        # Previous page button
        self.prev_button = tk.Button(
            pagination_frame,
            text="< Previous",
            command=self._prev_page,
            state="disabled"
        )
        self.prev_button.pack(side='left')
        
        # Page info label
        self.page_info = tk.Label(
            pagination_frame,
            text="Page 1 of 1",
            bg='white'
        )
        self.page_info.pack(side='left', padx=10)
        
        # Next page button
        self.next_button = tk.Button(
            pagination_frame,
            text="Next >",
            command=self._next_page,
            state="disabled"
        )
        self.next_button.pack(side='left')
        
        # Records per page dropdown
        records_label = tk.Label(
            pagination_frame,
            text="Records per page:",
            bg='white'
        )
        records_label.pack(side='right', padx=(0, 5))
        
        records_values = [10, 20, 50, 100]
        records_dropdown = ttk.Combobox(
            pagination_frame,
            values=records_values,
            width=5,
            state="readonly"
        )
        records_dropdown.current(records_values.index(self.records_per_page))
        records_dropdown.pack(side='right')
        records_dropdown.bind("<<ComboboxSelected>>", self._change_records_per_page)
        
        # Create action buttons
        button_frame = tk.Frame(self.records_tab, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Export button
        export_button = tk.Button(
            button_frame,
            text="Export to CSV",
            command=self._export_to_csv,
            bg="#2196F3",
            fg="white",
            width=15
        )
        export_button.pack(side='left', padx=(0, 10))
        
        # Delete button
        delete_button = tk.Button(
            button_frame,
            text="Delete Selected",
            command=self._delete_selected,
            bg="#F44336",
            fg="white",
            width=15
        )
        delete_button.pack(side='left')
        
        # Close button
        close_button = tk.Button(
            button_frame,
            text="Close",
            command=self.destroy,
            width=15
        )
        close_button.pack(side='right')
    
    def _load_data(self):
        """Load data into the treeview based on current filters"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get search parameters
        search_term = self.search_var.get().strip()
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        
        # Calculate offset
        offset = (self.current_page - 1) * self.records_per_page
        
        # Get total count
        self.total_records = get_record_count(
            search_term=search_term if search_term else None,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None
        )
        
        # Calculate total pages
        self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)
        
        # Adjust current page if needed
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
            offset = (self.current_page - 1) * self.records_per_page
        
        # Get records
        records = get_shipping_records(
            limit=self.records_per_page,
            offset=offset,
            search_term=search_term if search_term else None,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None
        )
        
        # Populate treeview
        for record in records:
            self.tree.insert(
                "",
                "end",
                values=(
                    record["id"],
                    record["timestamp"],
                    record["tracking_number"] or "",
                    record["sku"] or "",
                    record["status"] or "",
                    record["notes"] or ""
                )
            )
        
        # Update pagination controls
        self._update_pagination()
    
    def _update_pagination(self):
        """Update pagination controls based on current state"""
        # Update page info
        self.page_info.config(text=f"Page {self.current_page} of {self.total_pages} ({self.total_records} records)")
        
        # Update button states
        self.prev_button.config(state="normal" if self.current_page > 1 else "disabled")
        self.next_button.config(state="normal" if self.current_page < self.total_pages else "disabled")
    
    def _prev_page(self):
        """Go to the previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_data()
    
    def _next_page(self):
        """Go to the next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_data()
    
    def _change_records_per_page(self, event):
        """Change the number of records displayed per page"""
        self.records_per_page = int(event.widget.get())
        self.current_page = 1  # Reset to first page
        self._load_data()
    
    def _edit_record(self, event):
        """Edit the selected record"""
        # Get the selected item
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get the record ID
        item = self.tree.item(selection[0])
        record_id = item["values"][0]
        tracking_number = item["values"][2]
        sku = item["values"][3]
        status = item["values"][4]
        notes = item["values"][5]
        
        # Create edit dialog
        edit_dialog = tk.Toplevel(self)
        edit_dialog.title("Edit Record")
        edit_dialog.geometry("400x300")
        edit_dialog.configure(bg='white')
        edit_dialog.transient(self)
        edit_dialog.grab_set()
        
        # Create form
        form_frame = tk.Frame(edit_dialog, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Tracking number
        tk.Label(form_frame, text="Tracking Number:", bg='white').grid(row=0, column=0, sticky='w', pady=(0, 5))
        tracking_var = tk.StringVar(value=tracking_number)
        tk.Entry(form_frame, textvariable=tracking_var, width=30).grid(row=0, column=1, sticky='w', pady=(0, 5))
        
        # SKU
        tk.Label(form_frame, text="SKU:", bg='white').grid(row=1, column=0, sticky='w', pady=(0, 5))
        sku_var = tk.StringVar(value=sku)
        tk.Entry(form_frame, textvariable=sku_var, width=30).grid(row=1, column=1, sticky='w', pady=(0, 5))
        
        # Status
        tk.Label(form_frame, text="Status:", bg='white').grid(row=2, column=0, sticky='w', pady=(0, 5))
        status_var = tk.StringVar(value=status)
        status_combo = ttk.Combobox(form_frame, textvariable=status_var, width=27)
        status_combo['values'] = ('Printed', 'Shipped', 'Delivered', 'Returned', 'Cancelled')
        status_combo.grid(row=2, column=1, sticky='w', pady=(0, 5))
        
        # Notes
        tk.Label(form_frame, text="Notes:", bg='white').grid(row=3, column=0, sticky='w', pady=(0, 5))
        notes_var = tk.StringVar(value=notes)
        notes_entry = tk.Text(form_frame, width=30, height=5)
        notes_entry.grid(row=3, column=1, sticky='w', pady=(0, 5))
        notes_entry.insert('1.0', notes)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Save button
        save_button = tk.Button(
            button_frame,
            text="Save",
            command=lambda: self._save_edited_record(
                edit_dialog,
                record_id,
                tracking_var.get(),
                sku_var.get(),
                status_var.get(),
                notes_entry.get('1.0', 'end-1c')
            ),
            bg="#4CAF50",
            fg="white",
            width=10
        )
        save_button.pack(side='left', padx=(0, 10))
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=edit_dialog.destroy,
            width=10
        )
        cancel_button.pack(side='left')
    
    def _save_edited_record(self, dialog, record_id, tracking_number, sku, status, notes):
        """Save the edited record"""
        # Validate inputs
        if not sku:
            messagebox.showerror("Error", "SKU is required")
            return
        
        if not status:
            messagebox.showerror("Error", "Status is required")
            return
        
        # Update the record
        success = update_shipping_record(
            record_id,
            tracking_number=tracking_number,
            sku=sku,
            status=status,
            notes=notes
        )
        
        if success:
            # Close the dialog
            dialog.destroy()
            
            # Reload data
            self._load_data()
        else:
            messagebox.showerror("Error", "Failed to update record")
    
    def _delete_selected(self):
        """Delete the selected record(s)"""
        # Get the selected items
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "No records selected")
            return
        
        # Confirm deletion
        if len(selection) == 1:
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        else:
            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete these {len(selection)} records?")
        
        if not confirm:
            return
        
        # Delete each selected record
        for item in selection:
            record_id = self.tree.item(item)["values"][0]
            delete_shipping_record(record_id)
        
        # Reload data
        self._load_data()
        
        # Show success message
        if len(selection) == 1:
            messagebox.showinfo("Success", "Record deleted successfully")
        else:
            messagebox.showinfo("Success", f"{len(selection)} records deleted successfully")
    
    def _export_to_csv(self):
        """Export current filtered records to CSV"""
        # Get file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export to CSV"
        )
        
        if not file_path:
            return
        
        # Get search parameters
        search_term = self.search_var.get().strip()
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        
        # Export to CSV
        success = export_to_csv(
            file_path,
            search_term=search_term if search_term else None,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None
        )
        
        if success:
            messagebox.showinfo("Success", f"Data exported to {file_path}")
        else:
            messagebox.showerror("Error", "Failed to export data")
    


def create_returns_data_dialog(parent, config_manager):
    """
    Create and return a Returns Data dialog
    
    Args:
        parent: Parent widget
        config_manager: Configuration manager instance
        
    Returns:
        ReturnsDataDialog: The created dialog
    """
    return ReturnsDataDialog(parent, config_manager)

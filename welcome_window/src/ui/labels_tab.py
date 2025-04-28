"""
Labels tab for the Returns Data dialog.
This module provides a tab for viewing and managing label metadata.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import threading

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_colored_button
from src.utils.label_database import (
    initialize_database, 
    search_labels, 
    get_label_count,
    get_unique_values,
    delete_label
)
from src.utils.file_utils import find_files_by_sku
from src.ui.labels_settings_dialog import create_labels_settings_dialog
from src.ui.label_details_dialog import create_label_details_dialog

class LabelsTab(ttk.Frame):
    """Tab for viewing and managing label metadata"""
    
    def __init__(self, parent, config_manager):
        """
        Initialize the Labels tab
        
        Args:
            parent: Parent widget (notebook)
            config_manager: Configuration manager instance
        """
        super().__init__(parent)
        
        # Store references
        self.parent = parent
        self.config_manager = config_manager
        
        # Initialize variables
        self.search_var = tk.StringVar()
        self.field_var = tk.StringVar(value="All Fields")
        
        # Pagination variables
        self.current_page = 1
        self.records_per_page = 20
        self.total_records = 0
        self.total_pages = 1
        
        # Status variable
        self.status_var = tk.StringVar(value="Initializing...")
        
        # Create UI
        self._create_ui()
        
        # Initialize database in a separate thread to avoid blocking the UI
        threading.Thread(target=self._initialize_database).start()
    
    def _initialize_database(self):
        """Initialize the database and load initial data"""
        try:
            # Initialize the database
            success = initialize_database()
            
            if success:
                # Update status
                self.after(0, lambda: self.status_var.set("Loading data..."))
                
                # Load initial data
                self.after(0, self._load_data)
            else:
                # Update status if initialization failed
                self.after(0, lambda: self.status_var.set("Database initialization failed"))
        except Exception as e:
            # Handle any exceptions
            print(f"Error initializing database: {e}")
            self.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Create main container with padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Create top section with settings and search
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Settings button
        settings_button = create_colored_button(
            top_frame,
            text="Settings",
            color="#4CAF50", 
            hover_color="#45a049",
            command=self._open_settings
        )
        settings_button.pack(side='left', padx=(0, 10))
        
        # Search section
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side='right')
        
        # Field selection
        field_label = ttk.Label(search_frame, text="Field:")
        field_label.pack(side='left', padx=(0, 5))
        
        # Get available fields
        fields = ["All Fields", "upc", "item_variant_number", "department", 
                 "category", "color", "website_color", "website_name", 
                 "label_name", "sku"]
        
        field_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.field_var,
            values=fields,
            width=15,
            state="readonly"
        )
        field_combo.pack(side='left', padx=(0, 10))
        
        # Search entry
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=(0, 5))
        search_entry.bind("<Return>", lambda e: self._load_data())
        
        # Search button
        search_button = create_colored_button(
            search_frame,
            text="Search",
            color="#2196F3",
            hover_color="#0b7dda",
            command=self._load_data
        )
        search_button.pack(side='left')
        
        # Create treeview for results with both scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Create vertical scrollbar
        y_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        y_scrollbar.pack(side='right', fill='y')
        
        # Create horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        x_scrollbar.pack(side='bottom', fill='x')
        
        # Define columns - id is included but will be hidden
        columns = ("id", "upc", "website_name", "item_variant_number", "label_name", "color", "category", "website_color", "department")
        
        # Create treeview with both scrollbars
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            selectmode='extended',
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Pack the treeview
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Define column headings
        self.tree.heading("id", text="ID")  # Still define heading even though column is hidden
        self.tree.heading("upc", text="UPC")
        self.tree.heading("website_name", text="Website")
        self.tree.heading("item_variant_number", text="Variant")
        self.tree.heading("label_name", text="Label Name")
        self.tree.heading("color", text="Color")
        self.tree.heading("category", text="Category")
        self.tree.heading("website_color", text="Website Color")
        self.tree.heading("department", text="Department")
        
        # Define column widths - set id column width to 0 to hide it
        self.tree.column("id", width=0, minwidth=0, stretch=False)
        self.tree.column("upc", width=120, minwidth=80)
        self.tree.column("website_name", width=150, minwidth=100)
        self.tree.column("item_variant_number", width=120, minwidth=100)
        self.tree.column("label_name", width=200, minwidth=120)
        self.tree.column("color", width=100, minwidth=80)
        self.tree.column("category", width=100, minwidth=80)
        self.tree.column("website_color", width=120, minwidth=100)
        self.tree.column("department", width=100, minwidth=80)
        
        # Bind double-click to view label
        self.tree.bind("<Double-1>", self._view_label)
        
        # Create right-click menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="View Label Details", command=self._view_selected_from_menu)
        self.context_menu.add_command(label="Delete", command=self._delete_selected)
        
        # Bind right-click to show menu
        self.tree.bind("<Button-3>", self._show_context_menu)
        
        # Create pagination frame
        pagination_frame = ttk.Frame(main_frame)
        pagination_frame.pack(fill='x', pady=(10, 0))
        
        # Previous page button
        prev_button = ttk.Button(pagination_frame, text="< Prev", command=self._prev_page)
        prev_button.pack(side='left', padx=(0, 5))
        
        # Page info
        self.page_info = ttk.Label(pagination_frame, text="Page 1 of 1")
        self.page_info.pack(side='left', padx=5)
        
        # Next page button
        next_button = ttk.Button(pagination_frame, text="Next >", command=self._next_page)
        next_button.pack(side='left', padx=5)
        
        # Records per page
        per_page_label = ttk.Label(pagination_frame, text="Records per page:")
        per_page_label.pack(side='left', padx=(20, 5))
        
        per_page_combo = ttk.Combobox(
            pagination_frame,
            values=[10, 20, 50, 100],
            width=5,
            state="readonly"
        )
        per_page_combo.set(self.records_per_page)
        per_page_combo.pack(side='left')
        per_page_combo.bind("<<ComboboxSelected>>", self._change_records_per_page)
        
        # Record count
        self.record_count_var = tk.StringVar(value="0 records found")
        record_count = ttk.Label(pagination_frame, textvariable=self.record_count_var)
        record_count.pack(side='right')
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', pady=(10, 0))
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side='left')
    
    def _load_data(self):
        """Load data into the treeview based on current filters"""
        # Get search parameters
        search_term = self.search_var.get().strip()
        field = None if self.field_var.get() == "All Fields" else self.field_var.get().lower()
        
        # Calculate offset
        offset = (self.current_page - 1) * self.records_per_page
        
        # Update status
        self.status_var.set("Loading data...")
        self.update_idletasks()
        
        try:
            # Get total count for pagination
            self.total_records = get_label_count(search_term, field)
            self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)
            
            # Adjust current page if needed
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
                offset = (self.current_page - 1) * self.records_per_page
            
            # Update pagination controls
            self._update_pagination()
            
            # Update record count
            self.record_count_var.set(f"{self.total_records} records found")
            
            try:
                # Get records for current page
                records = search_labels(
                    search_term, 
                    field, 
                    limit=self.records_per_page, 
                    offset=offset
                )
                
                # Clear existing items
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Insert new records
                for record in records:
                    values = (
                        record["id"],
                        record["upc"],
                        record["website_name"],
                        record["item_variant_number"],
                        record["label_name"],
                        record["color"],
                        record["category"],
                        record["website_color"],
                        record["department"]
                    )
                    self.tree.insert("", "end", values=values)
                
            except Exception as e:
                print(f"Error loading records: {e}")
                self.status_var.set(f"Error: {str(e)}")
                self.record_count_var.set("0 records found")
                self.page_info.config(text="Page 1 of 1")
            
            # Update status
            if self.status_var.get().startswith("Loading"):
                self.status_var.set("Ready")
        except Exception as e:
            print(f"Critical error in _load_data: {e}")
            self.status_var.set("Error loading data")
    
    def _update_pagination(self):
        """Update pagination controls based on current state"""
        self.page_info.config(text=f"Page {self.current_page} of {self.total_pages}")
    
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
    
    def _open_settings(self):
        """Open the labels settings dialog"""
        # Create the settings dialog
        create_labels_settings_dialog(
            self.winfo_toplevel(),  # Use the top-level window as parent
            self.config_manager,
            callback=self._load_data  # Reload data after successful import/export
        )
    
    def _view_label(self, event):
        """View the label details for the selected record"""
        # Get selected item
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        # Get values from the selected item
        values = self.tree.item(selected_item[0], 'values')
        
        # Create a record dictionary with all fields
        record = {
            'id': values[0],
            'upc': values[1],
            'website_name': values[2],
            'item_variant_number': values[3],
            'label_name': values[4],
            'color': values[5],
            'category': values[6],
            'website_color': values[7],
            'department': values[8],
            'sku': values[3]  # Set sku to be the same as item_variant_number for compatibility
        }
        
        # Update status
        self.status_var.set(f"Opening details for: {record['label_name']}")
        
        # Open the label details dialog
        create_label_details_dialog(
            self.winfo_toplevel(),
            record,
            self.config_manager
        )
        
        # Reset status
        self.status_var.set("Ready")
    
    def _view_selected_from_menu(self):
        """View the label details for the selected record from context menu"""
        # Get selected item
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("No Selection", "Please select a label record first")
            return
        
        # Get values from the selected item
        values = self.tree.item(selected_item[0], 'values')
        
        # Create a record dictionary with all fields
        record = {
            'id': values[0],
            'upc': values[1],
            'website_name': values[2],
            'item_variant_number': values[3],
            'label_name': values[4],
            'color': values[5],
            'category': values[6],
            'website_color': values[7],
            'department': values[8],
            'sku': values[3]  # Set sku to be the same as item_variant_number for compatibility
        }
        
        # Update status
        self.status_var.set(f"Opening details for: {record['label_name']}")
        
        # Open the label details dialog
        create_label_details_dialog(
            self.winfo_toplevel(),
            record,
            self.config_manager
        )
        
        # Reset status
        self.status_var.set("Ready")
    
    def _show_context_menu(self, event):
        """Show the context menu on right-click"""
        # Select the item under the cursor
        item = self.tree.identify_row(event.y)
        if item:
            # Select the item
            self.tree.selection_set(item)
            # Show the context menu
            self.context_menu.post(event.x_root, event.y_root)
    
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
        
        # Update status
        self.status_var.set("Deleting records...")
        self.update_idletasks()
        
        # Delete each selected record
        success_count = 0
        for item in selection:
            record_id = self.tree.item(item)["values"][0]
            if delete_label(record_id):
                success_count += 1
        
        # Reload data
        self._load_data()
        
        # Show success message
        if success_count == 1:
            messagebox.showinfo("Success", "Record deleted successfully")
        else:
            messagebox.showinfo("Success", f"{success_count} records deleted successfully")
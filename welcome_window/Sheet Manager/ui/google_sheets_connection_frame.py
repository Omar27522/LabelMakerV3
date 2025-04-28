import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import webbrowser
import threading
from utils.sheets_utils import validate_sheet_url, test_sheet_connection, get_sheet_names
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import from config
from config.settings_manager import settings_manager

class GoogleSheetsConnectionFrame(tk.Frame):
    """
    Frame for entering and verifying Google Sheets settings.
    Allows the user to input a Sheet URL and Sheet Name,
    test the connection, and view status before proceeding.
    """
    def __init__(self, parent, on_verified=None):
        super().__init__(parent, bg="white")
        self.parent = parent
        self.on_verified = on_verified
        self.sheet_id = None
        self.sheet_names = []
        self._create_widgets()
        self._load_settings()
        
        # Config directory is now handled by settings_manager

    def _create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#1976d2", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="Google Sheets Connection", font=("Roboto", 16, "bold"), 
                        fg="white", bg="#1976d2")
        title.pack(side=tk.LEFT, padx=20)
        
        # Main content area
        content = tk.Frame(self, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # URL section
        url_frame = tk.LabelFrame(content, text="Google Sheet URL", bg="white", font=("Roboto", 10, "bold"))
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.url_entry = tk.Entry(url_frame, width=60, font=("Roboto", 10))
        self.url_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        url_help_btn = tk.Button(url_frame, text="?", width=2, command=self._show_url_help)
        url_help_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Sheet selection section
        sheet_frame = tk.LabelFrame(content, text="Sheet Selection", bg="white", font=("Roboto", 10, "bold"))
        sheet_frame.pack(fill=tk.X, pady=(0, 15))
        
        sheet_inner = tk.Frame(sheet_frame, bg="white")
        sheet_inner.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(sheet_inner, text="Sheet Name:", bg="white").grid(row=0, column=0, sticky="w")
        
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(sheet_inner, textvariable=self.sheet_var, width=30, state="readonly")
        self.sheet_combo.grid(row=0, column=1, padx=5)
        
        self.refresh_sheets_btn = tk.Button(sheet_inner, text="Get Sheets", command=self._get_sheets)
        self.refresh_sheets_btn.grid(row=0, column=2, padx=5)
        
        # Manual entry option
        tk.Label(sheet_inner, text="Or enter manually:", bg="white").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.name_entry = tk.Entry(sheet_inner, width=30)
        self.name_entry.grid(row=1, column=1, padx=5, pady=(10, 0))
        
        # Status section
        status_frame = tk.LabelFrame(content, text="Connection Status", bg="white", font=("Roboto", 10, "bold"))
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = tk.Label(status_frame, text="Not Connected", fg="gray", bg="white", 
                                   font=("Roboto", 10), anchor="w")
        self.status_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Progress indicator
        self.progress = ttk.Progressbar(content, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 15))
        self.progress.pack_forget()  # Hidden initially
        
        # Credentials section
        creds_frame = tk.LabelFrame(content, text="Credentials", bg="white", font=("Roboto", 10, "bold"))
        creds_frame.pack(fill=tk.X, pady=(0, 15))
        
        creds_inner = tk.Frame(creds_frame, bg="white")
        creds_inner.pack(fill=tk.X, padx=10, pady=10)
        
        self.creds_label = tk.Label(creds_inner, text="No credentials file selected", 
                                  fg="gray", bg="white", anchor="w")
        self.creds_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_btn = tk.Button(creds_inner, text="Browse", command=self._browse_credentials)
        self.browse_btn.pack(side=tk.RIGHT)
        
        # Action buttons
        button_frame = tk.Frame(content, bg="white")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.test_btn = tk.Button(button_frame, text="Test Connection", command=self._on_test,
                                bg="#1976d2", fg="white", font=("Roboto", 10, "bold"),
                                relief=tk.FLAT, padx=15, pady=5)
        self.test_btn.pack(side=tk.LEFT)
        
        self.save_btn = tk.Button(button_frame, text="Save & Continue", command=self._on_save,
                                bg="#388e3c", fg="white", font=("Roboto", 10, "bold"),
                                relief=tk.FLAT, padx=15, pady=5, state=tk.DISABLED)
        self.save_btn.pack(side=tk.RIGHT)
        
        # Check for credentials file
        self._check_credentials()

    def _load_settings(self):
        try:
            # Get settings from settings manager
            url = settings_manager.get('google_sheets', 'google_sheet_url')
            if url:
                self.url_entry.insert(0, url)
                # Extract sheet ID for later use
                is_valid, sheet_id = validate_sheet_url(url)
                if is_valid:
                    self.sheet_id = sheet_id
            
            sheet_name = settings_manager.get('google_sheets', 'google_sheet_name')
            if sheet_name:
                self.name_entry.insert(0, sheet_name)
            
            # Update status if previously connected
            if settings_manager.get('google_sheets', 'google_sheets_connection_status') == "Connected":
                self.status_label.config(text="Previously Connected - Please Test Again", fg="orange")
        except Exception as e:
            self.status_label.config(text=f"Error loading settings: {str(e)}", fg="red")

    def _check_credentials(self):
        """Check if credentials file exists and update UI accordingly"""
        from utils.sheets_utils import get_credentials_file_path, file_exists
        
        creds_path = get_credentials_file_path()
        if file_exists(creds_path):
            self.creds_label.config(text=f"Using: {os.path.basename(creds_path)}", fg="green")
        else:
            self.creds_label.config(text="No credentials file found", fg="red")

    def _browse_credentials(self):
        """Allow user to select a credentials file"""
        filename = filedialog.askopenfilename(
            title="Select Google Service Account Credentials",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            # Copy to expected location
            import shutil
            dest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credentials.json')
            try:
                shutil.copy(filename, dest_path)
                self.creds_label.config(text=f"Using: {os.path.basename(filename)}", fg="green")
                messagebox.showinfo("Success", "Credentials file imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy credentials file: {str(e)}")

    def _show_url_help(self):
        """Show help about Google Sheet URL format"""
        help_text = (
            "The Google Sheet URL should be in the format:\n\n"
            "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID\n\n"
            "You can find this URL by opening your Google Sheet in a browser "
            "and copying the URL from the address bar.\n\n"
            "Note: Make sure your Google Service Account has access to this sheet."
        )
        messagebox.showinfo("Google Sheet URL Help", help_text)
        
        # Ask if user wants to open Google Sheets
        if messagebox.askyesno("Open Google Sheets", "Would you like to open Google Sheets in your browser?"):
            webbrowser.open("https://docs.google.com/spreadsheets")

    def _get_sheets(self):
        """Get available sheets from the Google Sheet"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a Google Sheet URL first")
            return
            
        is_valid, sheet_id = validate_sheet_url(url)
        if not is_valid:
            messagebox.showerror("Invalid URL", sheet_id)
            return
            
        self.sheet_id = sheet_id
        
        # Show progress indicator
        self.progress.pack(fill=tk.X, pady=(0, 15))
        self.progress.start()
        self.refresh_sheets_btn.config(state=tk.DISABLED)
        
        # Run in a separate thread to keep UI responsive
        threading.Thread(target=self._fetch_sheets_thread, daemon=True).start()

    def _fetch_sheets_thread(self):
        """Fetch sheets in a background thread"""
        success, result = get_sheet_names(self.sheet_id)
        
        # Update UI in the main thread
        self.after(0, lambda: self._update_sheet_list(success, result))

    def _update_sheet_list(self, success, result):
        """Update the sheet dropdown with fetched sheet names"""
        # Hide progress indicator
        self.progress.stop()
        self.progress.pack_forget()
        self.refresh_sheets_btn.config(state=tk.NORMAL)
        
        if success:
            self.sheet_names = result
            self.sheet_combo['values'] = self.sheet_names
            if self.sheet_names:
                self.sheet_combo.current(0)
                self.status_label.config(text=f"Found {len(self.sheet_names)} sheets", fg="blue")
            else:
                self.status_label.config(text="No sheets found in this document", fg="orange")
        else:
            self.status_label.config(text=f"Error: {result}", fg="red")
            messagebox.showerror("Error", result)

    def _on_test(self):
        """Test the connection to the Google Sheet"""
        url = self.url_entry.get().strip()
        
        # Get sheet name from combo if selected, otherwise from entry
        sheet_name = self.sheet_var.get()
        if not sheet_name:
            sheet_name = self.name_entry.get().strip()
            
        if not url or not sheet_name:
            messagebox.showerror("Error", "Please enter both a Google Sheet URL and Sheet Name")
            return
            
        is_valid, sheet_id_or_msg = validate_sheet_url(url)
        if not is_valid:
            self.status_label.config(text=f"Error: {sheet_id_or_msg}", fg="red")
            messagebox.showerror("Invalid URL", sheet_id_or_msg)
            self.save_btn.config(state=tk.DISABLED)
            return
            
        self.sheet_id = sheet_id_or_msg
        
        # Show progress indicator
        self.progress.pack(fill=tk.X, pady=(0, 15))
        self.progress.start()
        self.test_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Testing connection...", fg="blue")
        
        # Run in a separate thread to keep UI responsive
        threading.Thread(
            target=self._test_connection_thread, 
            args=(sheet_id_or_msg, sheet_name),
            daemon=True
        ).start()

    def _test_connection_thread(self, sheet_id, sheet_name):
        """Test connection in a background thread"""
        success, msg = test_sheet_connection(sheet_id, sheet_name)
        
        # Update UI in the main thread
        self.after(0, lambda: self._update_connection_status(success, msg, sheet_name))

    def _update_connection_status(self, success, msg, sheet_name):
        """Update UI after connection test"""
        # Hide progress indicator
        self.progress.stop()
        self.progress.pack_forget()
        self.test_btn.config(state=tk.NORMAL)
        
        if success:
            self.status_label.config(text="Connected! ✓", fg="green")
            messagebox.showinfo("Success", f"Successfully connected to sheet '{sheet_name}'!")
            self.save_btn.config(state=tk.NORMAL)
            
            # Update name entry with the verified sheet name
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, sheet_name)
        else:
            self.status_label.config(text=f"Error: {msg}", fg="red")
            messagebox.showerror("Connection Failed", msg)
            self.save_btn.config(state=tk.DISABLED)

    def _on_save(self):
        """Save settings and continue"""
        url = self.url_entry.get().strip()
        
        # Get sheet name from entry (which should have the verified name)
        sheet_name = self.name_entry.get().strip()
        
        # Prepare settings
        try:
            # Update Google Sheets settings using the settings manager
            settings_manager.update('google_sheets', {
                'google_sheet_url': url,
                'google_sheet_name': sheet_name,
                'google_sheet_id': self.sheet_id,
                'google_sheets_connection_status': "Connected"
            })
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
            # Call the verification callback
            if self.on_verified:
                self.on_verified()
                
        except Exception as e:
            error_msg = f"Failed to save settings: {str(e)}"
            self.status_label.config(text=f"Error: {error_msg}", fg="red")
            messagebox.showerror("Error", error_msg)

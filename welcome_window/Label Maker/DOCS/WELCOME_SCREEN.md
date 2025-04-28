# Welcome Screen Redesign

## Overview

The Welcome Screen serves as the entry point to the Label Maker V3 application, providing access to different functional modules based on user role and task requirements. This document outlines the design, functionality, and implementation details for the new Welcome Screen interface.

## Design Specifications

![Welcome Screen Layout](../assets/welcome_screen.png)

### Layout Components

- **Header**: Application title "Label Maker V3" with version number
- **Main Navigation Area**: Four distinct buttons arranged in a grid layout
  - **User**: Large green button (left panel)
  - **Management**: Blue button (top right)
  - **Labels**: Orange button (middle right)
  - **Settings**: Gray button (bottom, full width)
- **Footer**: Version information

### Color Scheme

- **User Button**: #4CAF50 (Green)
- **Management Button**: #2196F3 (Blue)
- **Labels Button**: #FF9800 (Orange)
- **Settings Button**: #9E9E9E (Gray)
- **Background**: #F5F5F5 (Light Gray)
- **Text**: #212121 (Dark Gray)

### Dimensions

- **Window Size**: 500px × 400px
- **User Button**: 300px × 200px
- **Management/Labels Buttons**: 180px × 100px each
- **Settings Button**: 480px × 50px

## Functional Specifications

### User Button

- **Purpose**: Provides a simplified interface for tracking number processing
- **Target Users**: Warehouse staff handling returns
- **Functionality**:
  - Opens a streamlined interface with a single text input field for tracking numbers
  - After valid tracking number entry, reveals a second field for SKU input
  - Automatically validates inputs against Google Sheets database
  - Automatically prints label upon successful validation
  - No manual print button required

### Management Button

- **Purpose**: Access to the full Label Maker application
- **Target Users**: Supervisors and administrators
- **Functionality**:
  - Opens the existing Label Maker interface with all features
  - Provides access to label creation, editing, and batch processing
  - Includes reporting and advanced configuration options

### Labels Button

- **Purpose**: Quick access to view and manage existing labels
- **Target Users**: Quality control and inventory staff
- **Functionality**:
  - Opens the View Labels interface
  - Allows searching, filtering, and viewing of previously created labels
  - Provides reprinting capabilities for existing labels
  - Includes basic reporting features

### Settings Button

- **Purpose**: Configuration of application settings
- **Target Users**: All users with appropriate permissions
- **Functionality**:
  - Printer configuration
  - User preferences
  - System integration settings (Google Sheets, web APIs)
  - Role-based access control

## Implementation Details

### Technical Requirements

- **Framework**: Tkinter (consistent with existing application)
- **New Dependencies**:
  - `gspread` or equivalent for Google Sheets API integration
  - `requests` or equivalent for web API integration
  - `oauth2client` for secure authentication

### Code Structure

```python
class WelcomeScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Welcome")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Configure window
        self.iconbitmap("assets/icons/app_icon.ico")
        
        # Create header
        self.header_frame = tk.Frame(self)
        self.header_frame.pack(fill="x", pady=10)
        
        tk.Label(self.header_frame, text="Welcome", font=("Arial", 18, "bold")).pack()
        tk.Label(self.header_frame, text="Label Maker V3", font=("Arial", 14)).pack()
        
        # Create button frame
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid layout
        self.button_frame.columnconfigure(0, weight=3)
        self.button_frame.columnconfigure(1, weight=2)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        
        # Create buttons
        self.user_button = tk.Button(self.button_frame, text="User", 
                                    bg="#4CAF50", fg="white", font=("Arial", 18, "bold"),
                                    command=self.open_user_interface)
        self.user_button.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5), pady=5)
        
        self.management_button = tk.Button(self.button_frame, text="Management", 
                                         bg="#2196F3", fg="white", font=("Arial", 14),
                                         command=self.open_management)
        self.management_button.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0, 5))
        
        self.labels_button = tk.Button(self.button_frame, text="Labels", 
                                     bg="#FF9800", fg="white", font=("Arial", 14),
                                     command=self.open_view_labels)
        self.labels_button.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Settings button (spans full width)
        self.settings_frame = tk.Frame(self)
        self.settings_frame.pack(fill="x", padx=10, pady=5)
        
        self.settings_button = tk.Button(self.settings_frame, text="Settings", 
                                       bg="#9E9E9E", fg="white", font=("Arial", 12),
                                       command=self.open_settings)
        self.settings_button.pack(fill="x")
        
        # Version info
        tk.Label(self, text=f"Ver. {VERSION}", font=("Arial", 8), 
                fg="gray").pack(side="right", padx=5, pady=5)
    
    def open_user_interface(self):
        # Open the simplified user interface
        self.withdraw()  # Hide welcome screen
        user_window = UserInterface(self)
        user_window.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(user_window))
    
    def open_management(self):
        # Open the full Label Maker interface
        self.withdraw()
        # Launch existing main application window
        
    def open_view_labels(self):
        # Open the View Labels interface
        self.withdraw()
        # Launch existing view labels window
        
    def open_settings(self):
        # Open the Settings interface
        settings_window = SettingsWindow(self)
        
    def on_child_close(self, child_window):
        # When a child window is closed, show the welcome screen again
        child_window.destroy()
        self.deiconify()
```

### User Interface Implementation

```python
class UserInterface(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Returns Processing")
        self.geometry("400x300")
        
        # Main frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tracking number input
        tk.Label(self.main_frame, text="Enter Tracking Number:", 
                font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.tracking_entry = tk.Entry(self.main_frame, font=("Arial", 14))
        self.tracking_entry.pack(fill="x", pady=(0, 15))
        self.tracking_entry.bind("<Return>", self.validate_tracking)
        self.tracking_entry.focus_set()
        
        # SKU input (initially hidden)
        self.sku_frame = tk.Frame(self.main_frame)
        self.sku_frame.pack(fill="x", pady=5)
        self.sku_frame.pack_forget()  # Hidden initially
        
        tk.Label(self.sku_frame, text="Enter SKU:", 
                font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.sku_entry = tk.Entry(self.sku_frame, font=("Arial", 14), state="disabled")
        self.sku_entry.pack(fill="x")
        self.sku_entry.bind("<Return>", self.validate_sku)
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.main_frame, textvariable=self.status_var,
                                   font=("Arial", 10), fg="blue")
        self.status_label.pack(fill="x", pady=15)
        
        # Google Sheets API client
        self.gs_client = None
        self.initialize_google_sheets()
    
    def initialize_google_sheets(self):
        # Initialize Google Sheets connection
        try:
            # Code to initialize Google Sheets API
            self.status_var.set("Connected to database")
        except Exception as e:
            self.status_var.set(f"Error connecting to database: {str(e)}")
    
    def validate_tracking(self, event=None):
        tracking = self.tracking_entry.get().strip()
        if not tracking:
            self.status_var.set("Please enter a tracking number")
            return
        
        self.status_var.set("Validating tracking number...")
        # Call Google Sheets API to validate tracking number
        
        # If valid, show SKU input
        self.sku_frame.pack(fill="x", pady=5)
        self.sku_entry.config(state="normal")
        self.sku_entry.focus_set()
        self.status_var.set("Tracking number validated. Please enter SKU.")
    
    def validate_sku(self, event=None):
        sku = self.sku_entry.get().strip()
        if not sku:
            self.status_var.set("Please enter an SKU")
            return
        
        self.status_var.set("Validating SKU...")
        # Call Google Sheets API to validate SKU
        
        # If valid, print label automatically
        self.print_label()
    
    def print_label(self):
        tracking = self.tracking_entry.get().strip()
        sku = self.sku_entry.get().strip()
        
        self.status_var.set("Printing label...")
        # Code to generate and print label
        
        # Reset form for next entry
        self.tracking_entry.delete(0, tk.END)
        self.sku_entry.delete(0, tk.END)
        self.sku_frame.pack_forget()
        self.sku_entry.config(state="disabled")
        self.tracking_entry.focus_set()
        
        self.status_var.set("Label printed successfully. Ready for next item.")
```

## Integration Points

### Google Sheets Integration

The application will connect to Google Sheets for data validation and tracking:

1. **Authentication**:
   - Use service account or OAuth 2.0 for secure access
   - Store credentials securely in encrypted configuration

2. **Data Structure**:
   - Tracking numbers and associated SKUs stored in designated spreadsheet
   - Status tracking for processed returns
   - Timestamp and user information for audit purposes

3. **Operations**:
   - Read operations for validation
   - Write operations for updating processing status
   - Real-time synchronization with multiple users

### Web System Integration

For integration with web-based warehouse systems:

1. **API Endpoints**:
   - RESTful API calls to validate and update information
   - Webhook support for real-time notifications

2. **Data Exchange**:
   - JSON formatted data exchange
   - Secure HTTPS communication
   - Error handling and retry logic

## Security Considerations

1. **Authentication**:
   - Secure storage of API credentials
   - Role-based access to different functions
   - Session management for user authentication

2. **Data Protection**:
   - Encryption of sensitive data
   - Secure communication channels
   - Audit logging of all operations

3. **Error Handling**:
   - Graceful degradation when services are unavailable
   - Clear error messages without exposing system details
   - Automatic retry with exponential backoff

## Implementation Timeline

1. **Phase 1: Welcome Screen and Navigation**
   - Implement the new welcome screen interface
   - Create navigation flow between different modules
   - Establish basic application structure

2. **Phase 2: Simplified User Interface**
   - Develop the streamlined tracking number interface
   - Implement dynamic form behavior
   - Create label generation and printing functionality

3. **Phase 3: External Integration**
   - Implement Google Sheets API integration
   - Add web system API connectivity
   - Develop data validation and synchronization

4. **Phase 4: Testing and Deployment**
   - User acceptance testing
   - Performance optimization
   - Documentation and training materials

## Conclusion

The Welcome Screen redesign provides a more intuitive entry point to the Label Maker application, with clear pathways for different user roles and tasks. The simplified user interface for tracking number processing will significantly streamline the returns workflow, reducing processing time and minimizing errors.

---

*Last updated: February 26, 2025*

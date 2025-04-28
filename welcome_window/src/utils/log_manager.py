"""
Centralized logging system for the application.
This module provides a dedicated database for logs and eliminates redundancy.
"""
import os
import sqlite3
import datetime
import threading
from typing import Optional, Dict, List, Tuple, Any

# Import the application logger
from src.utils.app_logger import get_app_logger

# Get the application logger
logger = get_app_logger()

# Thread-local storage for database connections
_local = threading.local()

def get_logs_db_path() -> Tuple[str, str]:
    """
    Get the path to the logs database.
    
    Returns:
        tuple: (logs_dir, db_path)
    """
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Define the logs directory
    logs_dir = os.path.join(project_root, 'logs')
    
    # Define a specific directory for shipping logs
    shipping_logs_dir = os.path.join(logs_dir, 'shipping_logs')
    
    # Create the shipping logs directory if it doesn't exist
    os.makedirs(shipping_logs_dir, exist_ok=True)
    
    # Define the database path
    db_path = os.path.join(shipping_logs_dir, 'shipping_logs.db')
    
    return shipping_logs_dir, db_path

def get_db_connection() -> sqlite3.Connection:
    """
    Get a thread-local database connection.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    if not hasattr(_local, 'conn'):
        # Initialize the database if needed
        initialize_logs_db()
        
        # Get the database path
        _, db_path = get_logs_db_path()
        
        # Create a new connection for this thread
        _local.conn = sqlite3.connect(db_path)
        
        # Enable foreign keys
        _local.conn.execute('PRAGMA foreign_keys = ON')
        
        # Configure connection to return rows as dictionaries
        _local.conn.row_factory = sqlite3.Row
    
    return _local.conn

def close_db_connection():
    """
    Close the thread-local database connection if it exists.
    """
    if hasattr(_local, 'conn'):
        _local.conn.close()
        del _local.conn

def initialize_logs_db() -> bool:
    """
    Initialize the logs database with necessary tables.
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        # Get the database path
        _, db_path = get_logs_db_path()
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create the shipping_logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS shipping_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tracking_number TEXT,
            sku TEXT,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Create indices for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_shipping_logs_timestamp ON shipping_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_shipping_logs_tracking ON shipping_logs(tracking_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_shipping_logs_sku ON shipping_logs(sku)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_shipping_logs_status ON shipping_logs(status)')
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error initializing logs database: {str(e)}")
        return False

def log_shipping_event(
    tracking_number: str,
    sku: str,
    action: str,
    status: str,
    details: Optional[str] = None
) -> bool:
    """
    Log a shipping-related event to the database.
    
    Args:
        tracking_number: The tracking number (can be empty)
        sku: The SKU (can be empty)
        action: The action (e.g., 'print', 'create', 'log_only')
        status: The status (e.g., 'success', 'error', 'pending')
        details: Additional details about the event
        
    Returns:
        bool: True if logging was successful, False otherwise
    """
    try:
        # Get the database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        created_at = timestamp  # For audit purposes
        
        # Insert the log entry
        cursor.execute(
            """
            INSERT INTO shipping_logs 
            (timestamp, tracking_number, sku, action, status, details, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (timestamp, tracking_number, sku, action, status, details, created_at)
        )
        
        # Commit the changes
        conn.commit()
        
        return True
    
    except Exception as e:
        logger.error(f"Error logging shipping event: {str(e)}")
        return False

def get_shipping_logs(
    limit: int = 100,
    offset: int = 0,
    tracking_number: Optional[str] = None,
    sku: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get shipping logs with optional filtering.
    
    Args:
        limit: Maximum number of logs to return
        offset: Number of logs to skip
        tracking_number: Filter by tracking number
        sku: Filter by SKU
        start_date: Filter by start date (YYYY-MM-DD)
        end_date: Filter by end date (YYYY-MM-DD)
        status: Filter by status
        
    Returns:
        list: List of log entries as dictionaries
    """
    try:
        # Get the database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build the query
        query = "SELECT * FROM shipping_logs WHERE 1=1"
        params = []
        
        # Add filters
        if tracking_number:
            query += " AND tracking_number LIKE ?"
            params.append(f"%{tracking_number}%")
        
        if sku:
            query += " AND sku LIKE ?"
            params.append(f"%{sku}%")
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(f"{start_date} 00:00:00")
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(f"{end_date} 23:59:59")
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        # Add ordering and limits
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute the query
        cursor.execute(query, params)
        
        # Convert rows to dictionaries
        logs = []
        for row in cursor.fetchall():
            logs.append(dict(row))
        
        return logs
    
    except Exception as e:
        logger.error(f"Error getting shipping logs: {str(e)}")
        return []

def export_logs_to_csv(
    file_path: str,
    tracking_number: Optional[str] = None,
    sku: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
) -> bool:
    """
    Export shipping logs to a CSV file with optional filtering.
    
    Args:
        file_path: Path to save the CSV file
        tracking_number: Filter by tracking number
        sku: Filter by SKU
        start_date: Filter by start date (YYYY-MM-DD)
        end_date: Filter by end date (YYYY-MM-DD)
        status: Filter by status
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        import csv
        
        # Get the logs
        logs = get_shipping_logs(
            limit=10000,  # High limit for export
            tracking_number=tracking_number,
            sku=sku,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        
        # Check if there are logs to export
        if not logs:
            return False
        
        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            # Define the fieldnames
            fieldnames = ['timestamp', 'tracking_number', 'sku', 'action', 'status', 'details']
            
            # Create the CSV writer
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write the header
            writer.writeheader()
            
            # Write the rows
            for log in logs:
                # Only include the fields we want
                row = {field: log.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        return True
    
    except Exception as e:
        logger.error(f"Error exporting logs to CSV: {str(e)}")
        return False

def migrate_from_text_log(archive_after_import: bool = True) -> Tuple[bool, int, int]:
    """
    Migrate shipping records from the text log file to the database.
    
    Args:
        archive_after_import: Whether to archive the text log file after import
        
    Returns:
        tuple: (success, count, skipped) - Import status, records imported, and records skipped
    """
    try:
        # Ensure database is initialized
        initialize_logs_db()
        
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Define the log file path
        log_file_path = os.path.join(project_root, 'logs', 'shipping_records.txt')
        
        # Check if the log file exists
        if not os.path.exists(log_file_path):
            return True, 0, 0  # No file to import, consider it successful with 0 records
        
        # Get the database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Read the log file
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Process each line
        count = 0
        skipped = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse the line - Format: "YYYY-MM-DD HH:MM:SS | Tracking: XXX | SKU: YYY | Label: ZZZ"
                parts = line.split(' | ')
                if len(parts) < 3:
                    skipped += 1
                    continue
                
                timestamp = parts[0]
                
                # Extract tracking number, SKU, and label info
                tracking_number = ""
                sku = ""
                label_info = ""
                
                for part in parts[1:]:
                    if part.startswith("Tracking: "):
                        tracking_number = part[len("Tracking: "):]
                    elif part.startswith("SKU: "):
                        sku = part[len("SKU: "):]
                    elif part.startswith("Label: "):
                        label_info = part[len("Label: "):]
                
                # Determine action and status based on label_info
                action = "unknown"
                status = "unknown"
                
                if "No print - logging only" in label_info:
                    action = "log_only"
                    status = "success"
                elif "Label printed successfully" in label_info:
                    action = "print"
                    status = "success"
                elif ".png" in label_info or ".jpg" in label_info:
                    action = "print"
                    status = "success"
                
                # Insert the record
                cursor.execute(
                    """
                    INSERT INTO shipping_logs 
                    (timestamp, tracking_number, sku, action, status, details, created_at) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (timestamp, tracking_number, sku, action, status, label_info, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
                
                count += 1
            
            except Exception as e:
                logger.warning(f"Error parsing log line: {line}, Error: {str(e)}")
                skipped += 1
                continue
        
        # Commit changes
        conn.commit()
        
        # Archive the text log file if requested
        if archive_after_import and count > 0:
            try:
                # Create archive directory if it doesn't exist
                archive_dir = os.path.join(project_root, 'logs', 'archive')
                os.makedirs(archive_dir, exist_ok=True)
                
                # Create a timestamped archive filename
                import time
                archive_filename = f"shipping_records_{int(time.time())}.txt.bak"
                archive_path = os.path.join(archive_dir, archive_filename)
                
                # Move the file to archive
                import shutil
                shutil.copy2(log_file_path, archive_path)
                
                # Clear the original file but keep it (create empty file)
                with open(log_file_path, 'w') as f:
                    f.write(f"# Archived on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# {count} records imported to database, {skipped} records skipped\n")
                    f.write(f"# Archive file: {archive_filename}\n\n")
                    f.write("# This file is no longer used. All logs are now stored in the database.\n")
            except Exception as e:
                logger.error(f"Error archiving text log: {str(e)}")
        
        return True, count, skipped
    
    except Exception as e:
        logger.error(f"Error migrating from text log: {e}")
        return False, 0, 0

def migrate_from_shipping_records_db() -> Tuple[bool, int, int]:
    """
    Migrate shipping records from the old database to the new logs database.
    
    Returns:
        tuple: (success, count, skipped) - Import status, records imported, and records skipped
    """
    try:
        # Ensure logs database is initialized
        initialize_logs_db()
        
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Define the old database path
        old_db_path = os.path.join(project_root, 'data', 'shipping_records.db')
        
        # Check if the old database exists
        if not os.path.exists(old_db_path):
            return True, 0, 0  # No database to import, consider it successful with 0 records
        
        # Connect to the old database
        old_conn = sqlite3.connect(old_db_path)
        old_conn.row_factory = sqlite3.Row
        old_cursor = old_conn.cursor()
        
        # Get the new database connection
        new_conn = get_db_connection()
        new_cursor = new_conn.cursor()
        
        # Get all records from the old database
        old_cursor.execute("SELECT * FROM shipping_records ORDER BY timestamp")
        
        # Process each record
        count = 0
        skipped = 0
        
        for row in old_cursor.fetchall():
            try:
                # Extract data
                timestamp = row['timestamp']
                tracking_number = row['tracking_number']
                sku = row['sku']
                status = row['status']
                notes = row['notes'] or ""
                
                # Determine action based on status
                action = "unknown"
                if "printed" in status.lower():
                    action = "print"
                elif "logged" in status.lower():
                    action = "log_only"
                
                # Insert the record
                new_cursor.execute(
                    """
                    INSERT INTO shipping_logs 
                    (timestamp, tracking_number, sku, action, status, details, created_at) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (timestamp, tracking_number, sku, action, status, notes, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
                
                count += 1
            
            except Exception as e:
                logging.warning(f"Error migrating record: {dict(row)}, Error: {str(e)}")
                skipped += 1
                continue
        
        # Commit changes
        new_conn.commit()
        
        # Close old connection
        old_conn.close()
        
        return True, count, skipped
    
    except Exception as e:
        logging.error(f"Error migrating from shipping records database: {str(e)}")
        return False, 0, 0

def run_migration_wizard(parent_window=None) -> bool:
    """
    Run a migration wizard to migrate logs from old sources.
    
    Args:
        parent_window: Optional parent window for message dialogs
        
    Returns:
        bool: True if migration was successful, False otherwise
    """
    from tkinter import messagebox
    import threading
    
    # Check if the logs database exists
    _, db_path = get_logs_db_path()
    if os.path.exists(db_path):
        # Database already exists, ask if user wants to reimport
        if parent_window and not messagebox.askyesno(
            "Migration",
            "Logs database already exists. Do you want to reimport logs from old sources?"
        ):
            return True
    
    # Run the migration in a separate thread to avoid blocking the UI
    def migration_task():
        try:
            results = []
            
            # Migrate from text log
            text_success, text_count, text_skipped = migrate_from_text_log(archive_after_import=True)
            results.append(("Text Log", text_success, text_count, text_skipped))
            
            # Migrate from old database
            db_success, db_count, db_skipped = migrate_from_shipping_records_db()
            results.append(("Database", db_success, db_count, db_skipped))
            
            # Show results
            if parent_window:
                message = "Migration results:\n\n"
                
                for source, success, count, skipped in results:
                    status = "Success" if success else "Failed"
                    message += f"{source}: {status}\n"
                    if success:
                        message += f"  - {count} records imported\n"
                        if skipped > 0:
                            message += f"  - {skipped} records skipped\n"
                
                # Use after to ensure this runs in the main thread
                parent_window.after(0, lambda: messagebox.showinfo("Migration Complete", message))
            
            return all(success for _, success, _, _ in results)
                
        except Exception as e:
            logging.error(f"Error during migration: {str(e)}")
            if parent_window:
                parent_window.after(0, lambda: messagebox.showerror(
                    "Migration Error", 
                    f"An error occurred during migration: {str(e)}"
                ))
            return False
    
    # Start the migration thread
    if parent_window:
        # Show a progress message
        messagebox.showinfo(
            "Migration Started", 
            "Migration of shipping records has started.\nThis may take a moment..."
        )
        
    migration_thread = threading.Thread(target=migration_task)
    migration_thread.daemon = True
    migration_thread.start()
    
    return True  # Return immediately, actual results will be shown via messagebox

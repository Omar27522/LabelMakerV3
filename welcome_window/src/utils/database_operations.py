"""
Database operations module for the Label Maker application.
This module provides functions for interacting with a local SQLite database
to store and retrieve shipping records.
"""

import os
import sqlite3
import datetime
import logging
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.file_utils import ensure_directory_exists

def get_database_path():
    """
    Get the path to the SQLite database file.
    
    Returns:
        tuple: (database_directory, database_file_path)
    """
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Define the database directory
    database_directory = os.path.join(project_root, 'database')
    
    # Ensure the database directory exists
    ensure_directory_exists(database_directory)
    
    # Define the database file path
    database_file_path = os.path.join(database_directory, 'shipping_records.db')
    
    return database_directory, database_file_path

def initialize_database():
    """
    Initialize the database with necessary tables if they don't exist.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        _, db_path = get_database_path()
        
        # Connect to the database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create the shipping_records table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS shipping_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tracking_number TEXT,
            sku TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        )
        ''')
        
        # Create an index on tracking_number and sku for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracking_number ON shipping_records (tracking_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sku ON shipping_records (sku)')
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        return False

def add_shipping_record(tracking_number, sku, status, notes=""):
    """
    Add a new shipping record to the database.
    
    Args:
        tracking_number (str): Tracking number (can be empty)
        sku (str): SKU of the product
        status (str): Status of the shipment (e.g., "Printed", "Shipped")
        notes (str, optional): Additional notes
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure database is initialized
        initialize_database()
        
        _, db_path = get_database_path()
        
        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert the record
        cursor.execute(
            "INSERT INTO shipping_records (timestamp, tracking_number, sku, status, notes) VALUES (?, ?, ?, ?, ?)",
            (timestamp, tracking_number, sku, status, notes)
        )
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        logging.error(f"Error adding shipping record: {str(e)}")
        return False

def get_shipping_records(limit=100, offset=0, search_term=None, start_date=None, end_date=None):
    """
    Retrieve shipping records from the database with optional filtering.
    
    Args:
        limit (int, optional): Maximum number of records to retrieve
        offset (int, optional): Number of records to skip
        search_term (str, optional): Search term to filter by tracking number or SKU
        start_date (str, optional): Start date for filtering (format: YYYY-MM-DD)
        end_date (str, optional): End date for filtering (format: YYYY-MM-DD)
        
    Returns:
        list: List of shipping records as dictionaries
    """
    try:
        # Ensure database is initialized
        initialize_database()
        
        _, db_path = get_database_path()
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Build the query
        query = "SELECT * FROM shipping_records"
        params = []
        
        # Add WHERE clause if filters are provided
        where_clauses = []
        
        if search_term:
            # Use the enhanced search functionality
            search_clause, params = _build_enhanced_search_conditions(search_term, params)
            if search_clause:
                where_clauses.append(search_clause)
        
        if start_date:
            where_clauses.append("timestamp >= ?")
            params.append(f"{start_date} 00:00:00")
        
        if end_date:
            where_clauses.append("timestamp <= ?")
            params.append(f"{end_date} 23:59:59")
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Add ORDER BY, LIMIT, and OFFSET
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute the query
        cursor.execute(query, params)
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries
        records = [dict(row) for row in rows]
        
        # Close connection
        conn.close()
        
        return records
    
    except Exception as e:
        logging.error(f"Error retrieving shipping records: {str(e)}")
        return []

def get_record_count(search_term=None, start_date=None, end_date=None):
    """
    Get the total count of shipping records with optional filtering.
    
    Args:
        search_term (str, optional): Search term to filter by tracking number or SKU
        start_date (str, optional): Start date for filtering (format: YYYY-MM-DD)
        end_date (str, optional): End date for filtering (format: YYYY-MM-DD)
        
    Returns:
        int: Total count of matching records
    """
    try:
        # Ensure database is initialized
        initialize_database()
        
        _, db_path = get_database_path()
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Build the query
        query = "SELECT COUNT(*) FROM shipping_records"
        params = []
        
        # Add WHERE clause if filters are provided
        where_clauses = []
        
        if search_term:
            # Use the enhanced search functionality
            search_clause, params = _build_enhanced_search_conditions(search_term, params)
            if search_clause:
                where_clauses.append(search_clause)
        
        if start_date:
            where_clauses.append("timestamp >= ?")
            params.append(f"{start_date} 00:00:00")
        
        if end_date:
            where_clauses.append("timestamp <= ?")
            params.append(f"{end_date} 23:59:59")
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Execute the query
        cursor.execute(query, params)
        
        # Fetch result
        count = cursor.fetchone()[0]
        
        # Close connection
        conn.close()
        
        return count
    
    except Exception as e:
        logging.error(f"Error getting record count: {str(e)}")
        return 0

def update_shipping_record(record_id, tracking_number=None, sku=None, status=None, notes=None):
    """
    Update an existing shipping record.
    
    Args:
        record_id (int): ID of the record to update
        tracking_number (str, optional): New tracking number
        sku (str, optional): New SKU
        status (str, optional): New status
        notes (str, optional): New notes
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure database is initialized
        initialize_database()
        
        _, db_path = get_database_path()
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Build the update query
        query = "UPDATE shipping_records SET "
        params = []
        update_fields = []
        
        if tracking_number is not None:
            update_fields.append("tracking_number = ?")
            params.append(tracking_number)
        
        if sku is not None:
            update_fields.append("sku = ?")
            params.append(sku)
        
        if status is not None:
            update_fields.append("status = ?")
            params.append(status)
        
        if notes is not None:
            update_fields.append("notes = ?")
            params.append(notes)
        
        # If no fields to update, return early
        if not update_fields:
            return True
        
        query += ", ".join(update_fields)
        query += " WHERE id = ?"
        params.append(record_id)
        
        # Execute the query
        cursor.execute(query, params)
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        logging.error(f"Error updating shipping record: {str(e)}")
        return False

def delete_shipping_record(record_id):
    """
    Delete a shipping record from the database.
    
    Args:
        record_id (int): ID of the record to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure database is initialized
        initialize_database()
        
        _, db_path = get_database_path()
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete the record
        cursor.execute("DELETE FROM shipping_records WHERE id = ?", (record_id,))
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        logging.error(f"Error deleting shipping record: {str(e)}")
        return False

def import_from_text_log():
    """
    Import existing shipping records from the text log file.
    
    Returns:
        tuple: (success, count) - Whether the import was successful and how many records were imported
    """
    try:
        # Ensure database is initialized
        initialize_database()
        
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Define the log file path
        log_file_path = os.path.join(project_root, 'logs', 'shipping_records.txt')
        
        # Check if the log file exists
        if not os.path.exists(log_file_path):
            return True, 0  # No file to import, consider it successful with 0 records
        
        # Connect to the database
        _, db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read the log file
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Process each line
        count = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse the line
                # Expected format: "YYYY-MM-DD HH:MM:SS - Tracking=XXX, SKU=YYY, Status=ZZZ"
                parts = line.split(' - ', 1)
                if len(parts) != 2:
                    continue
                
                timestamp = parts[0]
                info_part = parts[1]
                
                # Extract tracking number, SKU, and status
                tracking_number = ""
                sku = ""
                status = ""
                
                info_items = info_part.split(', ')
                for item in info_items:
                    if item.startswith("Tracking="):
                        tracking_number = item[len("Tracking="):]
                    elif item.startswith("SKU="):
                        sku = item[len("SKU="):]
                    elif item.startswith("Status="):
                        status = item[len("Status="):]
                
                # Skip if SKU or status is missing
                if not sku or not status:
                    continue
                
                # Insert the record
                cursor.execute(
                    "INSERT INTO shipping_records (timestamp, tracking_number, sku, status, notes) VALUES (?, ?, ?, ?, ?)",
                    (timestamp, tracking_number, sku, status, "Imported from text log")
                )
                
                count += 1
            
            except Exception as e:
                logging.warning(f"Error parsing log line: {line}, Error: {str(e)}")
                continue
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return True, count
    
    except Exception as e:
        logging.error(f"Error importing from text log: {str(e)}")
        return False, 0

def _build_enhanced_search_conditions(search_term, params):
    """
    Build enhanced search conditions for Google-like searches across multiple fields.
    Supports partial word matching and multi-word searches.
    
    Args:
        search_term (str): The search term to process
        params (list): The list of parameters to extend with search values
        
    Returns:
        tuple: (where_clause, updated_params)
    """
    if not search_term or not search_term.strip():
        return None, params
    
    # Split search term into individual words for more flexible searching
    search_words = search_term.strip().split()
    
    if not search_words:
        return None, params
    
    # Define all searchable fields
    fields = ["tracking_number", "sku", "status", "notes"]
    
    # Create a list of conditions for each word
    word_conditions = []
    
    for word in search_words:
        # Create a list of conditions for each field for this word
        field_conditions = []
        
        for field in fields:
            # Add conditions for each field - partial word matching
            field_conditions.append(f"{field} LIKE ?")
            params.append(f"%{word}%")
        
        # Join the field conditions with OR (word appears in any field)
        word_condition = "(" + " OR ".join(field_conditions) + ")"
        word_conditions.append(word_condition)
    
    # Join the word conditions with OR (any word can match)
    # This is more flexible than AND, which requires all words to match
    where_clause = "(" + " OR ".join(word_conditions) + ")"
    
    return where_clause, params

def export_to_csv(file_path, search_term=None, start_date=None, end_date=None):
    """
    Export shipping records to a CSV file.
    
    Args:
        file_path (str): Path to save the CSV file
        search_term (str, optional): Search term to filter by tracking number or SKU
        start_date (str, optional): Start date for filtering (format: YYYY-MM-DD)
        end_date (str, optional): End date for filtering (format: YYYY-MM-DD)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import csv
        
        # Get all matching records (no limit)
        records = get_shipping_records(limit=1000000, offset=0, search_term=search_term, 
                                      start_date=start_date, end_date=end_date)
        
        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'timestamp', 'tracking_number', 'sku', 'status', 'notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for record in records:
                writer.writerow(record)
        
        return True
    
    except Exception as e:
        logging.error(f"Error exporting to CSV: {str(e)}")
        return False

"""
Database operations for label metadata.
This module provides functions for managing label metadata in a SQLite database.
"""

import os
import sqlite3
import csv
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def get_database_path():
    """
    Get the path to the labels database file.
    
    Returns:
        str: Path to the database file
    """
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Define the database file path in the database directory
    db_path = os.path.join(project_root, 'database', 'labels.db')
    
    return db_path

def initialize_database():
    """
    Initialize the labels database.
    Creates the necessary tables if they don't exist.
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    # Get the database path
    db_path = get_database_path()
    
    # Ensure the database directory exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir)
        except Exception as e:
            print(f"Error creating database directory: {e}")
            return False
    try:
        # Connect to the database
        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()
        
        # Create the labels table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS label_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upc TEXT,
            item_variant_number TEXT,
            department TEXT,
            category TEXT,
            color TEXT,
            website_color TEXT,
            website_name TEXT,
            label_name TEXT,
            sku TEXT,
            user_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create indexes for faster searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_upc ON label_metadata (upc)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_variant ON label_metadata (item_variant_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_department ON label_metadata (department)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON label_metadata (category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_color ON label_metadata (color)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_website_name ON label_metadata (website_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_label_name ON label_metadata (label_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sku ON label_metadata (sku)')
        
        # Commit the changes
        conn.commit()
        
        # Close the connection
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error initializing labels database: {e}")
        return False

def import_csv(file_path, replace_existing=False):
    """
    Import label metadata from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        replace_existing (bool): If True, existing data will be replaced
        
    Returns:
        tuple: (success, count) where success is a bool indicating if the import was successful
               and count is the number of records imported
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()
        
        # If replacing existing data, delete all records
        if replace_existing:
            cursor.execute('DELETE FROM label_metadata')
        
        # Read the CSV file
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            # Prepare for batch insert
            records = []
            
            for row in csv_reader:
                # Skip entries that contain only "--"
                if row.get('Label Name', '').strip() == "--" or row.get('Website Name', '').strip() == "--":
                    continue
                
                # Extract SKU from the Variant or label name
                sku = row.get('Variant', '').strip()
                if not sku:
                    # Try to extract from label name
                    label_name = row.get('Label Name', '')
                    if ' -- ' in label_name:
                        sku = label_name.split(' -- ')[1].strip()
                
                # Prepare the record
                record = (
                    row.get('Upc', '').strip(),
                    row.get('Variant', '').strip(),
                    row.get('Department', '').strip(),
                    row.get('Category', '').strip(),
                    row.get('Color', '').strip(),
                    row.get('Website Color', '').strip(),
                    row.get('Website Name', '').strip(),
                    row.get('Label Name', '').strip(),
                    sku
                )
                
                records.append(record)
            
            # Insert the records in batches
            cursor.executemany('''
            INSERT INTO label_metadata (
                upc, item_variant_number, department, category, color, 
                website_color, website_name, label_name, sku
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', records)
            
            # Get the number of records imported
            count = len(records)
            
            # Commit the changes
            conn.commit()
            
            # Close the connection
            conn.close()
            
            return True, count
    except Exception as e:
        print(f"Error importing CSV: {e}")
        return False, 0

def search_labels(search_term=None, field=None, limit=100, offset=0):
    """
    Search for label metadata.
    
    Args:
        search_term (str): Term to search for
        field (str): Specific field to search in (if None, search in all fields)
        limit (int): Maximum number of records to return
        offset (int): Offset for pagination
        
    Returns:
        list: List of matching records
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(get_database_path())
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Build the query based on search parameters
        if search_term and field:
            # Search in a specific field
            query = f'''
            SELECT * FROM label_metadata 
            WHERE {field} LIKE ? 
            ORDER BY label_name 
            LIMIT ? OFFSET ?
            '''
            cursor.execute(query, (f'%{search_term}%', limit, offset))
        elif search_term:
            # Split search term into words for multi-word search
            search_words = search_term.strip().split()
            
            if search_words:
                # Create conditions for each word
                word_conditions = []
                params = []
                
                # Define all searchable fields
                fields = [
                    "upc", "item_variant_number", "department", "category",
                    "color", "website_color", "website_name", "label_name", "sku"
                ]
                
                # For each word, create a condition that checks all fields
                for word in search_words:
                    word_clauses = []
                    for field_name in fields:
                        word_clauses.append(f"{field_name} LIKE ?")
                        params.append(f"%{word}%")
                    
                    # Join the field conditions with OR (word appears in any field)
                    word_condition = "(" + " OR ".join(word_clauses) + ")"
                    word_conditions.append(word_condition)
                
                # Join the word conditions with AND (all words must match)
                where_clause = " AND ".join(word_conditions)
                
                # Build the final query
                query = f'''
                SELECT * FROM label_metadata 
                WHERE {where_clause} 
                ORDER BY label_name 
                LIMIT ? OFFSET ?
                '''
                
                # Add limit and offset to params
                params.extend([limit, offset])
                
                # Execute the query
                cursor.execute(query, params)
            else:
                # Empty search term after splitting, return all records
                query = '''
                SELECT * FROM label_metadata 
                ORDER BY label_name 
                LIMIT ? OFFSET ?
                '''
                cursor.execute(query, (limit, offset))
        else:
            # No search term, return all records
            query = '''
            SELECT * FROM label_metadata 
            ORDER BY label_name 
            LIMIT ? OFFSET ?
            '''
            cursor.execute(query, (limit, offset))
        
        # Fetch the results
        results = [dict(row) for row in cursor.fetchall()]
        
        # Close the connection
        conn.close()
        
        return results
    except Exception as e:
        print(f"Error searching labels: {e}")
        return []

def get_label_count(search_term=None, field=None):
    """
    Get the total count of labels matching the search criteria.
    
    Args:
        search_term (str): Term to search for
        field (str): Specific field to search in (if None, search in all fields)
        
    Returns:
        int: Total count of matching records
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()
        
        # Build the query based on search parameters
        if search_term and field:
            # Search in a specific field
            query = f'''
            SELECT COUNT(*) FROM label_metadata 
            WHERE {field} LIKE ?
            '''
            cursor.execute(query, (f'%{search_term}%',))
        elif search_term:
            # Search in all fields
            query = '''
            SELECT COUNT(*) FROM label_metadata 
            WHERE upc LIKE ? 
            OR item_variant_number LIKE ? 
            OR department LIKE ? 
            OR category LIKE ? 
            OR color LIKE ? 
            OR website_color LIKE ? 
            OR website_name LIKE ? 
            OR label_name LIKE ? 
            OR sku LIKE ?
            '''
            params = tuple([f'%{search_term}%'] * 9)
            cursor.execute(query, params)
        else:
            # No search term, count all records
            query = 'SELECT COUNT(*) FROM label_metadata'
            cursor.execute(query)
        
        # Fetch the result
        count = cursor.fetchone()[0]
        
        # Close the connection
        conn.close()
        
        return count
    except Exception as e:
        print(f"Error getting label count: {e}")
        return 0

def get_unique_values(field):
    """
    Get unique values for a specific field.
    Useful for populating dropdown filters.
    
    Args:
        field (str): Field to get unique values for
        
    Returns:
        list: List of unique values
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()
        
        # Get unique values
        query = f'SELECT DISTINCT {field} FROM label_metadata ORDER BY {field}'
        cursor.execute(query)
        
        # Fetch the results
        results = [row[0] for row in cursor.fetchall() if row[0]]
        
        # Close the connection
        conn.close()
        
        return results
    except Exception as e:
        print(f"Error getting unique values: {e}")
        return []

def delete_label(label_id):
    """
    Delete a label record.
    
    Args:
        label_id (int): ID of the label to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()
        
        # Delete the record
        cursor.execute('DELETE FROM label_metadata WHERE id = ?', (label_id,))
        
        # Commit the changes
        conn.commit()
        
        # Close the connection
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error deleting label: {e}")
        return False

def update_label_notes(label_id, notes, sync_by_prefix=True):
    """
    Update the user notes for a label record and optionally sync across all items with the same prefix.
    
    Args:
        label_id (int): ID of the label to update
        notes (str): User notes to save
        sync_by_prefix (bool): If True, sync notes to all items with the same variant prefix
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()
        
        # Check if the user_notes column exists
        cursor.execute("PRAGMA table_info(label_metadata)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add the user_notes column if it doesn't exist
        if 'user_notes' not in columns:
            cursor.execute('ALTER TABLE label_metadata ADD COLUMN user_notes TEXT')
        
        if sync_by_prefix:
            # Get the variant number for this label
            cursor.execute('SELECT item_variant_number FROM label_metadata WHERE id = ?', (label_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                variant_number = result[0]
                # Extract the prefix (first 6 characters)
                prefix = variant_number[:6] if len(variant_number) >= 6 else variant_number
                
                # Update all records with the same prefix
                cursor.execute(
                    'UPDATE label_metadata SET user_notes = ? WHERE item_variant_number LIKE ?', 
                    (notes, f"{prefix}%")
                )
                updated_count = cursor.rowcount
                print(f"Updated notes for {updated_count} items with prefix {prefix}")
            else:
                # If we can't get the variant number, just update this record
                cursor.execute('UPDATE label_metadata SET user_notes = ? WHERE id = ?', (notes, label_id))
        else:
            # Update only this record
            cursor.execute('UPDATE label_metadata SET user_notes = ? WHERE id = ?', (notes, label_id))
        
        # Commit the changes
        conn.commit()
        
        # Close the connection
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error updating label notes: {e}")
        return False

import sqlite3
import os

# Database configuration
DATABASE = 'database.db'

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def init_db():
    """Initialize the database with the items table"""
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
        # Insert some initial data
        conn.execute('INSERT INTO items (name, description) VALUES (?, ?)', 
                   ('Item 1', 'Description for item 1'))
        conn.execute('INSERT INTO items (name, description) VALUES (?, ?)', 
                   ('Item 2', 'Description for item 2'))
        conn.commit()
        conn.close()
        print("Database initialized with default items.")
#database.py
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database setup from environment variables
DB_PATH = os.getenv('DB_PATH', 'mobile_data.db')


def init_db():
    """Initialize the database with required tables if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create forms table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS forms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_registration TEXT,
        date TEXT,
        requester_name TEXT NOT NULL,
        recipient_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create form items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS form_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        form_id INTEGER NOT NULL,
        item_number INTEGER NOT NULL,
        material_description TEXT NOT NULL,
        material_code TEXT,
        quantity INTEGER NOT NULL,
        unit TEXT,
        FOREIGN KEY (form_id) REFERENCES forms (id) ON DELETE CASCADE
    )
    ''')

    # Keep the original items table for backward compatibility
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")
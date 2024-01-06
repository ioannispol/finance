import sqlite3
from datetime import datetime

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def setup_database(conn):
    """Create tables for income and expenses in the database"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(e)

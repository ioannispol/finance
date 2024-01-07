import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import datetime


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


def setup_user_database(conn):
    """
    Sets up the user database table if it does not exist.

    Args:
        conn: The connection object to the database.

    Raises:
        sqlite3.Error: If an error occurs while executing the create table query.
    """

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def setup_recurring_transactions_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                start_date TEXT NOT NULL,
                frequency TEXT NOT NULL  -- e.g., 'monthly', 'weekly'
            )
        """)
        
        # Add 'last_processed_date' column if it does not exist
        cursor.execute("""
            SELECT count(*) FROM pragma_table_info('recurring_transactions') 
            WHERE name='last_processed_date'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE recurring_transactions ADD COLUMN last_processed_date TEXT")

        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


# def sync_recurring_transactions_to_main(conn):
#     today = datetime.date.today()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM recurring_transactions")
#     recurring_transactions = cursor.fetchall()

#     for transaction in recurring_transactions:
#         id, type, name, amount, start_date_str, frequency = transaction
#         start_date = datetime.datetime.strptime(start_date_str, "%d-%m-%Y").date()

#         if is_due_for_addition(today, start_date, frequency):
#             table = 'income' if type == 'income' else 'expenses'
#             cursor.execute(f"INSERT INTO {table} (date, name, amount) VALUES (?, ?, ?)", 
#                            (today.strftime("%d-%m-%Y"), name, amount))
#             # Update the start_date in the recurring_transactions table to today
#             cursor.execute("UPDATE recurring_transactions SET start_date = ? WHERE id = ?", 
#                            (today.strftime("%d-%m-%Y"), id))
#     conn.commit()
def sync_recurring_transactions_to_main(conn):
    today = datetime.date.today()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recurring_transactions")
    recurring_transactions = cursor.fetchall()

    for transaction in recurring_transactions:
        id, type, name, amount, start_date_str, frequency, last_processed_str = transaction
        start_date = datetime.datetime.strptime(start_date_str, "%d-%m-%Y").date()
        last_processed = datetime.datetime.strptime(last_processed_str, "%d-%m-%Y").date() if last_processed_str else start_date

        if is_due_for_addition(today, last_processed, frequency):
            table = 'income' if type == 'income' else 'expenses'
            cursor.execute(f"INSERT INTO {table} (date, name, amount) VALUES (?, ?, ?)", 
                           (today.strftime("%d-%m-%Y"), name, amount))
            cursor.execute("UPDATE recurring_transactions SET last_processed_date = ? WHERE id = ?", 
                           (today.strftime("%d-%m-%Y"), id))
    conn.commit()



# def is_due_for_addition(today, start_date, frequency):
#     if frequency == 'monthly':
#         # Check if a month or more has passed since the start date
#         return (today.year > start_date.year or 
#                 (today.year == start_date.year and today.month > start_date.month))
#     # Implement logic for other frequencies ('weekly', 'daily', etc.)
#     return False
def is_due_for_addition(today, start_date, frequency):
    if today < start_date:
        return False  # Transaction start date is in the future

    delta = today - start_date
    if frequency == 'daily':
        return True  # Every day
    elif frequency == 'weekly' and delta.days % 7 == 0:
        return True  # Every week
    elif frequency == 'monthly' and start_date.day == today.day:
        return True  # Same day of the month
    elif frequency == 'yearly' and start_date.day == today.day and start_date.month == today.month:
        return True  # Same day and month each year

    return False  # Not due for addition

def add_to_income(conn, name, amount, date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO income (date, name, amount) VALUES (?, ?, ?)", (date, name, amount))
    conn.commit()

def add_to_expenses(conn, name, amount, date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, name, amount) VALUES (?, ?, ?)", (date, name, amount))
    conn.commit()

import sqlite3
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
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def sync_recurring_transactions_to_main(conn):
    today = datetime.date.today()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM recurring_transactions")
    recurring_transactions = cursor.fetchall()

    for transaction in recurring_transactions:
        id, type, name, amount, start_date_str, frequency = transaction
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()

        # Determine if the transaction should be added based on frequency and start date
        if is_due_for_addition(today, start_date, frequency):
            if type == 'income':
                add_to_income(conn, name, amount, today)
            elif type == 'expense':
                add_to_expenses(conn, name, amount, today)

def is_due_for_addition(today, start_date, frequency):
    # Logic to determine if a recurring transaction is due based on its frequency
    # For example, if the frequency is 'monthly', check if a month has passed since the last addition
    pass

def add_to_income(conn, name, amount, date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO income (date, name, amount) VALUES (?, ?, ?)", (date, name, amount))
    conn.commit()

def add_to_expenses(conn, name, amount, date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, name, amount) VALUES (?, ?, ?)", (date, name, amount))
    conn.commit()

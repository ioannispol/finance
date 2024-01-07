from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem
from PyQt5.QtCore import QDate
import sqlite3
import csv
from datetime import datetime

def add_transaction(conn, transaction_list_widget, date_edit, name_line_edit, amount_line_edit, table):
    name = name_line_edit.text()
    amount = amount_line_edit.text()
    selected_date = date_edit.date().toPyDate()
    formatted_date = selected_date.strftime("%Y-%m-%d")

    try:
        amount = float(amount)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table} (date, name, amount) VALUES (?, ?, ?)", 
                       (formatted_date, name, amount))
        conn.commit()

        transaction_list_widget.addItem(f"{formatted_date} - {name}: £{amount:.2f}")
        name_line_edit.clear()
        amount_line_edit.clear()
    except ValueError:
        QMessageBox.warning(None, "Invalid Entry", "Please enter a valid amount.")

def calculate_summary(income_list_widget, expense_list_widget):
    income = sum(float(item.text().split(': £')[1]) for item in income_list_widget.findItems("", Qt.MatchContains))
    expenses = sum(float(item.text().split(': £')[1]) for item in expense_list_widget.findItems("", Qt.MatchContains))
    net_balance = income - expenses
    return income, expenses, net_balance

def display_summary(income, expenses, net_balance):
    QMessageBox.information(None, "Financial Summary",
                            f"Total Income: £{income:.2f}\n"
                            f"Total Expenses: £{expenses:.2f}\n"
                            f"Net Balance: £{net_balance:.2f}")

def fetch_data(conn, table):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, date, name, amount FROM {table}")
    rows = cursor.fetchall()
    return rows


def update_data_view(conn, table, tree_widget):
    tree_widget.clear()
    data = fetch_data(conn, table)
    for row in data:
        # Create a QTreeWidgetItem for each row
        item = QTreeWidgetItem(tree_widget)
        # Set values for each column
        for i, value in enumerate(row):
            item.setText(i, str(value))



def clear_treeview(tree_widget):
    tree_widget.clear()


def clear_data(conn, table):
    try:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table}")
        conn.commit()
        QMessageBox.information(None, "Data Cleared", f"All data from '{table}' has been cleared.")
    except sqlite3.Error as e:
        QMessageBox.warning(None, "Database Error", f"An error occurred: {e}")


def delete_selected_entry(conn, tree_widget, table):
    selected_items = tree_widget.selectedItems()
    if not selected_items:
        QMessageBox.information(None, "Selection Required", "Please select an item to delete.")
        return

    if QMessageBox.question(None, "Confirm Deletion", "Are you sure you want to delete this item?") == QMessageBox.Yes:
        for item in selected_items:
            item_id = item.text().split(" - ")[0]
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
            conn.commit()
        update_data_view(conn, table, tree_widget)


def fetch_monthly_summary(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as Month, 
               SUM(case when table_name = 'income' then amount else 0 end) as Total_Income,
               SUM(case when table_name = 'expenses' then amount else 0 end) as Total_Expenses
        FROM (
            SELECT date, amount, 'income' as table_name FROM income
            UNION ALL
            SELECT date, amount, 'expenses' FROM expenses
        )
        GROUP BY Month
        ORDER BY Month
    """)
    return cursor.fetchall()


def plot_data(conn, matplotlib_widget):
    data = fetch_monthly_summary(conn)
    if data:
        months, incomes, expenses = zip(*data)
        matplotlib_widget.figure.clear()
        ax = matplotlib_widget.figure.add_subplot(111)
        ax.plot(months, incomes, label='Income', marker='o')
        ax.plot(months, expenses, label='Expenses', marker='o')
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount')
        ax.set_title('Monthly Income and Expenses')
        ax.legend()
        matplotlib_widget.draw()
    else:
        # Handle case with no data
        pass


def fetch_total(conn, table):
    cursor = conn.cursor()
    cursor.execute(f"SELECT SUM(amount) FROM {table}")
    result = cursor.fetchone()
    return result[0] if result[0] is not None else 0


def export_data_to_file(conn, file_path):
    cursor = conn.cursor()
    # Assuming you have a unified way to fetch all relevant data
    cursor.execute("SELECT * FROM income UNION ALL SELECT * FROM expenses")
    rows = cursor.fetchall()

    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Date', 'Name', 'Amount'])  # Writing headers
        for row in rows:
            writer.writerow(row)
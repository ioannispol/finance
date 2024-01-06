import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def add_transaction(conn, transaction_list, date_entry, name_entry, amount_entry, table):
    name = name_entry.get()
    amount = amount_entry.get()
    selected_date = date_entry.get_date()  # Get the selected date
    formatted_date = selected_date.strftime("%Y-%m-%d")  # Format the date

    try:
        amount = float(amount)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table} (date, name, amount) VALUES (?, ?, ?)", 
                       (formatted_date, name, amount))
        conn.commit()

        transaction_list.insert(tk.END, f"{formatted_date} - {name}: £{amount:.2f}")
        name_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Invalid Entry", "Please enter a valid amount.")


def calculate_summary(income_list, expense_list):
    income = sum(float(item.split(': £')[1]) for item in income_list.get(0, tk.END))
    expenses = sum(float(item.split(': £')[1]) for item in expense_list.get(0, tk.END))
    net_balance = income - expenses
    return income, expenses, net_balance


def display_summary(income, expenses, net_balance):
    messagebox.showinfo("Financial Summary",
                        f"Total Income: £{income:.2f}\n"
                        f"Total Expenses: £{expenses:.2f}\n"
                        f"Net Balance: £{net_balance:.2f}")


def fetch_data(conn, table):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, date, name, amount FROM {table}")
    rows = cursor.fetchall()
    return rows


def update_data_view(conn, table, tree):
    """
    Update the Treeview widget in tab2 with data from the selected table (income or expenses).

    :param conn: Database connection object.
    :param table: Table name ('income' or 'expenses') from which data is to be fetched.
    :param tree: Treeview widget where the data will be displayed.
    """
    # Clear existing data in the treeview
    for i in tree.get_children():
        tree.delete(i)

    # Fetch new data and insert it into the treeview
    data = fetch_data(conn, table)
    for row in data:
        tree.insert('', tk.END, values=row)
        
def clear_treeview(tree):
    """Clear all entries in the Treeview widget."""
    tree.delete(*tree.get_children())


def delete_selected_entry(conn, tree, table):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showinfo("Selection Required", "Please select an item to delete.")
        return

    # Confirm deletion
    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this item?"):
        for item in selected_item:
            # Fetch the ID of the selected item
            item_id = tree.item(item, 'values')[0]  # ID is the first element in values
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
            conn.commit()
        update_data_view(conn, table, tree)


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
    rows = cursor.fetchall()
    return rows
     
def plot_data(conn, frame):
    # Clear previous figure
    for widget in frame.winfo_children():
        widget.destroy()

    data = fetch_monthly_summary(conn)
    if data:
        months, incomes, expenses = zip(*data)

        fig, ax = plt.subplots()
        ax.plot(months, incomes, label='Income', marker='o')
        ax.plot(months, expenses, label='Expenses', marker='o')
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount')
        ax.set_title('Monthly Income and Expenses')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=frame)  
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill='both')
        canvas.draw()
    else:
        tk.Label(frame, text="No data available to plot.").pack()
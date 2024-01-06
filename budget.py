import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

# Initialize database
db_conn = create_connection("budgeting.db")
setup_database(db_conn)

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


def setup_tab2(tab2):
    # Create and pack the Treeview widget within tab2
    tree = ttk.Treeview(tab2, columns=('Date', 'Name', 'Amount'), show='headings')
    tree.heading('Date', text='Date')
    tree.heading('Name', text='Name')
    tree.heading('Amount', text='Amount')
    tree.pack(expand=True, fill='both')
    
    tree["columns"] = ("ID", "Date", "Name", "Amount")
    tree.column("ID", width=0, stretch=tk.NO)  # Hide the ID column from the view
    tree.heading("Date", text="Date")
    tree.heading("Name", text="Name")
    tree.heading("Amount", text="Amount")

    # Buttons to update the Treeview
    view_income_button = ttk.Button(tab2, text="View Income Data", 
                                    command=lambda: update_data_view(db_conn, 'income', tree))
    view_income_button.pack()

    view_expenses_button = ttk.Button(tab2, text="View Expenses Data", 
                                      command=lambda: update_data_view(db_conn, 'expenses', tree))
    view_expenses_button.pack()
    
    clear_data_button = ttk.Button(tab2, text="Clear Data", 
                                   command=lambda: clear_treeview(tree))
    clear_data_button.pack()
    
    # Delete button
    delete_button = ttk.Button(tab2, text="Delete Selected Entry", 
                               command=lambda: delete_selected_entry(db_conn, tree, 'income' if table_selection.get() == 'income' else 'expenses'))
    delete_button.pack()

    # Radio buttons to choose between income and expenses
    table_selection = tk.StringVar(value='income')
    radio_income = ttk.Radiobutton(tab2, text="Income", variable=table_selection, value='income')
    radio_expenses = ttk.Radiobutton(tab2, text="Expenses", variable=table_selection, value='expenses')
    radio_income.pack()
    radio_expenses.pack()

    return tree


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

def setup_graph_tab(conn, frame):
    # Clear the frame first
    for widget in frame.winfo_children():
        widget.destroy()

    # Fetch and plot data
    plot_data(conn, frame)  # Assuming plot_data is defined as previously discussed


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


def create_menu(app):
    menubar = tk.Menu(app)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Exit", command=app.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Budgeting App v1.0"))
    menubar.add_cascade(label="Help", menu=help_menu)

    app.config(menu=menubar)


def main():
    app = tk.Tk()
    app.title("Budgeting App")
    
    create_menu(app)

    # Set up the notebook (tabbed interface)
    notebook = ttk.Notebook(app)
    tab1 = ttk.Frame(notebook)  # Tab for adding data
    tab2 = ttk.Frame(notebook)  # Tab for viewing data
    tab3 = ttk.Frame(notebook)  # Tab for the graph

    notebook.add(tab1, text="Add Data")
    notebook.add(tab2, text="View Data")
    notebook.add(tab3, text="View Graph")
    notebook.pack(expand=True, fill='both')

    # Tab 1: Adding Data
    # Income section
    income_frame = ttk.LabelFrame(tab1, text="Income")
    income_frame.pack(fill="both", expand="yes", padx=10, pady=5)

    # Income date label and DateEntry
    ttk.Label(income_frame, text="Date:").pack(side="left", padx=(0, 5))
    income_date_entry = DateEntry(income_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
    income_date_entry.pack(side="left", padx=(0, 5))

    # Income name label and entry
    ttk.Label(income_frame, text="Description:").pack(side="top", padx=(0, 5))
    income_name_entry = ttk.Entry(income_frame)
    income_name_entry.pack(side="top", padx=(0, 5))

    # Income amount label and entry
    ttk.Label(income_frame, text="Amount:").pack(side="top", padx=(0, 5))
    income_amount_entry = ttk.Entry(income_frame)
    income_amount_entry.pack(side="top", padx=(0, 5))

    # Income list and add button
    income_list = tk.Listbox(income_frame)
    income_list.pack(side="top", fill="both", expand="yes")
    income_add_button = ttk.Button(income_frame, text="Add Income", 
                                   command=lambda: add_transaction(db_conn, income_list, income_date_entry, income_name_entry, income_amount_entry, 'income'))
    income_add_button.pack(side="top")

    # Expense section
    expense_frame = ttk.LabelFrame(tab1, text="Expenses")
    expense_frame.pack(fill="both", expand="yes", padx=10, pady=5)

    # Expense date label and DateEntry
    ttk.Label(expense_frame, text="Date:").pack(side="left", padx=(0, 5))
    expense_date_entry = DateEntry(expense_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2)
    expense_date_entry.pack(side="left", padx=(0, 5))

    # Expense name label and entry
    ttk.Label(expense_frame, text="Description:").pack(side="top", padx=(0, 5))
    expense_name_entry = ttk.Entry(expense_frame)

    expense_name_entry.pack(side="top", padx=(0, 5))

    # Expense amount label and entry
    ttk.Label(expense_frame, text="Amount:").pack(side="top", padx=(0, 5))
    expense_amount_entry = ttk.Entry(expense_frame)
    expense_amount_entry.pack(side="top", padx=(0, 5))

    # Expense list and add button
    expense_list = tk.Listbox(expense_frame)
    expense_list.pack(side="top", fill="both", expand="yes")
    expense_add_button = ttk.Button(expense_frame, text="Add Expense", 
                                    command=lambda: add_transaction(db_conn, expense_list, expense_date_entry, expense_name_entry, expense_amount_entry, 'expenses'))
    expense_add_button.pack(side="top")

    # Summary button in Tab 1
    summary_button = ttk.Button(tab1, text="Show Summary", 
                                command=lambda: display_summary(*calculate_summary(income_list, expense_list)))
    summary_button.pack(pady=10)

    # Set up Tab 2: Viewing Data
    setup_tab2(tab2)

    # Set up Tab 3: Graph
    setup_graph_tab(db_conn, tab3)  # Assuming setup_graph_tab is defined to setup the graph

    app.mainloop()



if __name__ == "__main__":
    main()

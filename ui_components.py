import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

from utils import (add_transaction,
                   calculate_summary,
                   display_summary,
                   fetch_data,
                   update_data_view,
                   delete_selected_entry,
                   clear_treeview,
                   plot_data)

def setup_tab1(tab1):
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

def setup_tab3(tab3):
    # Clear the frame first
    for widget in frame.winfo_children():
        widget.destroy()

    # Fetch and plot data
    plot_data(conn, frame)

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

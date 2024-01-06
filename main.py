import tkinter as tk
from tkinter import ttk
from database import create_connection, setup_database
from ui_components import setup_tab1, setup_tab2, setup_tab3, create_menu

def main():
    app = tk.Tk()
    app.title("Budgeting App")
    
    db_conn = create_connection("budgeting.db")
    setup_database(db_conn)

    create_menu(app)

    notebook = ttk.Notebook(app)
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)

    notebook.add(tab1, text="Add Data")
    notebook.add(tab2, text="View Data")
    notebook.add(tab3, text="View Graph")
    notebook.pack(expand=True, fill='both')

    setup_tab1(tab1)
    setup_tab2(tab2)
    setup_tab3(tab3)

    app.mainloop()

if __name__ == "__main__":
    main()

import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QDateEdit, QListWidget, QMessageBox, QTreeWidget, QTreeWidgetItem, 
                             QComboBox, QRadioButton, QButtonGroup, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QDate
from utils import (add_transaction, calculate_summary, display_summary, 
                   fetch_total, fetch_data, update_data_view, delete_selected_entry,
                   clear_treeview, plot_data, clear_data)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class TabOne(QWidget):
    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setup_transaction_type_dropdown(layout)
        self.setup_date_edit(layout)
        self.setup_transaction_fields(layout)
        self.setup_summary_section(layout)

    def setup_transaction_type_dropdown(self, layout):
        self.transaction_type = QComboBox()
        self.transaction_type.addItem("Income", "income")
        self.transaction_type.addItem("Expense", "expenses")
        layout.addWidget(QLabel("Transaction Type:"))
        layout.addWidget(self.transaction_type)

    def setup_date_edit(self, layout):
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd-MM-yyyy")
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.date_edit)

    def setup_transaction_fields(self, layout):
        self.name_line_edit = QLineEdit()
        self.amount_line_edit = QLineEdit()
        self.transaction_list_widget = QListWidget()
        add_btn = QPushButton("Add Transaction")
        add_btn.clicked.connect(self.on_add_transaction)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.name_line_edit)
        layout.addWidget(QLabel("Amount:"))
        layout.addWidget(self.amount_line_edit)
        layout.addWidget(add_btn)
        layout.addWidget(self.transaction_list_widget)

    def setup_summary_section(self, layout):
        summary_btn = QPushButton("Calculate Summary")
        summary_btn.clicked.connect(self.on_calculate_summary)
        self.total_income_label = QLabel("Total Income: £0.00")
        self.total_expenses_label = QLabel("Total Expenses: £0.00")
        self.net_balance_label = QLabel("Net Balance: £0.00")
        layout.addWidget(summary_btn)
        layout.addWidget(self.total_income_label)
        layout.addWidget(self.total_expenses_label)
        layout.addWidget(self.net_balance_label)

    def on_add_transaction(self):
        # Get the selected transaction type from the dropdown
        transaction_type = self.transaction_type.currentData()
        add_transaction(self.db_conn,
                        self.transaction_list_widget,
                        self.date_edit,
                        self.name_line_edit,
                        self.amount_line_edit,
                        transaction_type)  # Example for 'income'
    
    def on_calculate_summary(self):
        # Assuming you have functions to fetch data for income and expenses
        income = fetch_total(self.db_conn, "income")
        expenses = fetch_total(self.db_conn, "expenses")
        net_balance = income - expenses

        self.total_income_label.setText(f"Total Income: £{income:.2f}")
        self.total_expenses_label.setText(f"Total Expenses: £{expenses:.2f}")
        self.net_balance_label.setText(f"Net Balance: £{net_balance:.2f}")


class TabTwo(QWidget):
    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setup_radio_buttons(layout)
        self.setup_table_widget(layout)
        self.setup_buttons(layout)

    def setup_radio_buttons(self, layout):
        self.radio_group = QButtonGroup(self)
        income_radio = QRadioButton("Income")
        expenses_radio = QRadioButton("Expenses")
        self.radio_group.addButton(income_radio, 1)
        self.radio_group.addButton(expenses_radio, 2)
        income_radio.setChecked(True)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(income_radio)
        radio_layout.addWidget(expenses_radio)
        layout.addLayout(radio_layout)

    def setup_table_widget(self, layout):
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Date", "Name", "Amount"])
        layout.addWidget(self.table_widget)

    def setup_buttons(self, layout):
        self.update_btn = QPushButton("Update Data")
        self.update_btn.clicked.connect(self.on_update_data)
        self.clear_db_btn = QPushButton("Clear Database")
        self.clear_db_btn.clicked.connect(self.on_clear_db)
        layout.addWidget(self.update_btn)
        layout.addWidget(self.clear_db_btn)

    def on_update_data(self):
        selected_type = self.radio_group.checkedId()
        table = "income" if selected_type == 1 else "expenses"
        self.update_data_view(table)

    def update_data_view(self, table):
        self.table_widget.setRowCount(0)
        data = fetch_data(self.db_conn, table)
        for row_data in data:
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            for column, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_widget.setItem(row, column, item)

    def on_clear_db(self):
        selected_type = self.radio_group.checkedId()
        table = "income" if selected_type == 1 else "expenses"
        confirm_reply = QMessageBox.question(self, 'Confirm Clear', f"Are you sure you want to clear all data from '{table}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm_reply == QMessageBox.Yes:
            clear_data(self.db_conn, table)
            self.update_data_view(table)

class TabThree(QWidget):

    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setup_plot_section(layout)

    def setup_plot_section(self, layout):
        self.canvas = FigureCanvas(Figure())
        self.update_btn = QPushButton("Plot Data")
        self.update_btn.clicked.connect(self.on_plot_data)
        layout.addWidget(self.update_btn)
        layout.addWidget(self.canvas)

    def on_plot_data(self):
        plot_data(self.db_conn, self.canvas)


def create_main_window(db_conn):
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Budgeting App")

    tab_widget = QTabWidget()
    tab_one = TabOne(db_conn)
    tab_two = TabTwo(db_conn)
    tab_three = TabThree(db_conn)

    tab_widget.addTab(tab_one, "Add Data")
    tab_widget.addTab(tab_two, "View Data")
    tab_widget.addTab(tab_three, "View Graph")

    main_window.setCentralWidget(tab_widget)
    main_window.show()
    sys.exit(app.exec_())

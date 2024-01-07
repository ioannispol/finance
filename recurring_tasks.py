from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import QDate
import sqlite3
import datetime

class RecurringTransactionTab(QWidget):
    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Transaction type
        self.type_combo_box = QComboBox()
        self.type_combo_box.addItems(["Income", "Expense"])

        # Transaction name
        self.name_line_edit = QLineEdit()

        # Transaction amount
        self.amount_line_edit = QLineEdit()

        # Start date for the recurring transaction
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setDisplayFormat("dd-MM-yyyy")

        # Frequency of the transaction
        self.frequency_combo_box = QComboBox()
        self.frequency_combo_box.addItems(["Daily", "Weekly", "Monthly", "Yearly"])

        # Add Transaction button
        add_button = QPushButton("Add Recurring Transaction")
        add_button.clicked.connect(self.add_recurring_transaction)

        # Set up layout
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Type:"))
        form_layout.addWidget(self.type_combo_box)
        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_line_edit)
        form_layout.addWidget(QLabel("Amount:"))
        form_layout.addWidget(self.amount_line_edit)
        form_layout.addWidget(QLabel("Start Date:"))
        form_layout.addWidget(self.start_date_edit)
        form_layout.addWidget(QLabel("Frequency:"))
        form_layout.addWidget(self.frequency_combo_box)

        layout.addLayout(form_layout)
        layout.addWidget(add_button)

        # Table to display existing recurring transactions
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)  # ID, Type, Name, Amount, Frequency
        self.table_widget.setHorizontalHeaderLabels(["ID", "Type", "Name", "Amount", "Frequency"])
        self.load_recurring_transactions()

        layout.addWidget(self.table_widget)

    def add_recurring_transaction(self):
        type = self.type_combo_box.currentText().lower()
        name = self.name_line_edit.text()
        amount = self.amount_line_edit.text()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        frequency = self.frequency_combo_box.currentText().lower()

        # Validate input
        if not name or not amount.isdigit() or float(amount) <= 0:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid transaction details.")
            return

        # Insert into database
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO recurring_transactions (type, name, amount, start_date, frequency)
                VALUES (?, ?, ?, ?, ?)
            """, (type, name, float(amount), start_date, frequency))
            self.db_conn.commit()
            self.load_recurring_transactions()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred: {e}")

    def load_recurring_transactions(self):
        self.table_widget.setRowCount(0)
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT * FROM recurring_transactions")
            for row in cursor.fetchall():
                current_row = self.table_widget.rowCount()
                self.table_widget.insertRow(current_row)
                for column, item in enumerate(row):
                    self.table_widget.setItem(current_row, column, QTableWidgetItem(str(item)))
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred: {e}")

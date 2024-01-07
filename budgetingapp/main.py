import sys

from PyQt5.QtWidgets import \
    QApplication, QMainWindow, QTabWidget, QAction, QMessageBox, QFileDialog, QDialog
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication
from database import create_connection, setup_database
from ui_components import TabOne, TabTwo, TabThree
from utils import export_data_to_file
from budgetingapp.authentication import create_user, LoginDialog, add_default_user
from database import \
    setup_user_database, setup_recurring_transactions_table, sync_recurring_transactions_to_main
from recurring_tasks import RecurringTransactionTab


class MainWindow(QMainWindow):
    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.setWindowTitle("Budgeting App")

        # Create the tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Initialize tabs with database connection
        self.tab_one = TabOne(self.db_conn)
        self.tab_two = TabTwo(self.db_conn)
        self.tab_three = TabThree(self.db_conn)
        self.recurring_tab = RecurringTransactionTab(self.db_conn)

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.tab_one, "Add Data")
        self.tab_widget.addTab(self.tab_two, "View Data")
        self.tab_widget.addTab(self.recurring_tab, "Recurring Transactions")
        self.tab_widget.addTab(self.tab_three, "View Graph")
        self.create_menu_bar()
        
        # Setup a timer to sync recurring transactions
        self.sync_timer = QTimer(self)
        self.sync_timer.timeout.connect(lambda: self.sync_recurring_transactions())
        self.sync_timer.start(60000)  # Time in milliseconds (60000 ms = 1 minute)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # Save action
        save_action = QAction("&Save", self)
        save_action.triggered.connect(self.on_save_data)
        file_menu.addAction(save_action)

        # Add Exit action
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        # Add About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_about_dialog(self):
        QMessageBox.information(self, "About", "Budgeting App\nVersion 1.0")

    def on_save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if file_path:
            export_data_to_file(self.db_conn, file_path)
            QMessageBox.information(self, "Success", "Data saved successfully.")

    def sync_recurring_transactions(self):
        sync_recurring_transactions_to_main(self.db_conn)
        # Optionally, refresh views if necessary


def set_dark_theme(app):
    app.setStyle("Fusion")  # Optional: set style to 'Fusion' which works well with dark themes

    palette = QPalette()

    # Define colors
    dark_color = QColor(45, 45, 45)
    disabled_color = QColor(127, 127, 127)

    palette.setColor(QPalette.Window, dark_color)
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(18, 18, 18))
    palette.setColor(QPalette.AlternateBase, dark_color)
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Disabled, QPalette.Text, disabled_color)
    palette.setColor(QPalette.Button, dark_color)
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_color)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)
    
def main():
    app = QApplication(sys.argv)
    set_dark_theme(app)

    db_conn = create_connection("budgeting.db")
    setup_database(db_conn)
    setup_recurring_transactions_table(db_conn)
    sync_recurring_transactions_to_main(db_conn)
    add_default_user(db_conn)

    setup_user_database(db_conn)  # Set up user database

    # Show login dialog
    login_dialog = LoginDialog(db_conn)
    if login_dialog.exec() == QDialog.Accepted:
        main_window = MainWindow(db_conn)
        main_window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)  # Exit the application if login fails


if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # set_dark_theme(app)
    # db_conn = create_connection("budgeting.db")
    # setup_database(db_conn)
    # add_default_user(db_conn)
    # mainWin = MainWindow(db_conn)
    # mainWin.show()
    # sys.exit(app.exec_())
    main()

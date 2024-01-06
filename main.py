import sys

from PyQt5.QtWidgets import \
    QApplication, QMainWindow, QTabWidget, QAction, QMessageBox, QFileDialog

from database import create_connection, setup_database
from ui_components import TabOne, TabTwo, TabThree
from utils import export_data_to_file

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

        # Add tabs to the tab widget
        self.tab_widget.addTab(self.tab_one, "Add Data")
        self.tab_widget.addTab(self.tab_two, "View Data")
        self.tab_widget.addTab(self.tab_three, "View Graph")
        self.create_menu_bar()
        
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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_conn = create_connection("budgeting.db")
    setup_database(db_conn)
    mainWin = MainWindow(db_conn)
    mainWin.show()
    sys.exit(app.exec_())

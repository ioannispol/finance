from PyQt5.QtWidgets import \
    QDialog, QLineEdit, QLabel, QVBoxLayout, QPushButton, QMessageBox

from utils import check_user

class LoginDialog(QDialog):
    def __init__(self, db_conn):
        super().__init__()
        self.db_conn = db_conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.username_line_edit = QLineEdit()
        self.password_line_edit = QLineEdit()
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.check_login)

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_line_edit)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_line_edit)
        layout.addWidget(login_button)

    def check_login(self):
        if check_user(self.db_conn,
                      self.username_line_edit.text(),
                      self.password_line_edit.text()):
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

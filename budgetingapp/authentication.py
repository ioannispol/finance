import sqlite3
from hashlib import sha256

from PyQt5.QtWidgets import \
    QDialog, QLineEdit, QLabel, QVBoxLayout, QPushButton, QMessageBox


def create_user(conn, username, password):
    hashed_password = sha256(password.encode()).hexdigest()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    return True


def check_user(conn, username, password):
    hashed_password = sha256(password.encode()).hexdigest()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    return cursor.fetchone() is not None


def add_default_user(conn):
    username = "admin"
    password = "admin"  # You should choose a more secure default password
    if not check_user(conn, username, password):
        create_user(conn, username, password)


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
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()
        if check_user(self.db_conn, username, password):
            self.accept()  # Close the dialog and return success
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect username or password")
"""
Database Management GUI
A graphical interface to manage users in the SQLite database.
"""
import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules import database, auth


class DatabaseManagerGUI(QtWidgets.QMainWindow):
    """GUI for managing the user database."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Manager - User Management")
        self.setGeometry(100, 100, 900, 600)
        
        # Initialize database
        database.init_db()
        
        # Create central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QtWidgets.QLabel("👥 User Database Manager")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(title)
        
        # Database info
        info_layout = QtWidgets.QHBoxLayout()
        self.db_path_label = QtWidgets.QLabel(f"Database: {database.DB_PATH}")
        self.db_path_label.setStyleSheet("color: #666; padding: 5px;")
        info_layout.addWidget(self.db_path_label)
        info_layout.addStretch()
        
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_users)
        refresh_btn.setStyleSheet("padding: 5px 15px;")
        info_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(info_layout)
        
        # Users table
        table_label = QtWidgets.QLabel("Users:")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(table_label)
        
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Email", "Created At", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        main_layout.addWidget(self.table)
        
        # Add user section
        add_section = QtWidgets.QGroupBox("➕ Add New User")
        add_layout = QtWidgets.QHBoxLayout()
        
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Email address")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        
        add_btn = QtWidgets.QPushButton("Add User")
        add_btn.setStyleSheet("padding: 8px 20px; background-color: #4CAF50; color: white; font-weight: bold;")
        add_btn.clicked.connect(self.add_user)
        
        add_layout.addWidget(QtWidgets.QLabel("Email:"))
        add_layout.addWidget(self.email_input)
        add_layout.addWidget(QtWidgets.QLabel("Password:"))
        add_layout.addWidget(self.password_input)
        add_layout.addWidget(add_btn)
        
        add_section.setLayout(add_layout)
        main_layout.addWidget(add_section)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Load users
        self.refresh_users()
        
        # Apply dark theme
        self.apply_dark_theme()
    
    def apply_dark_theme(self):
        """Apply a modern dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                gridline-color: #404040;
                border: 1px solid #404040;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
                padding: 8px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QGroupBox {
                border: 1px solid #404040;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
    
    def refresh_users(self):
        """Refresh the users table."""
        # Clear existing table
        self.table.setRowCount(0)
        
        # Get all users from database (including full data with ID)
        import sqlite3
        conn = sqlite3.connect(str(database.DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        users = [dict(row) for row in rows]
        
        # Set row count
        self.table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            # ID - ensure we get the actual ID from database
            id_item = QtWidgets.QTableWidgetItem(str(user['id']))
            id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)
            
            # Email
            email_item = QtWidgets.QTableWidgetItem(user['email'])
            self.table.setItem(row, 1, email_item)
            
            # Created At
            created_item = QtWidgets.QTableWidgetItem(str(user['created_at']))
            self.table.setItem(row, 2, created_item)
            
            # Delete button
            delete_btn = QtWidgets.QPushButton("🗑️ Delete")
            delete_btn.setStyleSheet("background-color: #d32f2f; padding: 5px 10px;")
            delete_btn.clicked.connect(lambda checked, email=user['email']: self.delete_user(email))
            self.table.setCellWidget(row, 3, delete_btn)
        
        self.table.resizeColumnsToContents()
        self.statusBar().showMessage(f"Loaded {len(users)} user(s)")
    
    def add_user(self):
        """Add a new user to the database."""
        email = self.email_input.text().strip().lower()
        password = self.password_input.text()
        
        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "Please fill in both email and password.")
            return
        
        # Check if user exists
        existing_user = database.get_user_by_email(email)
        if existing_user:
            QtWidgets.QMessageBox.warning(self, "Error", f"User with email {email} already exists.")
            return
        
        try:
            # Hash password
            password_hash = auth.hash_password(password)
            password_hash_str = password_hash.decode('utf-8')
            
            # Create user
            user = database.create_user(email, password_hash_str)
            if user:
                # Show success message with the actual ID assigned
                QtWidgets.QMessageBox.information(
                    self, 
                    "Success", 
                    f"User created successfully!\n\nEmail: {email}\nID: {user['id']}"
                )
                self.email_input.clear()
                self.password_input.clear()
                # Force refresh to show updated IDs
                self.refresh_users()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Failed to create user.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error creating user: {str(e)}")
    
    def delete_user(self, email):
        """Delete a user from the database."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete user:\n{email}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                # Delete using SQLite directly
                import sqlite3
                conn = sqlite3.connect(str(database.DB_PATH))
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE email = ?", (email,))
                conn.commit()
                conn.close()
                
                if cursor.rowcount > 0:
                    QtWidgets.QMessageBox.information(self, "Success", f"User {email} deleted successfully!")
                    self.refresh_users()
                else:
                    QtWidgets.QMessageBox.warning(self, "Error", "User not found.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error deleting user: {str(e)}")


def main():
    """Run the database manager GUI."""
    app = QtWidgets.QApplication(sys.argv)
    
    window = DatabaseManagerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


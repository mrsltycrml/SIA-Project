"""
Database module for SQLite operations.
Handles database connection and user table management.
"""
import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager


# Database file path (in project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "users.db"


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures proper connection handling and transaction management.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """
    Initialize the database and create the users table if it doesn't exist.
    This function is safe to call multiple times - it won't recreate existing tables.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create index on email for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)


def get_user_by_email(email):
    """
    Retrieve a user from the database by email.
    
    Args:
        email: User's email address
        
    Returns:
        dict with user data if found, None otherwise
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def create_user(email, password_hash):
    """
    Create a new user in the database.
    
    Args:
        email: User's email address
        password_hash: Bcrypt hashed password
        
    Returns:
        dict with user data if successful
        
    Raises:
        sqlite3.IntegrityError: If email already exists
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
        )
        user_id = cursor.lastrowid
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_users():
    """
    Retrieve all users from the database.
    
    Returns:
        list of dicts with user data
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, created_at FROM users ORDER BY id")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


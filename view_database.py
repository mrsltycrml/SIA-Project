"""
Simple script to view database contents.
Run this to see all users stored in the database.
"""
import sys
from pathlib import Path
import sqlite3

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules import database


def view_database():
    """Display all users in the database in a formatted way."""
    db_path = database.DB_PATH
    
    print("\n" + "=" * 70)
    print("📊 DATABASE CONTENTS VIEWER")
    print("=" * 70)
    
    if not db_path.exists():
        print(f"\n❌ Database file not found at: {db_path}")
        print("   The database will be created when you first register a user.")
        return
    
    print(f"\n📁 Database location: {db_path}")
    print(f"📏 Database size: {db_path.stat().st_size:,} bytes\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ 'users' table does not exist yet.")
            conn.close()
            return
        
        # Get all users
        cursor.execute("SELECT * FROM users ORDER BY id")
        rows = cursor.fetchall()
        
        if not rows:
            print("📭 No users found in database.\n")
            print("   Register a user through the web interface or test script to see data here.")
        else:
            print(f"👥 Found {len(rows)} user(s):\n")
            print("-" * 70)
            
            for row in rows:
                user = dict(row)
                print(f"\n🆔 ID: {user['id']}")
                print(f"📧 Email: {user['email']}")
                print(f"🔐 Password Hash: {user['password_hash'][:60]}...")
                print(f"📅 Created At: {user['created_at']}")
                print("-" * 70)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error reading database: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    view_database()


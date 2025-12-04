"""
Test script for authentication system.
Run this script to test the database and authentication functionality.
"""
import sys
from pathlib import Path

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules import database, auth


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 70 + "\n")


def test_database_initialization():
    """Test database initialization."""
    print("🔧 Testing database initialization...")
    try:
        database.init_db()
        print("✅ Database initialized successfully!")
        print(f"   Database file location: {database.DB_PATH}")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False


def test_user_creation():
    """Test creating a new user."""
    print("\n📝 Testing user creation...")
    
    test_email = "test@example.com"
    test_password = "TestPassword123!"
    
    # Check if user already exists
    existing_user = database.get_user_by_email(test_email)
    if existing_user:
        print(f"⚠️  User '{test_email}' already exists. Skipping creation.")
        return existing_user
    
    # Hash password
    print(f"   Hashing password for '{test_email}'...")
    password_hash = auth.hash_password(test_password)
    password_hash_str = password_hash.decode('utf-8')
    print(f"   Password hash generated: {password_hash_str[:50]}...")
    
    # Create user
    try:
        user = database.create_user(test_email, password_hash_str)
        if user:
            print(f"✅ User created successfully!")
            print(f"   User ID: {user['id']}")
            print(f"   Email: {user['email']}")
            print(f"   Created at: {user['created_at']}")
            return user
        else:
            print("❌ Failed to create user")
            return None
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None


def test_password_verification():
    """Test password verification."""
    print("\n🔐 Testing password verification...")
    
    test_email = "test@example.com"
    correct_password = "TestPassword123!"
    wrong_password = "WrongPassword!"
    
    # Get user from database
    user = database.get_user_by_email(test_email)
    if not user:
        print(f"⚠️  User '{test_email}' not found. Run user creation test first.")
        return False
    
    # Test correct password
    print(f"   Testing correct password...")
    if auth.verify_password(correct_password, user['password_hash']):
        print("✅ Correct password verified successfully!")
    else:
        print("❌ Correct password verification failed!")
        return False
    
    # Test wrong password
    print(f"   Testing wrong password...")
    if not auth.verify_password(wrong_password, user['password_hash']):
        print("✅ Wrong password correctly rejected!")
    else:
        print("❌ Wrong password was incorrectly accepted!")
        return False
    
    return True


def view_all_users():
    """Display all users in the database."""
    print("\n👥 Viewing all users in database...")
    try:
        users = database.get_all_users()
        if not users:
            print("   No users found in database.")
        else:
            print(f"   Found {len(users)} user(s):\n")
            for user in users:
                print(f"   ID: {user['id']}")
                print(f"   Email: {user['email']}")
                print(f"   Created at: {user['created_at']}")
                print()
        return True
    except Exception as e:
        print(f"❌ Error retrieving users: {e}")
        return False


def view_database_details():
    """Show database file details."""
    print("\n📊 Database Details:")
    db_path = database.DB_PATH
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"   File: {db_path}")
        print(f"   Size: {size:,} bytes ({size / 1024:.2f} KB)")
        print(f"   Exists: ✅ Yes")
    else:
        print(f"   File: {db_path}")
        print(f"   Exists: ❌ No (will be created on first use)")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🧪 AUTHENTICATION SYSTEM TEST SUITE")
    print("=" * 70)
    
    # Test 1: Database initialization
    print_separator()
    if not test_database_initialization():
        print("\n❌ Database initialization failed. Cannot continue.")
        return
    
    # Show database details
    view_database_details()
    
    # Test 2: User creation
    print_separator()
    test_user_creation()
    
    # Test 3: Password verification
    print_separator()
    test_password_verification()
    
    # Test 4: View all users
    print_separator()
    view_all_users()
    
    # Final summary
    print_separator()
    print("✨ Test suite completed!")
    print("\n💡 Tips:")
    print("   - You can run this script multiple times to test different scenarios")
    print("   - The database file is located at:", database.DB_PATH)
    print("   - You can also inspect the database using SQLite tools:")
    print("     sqlite3 users.db \"SELECT * FROM users;\"")
    print_separator()


if __name__ == "__main__":
    main()


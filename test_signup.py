"""
Test script to simulate a signup request and verify database updates.
This helps debug why signups through the web interface might not be working.
"""
import sys
from pathlib import Path

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules import database, auth


def test_signup_flow():
    """Simulate the signup flow exactly as the Flask app does."""
    print("\n" + "=" * 70)
    print("🧪 TESTING SIGNUP FLOW (Simulating Flask App)")
    print("=" * 70 + "\n")
    
    # Initialize database
    print("1️⃣ Initializing database...")
    database.init_db()
    print(f"   ✅ Database initialized at: {database.DB_PATH}")
    print(f"   ✅ Database exists: {database.DB_PATH.exists()}\n")
    
    # Simulate signup form submission
    test_email = "newuser@test.com"
    test_password = "MySecurePassword123!"
    
    print(f"2️⃣ Simulating signup for: {test_email}")
    print(f"   Password: {test_password}\n")
    
    # Step 1: Check if user exists (as Flask app does)
    print("3️⃣ Checking if user already exists...")
    existing_user = database.get_user_by_email(test_email)
    if existing_user:
        print(f"   ⚠️  User already exists: {existing_user}")
        print("   (This is expected if you've run this test before)\n")
    else:
        print("   ✅ User does not exist, proceeding with signup...\n")
    
    # Step 2: Hash password (as Flask app does)
    print("4️⃣ Hashing password with bcrypt...")
    password_hash = auth.hash_password(test_password)
    password_hash_str = password_hash.decode('utf-8')
    print(f"   ✅ Password hashed: {password_hash_str[:50]}...\n")
    
    # Step 3: Create user (as Flask app does)
    print("5️⃣ Creating user in database...")
    try:
        user = database.create_user(test_email, password_hash_str)
        if user:
            print(f"   ✅ User created successfully!")
            print(f"      ID: {user['id']}")
            print(f"      Email: {user['email']}")
            print(f"      Created at: {user['created_at']}\n")
        else:
            print("   ❌ User creation returned None\n")
            return False
    except Exception as e:
        print(f"   ❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Verify user was saved
    print("6️⃣ Verifying user was saved to database...")
    saved_user = database.get_user_by_email(test_email)
    if saved_user:
        print(f"   ✅ User found in database!")
        print(f"      ID: {saved_user['id']}")
        print(f"      Email: {saved_user['email']}\n")
    else:
        print("   ❌ User NOT found in database after creation!\n")
        return False
    
    # Step 5: Test password verification
    print("7️⃣ Testing password verification...")
    if auth.verify_password(test_password, saved_user['password_hash']):
        print("   ✅ Password verification successful!\n")
    else:
        print("   ❌ Password verification failed!\n")
        return False
    
    # Step 6: Show all users
    print("8️⃣ Current users in database:")
    all_users = database.get_all_users()
    print(f"   Total users: {len(all_users)}")
    for u in all_users:
        print(f"      - {u['email']} (ID: {u['id']})")
    
    print("\n" + "=" * 70)
    print("✅ SIGNUP FLOW TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    test_signup_flow()


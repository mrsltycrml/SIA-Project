"""
Check where the database is being created and if there are multiple database files.
This helps diagnose if the Flask app is using a different database path.
"""
import sys
from pathlib import Path
import os

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules import database

print("\n" + "=" * 70)
print("🔍 DATABASE PATH DIAGNOSTIC")
print("=" * 70 + "\n")

# Show the database path from the module
print("1️⃣ Database path from module:")
print(f"   {database.DB_PATH}")
print(f"   Exists: {database.DB_PATH.exists()}")
print(f"   Absolute: {database.DB_PATH.resolve()}\n")

# Check if there are other .db files
print("2️⃣ Searching for other database files in project...")
db_files = list(Path(PROJECT_ROOT).glob("*.db"))
if db_files:
    print(f"   Found {len(db_files)} .db file(s):")
    for db_file in db_files:
        size = db_file.stat().st_size if db_file.exists() else 0
        print(f"      - {db_file.name} ({size:,} bytes)")
else:
    print("   No .db files found in project root")

# Check in api folder
api_db_files = list(Path(PROJECT_ROOT / "api").glob("*.db"))
if api_db_files:
    print(f"\n   Found {len(api_db_files)} .db file(s) in api folder:")
    for db_file in api_db_files:
        size = db_file.stat().st_size if db_file.exists() else 0
        print(f"      - {db_file.name} ({size:,} bytes)")

# Show current working directory
print(f"\n3️⃣ Current working directory:")
print(f"   {os.getcwd()}\n")

# Show project root
print(f"4️⃣ Project root (from module):")
print(f"   {database.PROJECT_ROOT}\n")

# Test database connection
print("5️⃣ Testing database connection...")
try:
    database.init_db()
    users = database.get_all_users()
    print(f"   ✅ Database connection successful!")
    print(f"   ✅ Found {len(users)} user(s) in database")
    for user in users:
        print(f"      - {user['email']} (ID: {user['id']})")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70 + "\n")


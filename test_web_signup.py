"""
Test script to simulate a web signup request.
This helps verify that the signup endpoint is working correctly.
"""
import requests
import sys
from pathlib import Path

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules import database, auth


def test_web_signup():
    """Test signup by making an HTTP request to the Flask app."""
    print("\n" + "=" * 70)
    print("🌐 TESTING WEB SIGNUP (HTTP Request)")
    print("=" * 70 + "\n")
    
    # Check if Flask app is running
    base_url = "http://localhost:5000"
    
    print("1️⃣ Checking if Flask app is running...")
    try:
        response = requests.get(f"{base_url}/", timeout=2)
        print(f"   ✅ Flask app is running (Status: {response.status_code})\n")
    except requests.exceptions.ConnectionError:
        print("   ❌ Flask app is not running!")
        print("   💡 Please start your Flask app first:")
        print("      - If using IDE debug mode, make sure it's running")
        print("      - Or run: python api/app.py\n")
        return False
    except Exception as e:
        print(f"   ❌ Error connecting: {e}\n")
        return False
    
    # Show current users
    print("2️⃣ Current users in database:")
    current_users = database.get_all_users()
    print(f"   Total: {len(current_users)}")
    for u in current_users:
        print(f"      - {u['email']} (ID: {u['id']})")
    print()
    
    # Test signup
    test_email = "webuser@test.com"
    test_password = "WebTestPassword123!"
    
    print(f"3️⃣ Attempting signup via web interface...")
    print(f"   Email: {test_email}")
    print(f"   Password: {test_password}\n")
    
    try:
        # Make POST request to signup endpoint
        signup_data = {
            "email": test_email,
            "password": test_password
        }
        
        response = requests.post(
            f"{base_url}/signup",
            data=signup_data,
            allow_redirects=False,
            timeout=5
        )
        
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}\n")
        
        if response.status_code == 302:  # Redirect (success)
            location = response.headers.get('Location', '')
            if 'login' in location:
                print("   ✅ Signup appears successful (redirected to login)\n")
            else:
                print(f"   ⚠️  Redirected to: {location}\n")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}\n")
            print(f"   Response content (first 500 chars):")
            print(f"   {response.text[:500]}\n")
    
    except Exception as e:
        print(f"   ❌ Error making request: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # Check database again
    print("4️⃣ Checking database after signup...")
    updated_users = database.get_all_users()
    print(f"   Total users now: {len(updated_users)}")
    
    new_user = database.get_user_by_email(test_email)
    if new_user:
        print(f"   ✅ New user found in database!")
        print(f"      ID: {new_user['id']}")
        print(f"      Email: {new_user['email']}")
        print(f"      Created at: {new_user['created_at']}\n")
    else:
        print(f"   ❌ New user NOT found in database!\n")
        print("   All users:")
        for u in updated_users:
            print(f"      - {u['email']} (ID: {u['id']})")
        print()
        return False
    
    print("=" * 70)
    print("✅ WEB SIGNUP TEST COMPLETED!")
    print("=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        test_web_signup()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


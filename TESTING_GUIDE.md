# Testing Authentication System - Step by Step Guide

## Issue: Database showing test email instead of your signup email

### Step 1: Make sure Flask app is running with latest code

1. **Stop your Flask app** if it's currently running (Ctrl+C in the terminal)

2. **Restart the Flask app** to load the new debug logging:
   ```powershell
   python api/app.py
   ```

3. You should see output like:
   ```
   * Running on http://0.0.0.0:5000
   ```

### Step 2: Test Signup

1. **Open your browser** and go to: `http://localhost:5000/signup`

2. **Fill out the form** with:
   - Email: `yourname@example.com` (use a NEW email, not one that exists)
   - Password: `YourPassword123!`

3. **Click "Create account"**

4. **Watch the Flask console** - you should see debug output like:
   ```
   [DEBUG] Signup form submitted
   [DEBUG] Form data: {'email': 'yourname@example.com', 'password': 'YourPassword123!'}
   [DEBUG] Processed email: 'yourname@example.com'
   [DEBUG] Password length: 17
   [DEBUG] Hashing password for: yourname@example.com
   [DEBUG] Creating user in database: yourname@example.com
   [DEBUG] User created successfully! ID: 3, Email: yourname@example.com
   ```

### Step 3: Verify the Database

**Option A: Use the view script**
```powershell
python view_database.py
```

**Option B: Visit the debug endpoint**
Go to: `http://localhost:5000/debug/db`

You should see your new user in the list!

### Step 4: If it's still not working

Check the Flask console output for:
- What email is being received
- Any error messages
- Whether the user creation is actually happening

**Common Issues:**

1. **"User already exists"** - You're trying to sign up with an email that's already in the database
   - Solution: Use a different email or check existing users first

2. **No debug output** - The form might not be submitting
   - Check browser console for JavaScript errors
   - Make sure you're clicking the submit button

3. **Error messages in console** - There might be a database or code error
   - Share the error message for help

### Step 5: Check Current Users

Before signing up, check what users already exist:
```powershell
python view_database.py
```

This will show you all existing users so you can use a new email.

---

## Quick Commands Reference

- **View database**: `python view_database.py`
- **Test signup flow**: `python test_signup.py`
- **Check database path**: `python check_database_path.py`
- **Debug endpoint**: Visit `http://localhost:5000/debug/db` in browser


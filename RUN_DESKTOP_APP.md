# Running Desktop App from Terminal

## Quick Start

To run the desktop application from the terminal:

```powershell
python desktop_app.py
```

## What Changed

The desktop app now uses the **same SQLite database** as the Flask web app:
- ✅ Users created in the desktop app are saved to `users.db`
- ✅ Users created in the web app can login to the desktop app
- ✅ Uses bcrypt for secure password hashing (same as web app)
- ✅ All authentication is now persistent and shared between web and desktop

## Testing

1. **Run the desktop app:**
   ```powershell
   python desktop_app.py
   ```

2. **Sign up a new user** in the desktop app

3. **Check the database:**
   ```powershell
   python view_database.py
   ```

4. **Try logging in** with the same credentials in:
   - The desktop app
   - The web app at `http://localhost:5000/login`

Both should work with the same credentials!

## Troubleshooting

If you get an error about missing modules:
```powershell
pip install -r requirements.txt
```

If the app doesn't start, check that PyQt5 is installed:
```powershell
pip install PyQt5 PyQtWebEngine
```


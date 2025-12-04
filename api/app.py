import os
import sys
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from dotenv import load_dotenv

# Ensure the project root (which contains the `modules` package) is on sys.path,
# regardless of whether this file is run from the project root or from the `api` folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules import music, videos, games, database, auth

load_dotenv()

app = Flask(__name__, static_folder="../static", template_folder="../templates")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize database and create users table if it doesn't exist
database.init_db()

# Simple helper
def current_user():
    return session.get("user")

@app.route("/")
def index():
    user = current_user()
    return render_template("index.html", user=user)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Debug: Print form data
        print(f"\n[DEBUG] Signup form submitted", flush=True)
        print(f"[DEBUG] Form data: {dict(request.form)}", flush=True)
        
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        print(f"[DEBUG] Processed email: '{email}'", flush=True)
        print(f"[DEBUG] Password length: {len(password)}", flush=True)
        
        # Validate input
        if not email or not password:
            print(f"[DEBUG] Validation failed: email={bool(email)}, password={bool(password)}", flush=True)
            flash("Email and password are required", "danger")
            return render_template("signup.html")
        
        # Check if user already exists
        existing_user = database.get_user_by_email(email)
        if existing_user:
            print(f"[DEBUG] User already exists: {email}", flush=True)
            flash("User already exists", "danger")
            return render_template("signup.html")
        
        # Hash password using bcrypt
        print(f"[DEBUG] Hashing password for: {email}", flush=True)
        password_hash = auth.hash_password(password)
        
        # Store password hash as string (SQLite TEXT type)
        password_hash_str = password_hash.decode('utf-8')
        
        try:
            # Create user in database
            print(f"[DEBUG] Creating user in database: {email}", flush=True)
            user = database.create_user(email, password_hash_str)
            if user:
                print(f"[DEBUG] User created successfully! ID: {user['id']}, Email: {user['email']}", flush=True)
                flash("Signup successful. You can now log in.", "success")
                return redirect(url_for("login"))
            else:
                print(f"[DEBUG] User creation returned None", flush=True)
                flash("Error creating account. Please try again.", "danger")
        except sqlite3.IntegrityError as e:
            print(f"[DEBUG] IntegrityError: {e}", flush=True)
            flash("User already exists", "danger")
        except Exception as e:
            # Log the error for debugging (in production, use proper logging)
            print(f"[DEBUG] Error creating user: {e}", flush=True)
            import traceback
            traceback.print_exc()
            flash(f"Error creating account: {str(e)}", "danger")
    
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        
        # Validate input
        if not email or not password:
            flash("Email and password are required", "danger")
            return render_template("login.html")
        
        # Query database for user
        user = database.get_user_by_email(email)
        
        if not user:
            flash("Invalid email or password", "danger")
            return render_template("login.html")
        
        # Verify password against stored hash
        password_hash = user["password_hash"]
        if auth.verify_password(password, password_hash):
            session["user"] = {"email": user["email"], "id": user["id"]}
            flash("Logged in successfully", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)

@app.route("/music")
def music_page():
    user = current_user()
    q = request.args.get("q", "")
    results = []
    if q:
        results = music.search_tracks(q)
    return render_template("music.html", user=user, query=q, results=results)

@app.route("/videos")
def videos_page():
    user = current_user()
    q = request.args.get("q", "")
    watch_id = request.args.get("watch")

    # Get the catalog of movies (optionally filtered by search query)
    results = videos.search_videos(q)

    # Choose the movie to play
    selected = None
    if watch_id:
        selected = next((m for m in results if m["id"] == watch_id), None)
    if not selected and results:
        selected = results[0]

    return render_template(
        "videos.html", user=user, query=q, results=results, selected=selected
    )

@app.route("/games")
def games_page():
    user = current_user()
    games_list = games.list_games()
    return render_template("games.html", user=user, games=games_list)

@app.route("/game/<slug>")
def play_game(slug):
    user = current_user()
    game = games.get_game(slug)
    if not game:
        flash("Game not found", "danger")
        return redirect(url_for("games_page"))
    return render_template("play_game.html", user=user, game=game)

@app.route("/debug/db")
def debug_db():
    """Debug endpoint to view database status (remove in production)."""
    try:
        users = database.get_all_users()
        db_path = database.DB_PATH
        
        # Format users table
        users_html = ""
        if users:
            users_html = "<table border='1' cellpadding='10' style='border-collapse: collapse; margin: 20px 0;'>"
            users_html += "<tr><th>ID</th><th>Email</th><th>Created At</th></tr>"
            for u in users:
                users_html += f"<tr><td>{u['id']}</td><td>{u['email']}</td><td>{u['created_at']}</td></tr>"
            users_html += "</table>"
        else:
            users_html = "<p><em>No users found in database.</em></p>"
        
        return f"""
        <html>
        <head>
            <title>Database Debug Info</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h2 {{ color: #333; }}
                table {{ width: 100%; }}
                th {{ background: #4CAF50; color: white; text-align: left; }}
                tr:nth-child(even) {{ background: #f2f2f2; }}
                .info {{ background: #e7f3ff; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; }}
                a {{ color: #2196F3; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📊 Database Debug Info</h2>
                
                <div class="info">
                    <p><strong>Database Path:</strong> {db_path}</p>
                    <p><strong>Database Exists:</strong> {db_path.exists()}</p>
                    <p><strong>Database Size:</strong> {db_path.stat().st_size if db_path.exists() else 0:,} bytes</p>
                    <p><strong>Total Users:</strong> {len(users)}</p>
                </div>
                
                <h3>👥 Users in Database:</h3>
                {users_html}
                
                <p style="margin-top: 30px;">
                    <a href="/signup">➡️ Try Signup</a> | 
                    <a href="/login">➡️ Try Login</a> | 
                    <a href="/">➡️ Back to Home</a> |
                    <a href="/debug/db">🔄 Refresh</a>
                </p>
                
                <div class="info" style="margin-top: 30px;">
                    <p><strong>💡 Tip:</strong> After signing up, refresh this page to see your new user appear in the database!</p>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return f"""
        <html>
        <body style="font-family: Arial; margin: 40px;">
            <h2 style="color: red;">❌ Error</h2>
            <p><strong>Error:</strong> {str(e)}</p>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px;">{error_trace}</pre>
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
        """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)



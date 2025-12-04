import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from modules import music, videos, games
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# Simple in-memory user store for development (email -> password_hash)
USERS = {}

app = Flask(__name__, static_folder="../static", template_folder="../templates")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
        email = request.form["email"]
        password = request.form["password"]
        if email in USERS:
            flash("User already exists", "danger")
        else:
            USERS[email] = generate_password_hash(password)
            flash("Signup successful. You can now log in.", "success")
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        pw_hash = USERS.get(email)
        if not pw_hash or not check_password_hash(pw_hash, password):
            flash("Invalid email or password", "danger")
        else:
            session["user"] = {"email": email}
            flash("Logged in", "success")
            return redirect(url_for("dashboard"))
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
    results = []
    if q:
        results = videos.search_videos(q)
    return render_template("videos.html", user=user, query=q, results=results)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)



import requests
from sqlalchemy import create_engine, select

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
# from datetime import datetime

from helpers import login_required, apology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLAlchemy Library to use SQLite database
engine = create_engine("sqlite:///beautygifts.db", echo=True)

@app.route("/")
@login_required
def index():
    """Show home page"""

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        result = engine.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if not result:
            return apology("Invalid username", 403)
        else:
            for row in result:
                if check_password_hash(row['hash'], request.form.get("password")):
                    session["user_id"] = row["id"]

                    # Redirect user to home page
                    return redirect("/")
                
            return apology("invalid password", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("You must provide a Username", 400)
        if not password:
            return apology("You must provide a Password", 400)
        if not confirmation:
            return apology("You must repeat your password", 400)
        if password != confirmation:
            return apology("Your passwords did not match", 400)

        engine.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=generate_password_hash(password))
        return redirect("/login")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/about_us")
@login_required
def about_us():
    """Show about_us page"""
    return render_template("about_us.html")


@app.route("/eat_healthy")
@login_required
def eat_healthy():
    """Select and show recipes from Edamam API"""
    response = requests.get("https://api.edamam.com/search?q=chicken&app_id=a8f807ca&app_key=9e763f1edd4c3c936eb2506f1dbdddf5&calories=591-722&health=alcohol-free")
    if response.status_code == 200:
        hits = response.json()["hits"]
    else:
        hits = []

    return render_template("eat_healthy.html", hits=hits)


@app.route("/get_toned")
@login_required
def get_toned():
    """Show get_toned page"""
    return render_template("get_toned.html")

@app.route("/manage_weight")
@login_required
def manage_weight():
    """Show manage_weight page"""
    return render_template("manage_weight.html")

@app.route("/contact_us")
@login_required
def contact_us():
    """Show contact page"""
    return render_template("contact_us.html")
import requests
from sqlalchemy import create_engine, select

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

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

# My functions
def rounded(r):
    return round(r)

@app.route("/")
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
def about_us():
    """Show about_us page"""
    return render_template("about_us.html")


@app.route("/eat_healthy", methods=["GET", "POST"])
@login_required
def eat_healthy():
    """Select and show recipes from Edamam API"""
    if request.method == "GET":
        search_word = "chicken"
    else:
        search_word = request.form.get("search_word")

    response = requests.get("https://api.edamam.com/search?q=" + search_word + "&app_id=a8f807ca&app_key=9e763f1edd4c3c936eb2506f1dbdddf5&from=0&to=12&calories=591-722")
    
    if response.status_code == 200:
        hits = response.json()["hits"]
        count = response.json()["count"]
    else:
        hits = []
        count = 0
        
    return render_template("eat_healthy.html", hits=hits, count=count, round=rounded, search_word=search_word)


@app.route("/get_toned")
@login_required
def get_toned():
    """Show get_toned page"""
    return render_template("get_toned.html")

@app.route("/manage_weight", methods=["GET", "POST"])
@login_required
def manage_weight():
    """Show manage_weight page"""
    if request.method == "GET":
        tdee = ''
        return render_template("manage_weight.html", tdee=tdee, weight="0", height="0", age="0")
    else:
        gender = request.form.get("gender")
        weight = request.form.get("weight")
        height = request.form.get("height")
        age = request.form.get("age")
        activity = request.form.get("activity")
        session['currentWeight'] = weight
        session['height'] = height

        # Calculate the Mifflin-St. Jeor equation:
        caloriesPerDay = 10 * float(weight) + 6.25 * float(height) - 5 * float(age) + float(gender)

        # Calculates the TDEE:
        tdee = round(float(caloriesPerDay) * float(activity))
        return render_template("manage_weight.html", _anchor="dietaryNeedsContainer", tdee=tdee, weight=weight, height=height, age=age)

@app.route("/manage_weight/macronutrients", methods=["POST"])
@login_required
def macronutrients():
    """Handles the submit of the second form in manage_weight page"""
    action = request.form.get("action")
    desiredWeight = request.form.get("desiredWeight")
    currentWeight = session['currentWeight']
    height = session['height']

    print(action)
    print(desiredWeight)
    print(currentWeight)
    print(height)

    bmi = round((float(currentWeight) / (float(height)/100)**2), 1)
    print(bmi)

    # if action = ...
    # prot = 0.4 * tdee
    # fat = 30 * tdee
    # carbs = 30 * tdee

    # return redirect(url_for("manage_weight", weight=currentWeight, bmi=bmi) + '#macronutrientSummary') #, prot=prot, fat=fat, carbs=carbs)
    return render_template("manage_weight.html", _anchor="macronutrientSummary", weight=currentWeight, desiredWeight=desiredWeight, bmi=bmi)

@app.route("/contact_us")
def contact_us():
    """Show contact page"""
    return render_template("contact_us.html")
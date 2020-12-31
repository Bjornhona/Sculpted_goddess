import requests
from sqlalchemy import create_engine, select
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import login_required, apology
import uuid
import urllib
import json


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
engine = create_engine("sqlite:///sculptedgoddess.db", echo=True, pool_pre_ping=True)

# Create unique id's
uniqueId = uuid.uuid1()

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
        latestSearchWord = request.args.get("latestSearchWord")

        if latestSearchWord is not None:
            if latestSearchWord == "Saved recipes":
                search_word = latestSearchWord
                hits_str = request.args.get("hits")
                hits = json.loads(hits_str)
                count = request.args.get("count")

                # Check what recipes this user have saved in DB recipes table
                savedResp = engine.execute("SELECT * FROM recipes WHERE user_id=:user_id", user_id=session['user_id']);
                saved = savedResp.fetchall()

                for row in saved:
                    savedId = row[0]

                    for hit in hits:
                        hitId = hit['recipe']['uri']

                        # Adds key value pair in hits
                        if hitId == savedId:
                            hit['saved'] = True

                return render_template("eat_healthy.html", hits=hits, round=rounded, count=count, search_word=search_word)
            else:
                search_word = latestSearchWord;
        else:
            search_word = "chicken"

    else:
        # Search hits from API that matches a search-word the user entered in the Search input field
        search_word = request.form.get("search_word")
    hits = []
    count = 0
    response = None

    try:
        response = requests.get("https://api.edamam.com/search?q=" + search_word + "&app_id=a8f807ca&app_key=9e763f1edd4c3c936eb2506f1dbdddf5&from=0&to=12&calories=591-722")
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error ocurred: {err}")

    if response.status_code == 200:
        responseJSON = response.json()
        hits = responseJSON["hits"]
        count = responseJSON["count"]

    # Check what recipes this user have saved in DB recipes table
    savedResp = engine.execute("SELECT * FROM recipes WHERE user_id=:user_id", user_id=session['user_id']);
    saved = savedResp.fetchall()

    for row in saved:
        savedId = row[0]

        for hit in hits:
            hitId = hit['recipe']['uri']

            # Adds key value pair in hits
            if hitId == savedId:
                hit['saved'] = True

    return render_template("eat_healthy.html", hits=hits, round=rounded, count=count, search_word=search_word)


@app.route('/show_saved_recipes', methods=['GET', 'POST'])
@login_required
def show_saved_recipes():

    hits = []
    recipeCount = 0

    saved_recipes = engine.execute("SELECT * FROM recipes WHERE user_id=:user_id", user_id=session['user_id'])

    if saved_recipes is not None:
        for row in saved_recipes:
            recipeCount += 1

            recipe_id = row.recipe_id

            # Convert the id into a link
            r_id=urllib.parse.quote(recipe_id, safe='')

            # Get data for this recipe from Edamam API
            response = None

            try:
                response = requests.get("https://api.edamam.com/search?r=" + r_id + "&app_id=a8f807ca&app_key=9e763f1edd4c3c936eb2506f1dbdddf5&from=0&to=12&calories=591-722")
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
            except Exception as err:
                print(f"An error ocurred: {err}")

            # Add recipe to hits list
            if response.status_code == 200:
                responseJSON = response.json()
                recVal = {"recipe": responseJSON[0]}
                hits.append(recVal)
    
    hits_str=json.dumps(hits)

    return redirect(url_for('eat_healthy', latestSearchWord="Saved recipes", hits=hits_str, count=recipeCount))


@app.route('/save_recipe', methods=['POST'])
@login_required
def save_recipe():
    """Saves recipes in eat_healthy page by their id"""

    # Get the recipeId
    recipeId = request.form.get("recipeId")
    latestSearchWord = request.form.get("searchWord")

    # Check if already saved in DB recipes table
    isSavedResp = engine.execute("SELECT COUNT(*) FROM recipes WHERE user_id=:user_id AND recipe_id=:recipe_id", user_id=session['user_id'], recipe_id=recipeId);
    isSaved = isSavedResp.fetchall()[0][0]

    # Saves the recipe and search in recipes table in DB if not already saved. Else it is deleted from recipes table.
    if isSaved == 0:
        engine.execute("INSERT INTO recipes(recipe_id, user_id) VALUES(:recipe_id, :user_id)", recipe_id=recipeId, user_id=session['user_id'])
    else:
        engine.execute("DELETE FROM recipes WHERE user_id=:user_id AND recipe_id=:recipe_id", user_id=session['user_id'], recipe_id=recipeId);

    if latestSearchWord == "Saved recipes":
        return redirect(url_for('show_saved_recipes'))
    else:
        return redirect(url_for('eat_healthy', latestSearchWord=latestSearchWord))


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
        return render_template("manage_weight.html")
    else:
        gender = request.form.get("gender")
        weight = request.form.get("weight")
        height = request.form.get("height")
        age = request.form.get("age")
        activity = request.form.get("activity")

        # Save all entered data in session
        session['gender'] = gender
        session['currentWeight'] = weight
        session['height'] = height
        session['age'] = age
        session['activity'] = activity

        # Calculate the Mifflin-St. Jeor equation:
        caloriesPerDay = 10 * float(weight) + 6.25 * float(height) - 5 * float(age) + float(gender)

        # Calculates the TDEE:
        tdee = float(caloriesPerDay) * float(activity)
        session['tdee'] = tdee

        return render_template("manage_weight.html", tdee=round(tdee), weight=weight)


@app.route("/manage_weight/macronutrients", methods=["POST"])
@login_required
def macronutrients():
    """Handles the submit of the second form in manage_weight page"""

    # Import all data
    action = request.form.get("action")
    desiredWeight = request.form.get("desiredWeight")
    currentWeight = session['currentWeight']
    height = session['height']
    tdee = round(session['tdee'])

    # Save action goal and desired weight in session
    session['goal'] = action
    session['desiredWeight'] = desiredWeight

    # Calculate Body Mass Index (BMI) and it's result
    bmi = round((float(currentWeight) / (float(height)/100)**2), 1)

    def getBmiResult():
        if (bmi >= 30.0):
            return "Obese"
        elif (bmi < 30.0 and bmi >= 25.0):
            return "Overweight"
        elif (bmi < 25.0 and bmi >= 18.5):
            return "Normal"
        else:
            return "Underweight"

    bmiResult = getBmiResult()

    # Calculate recommended daily calorie intake depending on goal
    def calcDailyCal():
        if (action == "lose"):
            return tdee - 500
        elif (action == "gain"):
            return tdee + 100
        else:
            return tdee
    
    recommendedCalIntake = calcDailyCal()

    # Calculates 30 day milestone
    if (action == "lose"):
        milestoneWeight = round(float(currentWeight) - (0.453592 / 7 * 30))
    elif (action == "gain"):
        milestoneWeight = round(float(currentWeight) + (0.5))
    else:
        milestoneWeight = currentWeight

    # Calculates Recommended Macronutrients in grams depending on goal
    if (action == "lose"):
        prot = recommendedCalIntake * 0.40 / 4
        fat = recommendedCalIntake * 0.35 / 9
        carbs = recommendedCalIntake * 0.25 / 4
    elif (action == "gain"):
        prot = recommendedCalIntake * 0.25 / 4
        fat = recommendedCalIntake * 0.30 / 9
        carbs = recommendedCalIntake * 0.45 / 4
    else:
        prot = recommendedCalIntake * 0.22 / 4
        fat = recommendedCalIntake * 0.24 / 9
        carbs = recommendedCalIntake * 0.54 / 4

    # Saves macronutrient values in session as cals/day
    session['calInt'] = recommendedCalIntake
    session['calProt'] = prot * 4
    session['calFat'] = fat * 9
    session['calCarbs'] = carbs * 4

    # Calculates the circular progress bars values in vw
    if (action == "lose"):
        calVal = recommendedCalIntake * 100 / tdee
        mlstVal = float(desiredWeight) * 100 / float(currentWeight)
    elif (action == "gain"):
        calVal = tdee * 100 / recommendedCalIntake
        mlstVal = float(currentWeight) * 100 / float(desiredWeight)
    bmiVal = bmi * 100 / 60

    # Calculates the linear progress bars values in percentage
    protVal = prot * 4 * 100 / recommendedCalIntake
    fatVal = fat * 9 * 100 / recommendedCalIntake
    carbsVal = carbs * 4 * 100 / recommendedCalIntake

    return render_template("manage_weight.html", weight=currentWeight, desiredWeight=desiredWeight, 
        bmi=bmi, recommendedCalIntake=recommendedCalIntake, bmiResult=bmiResult, milestoneWeight=milestoneWeight, 
        prot=round(prot, 2), fat=round(fat, 2), carbs=round(carbs, 2), 
        calVal=calVal, mlstVal=mlstVal, bmiVal=bmiVal, 
        carbsVal=carbsVal, protVal=protVal, fatVal=fatVal)


@app.route("/manage_weight/save_macros")
@login_required
def save_macros():
    """Saves macronutrient data of the macro summary calculations in history"""

    # Get todays date and time
    time = datetime.now()

    # Latest Macronutrient data is updated in DB
    new_calInt = session['calInt']
    new_calProt = session['calProt']
    new_calFat = session['calFat']
    new_calCarbs = session['calCarbs']

    engine.execute("INSERT INTO macros (user_id, calInt, calProt, calFat, calCarbs) VALUES (:user_id, :calInt, :calProt, :calFat, :calCarbs) \
        ON CONFLICT(user_id) DO UPDATE SET calInt=:calInt, calProt=:calProt, calFat=:calFat, calCarbs=:calCarbs WHERE user_id=:user_id", \
        user_id=session['user_id'], calInt=new_calInt, calProt=new_calProt, calFat=new_calFat, calCarbs=new_calCarbs)

    # Is added to the history array in DB
    if session['gender'] == "-161":
        gender = "female"
    else:
        gender = "male"

    # Add history data to history table in DB
    engine.execute("INSERT INTO history (data_id, user_id, gender, weight, height, age, activity, goal, desiredWeight, time) \
        VALUES (:data_id, :user_id, :gender, :weight, :height, :age, :activity, :goal, :desiredWeight, :time)", \
        data_id = uniqueId.hex, user_id = session['user_id'], gender = gender, weight = session['currentWeight'], height = session['height'], \
        age = session['age'], activity = session['activity'], goal = session['goal'], desiredWeight = session['desiredWeight'], time = time)

    return redirect("/")


@app.route("/contact_us")
def contact_us():
    """Show contact page"""
    return render_template("contact_us.html")

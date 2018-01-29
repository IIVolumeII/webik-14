from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from pytrivia import Category, Diffculty, Type, Trivia
from random import shuffle

from helpers import *
from user import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    """User homepage and navigation hub"""

    # select username for welcome message
    user = get_user()
    username = user[0]["username"]

    return render_template("index.html", user = username)

@app.route("/config", methods=["GET", "POST"])
@login_required
def config():
    """Configure your game"""

    # show config forms
    return render_template("config.html")

@app.route("/quickplay", methods=["GET", "POST"])
@login_required
def quickplay():
    """Play with completely randomized questions"""

    # set settings for dataset entry
    my_api = Trivia(True)
    response = my_api.request(1, Category.General)
    results = response['results'][0]

    # save config variables
    category = results['category']
    qtype = results['type']
    difficulty = results['difficulty']

    # store questions and answers in variables
    question = results['question']
    correct_answer = results['correct_answer']
    incorrect_answers = results['incorrect_answers']

    # insert data into portfolio for respective questiontypes
    if qtype == 'multiple':
        answers = [correct_answer, incorrect_answers[0], incorrect_answers[1], incorrect_answers[2]]
        shuffle(answers)

        asked = db.execute("INSERT INTO portfolio (id, answer, category, qtype, difficulty) \
                            VALUES(:id, :answers, :category, :qtype, :difficulty)", \
                            answers = correct_answer, category = category, qtype = qtype, \
                            difficulty = difficulty, id=session["user_id"])

        # display trivia question multiple choice
        return render_template("play.html", question = question, answer = answers, category = category,
                                qtype = qtype, difficulty = difficulty)
    else:
        answers = [correct_answer, incorrect_answers]

        asked = db.execute("INSERT INTO portfolio (id, answer, category, qtype, difficulty) \
                            VALUES(:id, :answers, :category, :qtype, :difficulty)", \
                            answers = answers[0], category = category, qtype = qtype, \
                            difficulty = difficulty, id=session["user_id"] )

        # display trivia question true or false
        return render_template("playbool.html", question = question, answer = answers, category = category,
                                qtype = qtype, difficulty = difficulty)

@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    """Play the trivia game with configured settings"""

    # check if correct answer
    try:
        user_answer = request.form.get("answer")
        score(user_answer)
    except:
        pass

    # initial user config for first question
    try:
        cat = request.form.get("category")
        dif = request.form.get("difficulty")
        questiontype = request.form.get("qtype")
        qnumber = int(request.form.get("qnumber"))

    # retrieve initial user config for other questions
    except TypeError:
        config = qinit()
        qnumber = config[3]
        cat = config[0]
        dif = config[1]
        questiontype = config[2]

    # set settings for dataset entry
    my_api = Trivia(True)
    try:
        response = my_api.request(qnumber, getattr(Category,cat), getattr(Diffculty,dif),
                                    getattr(Type,questiontype))
    # delete data from portfolio and return user to scoreboard if out of questions
    except ValueError:
        quit = outofq()
        return render_template("scoreboard.html", score = user_answer)

    # store question config
    results = response['results'][qnumber - 1]
    qtype = results['type']
    category = results['category']
    qtype = results['type']
    difficulty = results['difficulty']

    # store questions and answers in variables
    question = results['question']
    correct_answer = results['correct_answer']
    incorrect_answers = results['incorrect_answers']

    # insert data into portfolio for respective questiontypes
    if qtype == 'multiple':
        answers = [correct_answer, incorrect_answers[0], incorrect_answers[1], incorrect_answers[2]]
        shuffle(answers)
        sconfigmulti(answers, cat, questiontype, dif, qnumber, correct_answer)

        # display trivia question multiple choice
        return render_template("play.html", question = question, answer = answers, category = category,
                                qtype = qtype, difficulty = difficulty)

    else:
        answers = [correct_answer, incorrect_answers]
        sconfigtf(answers, cat, questiontype, dif, qnumber, correct_answer)

        # display trivia question true or false
        return render_template("playbool.html", question = question, answer = answers, category = category,
                                qtype = qtype, difficulty = difficulty)


@app.route("/scoreboard", methods=["GET", "POST"])
@login_required
def scoreboard():
    """Scoreboard for users"""

    return render_template("scoreboard.html")

@app.route("/learnmore", methods=["GET", "POST"])
@login_required
def learnmore():
    """Text page with info about the game."""

    return render_template("learnmore.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("Please provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("Please provide password")

        # query database for username
        row = rows()

        # ensure username exists and password is correct
        if len(row) != 1 or not pwd_context.verify(request.form.get("password"), row[0]["hash"]):
            return apology("Invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = row[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # ensure username is submitted
    if not request.form.get("username"):
        return apology("Please provide a username")

    # ensure passwords are submitted and match
    if not request.form.get("password"):
        return apology("Please provide a password")
    if not request.form.get("password2"):
        return apology("Please fill in both password fields")
    if not request.form.get("password") == request.form.get("password2"):
        return apology("Please make sure your passwords match")

    # add user to database and store password as hash
    registered = new_user()

    # check if the username is already taken
    if not registered:
        return apology("Username is already taken. Please fill in a different username")

    # redirect user to home page
    return redirect(url_for("index"))



@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Profile for users"""

    return render_template("profile.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Changes password of user in session."""
    if request.method == "POST":

        # ensure password matches old password
        old_hash = old_hash()
        check_hash = check_hash()
        new_pass = request.form.get("new_password")

        # ensure new passwords match and all fields are filled in
        if not pwd_context.verify(request.form.get("old_password"), old_hash[0]["hash"]):
            return apology(check_hash)
        else:
            if not new_pass:
                return apology("Please provide a password")
            if not request.form.get("new_password2"):
                return apology("Please fill in both password fields")
            if not new_pass == request.form.get("new_password2"):
                return apology("Please make sure your passwords match")

        # update users' password
        update_pass()

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")

@app.route("/leaderboards", methods=["GET"])
def leaderboards():
    return render_template("leaderboards.html")
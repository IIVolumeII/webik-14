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
    user = username()

    return render_template("index.html", user = user)

@app.route("/config", methods=["GET", "POST"])
@login_required
def config():
    """Configure your game"""

    # delete previous session and show config forms
    delsession()
    return render_template("config.html")

@app.route("/quickplay", methods=["GET", "POST"])
@login_required
def quickplay():
    """Play with completely randomized questions"""

   # check if correct answer
    try:
        user_answer = request.form.get("answer")
        score(user_answer)
    # pass checking for the first question
    except:
        pass

    # insert user id for new players
    try:
        session_score()
    except:
        pass

    # set settings for dataset entry
    my_api = Trivia(True)

    # retrieve question
    response = my_api.request(1)


    # store question config
    results = response['results'][0]
    qtype = results['type']
    category = results['category']
    qtype = results['type']
    difficulty = results['difficulty']
    qnumber = 10000

    # store questions and answers in variables
    question = results['question']
    correct_answer = results['correct_answer']
    incorrect_answers = results['incorrect_answers']

    # insert data into portfolio for respective questiontypes
    if qtype == 'multiple':
        answers = [correct_answer, incorrect_answers[0], incorrect_answers[1], incorrect_answers[2]]
        shuffle(answers)
        sconfigmulti(answers, category, qtype, difficulty, qnumber, correct_answer)

        # display trivia question multiple choice
        return render_template("qplay.html", question = question, answer = answers, category = category,
                                qtype = qtype, difficulty = difficulty)

    else:
        answers = [correct_answer, incorrect_answers]
        sconfigtf(answers, category, qtype, difficulty, qnumber, correct_answer)

        # display trivia question true or false
        return render_template("qplaybool.html", question = question, answer = answers, category = category,
                                qtype = qtype, difficulty = difficulty)

@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    """Play the trivia game with configured settings"""


    # check if correct answer
    try:
        user_answer = request.form.get("answer")
        score(user_answer)
    # pass checking for the first question
    except:
        pass

    # initial user config for first question
    try:
        cat = request.form.get("category")
        dif = request.form.get("difficulty")
        questiontype = request.form.get("qtype")
        qnumber = int(request.form.get("qnumber"))

        # insert user id for new players
        session_score()

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
        return render_template("scoreboard.html", total_score = quit[0][0]["total_score"], \
                                session_score = quit[1][0]["session_score"])

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
    quick = q_score()
    quit = outofq()
    reset_score()
    return render_template("scoreboard.html", total_score = quit[0][0]["total_score"], \
                                session_score = quick)

@app.route("/learnmore", methods=["GET", "POST"])
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

        # login user
        username = request.form.get("username")
        login_user(username)

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

    if request.method == "POST":

        # ensure username is submitted
        if not request.form.get("username"):
            return apology("Please provide a username")

        # insert new user in database if forms are correct
        registered = new_user()

        # check if the username is already taken
        if not registered:
            return apology("Username is already taken. Please fill in a different username")

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Profile for users"""

    # select username for welcome message
    user = username()

    # select last session score and total score
    score = outofq()

    return render_template("profile.html", user = user, t_score = score[0][0]["total_score"], \
                            s_score = score[1][0]["session_score"])


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Changes password of user in session."""
    if request.method == "POST":

        # ensure password matches old password
        old_hash = get_hash()
        check_hash = pwd_context.verify(request.form.get("old_password"), old_hash[0]["hash"])
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
        update_pass(new_pass)

        return succes("Succesfully changed your password")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")

@app.route("/leaderboards", methods=["GET"])
def leaderboards():

    # lookup top 5 scores
    top = leaders()
    one = top[0][0]["total_score"]
    two = top[0][1]["total_score"]
    three = top[0][2]["total_score"]
    four = top[0][3]["total_score"]
    five = top[0][4]["total_score"]

    # lookup names associated with top 5 scores
    names = leader_names(top)
    name_1 = names[0][0]["username"]
    name_2 = names[1][0]["username"]
    name_3 = names[2][0]["username"]
    name_4 = names[3][0]["username"]
    name_5 = names[4][0]["username"]

    return render_template("leaderboards.html", score_1 = one, score_2 = two, score_3 = three, \
                            score_4 = four, score_5 = five, name_1 = name_1, name_2 = name_2, \
                            name_3 = name_3, name_4 = name_4, name_5 = name_5)
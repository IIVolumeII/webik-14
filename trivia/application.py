from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from pytrivia import Category, Diffculty, Type, Trivia
from random import shuffle

from helpers import *

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

    # select username for welcome message
    user = db.execute("SELECT username FROM users WHERE id=:id", id=session["user_id"])
    username = user[0]["username"]

    # select all values from the portfolio table
    portfolio = db.execute("SELECT * FROM portfolio WHERE id=:id", id=session["user_id"])

    return render_template("index.html", user = username)

@app.route("/config", methods=["GET", "POST"])
@login_required
def config():


    h = "g"

@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    """Redirect to lobby screen"""


    my_api = Trivia(True)
    response = my_api.request(1, Category.Books)
    results = response['results'][0]

    category = results['category']
    qtype = results['type']
    difficulty = results['difficulty']

    question = results['question']
    correct_answer = results['correct_answer']
    incorrect_answers = results['incorrect_answers']

    if qtype == 'multiple':
        answers = [correct_answer, incorrect_answers[0], incorrect_answers[1], incorrect_answers[2]]
        shuffle(answers)

        asked = db.execute("INSERT INTO portfolio (id, answer, category, qtype, difficulty) \
                            VALUES(:id, :answers, :category, :qtype, :difficulty)", \
                            answers = correct_answer, category = category, qtype = qtype, \
                            difficulty = difficulty, id=session["user_id"])

        return render_template("play.html", question = question, answer = answers, category = category,
                                qtype = qtype, difficulty = difficulty)
    else:
        answers = [correct_answer, incorrect_answers]

        asked = db.execute("INSERT INTO portfolio (id, answer, category, qtype, difficulty) \
                            VALUES(:id, :answers, :category, :qtype, :difficulty)", \
                            answers = answers[0], category = category, qtype = qtype, \
                            difficulty = difficulty, id=session["user_id"] )

        return render_template("playbool.html", question = question, answer = answers, category = category,
                                qtype = qtype, difficulty = difficulty)

@app.route("/scoreboard", methods=["GET", "POST"])
@login_required
def scoreboard():
    """Scoreboard for users"""

    if request.method == "POST":

        # ensure answer
        if not request.form.get("answer"):
            return apology("Please provide an answer")

        answer = request.form.get("answer")

        portfolio = db.execute("SELECT * FROM portfolio WHERE id = :id", id=session["user_id"])


    return render_template("scoreboard.html", answer = portfolio[-1]['answer'])

@app.route("/learnmore", methods=["GET", "POST"])
@login_required
def learnmore():
    """Text page with info about the game."""

    return render_template("learnmore")

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
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("Invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

        # ensure passwords are submitted and match
        if not request.form.get("password"):
            return apology("Please provide a password")
        if not request.form.get("password2"):
            return apology("Please fill in both password fields")
        if not request.form.get("password") == request.form.get("password2"):
            return apology("Please make sure your passwords match")

        # add user to database and store password as hash
        registered = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", \
                                username = request.form.get("username"), \
                                hash = pwd_context.hash(request.form.get("password")))

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

    return render_template("profile.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Changes password of user in session."""
    if request.method == "POST":

        # ensure password matches old password
        old_hash = db.execute("SELECT hash FROM users WHERE id=:id", id=session["user_id"])
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
        db.execute("UPDATE users set hash=:hash WHERE id=:id", \
                    hash=pwd_context.hash(new_pass), id=session["user_id"])

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")

import csv
import urllib.request

from functools import wraps
from pytrivia import Category, Diffculty, Type, Trivia
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp



# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def score(answer, portfolio):
    """Adds points for correct answer"""

    # check if answer is correct
    user_answer = answer
    real_answer = portfolio[-1]["answer"]
    if user_answer == real_answer:
        db.execute("UPDATE users set score=score+1 WHERE id=:id", \
                    id=session["user_id"])

def qinit(portfolio):
    """Initializes all but the first question"""

    cat = portfolio[-1]["category"]
    dif = portfolio[-1]["difficulty"]
    questiontype = portfolio[-1]["qtype"]
    qnumber = int(portfolio[-1]["qnumber"]) - 1
    config = [cat, dif, questiontype, qnumber]
    return (config)

def outofq(portfolio):
    """Checks if out of questions"""

    delete = db.execute("DELETE FROM portfolio WHERE id = :id", id=session["user_id"])
    u_score = db.execute("SELECT score FROM users WHERE id = :id", id=session["user_id"])
    return (u_score)




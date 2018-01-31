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

def succes(message, code=200):
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
    return render_template("succes.html", top=code, bottom=escape(message)), code


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

def score(answer):
    """Adds points for correct answer"""
    # select table
    portfolio = db.execute("SELECT * FROM portfolio WHERE id = :id", id=session["user_id"])

    # check if answer is correct
    user_answer = answer
    real_answer = portfolio[-1]["answer"]
    if user_answer == real_answer:
        db.execute("UPDATE score set total_score=total_score+1 WHERE id=:id", \
                    id=session["user_id"])
        db.execute("UPDATE score set session_score=session_score+1 WHERE id=:id", \
                    id=session["user_id"])

def qinit():
    """Initializes all but the first question"""
    # select table
    portfolio = db.execute("SELECT * FROM portfolio WHERE id = :id", id=session["user_id"])

    # setup question config
    cat = portfolio[-1]["category"]
    dif = portfolio[-1]["difficulty"]
    questiontype = portfolio[-1]["qtype"]
    qnumber = int(portfolio[-1]["qnumber"]) - 1
    config = [cat, dif, questiontype, qnumber]
    return (config)

def outofq():
    """Checks if out of questions"""

    # delete session from portfolio and return total score
    delete_portfolio = db.execute("DELETE FROM portfolio WHERE id = :id", id=session["user_id"])
    u_score = db.execute("SELECT total_score FROM score WHERE id = :id", id=session["user_id"])
    s_score = db.execute("SELECT session_score FROM score WHERE id = :id", id=session["user_id"])
    return [u_score, s_score]

def sconfigmulti(answers, cat, questiontype, dif, qnumber, correct_answer):
    # insert data into portfolio for respective questiontypes
    asked = db.execute("INSERT INTO portfolio (id, answer, category, qtype, difficulty, qnumber) \
                        VALUES(:id, :answers, :category, :qtype, :difficulty, :qnumber)", \
                        answers = correct_answer, category = cat, qtype = questiontype, \
                        difficulty = dif, qnumber = qnumber, id=session["user_id"])

def sconfigtf(answers, cat, questiontype, dif, qnumber, correct_answer):
    # insert data into portfolio for respective questiontypes
    asked = db.execute("INSERT INTO portfolio (id, answer, category, qtype, difficulty, qnumber) \
                        VALUES(:id, :answers, :category, :qtype, :difficulty, :qnumber)", \
                        answers = correct_answer, category = cat, qtype =questiontype, \
                        difficulty = dif, qnumber = qnumber, id=session["user_id"] )

def delsession():
    # delete session from portfolio
    db.execute("DELETE FROM portfolio WHERE id = :id", id=session["user_id"])

def session_score():
    # set user id into score table
    score = db.execute("INSERT INTO score (id) VALUES (:id)", id=session["user_id"])

def q_score():
    # return session score
    score = db.execute("SELECT session_score FROM score WHERE id = :id", id=session["user_id"])
    return score[0]["session_score"]

def reset_score():
    # reset session score
    db.execute("UPDATE score set session_score=0 WHERE id=:id", \
                id=session["user_id"])

def leaders():
    one = db.execute("SELECT * FROM score ORDER BY total_score DESC LIMIT 0, 5")
    two = db.execute("SELECT * FROM score ORDER BY total_score DESC LIMIT 0, 5")
    three = db.execute("SELECT * FROM score ORDER BY total_score DESC LIMIT 0, 5")
    four = db.execute("SELECT * FROM score ORDER BY total_score DESC LIMIT 0, 5")
    five = db.execute("SELECT * FROM score ORDER BY total_score DESC LIMIT 0, 5")

    return [one, two, three, four, five]

def leader_names(top):
    row_1 = top[1][0]["id"]
    row_2 = top[1][1]["id"]
    row_3 = top[1][2]["id"]
    row_4 = top[1][3]["id"]
    row_5 = top[1][4]["id"]

    name_1 = db.execute("SELECT username FROM users WHERE id = :id", id=row_1)
    name_2 = db.execute("SELECT username FROM users WHERE id = :id", id=row_2)
    name_3 = db.execute("SELECT username FROM users WHERE id = :id", id=row_3)
    name_4 = db.execute("SELECT username FROM users WHERE id = :id", id=row_4)
    name_5 = db.execute("SELECT username FROM users WHERE id = :id", id=row_5)

    return [name_1, name_2, name_3, name_4, name_5]

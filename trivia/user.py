from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from pytrivia import Category, Diffculty, Type, Trivia
from random import shuffle

from helpers import *


db = SQL("sqlite:///finance.db")

def new_user():

    # add user to database and store password as hash
    registered = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", \
                            username = request.form.get("username"), \
                            hash = pwd_context.hash(request.form.get("password")))

    return registered

def username():
    # select username in session
    user = db.execute("SELECT username FROM users WHERE id = :id", id=session["user_id"])
    username = user[0]["username"]
    return username

def login_user(username):

    # query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

    # ensure username exists and password is correct
    if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
        return apology("Invalid username and/or password")

    # remember which user has logged in
    session["user_id"] = rows[0]["id"]

def get_hash():
    # retrieve hash from database
    user_hash = db.execute("SELECT hash FROM users WHERE id=:id", id=session["user_id"])
    return user_hash
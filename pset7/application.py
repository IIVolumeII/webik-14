from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

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

# custom filter
app.jinja_env.filters["usd"] = usd

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

    # select cash from users table and convert to usd
    cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
    cash_usd = usd(cash[0]["cash"])

    # select and sum total from the portfolio table
    total = db.execute("SELECT SUM(total) FROM portfolio WHERE id=:id", id=session["user_id"])

    # sum cash and stock value to create a grand total
    try:
        grand_total = usd(total[0]["SUM(total)"] + cash[0]["cash"])
    except TypeError:
        grand_total = cash_usd

    return render_template("index.html", user = username, stocks = portfolio, \
                            cash = cash_usd, grand_total = grand_total)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""

    if request.method == "POST":

        # ensure amount of shares are filled in as a positive integer
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Please fill in a symbol with a positive integer")

        if shares <= 0:
            return apology("Please fill in a symbol with a positive integer")

        # ensure symbol is filled in correctly and save symbol as variable
        try:
            stock = lookup(request.form.get("symbol"))
        except:
            return apology("Please fill in both fields")
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("We could not provide information on the given symbol")

        # check if the user can afford the stock if not, send apology
        affordance = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
        affordance = float(affordance[0]['cash'])

        if not affordance > (shares * stock['price']):
            return apology("You do not have enough funds")

        # if affordable check if the user already owns the stock
        else:
            owned = db.execute("SELECT quantity FROM portfolio \
                           WHERE id = :id AND symbol=:symbol", \
                           id=session["user_id"], symbol=symbol)
            plus_total = shares*stock["price"]

            # if user doesn't own the stock create a new row for the stock
            if not owned:
                db.execute("INSERT INTO portfolio (id, symbol, quantity, price, total, usdtotal) \
                            VALUES (:id, :symbol, :quantity, :price, :total, :usdtotal);", id=session["user_id"], \
                            symbol=symbol, quantity=shares, price=usd(stock["price"]), \
                            total=plus_total, usdtotal=usd(plus_total))
            # if the user does own the stock update the row's quantity and total
            else:
                old_total = db.execute("SELECT total FROM portfolio \
                           WHERE id = :id AND symbol=:symbol", \
                           id=session["user_id"], symbol=symbol)
                new_total = old_total[0]["total"] + plus_total
                increase_quantity = owned[0]["quantity"] + shares
                db.execute("UPDATE portfolio SET quantity=:quantity, total=:total, usdtotal=:usdtotal WHERE id=:id AND \
                            symbol=:symbol",quantity=increase_quantity, total=new_total, usdtotal=usd(new_total), \
                            id=session["user_id"], symbol=symbol)

        # set user's new cash balance
        db.execute("UPDATE users SET cash = cash - :total WHERE id = :id;", \
        id=session["user_id"], total=shares*stock['price'])

        # insert transaction into history
        db.execute("INSERT INTO history (symbol, quantity, price, id) VALUES (:symbol, :quantity, :price, :id)", \
                    symbol = symbol, quantity = shares, price = usd(stock["price"]), id=session["user_id"])

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""

    history = db.execute("SELECT * FROM history WHERE id=:id", id=session["user_id"])
    return render_template("history.html", history=history)

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

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        # ensure a symbol is filled in
        if not request.form.get("symbol"):
            return apology("Please fill in a symbol")

        # ensure correct symbol and display form if symbol is correct
        symbol = lookup(request.form.get("symbol"))
        if not symbol:
            return apology("We could not provide information on the given symbol")

        # display stock information from helpers.py & stock_info.html
        return render_template("stock_info.html", stock = symbol)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")

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

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""

    if request.method == "POST":

        # ensure stock is in users portfolio
        symbol_search = request.form.get("symbol")

        symbol_portfolio = db.execute("SELECT symbol FROM portfolio WHERE id=:id AND symbol=:symbol", \
        id=session["user_id"], symbol=symbol_search)

        try:
            if not symbol_search in symbol_portfolio[0]["symbol"]:
                return apology("You do not own this stock")
        except IndexError:
            return apology("You do not own this stock")

        # ensure amount of shares are filled in as a positive integer
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Please fill in a symbol with a positive integer")

        if shares <= 0:
            return apology("Please fill in a symbol with a positive integer")

        # check if the user has enough shares to sell
        current_shares = db.execute("SELECT quantity FROM portfolio WHERE id=:id AND symbol=:symbol", \
        id=session["user_id"], symbol=symbol_search)
        if current_shares[0]["quantity"] < shares:
            return apology("You do not own enough ' {} ' to sell anything".format(symbol_search))

        # update quantity and total
        else:
            compute_shares = current_shares[0]["quantity"] - shares
            symbol = lookup(request.form.get("symbol"))
            old_total = db.execute("SELECT total FROM portfolio WHERE id=:id AND symbol=:symbol", \
            id=session["user_id"], symbol=symbol_search)
            new_total = symbol["price"] * shares
            compute_total = old_total[0]["total"] - new_total
            new_shares = db.execute("UPDATE portfolio SET quantity=:quantity, total=:total, usdtotal=:usdtotal \
                                    WHERE id=:id AND symbol=:symbol", quantity=compute_shares, \
                                    total=compute_total, id=session["user_id"], symbol=symbol_search, \
                                    usdtotal=usd(compute_total))

        # update user's cash balance
        cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        current_cash = cash[0]["cash"]
        new_cash = current_cash + new_total
        db.execute("UPDATE users SET cash=:cash WHERE id=:id", cash=new_cash, id=session["user_id"])

        # insert transaction into history
        price = db.execute("SELECT price FROM portfolio WHERE id=:id AND symbol=:symbol", \
                                    id=session["user_id"], symbol=symbol_search)
        symbol_price = usd(new_total / shares)
        db.execute("INSERT INTO history (symbol, quantity, price, id) VALUES (:symbol, :quantity, :price, :id)", \
                    symbol = symbol_search, quantity = -shares, price = symbol_price, id=session["user_id"])

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html")

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

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, session, redirect
import os, bcrypt
from stock_data import StockData
from helpers import get_db, initialize_db, status, check_password

# initialize the app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
initialize_db()

# jinja will use this to format numbers into currency
@app.template_filter("currency")
def currency(value):
    if value is None:
        return ""
    return "{:,.2f}".format(value)


@app.route("/", methods=["GET", "POST"])
def index():
    # if just landing on page
    if request.method == "GET":
        return render_template("index.html", logged_in=status())

    # get the user's input
    company = request.form.get("user_input")

    # check that user input is not empty
    if not company:
        return render_template("index.html", message="Please enter the name of the company you want to search!", logged_in=status())

    # check that data is retrieved successfully
    try:
        search_results = StockData().search(company)

    except ValueError:
        return render_template("index.html", message="Could not find results for the company you entered. Make sure the name is correct.", logged_in=status())

    return render_template("search.html", search_results=search_results, logged_in=status())


@app.route("/company", methods=["GET", "POST"])
def company():
    # if just landing on page
    if request.method == "GET":
        return render_template("company.html", logged_in=status())

    # get the user's input
    symbol = request.form.get("company")

    # check that user input is not empty
    if not symbol:
        return render_template("company.html", message="Select the name or symbol of a company from the results", logged_in=status())

    # retrieve the data
    data = StockData(symbol).package_data()    

    # store the search data
    session["last_symbol"] = symbol

    return render_template("company.html", **data, logged_in=status())


@app.route("/register", methods=["GET", "POST"])
def register():
    # if from other pages
    if request.method == "GET":
        return render_template("register.html")

    # check that username field is not empty
    username = request.form.get("username")
    if not username:
        return render_template("register.html", message="Please enter your username!")
    username = username.lower()

    # check that the password field is not empty
    password = request.form.get("password")
    if not password:
        return render_template("register.html", message="Please enter a password!")

    # check that the confirm password field is not empty
    confirm_password = request.form.get("confirm_password")
    if not confirm_password:
        return render_template("register.html", message="Please confirm your password!")

    # Check that password is at least 6 characters long and contains letters, digits and characters
    if not check_password(password):
        return render_template("register.html", message="Must contain at least one number and one letter")

    # check that the passwords match
    if password != confirm_password:
        return render_template("register.html", message="Passwords don't match")

    with get_db() as db:
        # check that the username does not exist in database
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user:
            return render_template("register.html", message="Username exists! Log in please.")

        # hash the password
        hash_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # add the user to the database
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_pw.decode("utf-8")))

        # get user's id
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        # Check that user has data
        if user:
            # Set user_id in session after successful login
            session["user_id"] = user["id"]

    # close the connection
    db.close()

    # Store the user's search - if available - in their database
    # store_last_search()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
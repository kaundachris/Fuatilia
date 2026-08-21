from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, session
import os
from stock_data import StockData
from helpers import status, retrieve_data

# initialize the app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# jinja will use this to format numbers into currency
@app.template_filter("currency")
def currency(value):
    if value is None:
        return ""
    return "${:,.2f}".format(value)


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
        search_results = StockData().search_results(company)

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
    data = retrieve_data(symbol)    

    # store the search data
    session["last_symbol"] = symbol

    return render_template("company.html", **data, logged_in=status())


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
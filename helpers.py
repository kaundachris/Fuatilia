from flask import session
import os, sqlite3, json
from datetime import date


def get_db():
    """creates or opens the database connection"""
    db_path = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "fuatilia.db"))
    connection = sqlite3.connect(db_path)

    # return rows as dictionary-like objects for easy parsing
    connection.row_factory = sqlite3.Row

    return connection


def initialize_db():
    """creates the database with all the fields needed"""
    with get_db() as db:
        # create the users table
        db.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
                )""")

        # store data on all companies searched
        db.execute("""CREATE TABLE IF NOT EXISTS companies(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                symbol TEXT NOT NULL,
                date_created DATE,
                UNIQUE(symbol)
                )""")

        # create a portfolio table (what each user has searched)
        db.execute("""CREATE TABLE IF NOT EXISTS portfolios(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                company_name TEXT NOT NULL,
                company_symbol TEXT NOT NULL,
                price_earnings REAL,
                price_book REAL,
                operating_profit_margin REAL,
                dividend_yield REAL,
                current_ratio REAL,
                debt_equity REAL,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(company_id) REFERENCES companies(id),
                UNIQUE(user_id, company_id)
                )""")

        # create the income statements table
        db.execute("""CREATE TABLE IF NOT EXISTS income_statements(
                company_id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                FOREIGN KEY(company_id) REFERENCES companies(id)
                )""")

        # create the balance sheets table
        db.execute("""CREATE TABLE IF NOT EXISTS balance_sheets(
                company_id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                FOREIGN KEY(company_id) REFERENCES companies(id)
                )""")

        # create the cashflow statements table
        db.execute("""CREATE TABLE IF NOT EXISTS cashflows(
                company_id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                FOREIGN KEY(company_id) REFERENCES companies(id)
                )""")

        # create the financial ratios table
        db.execute("""CREATE TABLE IF NOT EXISTS ratios(
                company_id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                FOREIGN KEY(company_id) REFERENCES companies(id)
                )""")

        # commit changes to the database
        db.commit()

    # close the connection
    db.close()


def status():
    """Checks if the user's id is in the session cookie"""

    if "user_id" in session:
        return True
    else:
        return False


def check_password(password):
    """checks that the password meets security requirements"""

    has_digit = False
    has_letter = False

    # check that the password is at least 6 character long
    if len(password) < 6:
        return False

    # check that the password has a number and letter
    for char in password:
        if char.isdigit():
            has_digit = True
        elif char.isalpha():
            has_letter = True

        ## if both of the above are true, exit early (saves time)
        if has_digit and has_letter:
            return True
    return False


def store_financial_statements(data, symbol):
    """stores financial statements of a searched company in the database"""

    # extract the data
    income_data = data["income_data"]
    balance_sheet_data = data["balance_sheet_data"]
    cashflow_data = data["cashflow_data"]
    ratio_data = data["ratio_data"]
    date_created = None
    if ratio_data:
        date_created = date.fromisoformat(ratio_data.get("date"))

    with get_db() as db:
        # add the company to the companies table
        db.execute('''INSERT OR IGNORE INTO companies (symbol, date_created)
            VALUES (?, ?)''',
            (symbol, date_created))

        # get the company id to use in storing the other attributes
        company_id = db.execute("SELECT id FROM companies WHERE symbol = ?", (symbol,)).fetchone()
        company_id = company_id["id"]

        # add the income statements to the income statements table
        if income_data:
            db.execute('''INSERT OR REPLACE INTO income_statements (company_id, data)
                VALUES (?, ?)''',
                (company_id, json.dumps(income_data)))

        # add the balance sheets to the balance sheets table
        if balance_sheet_data:
            db.execute('''INSERT OR REPLACE INTO balance_sheets (company_id, data)
                VALUES (?, ?)''',
                (company_id, json.dumps(balance_sheet_data)))
        
        # add the cashflow statements to the cashflows table
        if cashflow_data:
            db.execute('''INSERT OR REPLACE INTO cashflows (company_id, data)
                VALUES (?, ?)''',
                (company_id, json.dumps(cashflow_data)))
        
        # add the ratio data to the ratios table
        if ratio_data:
            db.execute('''INSERT OR REPLACE INTO ratios (company_id, data)
                VALUES (?, ?)''',
                (company_id, json.dumps(ratio_data)))

        # commit changes
        db.commit()

    # close the connection
    db.close()


def update_user_portfolio(data, symbol):
    # extract the data
    profile_data = data["profile_data"]
    ratio_data = data["ratio_data"]

    with get_db() as db:
        # get the company id to use in storing the portfolio attributes
        company_id = db.execute("SELECT id FROM companies WHERE symbol = ?", (symbol,)).fetchone()
        company_id = company_id["id"]
        user_id = session["user_id"]

        # add search to the portfolio table
        if profile_data:
            # if ratio data missing, coerce it into an empty dict
            if ratio_data is None:
                ratio_data = {}

            db.execute('''INSERT OR REPLACE INTO portfolios 
                (user_id, company_id, company_name, company_symbol, price_earnings, price_book,
                operating_profit_margin, dividend_yield, current_ratio, debt_equity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (user_id, company_id, profile_data["companyName"], profile_data["symbol"], ratio_data.get("priceToEarningsRatio"),
                    ratio_data.get("priceToBookRatio"), ratio_data.get("operatingProfitMargin"), ratio_data.get("dividendYieldPercentage"),
                    ratio_data.get("currentRatio"), ratio_data.get("debtToEquityRatio")))

        # commit changes
        db.commit()

    # close the connection
    db.close()


def retrieve_user_portfolio(sort_by=None, order="ASC"):
    """gets all the user search data to populate the portfolio page"""

    # ensure user is logged in
    if "user_id" not in session:
        return []
    
    # whitelist of sortable columns (prevents SQL injection)
    valid_columns = [
        "price_earnings", "price_book", "operating_profit_margin",
        "dividend_yield", "current_ratio", "debt_equity"
    ]

    # whitelist of allowable orders (prevents SQL injection)
    valid_orders = ["ASC", "DESC"]


    # validate the sort item selected
    if sort_by not in valid_columns:
        sort_by = None

    # set the order item to "ASC" always
    if order not in valid_orders:
        order = "ASC"

    #connect to database
    with get_db() as db:
        # get searches related to the user id
        if sort_by:
            # if sort parameter present, sort the results
            query = f"SELECT * FROM portfolios WHERE user_id = ? ORDER BY {sort_by} {order}"
            results = db.execute(query, (session["user_id"],)).fetchall()
        else:
            # if search parameter missing, return results as is
            results = db.execute("SELECT * FROM portfolios WHERE user_id = ?", (session["user_id"],)).fetchall()

    # close the connection
    db.close()

    return results


def needs_refresh(symbol):
    """determines whether to pull new data depending on age of existing data"""

    # extract the date
    with get_db() as db:
        date_created = db.execute("SELECT date_created FROM companies WHERE symbol = ?", (symbol,)).fetchone()
        if date_created:
            date_created = date_created["date_created"]

    # close the connection
    db.close()

    # compute the age of the data and return it
    if date_created:
        date_created = date.fromisoformat(date_created)
        age = date.today() - date_created
        return age.days > 366

    return True

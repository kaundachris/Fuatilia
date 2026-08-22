from flask import session
import os, sqlite3


def get_db():
    """creates or opens the database connection"""
    connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), "fuatilia.db"))

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
                UNIQUE(symbol)
                )""")

        # create a portfolio table - what each user has searched
        db.execute("""CREATE TABLE IF NOT EXISTS portfolios(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(company_id) REFERENCES companies(id),
                UNIQUE(user_id, company_id)
                )""")

        # create the company profiles table
        db.execute("""CREATE TABLE IF NOT EXISTS company_profiles(
                company_id INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                FOREIGN KEY(company_id) REFERENCES companies(id)
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

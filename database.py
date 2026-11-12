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
    db = get_db()
    try:
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
                statement_date DATE,
                date_searched DATE,
                profile_data TEXT NOT NULL,
                price_data TEXT NOT NULL,
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

    finally:
        # close the connection
        db.close()


def store_financial_statements(data, symbol):
    """stores financial statements of a searched company in the database"""

    # extract the data
    profile_data = data["profile_data"]
    price_data = data["price_data"]
    income_data = data["income_data"]
    balance_sheet_data = data["balance_sheet_data"]
    cashflow_data = data["cashflow_data"]
    ratio_data = data["ratio_data"]

    # store the relevant dates
    date_searched = date.today().isoformat()

    if ratio_data:
        # coerce the date to standard ISO format
        statement_date = date.fromisoformat(ratio_data.get("date")).isoformat()
    else:
        statement_date = None

    db = get_db()
    try:
        # add the company to the companies table
        # use COALESCE so that a failed ratios call (and thus null date) doesn't erase a stored good date
        db.execute("""INSERT INTO companies (symbol, statement_date, date_searched, profile_data, price_data)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (symbol) DO UPDATE SET
            statement_date = COALESCE(excluded.statement_date, companies.statement_date),
            date_searched = excluded.date_searched,
            profile_data = excluded.profile_data,
            price_data = excluded.price_data""",
            (symbol, statement_date, date_searched, json.dumps(profile_data), json.dumps(price_data)))

        # get the company id to use in storing the other attributes
        company_id = db.execute("SELECT id FROM companies WHERE symbol = ?", (symbol,)).fetchone()
        company_id = company_id["id"]

        # add the income statements to the income statements table
        if income_data:
            db.execute("""INSERT OR REPLACE INTO income_statements (company_id, data)
                VALUES (?, ?)""",
                (company_id, json.dumps(income_data)))

        # add the balance sheets to the balance sheets table
        if balance_sheet_data:
            db.execute("""INSERT OR REPLACE INTO balance_sheets (company_id, data)
                VALUES (?, ?)""",
                (company_id, json.dumps(balance_sheet_data)))
        
        # add the cashflow statements to the cashflows table
        if cashflow_data:
            db.execute("""INSERT OR REPLACE INTO cashflows (company_id, data)
                VALUES (?, ?)""",
                (company_id, json.dumps(cashflow_data)))
        
        # add the ratio data to the ratios table
        if ratio_data:
            db.execute("""INSERT OR REPLACE INTO ratios (company_id, data)
                VALUES (?, ?)""",
                (company_id, json.dumps(ratio_data)))

        # commit changes
        db.commit()

    finally:
        # close the connection
        db.close()

import os, sqlite3, json
from database import get_db


def update_user_portfolio(symbol, user_id):
    """takes the data just searched and adds it to the user's portfolio"""

    db = get_db()
    try:
        # get the company id to use in retrieving ratio data
        company_data = db.execute("SELECT id, profile_data FROM companies WHERE symbol = ?", (symbol,)).fetchone()
        company_id = company_data["id"]

        # retrieve the profile data from the database
        profile_data = company_data["profile_data"]
        profile_data = json.loads(profile_data)

        # retrieve the ratio data from the database
        ratio_data = db.execute("SELECT data FROM ratios WHERE company_id = ?", (company_id,)).fetchone()
        if ratio_data:
            ratio_data = json.loads(ratio_data["data"])

        # if ratio data missing, coerce it into an empty dict
        if ratio_data is None:
            ratio_data = {}

        # add the company data to the portfolio table
        db.execute("""INSERT OR REPLACE INTO portfolios 
            (user_id, company_id, company_name, company_symbol, price_earnings, price_book,
            operating_profit_margin, dividend_yield, current_ratio, debt_equity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, company_id, profile_data["companyName"], profile_data["symbol"], ratio_data.get("priceToEarningsRatio"),
                ratio_data.get("priceToBookRatio"), ratio_data.get("operatingProfitMargin"), ratio_data.get("dividendYieldPercentage"),
                ratio_data.get("currentRatio"), ratio_data.get("debtToEquityRatio")))

        # commit changes
        db.commit()

    finally:
        # close the connection
        db.close()


def retrieve_user_portfolio(user_id, sort_by=None, order="ASC"):
    """gets all the user search data to populate the portfolio page"""
    
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
    db = get_db()
    try:
        # get searches related to the user id
        if sort_by:
            # if sort parameter present, sort the results
            query = f"SELECT * FROM portfolios WHERE user_id = ? ORDER BY {sort_by} {order}"
            results = db.execute(query, (user_id,)).fetchall()
        else:
            # if search parameter missing, return results as is
            results = db.execute("SELECT * FROM portfolios WHERE user_id = ?", (user_id,)).fetchall()

    finally:
        # close the connection
        db.close()

    return results

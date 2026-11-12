from datetime import date
from database import get_db


def statements_need_refresh(symbol):
    """determines whether to pull new data depending on age of existing data"""

    # extract the date
    db = get_db()
    try:
        statement_date = db.execute("SELECT statement_date FROM companies WHERE symbol = ?", (symbol,)).fetchone()
        if statement_date:
            statement_date = statement_date["statement_date"]

    finally:
        # close the connection
        db.close()

    # compute the age of the data and return it
    if statement_date:
        statement_date = date.fromisoformat(statement_date)
        age = date.today() - statement_date
        return age.days > 366

    # if there is no date, return TRUE
    return True


def price_profile_need_refresh(symbol):
    """refetch data if data has not been fetched today"""

    # extract the date
    db = get_db()
    try:
        date_searched = db.execute("SELECT date_searched FROM companies WHERE symbol = ?", (symbol,)).fetchone()
        if date_searched:
            date_searched = date_searched["date_searched"]

    finally:
        # close the connection
        db.close()

    # compute the age of the data and return it
    if date_searched:
        date_searched = date.fromisoformat(date_searched)
        age = date.today() - date_searched
        return age.days >= 1

    # if there is no date, return TRUE
    return True

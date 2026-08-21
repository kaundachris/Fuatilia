from flask import session
from stock_data import StockData

def status():
    """
    Checks if the user's id is in the session cookie
    """

    if "user_id" in session:
        return True
    else:
        return False


def retrieve_data(symbol):
    """
    Retrieves the data related to the company

    Args:
        symbol: the symbol whose data you want to retrieve
    
    Returns:
        data: dict of the data retrieved
    """

    # set the symbol
    company = StockData(symbol)

    # check that profile data is retrieved successfully
    try:
        profile = company.profile()

    except ValueError:
        profile = None

    # check that price data is retrieved successfully
    try:
        prices = company.prices()

    except ValueError:
        prices = None

    # check that income statement data is retrieved successfully
    try:
        income_statements = company.income_statements()

    except ValueError:
        income_statements = None

    # check that balance sheet data is retrieved successfully
    try:
        balance_sheets = company.balance_sheets()

    except ValueError:
        balance_sheets = None

    # check that ratio data is retrieved successfully
    try:
        ratios = company.financial_ratios()

    except ValueError:
        ratios = None

    # store the data
    data = {
        "profile": profile,
        "prices": prices,
        "income_statements": income_statements,
        "balance_sheets": balance_sheets,
        "ratios": ratios
        }
    
    return data

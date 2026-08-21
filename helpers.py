from flask import session
from stock_data import StockData

def status():
    """Checks if the user's id is in the session cookie"""

    if "user_id" in session:
        return True
    else:
        return False

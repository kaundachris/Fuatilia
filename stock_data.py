from dotenv import load_dotenv
load_dotenv()

import requests, os


class StockData():
    API_KEY = os.environ.get("API_KEY")
    US_EXCHANGES = {"NASDAQ", "NYSE", "AMEX"}
    BASE_URL = "https://financialmodelingprep.com/stable/"

    # API endpoints
    SEARCH_ENDPOINT = "search-name?query="
    PROFILE_ENDPOINT = "profile?symbol="
    PRICES_ENDPOINT = "historical-price-eod/light?symbol="
    INCOME_STATEMENT_ENDPOINT = "income-statement?symbol="
    BALANCE_SHEET_ENDPOINT = "balance-sheet-statement?symbol="
    CASHFLOW_ENDPOINT = "cash-flow-statement?symbol="
    RATIOS_ENDPOINT = "ratios?symbol="


    def __init__(self, symbol=None):
        self.symbol = symbol
        self.session = requests.Session()


    def build_query(self, endpoint):
        """Builds the links you use to call data from the API"""

        # check that the symbol is present
        if self.symbol is None:
            raise ValueError("Symbol parameter is missing")

        # create the query
        link = f"{self.BASE_URL}{endpoint}{self.symbol}&apikey={self.API_KEY}"

        return link


    def api_call(self, link, identifier):
        """Passes a link to requests to call for data"""
        
        # call the API
        response = self.session.get(link).json()

        # ensure there is data in the filtered results
        if len(response) == 0 or (isinstance(response, dict) and "Error Message" in response):
            raise ValueError(f"No results returned for {identifier}")
        
        return response
    

    def search(self, query):
        """Gets the symbol for the company searched"""

        # create the query
        link = f"{self.BASE_URL}{self.SEARCH_ENDPOINT}{query}&apikey={self.API_KEY}"

        # call the API
        search_data = self.api_call(link, query)

        # filter for US results
        us_results = []
        symbols = []
        for result in search_data:
            if result["exchange"] in self.US_EXCHANGES and result["symbol"] not in symbols:
                us_results.append(result)
                symbols.append(result["symbol"])

        # ensure there is data in the filtered results
        if len(us_results) == 0:
            raise ValueError(f"No results for {query}")
        
        return us_results
    

    def fetch_data(self):
        """fetches the required data for the symbol"""

        # Gets the profile data
        try:
            link = self.build_query(self.PROFILE_ENDPOINT)
            profile_data = self.api_call(link, self.symbol)[0]
        except ValueError:
            profile_data = None

        # Gets the price data
        try:
            link = self.build_query(self.PRICES_ENDPOINT)
            price_data = self.api_call(link, self.symbol)
        except ValueError:
            price_data = None

        # Gets the income data
        try:
            link = self.build_query(self.INCOME_STATEMENT_ENDPOINT)
            income_data = self.api_call(link, self.symbol)
        except ValueError:
            income_data = None

        # Gets the balance sheet data
        try:
            link = self.build_query(self.BALANCE_SHEET_ENDPOINT)
            balance_sheet_data = self.api_call(link, self.symbol)
        except ValueError:
            balance_sheet_data = None

        # Gets the cashflow data
        try:
            link = self.build_query(self.CASHFLOW_ENDPOINT)
            cashflow_data = self.api_call(link, self.symbol)
        except ValueError:
            cashflow_data = None

        # Gets the ratio data
        try:
            link = self.build_query(self.RATIOS_ENDPOINT)
            ratio_data = self.api_call(link, self.symbol)
        except ValueError:
            ratio_data = None

        data = {
                "profile_data": profile_data,
                "price_data": price_data,
                "income_data": income_data,
                "balance_sheet_data": balance_sheet_data,
                "cashflow_data": cashflow_data,
                "ratio_data": ratio_data
                }

        return data

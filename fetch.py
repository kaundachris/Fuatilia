from dotenv import load_dotenv
load_dotenv()

import requests, os, json
from cache import  statements_need_refresh, price_profile_need_refresh
from database import get_db, store_financial_statements
from helpers import chart, build_data_dict
from concurrent.futures import ThreadPoolExecutor


class StockData():
    API_KEY = os.environ.get("API_KEY")
    US_EXCHANGES = {"NASDAQ", "NYSE", "AMEX"}
    BASE_URL = "https://financialmodelingprep.com/stable/"

    # API endpoints
    SEARCH_ENDPOINT = "search-name"
    PROFILE_ENDPOINT = "profile"
    PRICES_ENDPOINT = "historical-price-eod/light"
    INCOME_STATEMENT_ENDPOINT = "income-statement"
    BALANCE_SHEET_ENDPOINT = "balance-sheet-statement"
    CASHFLOW_ENDPOINT = "cash-flow-statement"
    RATIOS_ENDPOINT = "ratios"


    def __init__(self, symbol=None):
        self.symbol = symbol
        self.session = requests.Session()


    def build_query(self, endpoint, search_query=None):
        """Builds the links you use to call data from the API"""

        # build the base url
        url = f"{self.BASE_URL}{endpoint}"

        # check for any search query
        if search_query:
            # create the params
            params = {"query": search_query, "apikey": self.API_KEY}
            
            return {"url": url, "params": params}

        # else, check that a symbol is present
        if self.symbol:
            # create the params
            params = {"symbol": self.symbol, "apikey": self.API_KEY}
            
            return {"url": url, "params": params}

        raise ValueError("Symbol parameter is missing")       


    def api_call(self, url, params, identifier):
        """Passes a link to requests to call for data"""
        
        # call the API
        try:
            response = self.session.get(url=url, params=params, timeout=10).json()

        except requests.RequestException:
            raise ValueError("API timeout")

        # ensure there is data in the filtered results
        if len(response) == 0 or (isinstance(response, dict) and "Error Message" in response):
            raise ValueError(f"No results returned for {identifier}")
        
        return response
    

    def search(self, query):
        """Gets the symbol for the company searched"""

        # build the query
        query_data = self.build_query(endpoint=self.SEARCH_ENDPOINT, search_query=query)

        # call the API
        search_data = self.api_call(url=query_data["url"], params=query_data["params"], identifier=query)

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
    

    def fetch_data(self, endpoint):
        """fetches the required data for the symbol"""

        # Get the data
        try:
            query_data = self.build_query(endpoint)
            fetched_data = self.api_call(url=query_data["url"], params=query_data["params"], identifier=self.symbol)
        except ValueError as error:
            fetched_data = None
            print(error)

        return fetched_data


    def fetch_or_cache(self, table, company_id, endpoint):
        """get data from database. If not available, fetch data"""
        # Get the data from the database
        db = get_db()
        try:
            query = f"SELECT data FROM {table} WHERE company_id = ?"
            data = db.execute(query, (company_id,)).fetchone()
            if data:
                data = json.loads(data["data"])
            else:
                # otherwise, fetch the data
                data = self.fetch_data(endpoint=endpoint)
                if data and endpoint == self.RATIOS_ENDPOINT:
                    data = data[0]

        finally:
            db.close()

        return data


    def package_data(self):
        """Returns the company data in the required format for app.py for display on the site"""

        if price_profile_need_refresh(self.symbol):
            with ThreadPoolExecutor() as executor:
                # Runs the API calls concurrently
                future_profile = executor.submit(self.fetch_data, self.PROFILE_ENDPOINT)
                future_price = executor.submit(self.fetch_data, self.PRICES_ENDPOINT)

            # Gets the profile data
            profile_data = future_profile.result()
            if not profile_data:
                return None

            profile_data = profile_data[0]

            # Gets the price data
            price_data = future_price.result()

            # Draws the price chart
            price_chart = chart(price_data)

        else:
            db = get_db()
            try:
                # get the stored price and profile data
                price_profile_data = db.execute("SELECT * FROM companies WHERE symbol = ?", (self.symbol,)).fetchone()
                profile_data = json.loads(price_profile_data["profile_data"])
                price_data = json.loads(price_profile_data["price_data"])
                price_chart = chart(price_data)

            finally:
                db.close()
 
        if statements_need_refresh(self.symbol):
            with ThreadPoolExecutor() as executor:
                # Runs the API calls concurrently
                future_income = executor.submit(self.fetch_data, self.INCOME_STATEMENT_ENDPOINT)
                future_balance_sheet = executor.submit(self.fetch_data, self.BALANCE_SHEET_ENDPOINT)
                future_cashflow = executor.submit(self.fetch_data, self.CASHFLOW_ENDPOINT)
                future_ratio = executor.submit(self.fetch_data, self.RATIOS_ENDPOINT)

            # Gets the income data
            income_data = future_income.result()

            # Gets the balance sheet data
            balance_sheet_data = future_balance_sheet.result()

            # Gets the cashflow data
            cashflow_data = future_cashflow.result()

            # Gets the ratio data
            ratio_data = future_ratio.result()
            if ratio_data:
                ratio_data = ratio_data[0]

        else:
            db = get_db()
            try:
                # get the company's id
                company_id = db.execute("SELECT id FROM companies WHERE symbol = ?", (self.symbol,)).fetchone()
                company_id = company_id["id"]
            finally:
                db.close()

            # Gets the income data
            income_data = self.fetch_or_cache("income_statements", company_id, self.INCOME_STATEMENT_ENDPOINT)

            # Gets the balance sheet data
            balance_sheet_data = self.fetch_or_cache("balance_sheets", company_id, self.BALANCE_SHEET_ENDPOINT)

            # Gets the cashflow data
            cashflow_data = self.fetch_or_cache("cashflows", company_id, self.CASHFLOW_ENDPOINT)
                
            # Gets the ratio data
            ratio_data = self.fetch_or_cache("ratios", company_id, self.RATIOS_ENDPOINT)

        # build the data dict and store it
        data = build_data_dict(profile_data, price_data, income_data, balance_sheet_data, cashflow_data, ratio_data)
        store_financial_statements(data, self.symbol)

        # update price data to the chart for display
        data["price_data"] = price_chart

        return data

from dotenv import load_dotenv
load_dotenv()

import requests, os


class StockData():
    API_KEY = os.environ.get("API_KEY")
    US_EXCHANGES = {"NASDAQ", "NYSE", "AMEX"}
    BASE_URL = "https://financialmodelingprep.com/stable/"

    # search by name
    SEARCH_ENDPOINT = "search-name?query="

    # profile endpoint
    PROFILE_ENDPOINT = "profile?symbol="

    # price endpoint
    PRICES_ENDPOINT = "historical-price-eod/light?symbol="

    # income statement endpoint
    INCOME_STATEMENT_ENDPOINT = "income-statement?symbol="

    # balance sheet endpoint
    BALANCE_SHEET_ENDPOINT = "balance-sheet-statement?symbol="

    # cashflow endpoint
    CASHFLOW_ENDPOINT = "cash-flow-statement?symbol="

    # financial ratios endpoint
    RATIOS_ENDPOINT = "ratios?symbol="


    def __init__(self, symbol=None):
        self.symbol = symbol


    def build_query(self, endpoint):
        """
        Builds the links you use to call data from the API   
    
        Args:
            endpoint: the API endpoint you want to call e.g. search, profile 

        Returns:
            The full link to pass to the API

        Raises:
            ValueError: if the symbol is missing - the symbol is needed for the API call to work
        """

        # check that the symbol is present
        if self.symbol is None:
            raise ValueError("Symbol parameter is missing")

        # create the query
        link = f"{self.BASE_URL}{endpoint}{self.symbol}&apikey={self.API_KEY}"

        return link


    def api_call(self, link, identifier):
        """
        Passes a link to requests to call for data

        Args:
            link: the built link that we are using to call for data
            identifier: the search term or symbol passed used in the API call. Useful for a more descriptive error message

        Returns:
            The data retrieved by the API call
        
        Raises:
            ValueError: If there is no data from the call or if the data contains an error message
        """
        
        # call the API
        response = requests.get(link).json()

        # ensure there is data in the filtered results
        if len(response) == 0 or (isinstance(response, dict) and "Error Message" in response):
            raise ValueError(f"No results returned for {identifier}")
        
        return response


    def search_results(self, query):
        """
        Gets the symbol for the company searched

        Args:
            query: company whose data you want to pull

        Returns:
            All US results matching the company name 

        Raises:
            ValueError: if the search yields no results
        """

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
        
        # return the result
        return us_results
        

    def profile(self):
        """
        Gets the profile data of the company in question
        
        Returns:
            profile_data: a dict with several key value pairs
        """

        # create the query
        link = self.build_query(self.PROFILE_ENDPOINT)

        # call the API
        profile_data = self.api_call(link, self.symbol)

        # return the result
        return profile_data[0]


    def prices(self):
        """
        Gets the 5 year price data of the company in question

        Returns:
            price_data: a list of dicts containing 5 year daily closing prices 
        """

        # create the query
        link = self.build_query(self.PRICES_ENDPOINT)

        # call the API
        price_data = self.api_call(link, self.symbol)

        # return the result
        return price_data


    def income_statements(self):
        """
        Gets the 5 year income statements of the company in question
        
        Returns:
            income_data: a list of dicts containing yearly income data going back 5 years
        """

        # create the query
        link = self.build_query(self.INCOME_STATEMENT_ENDPOINT)

        # call the API
        income_data = self.api_call(link, self.symbol)

        # return the result
        return income_data


    def balance_sheets(self):
        """
        Gets the 5 year balance sheets of the company in question

        Returns:
            balance_sheet_data: a list of dicts containing yearly balance sheet data going back 5 years
        """

        # create the query
        link = self.build_query(self.BALANCE_SHEET_ENDPOINT)

        # call the API
        balance_sheet_data = self.api_call(link, self.symbol)

        # return the result
        return balance_sheet_data


    def cashflow_statements(self):
        """
        Gets the 5 year cashflow statements of the company in question

        Returns:
            cashflow_data: a list of dicts containing yearly cashflow data going back 5 years
        """

        # create the query
        link = self.build_query(self.CASHFLOW_ENDPOINT)

        # call the API
        cashflow_data = self.api_call(link, self.symbol)

        # return the result
        return cashflow_data


    def financial_ratios(self):
        """
        gets the 5 year financial ratios of the company in question

        Returns:
            ratio_data: a list of dicts containing yearly ratio data going back 5 years
        """
        
        # create the query
        link = self.build_query(self.RATIOS_ENDPOINT)

        # call the API
        ratio_data = self.api_call(link, self.symbol)

        # return the result
        return ratio_data

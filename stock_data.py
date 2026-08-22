from dotenv import load_dotenv
load_dotenv()

import requests, os
import pandas as pd
import plotly.express as px


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
    

    def fetch_data(self, endpoint):
        """fetches the required data for the symbol"""

        # Get the data
        try:
            link = self.build_query(endpoint)
            fetched_data = self.api_call(link, self.symbol)
        except ValueError:
            fetched_data = None

        return fetched_data


    def price_chart(self):
        """render the price chart (closing prices)"""

        # Gets the price data
        price_data = self.fetch_data(self.PRICES_ENDPOINT)

        # set price data to none if API returned nothing
        if not price_data:
            return None

        # load into a dataframe - offers safer handling
        df = pd.DataFrame(price_data)

        # convert date (string) to datetime object -reduces bugs
        df["date"] = pd.to_datetime(df["date"])
        graph = px.line(df, x="date", y ="price")

        # update the graph to match the design of the page
        graph.update_layout(
            # set background to black - like the html
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            # set font color to antiquewhite - like the html
            font_color="#FAEBD7",

            # set font to the page's family
            font_family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif",
            
            # set the vertical gridlines to grey and the graph boundary to white
            xaxis=dict(gridcolor="#333333", linecolor="#FAEBD7", zerolinecolor="#333333"),

            # set the horizontal gridlines to grey and the graph boundary to white
            yaxis=dict(gridcolor="#333333", linecolor="#FAEBD7", zerolinecolor="#333333"),
        )
        
        # set the color of the graph to blue for better visibility/differentiation
        graph.update_traces(line_color="#0A88B3")

        return graph.to_html(full_html=False, include_plotlyjs="cdn")


    def package_data(self):
        """Returns the company data in the required format for app.py"""

        # Gets the profile data
        profile_data = self.fetch_data(self.PROFILE_ENDPOINT)
        if profile_data:
            profile_data = profile_data[0]

        # Gets the price data
        price_data = self.price_chart()

        # Gets the income data
        income_data = self.fetch_data(self.INCOME_STATEMENT_ENDPOINT)

        # Gets the balance sheet data
        balance_sheet_data = self.fetch_data(self.BALANCE_SHEET_ENDPOINT)

        # Gets the cashflow data
        cashflow_data = self.fetch_data(self.CASHFLOW_ENDPOINT)

        # Gets the ratio data
        ratio_data = self.fetch_data(self.RATIOS_ENDPOINT)
        if ratio_data:
            ratio_data = ratio_data[0]

        data = {
                "profile_data": profile_data,
                "price_data": price_data,
                "income_data": income_data,
                "balance_sheet_data": balance_sheet_data,
                "cashflow_data": cashflow_data,
                "ratio_data": ratio_data
                }

        return data
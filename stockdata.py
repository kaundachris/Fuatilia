#import dependancies
from yfinance import Ticker
import plotly.express as px


class Stock():
    """
        Pulls the company's financial data, if present
        Picks the specific data needed
        Cleans it up for presentation
    """ 
    def __init__(self, ticker:str):
        # ticker is the persistent item of the class
        self.ticker = ticker
        self._stock = None
        self._info = None
        self._data = None

    #set the property so that the stock is called and stored into cache - reduces the calls to the API
    @property
    def stock(self):
        # if stock already exists, cache it to reduce API calls
        if self._stock is not None:
            return self._stock

        # cache the stock
        self._stock = Ticker(self.ticker)

        return self._stock

    #set the property so that the data is called and stored into cache - reduces the calls to the API
    @property
    def data(self):
        # if stock data already exists, cache it to reduce API calls
        if self._data is not None:
            return self._data
        
        # first, call the API for data; store data, if any
        data = self.stock.history(period="1y")

        # if no data, raise ValueError.
        if data.empty:
            raise ValueError(f"Data for {self.ticker} could not be found")

        # cache the data
        self._data = data

        return self._data

    #set the property so that the data is called and stored into cache - reduces the calls to the API
    @property
    def info(self):
        # if stock info already exists, cache it to reduce API calls
        if self._info is not None:
            return self._info
        
        # if no info, raise ValueError.
        if self.data.empty:
            raise ValueError(f"Data for {self.ticker} could not be found")
        
        # cache the info
        self._info = self.stock.info

        return self._info

    # Repeated pattern of accessing information on stock ofloaded to this function
    def get_info(self, key):
        return self.info.get(key)
   
    # Get the company's name
    @property
    def company_name(self):
        return self.get_info("longName") or "N/A" 
    
    # get the company's industry
    @property
    def company_industry(self):
        return self.get_info("industry") or "N/A" 
    
    # get the company's foward PE
    @property
    def company_forward_pe(self):
        forwardPE = self.get_info("forwardPE")
        if forwardPE is not None:
            return round(forwardPE, 2)
        else:
            return 0
    
    # get the company's earnings growth
    @property
    def company_earnings_growth(self):
        earnings_growth = self.get_info("earningsGrowth")
        if earnings_growth is not None:
            return round(earnings_growth * 100, 2)
        return 0
    
    # get the company's profit margin
    @property
    def company_profit_margin(self):
        profit_margin = self.get_info("profitMargins")
        if profit_margin is not None:
            return round(profit_margin * 100, 2)
        return 0

    # get the company's market capitalization
    @property
    def company_market_cap(self):
        market_cap = self.get_info("marketCap")
        if market_cap is not None:
            return market_cap
        return 0
    
    # get the company's price to book value
    @property
    def company_book_value(self):
        book_value = self.get_info("bookValue")
        if book_value is not None:
            return round(book_value, 2)
        return 0
    
    # get the company's price to book ratio
    @property
    def company_pb_ratio(self):
        pb_ratio = self.get_info("priceToBook")
        if pb_ratio is not None:
            return round(pb_ratio, 2)
        return 0
    
    # get the company's quick ratio
    @property
    def company_quick_ratio(self):
        quick_ratio = self.get_info("quickRatio")
        if quick_ratio is not None:
            return round(quick_ratio, 2)
        return 0
    
    # get the company's current ratio
    @property
    def company_current_ratio(self):
        current_ratio = self.get_info("currentRatio")
        if current_ratio is not None:
            return round(current_ratio, 2)
        return 0
    
    # get the company's free cashflow
    @property
    def company_free_cashflow(self):
        free_cashflow = self.get_info("freeCashflow")
        if free_cashflow is not None:
            return round(free_cashflow, 2)
        return 0
    
    # render the price chart
    @property
    def price_chart(self):
        # render only the closing prices
        data = self.data
        graph = px.line(data, x=data.index, y = "Close")

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

        return graph.to_html(full_html=False, include_plotlyjs='cdn')
            
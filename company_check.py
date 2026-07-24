import yfinance as yf

class CompanyLookup():
    """
        Checks the existence of a company
        If company exists, it returns the ticker of the company
        If it doesn't, it returns None
    """
    def __init__(self):
        # Reduces the number of API calls by storing any searches made
        self.COMPANY_TICKERS = {
            "google": "GOOGL",
            "apple": "AAPL",
            "tesla": "TSLA",
            "nvidia": "NVDA"
        }

    # check for existence of company
    def company_exists(self, company_name: str):
        # clean company name
        company_name = company_name.strip().lower()

        # if it looks like a ticker, return it directly
        if len(company_name) < 5:
            return company_name

        # if it is in the list of companies already, return the corresponding ticker
        if company_name in self.COMPANY_TICKERS:
            return self.COMPANY_TICKERS[company_name]

        results = yf.Search(company_name, max_results=5)
        quotes = results.quotes

        if quotes:
            # the first list in quotes is the priority
            ticker = quotes[0].get("symbol")

            if ticker:
                # store the company and ticker into the dictionary
                self.COMPANY_TICKERS[company_name] = ticker

                # return the ticker
                return ticker
        
        # if nothing is found, return None
        return None
        
class StockGrant:

    ticker = ""
    count = 0
    price = 0.0

    def __init__(self, ticker: str, count: int, price: float):
        self.ticker = ticker
        self.count = count
        self.price = price

    """
    Creates a StockGrant from the string that is stored in the config.ini file. 
    
    I.E. "TWTR,100,36.50" -> ticker = TWTR, count = 100, price = $36.50 
    """
    @staticmethod
    def create_from_config_ini(stock_entry: str):
        components = stock_entry.split(",")

        ticker = components[0]
        count = int(components[1])
        price = float(components[2])

        return StockGrant(ticker, count, price)

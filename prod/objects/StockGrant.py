class StockGrant:

    ticker = ""
    count = 0
    price = 0.0
    vests_left = 0

    def __init__(self, ticker: str, count: int, price: float, vests_left: int):
        self.ticker = ticker
        self.count = count
        self.price = price
        self.vests_left = vests_left

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
        vests_left = int(components[3])

        return StockGrant(ticker, count, price, vests_left)

    """
        Creates a config.ini string from the Stock Grant. 

        I.E. ticker = AAPL, count = 100, price = $36.50, vests left = 16 -> "AAPL,100,36.50,16"  
    """
    def get_config_ini_str(self) -> str:
        price_str = format(self.price, '.2f')
        return f'{self.ticker.upper()},{self.count},{price_str},{self.vests_left}'

    def __str__(self) -> str:
        price_str = format(self.price, '.2f')
        return f'{self.ticker} - {self.count} at ${price_str} (Vests Left: {self.vests_left})'

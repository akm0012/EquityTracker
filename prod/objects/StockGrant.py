class StockGrant:

    ticker = ""
    count = 0
    price = 0.0
    vests_left = 0
    # Optional label used to split grants of the same ticker onto separate rows.
    # Grants sharing a ticker AND group are combined; a different group is its own row.
    group = ""

    def __init__(self, ticker: str, count: int, price: float, vests_left: int, group: str = ""):
        self.ticker = ticker
        self.count = count
        self.price = price
        self.vests_left = vests_left
        self.group = group

    """
    Creates a StockGrant from the string that is stored in the config.ini file. 
    
    I.E. "TWTR,100,36.50,16" -> ticker = TWTR, count = 100, price = $36.50, vests left = 16 
    
    An optional 5th field is a "group" label. Grants that share a ticker but have different
    group labels are shown on their own row (useful when grants vest on independent schedules).
    
    I.E. "RDDT,399,147.86,2,b" -> ticker = RDDT, ..., group = "b"
    """
    @staticmethod
    def create_from_config_ini(stock_entry: str):
        components = stock_entry.split(",")

        ticker = components[0]
        count = int(components[1])
        price = float(components[2])
        vests_left = int(components[3])
        group = components[4].strip() if len(components) > 4 else ""

        return StockGrant(ticker, count, price, vests_left, group)

    """
        Creates a config.ini string from the Stock Grant. 

        I.E. ticker = AAPL, count = 100, price = $36.50, vests left = 16 -> "AAPL,100,36.50,16"  
        
        When a group label is set it is appended as a 5th field: "AAPL,100,36.50,16,b"
    """
    def get_config_ini_str(self) -> str:
        price_str = format(self.price, '.2f')
        config_str = f'{self.ticker.upper()},{self.count},{price_str},{self.vests_left}'
        if self.group:
            config_str += f',{self.group}'
        return config_str

    def __str__(self) -> str:
        price_str = format(self.price, '.2f')
        group_str = f' [{self.group}]' if self.group else ''
        return f'{self.ticker} - {self.count} at ${price_str} (Vests Left: {self.vests_left}){group_str}'

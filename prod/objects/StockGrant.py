class StockGrant:

    ticker = ""
    count = 0
    price = 0.0

    def __init__(self, ticker: str, count: int, price: float):
        self.ticker = ticker
        self.count = count
        self.price = price

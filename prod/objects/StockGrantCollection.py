from prod.objects.StockGrant import StockGrant


class StockGrantCollection:

    ticker = ""
    stock_grant_list = []

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock_grant_list = []

    def add_stock_grant(self, stock_grant: StockGrant):
        self.stock_grant_list.append(stock_grant)



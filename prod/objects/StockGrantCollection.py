from prod.objects.StockGrant import StockGrant


class StockGrantCollection:

    ticker = ""
    stock_grant_list = [StockGrant]

    # If true, we are only tracking this Stock and don't have any monetary grants in it.
    is_tracking_stock_only = True

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock_grant_list = []

    def add_stock_grant(self, stock_grant: StockGrant):
        if stock_grant.count > 0:
            self.is_tracking_stock_only = False
        self.stock_grant_list.append(stock_grant)

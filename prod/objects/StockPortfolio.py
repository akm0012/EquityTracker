from prod.objects.StockGrant import StockGrant
from prod.objects.StockGrantCollection import StockGrantCollection


class StockPortfolio:

    stock_grant_collection_dict = {}

    def __init__(self):
        self.stock_grant_collection_dict = {}

    def add_stock_grant(self, stock_grant: StockGrant):
        ticker = stock_grant.ticker

        # Check if there is already a Stock with that Key
        if self.stock_grant_collection_dict.keys().__contains__(ticker):
            # If so, get the current Stock Grant Collection and add this grant to it
            existing_stock_grant_collection = self.stock_grant_collection_dict[ticker]
            existing_stock_grant_collection.add_stock_grant(stock_grant)
            self.stock_grant_collection_dict[ticker] = existing_stock_grant_collection
        else:
            # If not, create a new Stock Grant Collection with the given grant
            stock_grant_collection = StockGrantCollection(ticker)
            stock_grant_collection.add_stock_grant(stock_grant)
            self.stock_grant_collection_dict[ticker] = stock_grant_collection

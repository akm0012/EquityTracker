from prod.objects.StockGrantCollection import StockGrantCollection


class StockPortfolio:

    stock_grant_collection_list = []

    def __init__(self):
        self.stock_grant_collection_list = []

    def add_stock_grant_collection(self, stock_grant_collection: StockGrantCollection):
        self.stock_grant_collection_list.append(stock_grant_collection)

from prod.objects.StockGrant import StockGrant
from prod.objects.StockGrantCollection import StockGrantCollection


class StockPortfolio:

    stock_grant_collection_dict = dict[str, StockGrantCollection]

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

    def get_all_stock_grant_collections(self) -> [StockGrantCollection]:
        return self.stock_grant_collection_dict.values()

    def get_all_stock_ticker_symbols(self) -> [str]:
        return self.stock_grant_collection_dict.keys()

    def get_stock_grant_collection(self, ticker: str) -> StockGrantCollection:
        # todo: error check
        return self.stock_grant_collection_dict[ticker]

    def get_all_stock_grants(self) -> [StockGrant]:
        stock_grant_list = []
        for key, value in self.stock_grant_collection_dict.items():
            for stock_grant in value.stock_grant_list:
                stock_grant_list.append(stock_grant)

        return stock_grant_list

    def get_max_grant_count(self) -> int:
        max_grant_count = 0
        for key, value in self.stock_grant_collection_dict.items():
            if value.is_tracking_stock_only:
                continue
            max_grant_count = max(max_grant_count, len(value.stock_grant_list))

        return max_grant_count


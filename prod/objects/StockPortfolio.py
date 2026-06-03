from prod.objects.StockGrant import StockGrant
from prod.objects.StockGrantCollection import StockGrantCollection


class StockPortfolio:

    stock_grant_collection_dict = dict[str, StockGrantCollection]

    def __init__(self):
        self.stock_grant_collection_dict = {}

    """
    The key a grant is filed under. Grants with no group label key by ticker (so they all
    combine onto one row, preserving the original behavior). A group label gives the grant
    its own row, separate from other grants of the same ticker.
    """
    @staticmethod
    def _row_key(stock_grant: StockGrant) -> str:
        if stock_grant.group:
            return f"{stock_grant.ticker}::{stock_grant.group}"
        return stock_grant.ticker

    def add_stock_grant(self, stock_grant: StockGrant):
        row_key = self._row_key(stock_grant)

        # Check if there is already a row with that key
        if self.stock_grant_collection_dict.keys().__contains__(row_key):
            # If so, get the current Stock Grant Collection and add this grant to it
            existing_stock_grant_collection = self.stock_grant_collection_dict[row_key]
            existing_stock_grant_collection.add_stock_grant(stock_grant)
            self.stock_grant_collection_dict[row_key] = existing_stock_grant_collection
        else:
            # If not, create a new Stock Grant Collection with the given grant
            stock_grant_collection = StockGrantCollection(stock_grant.ticker, stock_grant.group)
            stock_grant_collection.add_stock_grant(stock_grant)
            self.stock_grant_collection_dict[row_key] = stock_grant_collection

    def get_all_stock_grant_collections(self) -> [StockGrantCollection]:
        return self.stock_grant_collection_dict.values()

    """
    Returns the unique ticker symbols across all rows. Multiple rows can share a ticker
    (when grants are split onto separate rows), so this de-dupes for price subscriptions.
    """
    def get_all_stock_ticker_symbols(self) -> [str]:
        tickers = []
        for collection in self.stock_grant_collection_dict.values():
            if collection.ticker not in tickers:
                tickers.append(collection.ticker)
        return tickers

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

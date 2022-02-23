"""
This class handles all the retrieval of Stock data.
"""
from prod.network.ApiService import ApiService, UnknownStockError
from prod.objects.LiveStockInfo import LiveStockInfo
from prod.objects.StockPortfolio import StockPortfolio


class StockRepository:

    api_service: ApiService

    def __init__(self, api_service: ApiService):
        self.api_service = api_service

    def is_finnhub_api_key_valid(self, api_key: str) -> bool:
        try:
            self.api_service.get_stock("TWTR", api_key)
        except KeyError:
            return False
        return True

    def is_ticker_symbol_valid(self, ticker_symbol: str) -> bool:
        try:
            self.api_service.get_stock(ticker_symbol)
            return True
        except UnknownStockError:
            return False

    """
    Listens for live stock update via the callback. "LiveStockInfo" will be passed back. 
    It will first get the current price and send that back as an initial update, then socket will take over 
    and will send back updates as they are available. 
    """
    def listen_for_stock_price_updates(self, ticker_list: [str], price_callback):
        # Holds all the prices of the previous day for a specific stock. I.E. {TWTR : 35.50}
        yesterday_price_dict = {}

        # First, get a starting price for all the tickers interested
        for ticker in ticker_list:
            ticker = ticker.upper()
            stock_info = self.api_service.get_stock(ticker)
            yesterday_price_dict[ticker] = stock_info.previous_close_price
            price_callback(LiveStockInfo.map_from_stock_info(stock_info))

        # Then listen for live updates.
        self.api_service.listen_for_stock_updates(ticker_list, yesterday_price_dict, price_callback)

    def listen_for_portfolio_updates(self, portfolio: StockPortfolio, callback):
        self.listen_for_stock_price_updates(portfolio.get_all_stock_ticker_symbols(), callback)

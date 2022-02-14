import requests

from prod.objects.StockInfo import StockInfo
from prod.repository.ConfigRepository import ConfigRepository


class UnknownStockError(Exception):
    pass


class ApiService:

    config_repo: ConfigRepository

    def __init__(self, config_repo: ConfigRepository):
        self.config_repo = config_repo

    def get_stock(self, ticker: str) -> StockInfo:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}"
        param = {"symbol": ticker}
        headers = {"X-Finnhub-Token": self.config_repo.get_finnhub_api_key()}
        request = requests.get(url=url, params=param, headers=headers)
        data = request.json()

        stock_info = StockInfo(ticker, data)

        if stock_info.current_price == 0:
            raise UnknownStockError(f"{ticker} is not a valid Stock Symbol.")

        return stock_info


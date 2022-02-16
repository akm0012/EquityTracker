import requests
import websocket

from prod.objects.LiveStockInfo import LiveStockInfo
from prod.objects.StockInfo import StockInfo
from prod.repository.ConfigRepository import ConfigRepository


class UnknownStockError(Exception):
    pass


class ApiService:
    config_repo: ConfigRepository

    def __init__(self, config_repo: ConfigRepository):
        self.config_repo = config_repo

    def get_stock(self, ticker: str) -> StockInfo:
        ticker = ticker.upper()
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}"
        param = {"symbol": ticker}
        headers = {"X-Finnhub-Token": self.config_repo.get_finnhub_api_key()}
        request = requests.get(url=url, params=param, headers=headers)
        data = request.json()

        stock_info = StockInfo(ticker, data)

        if stock_info.current_price == 0:
            raise UnknownStockError(f"{ticker} is not a valid Stock Symbol.")

        return stock_info

    def listen_for_stock_updates(self, ticker_list: [str], stock_update_callback):
        websocket.enableTrace(False)
        web_socket = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={ConfigRepository().get_finnhub_api_key()}",
                                            on_open=lambda ws: self.__on_open__(ws, ticker_list),
                                            on_message=lambda ws, message: self.__on_web_socket_message__(ws, message, stock_update_callback),
                                            on_error=lambda ws, error: self.__on_web_socket_error__(ws, error),
                                            on_close=lambda ws: self.__on_close__(ws))

        web_socket.run_forever()

    @staticmethod
    def __on_open__(ws, ticker_list: [str]):
        for ticker in ticker_list:
            ws.send(f'{{"type":"subscribe","symbol":"{ticker}"}}')

    @staticmethod
    def __on_web_socket_message__(ws, message, callback):
        #todo Make a Stock Live Update with message
        # live_stock_update = LiveStockInfo("TWTR", message)
        mock_stock_update = LiveStockInfo("TWTR", 36.50, 1234567890)
        callback(mock_stock_update)

    @staticmethod
    def __on_web_socket_error__(ws, error):
        print(error)

    @staticmethod
    def __on_close__(ws):
        print("### closed ###")

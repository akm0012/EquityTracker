import requests
import websocket
import json

from prod.objects.LiveStockInfo import LiveStockInfo
from prod.objects.StockInfo import StockInfo
from prod.repository.ConfigRepository import ConfigRepository
from prod.util.LogUtil import log


class UnknownStockError(Exception):
    pass


class ApiService:
    config_repo: ConfigRepository

    def __init__(self, config_repo: ConfigRepository):
        self.config_repo = config_repo

    def get_stock(self, ticker: str, api_token="") -> StockInfo:
        if api_token == "":
            api_token = self.config_repo.get_finnhub_api_key()
        ticker = ticker.upper()
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}"
        param = {"symbol": ticker}
        headers = {"X-Finnhub-Token": api_token}
        request = requests.get(url=url, params=param, headers=headers)
        data = request.json()

        try:
            stock_info = StockInfo(ticker, data)
        except KeyError:
            raise UnknownStockError(f"{ticker} is not a valid Stock Symbol.")

        if stock_info.current_price == 0:
            raise UnknownStockError(f"{ticker} is not a valid Stock Symbol.")

        return stock_info

    def listen_for_stock_updates(self, ticker_list: [str], yesterday_price_dict: {}, stock_update_callback):
        websocket.enableTrace(False)
        web_socket = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={ConfigRepository().get_finnhub_api_key()}",
                                            on_open=lambda ws: self.__on_open__(ws, ticker_list),
                                            on_message=lambda ws, message: self.__on_web_socket_message__(ws, message, yesterday_price_dict, stock_update_callback),
                                            on_error=lambda ws, error: self.__on_web_socket_error__(ws, error),
                                            on_close=lambda ws, close_status_code, close_msg: self.__on_close__(ws, close_status_code, close_msg))

        web_socket.run_forever()

    @staticmethod
    def __on_open__(ws, ticker_list: [str]):
        for ticker in ticker_list:
            ws.send(f'{{"type":"subscribe","symbol":"{ticker.upper()}"}}')

    @staticmethod
    def __on_web_socket_message__(ws, message, yesterday_price_dict, callback):
        try:
            update_obj = json.loads(message)
            if update_obj["type"] == "ping":
                return
            update_ticker = update_obj["data"][0]["s"]
            update_price = update_obj["data"][0]["p"]
            update_time = update_obj["data"][0]["t"]
            yesterday_price = yesterday_price_dict[update_ticker]
            stock_update = LiveStockInfo(update_ticker, update_price, yesterday_price, update_time)
            callback(stock_update)
        except KeyError:
            log("Unable to parse update: " + message)

    @staticmethod
    def __on_web_socket_error__(ws, error):
        log(error)

    @staticmethod
    def __on_close__(ws, close_status_code, close_msg):
        log(f"### closed ### code: {close_status_code} msg: {close_msg}")

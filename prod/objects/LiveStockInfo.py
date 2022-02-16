from prod.objects.StockInfo import StockInfo
import time

class LiveStockInfo:

    ticker = ""
    current_price: float = 0.00
    updated_at_milli: int = 0

    # def __init__(self, ticker, json_data):
    #     self.ticker = ticker
    #     self.current_price = json_data["c"]
    #     self.updated_at_milli = json_data["t"]

    def __init__(self, ticker, price, time):
        self.ticker = ticker
        self.current_price = price
        self.updated_at_milli = time

    @staticmethod
    def map_from_stock_info(stock_info: StockInfo):
        return LiveStockInfo(stock_info.ticker, stock_info.current_price, int(round(time.time() * 1000)))

    def __str__(self) -> str:
        return f'[{self.ticker}: ${self.current_price} at {self.updated_at_milli} millis]'

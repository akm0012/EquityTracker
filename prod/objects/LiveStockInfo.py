from prod.objects.StockInfo import StockInfo
import time


class LiveStockInfo:

    ticker = ""
    current_price: float = 0.00
    previous_close_price: float = 0.00
    updated_at_milli: int = 0

    def __init__(self, ticker, price, previous_close_price, updated_at_milli):
        self.ticker = ticker
        self.current_price = price
        self.previous_close_price = previous_close_price
        self.updated_at_milli = updated_at_milli

    @staticmethod
    def map_from_stock_info(stock_info: StockInfo):
        return LiveStockInfo(
            stock_info.ticker,
            stock_info.current_price,
            stock_info.previous_close_price,
            int(round(time.time() * 1000)))

    def __str__(self) -> str:
        return f'[{self.ticker}: Curr: ${self.current_price} Prev: ${self.previous_close_price} at {self.updated_at_milli} millis]'

from prod.objects.StockInfo import StockInfo
import time


class LiveStockInfo:

    ticker = ""
    current_price: float = 0.00
    previous_close_price: float = 0.00
    updated_at_milli: int = 0
    # Today's open/high/low. Only known from the initial REST quote; websocket ticks leave
    # these at 0.00 and the UI carries the last known values forward for the session.
    day_high: float = 0.00
    day_low: float = 0.00
    open_price: float = 0.00

    def __init__(self, ticker, price, previous_close_price, updated_at_milli,
                 day_high=0.00, day_low=0.00, open_price=0.00):
        self.ticker = ticker
        self.current_price = price
        self.previous_close_price = previous_close_price
        self.updated_at_milli = updated_at_milli
        self.day_high = day_high
        self.day_low = day_low
        self.open_price = open_price

    @staticmethod
    def map_from_stock_info(stock_info: StockInfo):
        return LiveStockInfo(
            stock_info.ticker,
            stock_info.current_price,
            stock_info.previous_close_price,
            int(round(time.time() * 1000)),
            stock_info.day_high,
            stock_info.day_low,
            stock_info.open_price)

    def __str__(self) -> str:
        return f'[{self.ticker}: Curr: ${self.current_price} Prev: ${self.previous_close_price} at {self.updated_at_milli} millis]'

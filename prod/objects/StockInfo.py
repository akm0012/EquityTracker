class StockInfo:

    ticker = ""
    current_price: float = 0.00
    price_change: float = 0.00
    percent_change: float = 0.00
    day_high: float = 0.00
    day_low: float = 0.00
    open_price: float = 0.00
    previous_close_price: float = 0.00
    updated_at_seconds: int = 0

    def __init__(self, ticker, json_data):
        self.ticker = ticker
        self.current_price = json_data["c"]
        self.price_change = json_data["d"]
        self.percent_change = json_data["dp"]
        self.day_high = json_data["h"]
        self.day_low = json_data["l"]
        self.open_price = json_data["o"]
        self.previous_close_price = json_data["pc"]
        self.updated_at_seconds = json_data["t"]

    def __str__(self) -> str:
        return f'{self.ticker}\n' \
               f'Current: {self.current_price}'


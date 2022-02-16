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

    def __str__(self) -> str:
        return f'{self.ticker}\n' \
               f'Current: {self.current_price}\n' \
               f'Updated at: {self.updated_at_milli} millis'

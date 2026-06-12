from prod.objects.StockGrant import StockGrant


class StockGrantCollection:

    ticker = ""
    # Optional group label this row represents (see StockGrant.group).
    group = ""
    stock_grant_list = [StockGrant]

    # If true, we are only tracking this Stock and don't have any monetary grants in it.
    is_tracking_stock_only = True

    def __init__(self, ticker: str, group: str = ""):
        self.ticker = ticker
        self.group = group
        self.stock_grant_list = []

    def add_stock_grant(self, stock_grant: StockGrant):
        if stock_grant.count > 0:
            self.is_tracking_stock_only = False
        self.stock_grant_list.append(stock_grant)

    """
    Total current value of every grant in this row, based on the current stock price.
    """
    def get_total_value(self, current_price: float) -> float:
        total = 0.0
        for grant in self.stock_grant_list:
            total += grant.count * current_price
        return total

    """
    Unrealized gain/loss for this row: current value minus what the grants were worth at their
    grant price. Positive means the grants are up since they were granted.
    """
    def get_unrealized_gain(self, current_price: float) -> float:
        gain = 0.0
        for grant in self.stock_grant_list:
            gain += grant.count * (current_price - grant.price)
        return gain

    """
    Value of the next vest for this row only. Grants on separate rows vest on their own
    schedule, so only the grants in this collection are summed.
    """
    def get_next_vest_value(self, current_price: float) -> float:
        next_vest_total = 0.0
        for grant in self.stock_grant_list:
            if grant.vests_left == 0:
                continue
            next_vest_total += (grant.count * current_price) / grant.vests_left
        return next_vest_total

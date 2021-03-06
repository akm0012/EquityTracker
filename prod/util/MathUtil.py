from prod.objects.StockGrant import StockGrant


"""
Calculates the difference in percent of two numbers. 
IE: 50 -> 100 = 100%
    100 -> 50 = -50% 
"""
def calculate_percent_change(start: float, end: float) -> float:
    difference = end / start
    percent = difference * 100
    percent = percent - 100
    return round(percent, 2)


"""
Calculates the percent difference of a grant and it's current stock price. 
IE: current_stock_price = $60.00
    grant_price = $50.00
    shares = 2000

    Percent Difference = 20%
"""
def calculate_grant_percent_change(current_stock_price: float,
                                   num_of_shares: int,
                                   grant_share_price: float) -> float:
    current_grant_price = current_stock_price * num_of_shares
    original_grant_price = grant_share_price * num_of_shares

    percent_change = calculate_percent_change(original_grant_price, current_grant_price)
    return round(percent_change, 2)


def calculate_grant_percent_change_2(current_stock_price: float, stock_grant: StockGrant) -> float:
    return calculate_grant_percent_change(current_stock_price, stock_grant.count, stock_grant.price)

"""
Calculates the dollar difference of a grant and it's current stock price. 
IE: current_stock_price = $60.00
    grant_price = $50.00
    shares = 2000

    Dollar Difference = $20,000
"""
def calculate_grant_dollar_change(current_stock_price: float,
                                    num_of_shares: int,
                                    grant_share_price: float) -> float:
    current_grant_price = current_stock_price * num_of_shares
    original_grant_price = grant_share_price * num_of_shares

    dollar_change = current_grant_price - original_grant_price
    return round(dollar_change, 2)

"""
Calculates the percent difference of a list of grants and it's current stock price. 
IE: current_stock_price = $60.00
    
    grant_1 = StockGrant("TWTR", 2000, 50)
    grant_2 = StockGrant("TWTR", 100, 70)

    Percent Difference = 17.76%
"""
def calculate_multi_grant_percent_change(current_stock_price: float,
                                         stock_grant_list: list[StockGrant]):
    # Make sure all grants are for the same stock
    ticker = stock_grant_list[0].ticker
    for stock in stock_grant_list:
        if stock.ticker != ticker:
            raise ValueError("All Stocks must have the same Ticker.")

    original_total_grant_price = 0
    current_total_grant_price = 0
    for stock in stock_grant_list:
        original_total_grant_price += stock.price * stock.count
        current_total_grant_price += current_stock_price * stock.count

    total_percent_change = calculate_percent_change(original_total_grant_price, current_total_grant_price)
    return round(total_percent_change, 2)


"""
Calculates the dollar difference of a list of grants and it's current stock price. 
IE: current_stock_price = $60.00

    grant_1 = StockGrant("TWTR", 2000, 50)
    grant_2 = StockGrant("TWTR", 100, 70)

    Dollar Difference = $19,000
"""
def calculate_multi_grant_dollar_change(current_stock_price: float,
                                         stock_grant_list: list[StockGrant]):
    # Make sure all grants are for the same stock
    ticker = stock_grant_list[0].ticker
    for stock in stock_grant_list:
        if stock.ticker != ticker:
            raise ValueError("All Stocks must have the same Ticker.")

    original_total_grant_price = 0
    current_total_grant_price = 0
    for stock in stock_grant_list:
        original_total_grant_price += stock.price * stock.count
        current_total_grant_price += current_stock_price * stock.count

    total_dollar_change = current_total_grant_price - original_total_grant_price
    return round(total_dollar_change, 2)


"""
This will simply add up the current value of a list of grants. Based on the current stock price. 
"""
def calculate_multi_grant_dollar_amount(current_stock_price: float,
                                        stock_grant_list: list[StockGrant]) -> float:
    total_amount = 0
    for grant in stock_grant_list:
        total_amount += grant.count * current_stock_price

    return total_amount


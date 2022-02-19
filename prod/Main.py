import argparse
import sys

from prod.network.ApiService import ApiService
from prod.objects.StockGrant import StockGrant
from prod.objects.StockPortfolio import StockPortfolio
from prod.repository.ConfigRepository import ConfigRepository
from prod.repository.StockRepository import StockRepository
from prod.resources import Strings
from prod.util.LogUtil import log


class Main:

    config_repo = ConfigRepository()
    stock_repo = StockRepository(ApiService(config_repo))

    def process_arguments(self):
        parser = argparse.ArgumentParser(description=Strings.HELP_DESC)

        # Adding optional argument
        parser.add_argument("-t", "--Token", help=Strings.ARG_TOKEN_HELP)
        parser.add_argument("-r", "--Reset", action='store_true', help=Strings.ARG_RESET_HELP)
        parser.add_argument("--NUKE", action='store_true', help=Strings.ARG_NUKE_HELP)

        args = parser.parse_args()

        if args.Token:
            self.config_repo.save_finnhub_api_key(args.Token)
            print("Finnhub API Token saved.")
        elif args.Reset:
            self.config_repo.clear_stocks()
            print("Stocks and equity cleared.")
        elif args.NUKE:
            self.config_repo.create_empty_config_file()
            print("Config file blown away and reset.")

        return args


def get_api_token_from_user():
    # If there is already a token, we can skip this.
    if main.config_repo.get_finnhub_api_key() != "":
        return

    is_token_valid = False
    while not is_token_valid:
        finnhub_api_token = input(Strings.FINNHUB_INPUT_MSG)
        is_api_key_valid = main.stock_repo.is_finnhub_api_key_valid(finnhub_api_token)
        if is_api_key_valid:
            is_token_valid = True
            main.config_repo.save_finnhub_api_key(finnhub_api_token)
            print(Strings.FINNHUB_TOKEN_OK)
        else:
            print(Strings.FINNHUB_TOKEN_ERROR)


if __name__ == '__main__':
    main = Main()
    main.process_arguments()
    if len(sys.argv) > 1:
        sys.exit()

    # Step 1 - Welcome Message!
    print(Strings.WELCOME_MSG)

    # Step 2 - Get Finnhub API Token
    get_api_token_from_user()

    # Step 3 - Get Stocks / Grants
    print(Strings.GET_STOCK_MSG)
    portfolio = StockPortfolio()

# todo - Loop 1 asking if they want to enter more Stocks

    # Get the Stock Ticker
    is_stock_valid = False
    stock_ticker = ""
    while not is_stock_valid:
        stock_ticker = input(Strings.GET_STOCK_INPUT_MSG)
        stock_ticker.upper()
        if main.stock_repo.is_ticker_symbol_valid(stock_ticker):
            is_stock_valid = True
        else:
            print(Strings.GET_STOCK_ERROR)

# todo - Loop 2 asking if they want to enter more grants for stock_ticker

    # Get the grant number
    is_grant_count_valid = False
    grant_count = 0
    while not is_grant_count_valid:
        grant_count = input(Strings.GET_GRANTS_INPUT)
        try:
            grant_count = int(grant_count)
            is_grant_count_valid = True
        except:
            print(Strings.NOT_A_NUM_ERROR)

    # Get price of stock for grant
    grant_price = 0.0
    if grant_count > 0:
        is_grant_price_valid = False
        while not is_grant_price_valid:
            grant_price = input(Strings.GET_GRANTS_COST_INPUT)
            try:
                grant_price = float(grant_price)
                is_grant_price_valid = True
            except:
                print(Strings.NOT_A_NUM_ERROR)

    stock_grant = StockGrant(stock_ticker, grant_count, grant_price)
    log(stock_grant)

# todo - End Loop 2
# todo - End Loop 1











    # Step 3 - Ask for Stocks


    log("Main done.")







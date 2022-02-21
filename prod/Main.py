import argparse
import signal
import sys
import curses
from curses import wrapper

from prod.network.ApiService import ApiService
from prod.objects.StockGrant import StockGrant
from prod.objects.StockPortfolio import StockPortfolio
from prod.repository.ConfigRepository import ConfigRepository
from prod.repository.StockRepository import StockRepository
from prod.resources import Strings
from prod.util.LogUtil import log


def process_arguments():
    parser = argparse.ArgumentParser(description=Strings.HELP_DESC)

    # Adding optional argument
    parser.add_argument("-t", "--Token", help=Strings.ARG_TOKEN_HELP)
    parser.add_argument("-r", "--Reset", action='store_true', help=Strings.ARG_RESET_HELP)
    parser.add_argument("--NUKE", action='store_true', help=Strings.ARG_NUKE_HELP)

    args = parser.parse_args()

    if args.Token:
        config_repo.save_finnhub_api_key(args.Token)
        print("Finnhub API Token saved.")
    elif args.Reset:
        config_repo.clear_stocks()
        print("Stocks and equity cleared.")
    elif args.NUKE:
        config_repo.create_empty_config_file()
        print("Config file blown away and reset.")

    return args


def get_api_token_from_user():
    # If there is already a token, we can skip this.
    if config_repo.get_finnhub_api_key() != "":
        print(Strings.FINNHUB_TOKEN_EXIST)
        return

    is_token_valid = False
    while not is_token_valid:
        finnhub_api_token = input(Strings.FINNHUB_INPUT_MSG)
        is_api_key_valid = stock_repo.is_finnhub_api_key_valid(finnhub_api_token)
        if is_api_key_valid:
            is_token_valid = True
            config_repo.save_finnhub_api_key(finnhub_api_token)
            print(Strings.FINNHUB_TOKEN_OK)
        else:
            print(Strings.FINNHUB_TOKEN_ERROR)


def get_stock_portfolio_from_user() -> StockPortfolio:
    print(Strings.GET_STOCK_MSG)
    portfolio = StockPortfolio()

    # Loop asking for Stocks to add
    more_stocks_to_add = True
    while more_stocks_to_add:

        # Get the Stock Ticker
        stock_ticker = get_stock_ticker_from_user()

        get_stock_grants_from_user(portfolio, stock_ticker)

        more_stocks_to_add = prompt_user_yes_or_no(Strings.MORE_STOCKS_TO_ADD)

    return portfolio


def get_stock_grants_from_user(portfolio, stock_ticker):
    more_grants_to_add = True
    while more_grants_to_add:
        # Get the grant number
        grant_count = get_grant_count_from_user()

        # Get price of stock for grant
        grant_price = get_grant_price(grant_count)

        # Add stock grant to Portfolio
        stock_grant = StockGrant(stock_ticker, grant_count, grant_price)
        print(f"Adding {stock_grant} to portfolio.")
        portfolio.add_stock_grant(stock_grant)
        more_grants_to_add = grant_count != 0 and prompt_user_yes_or_no(Strings.MORE_GRANTS_TO_ADD % stock_ticker)


def get_grant_price(grant_count) -> float:
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
    return grant_price


def get_grant_count_from_user() -> int:
    is_grant_count_valid = False
    grant_count = 0
    while not is_grant_count_valid:
        grant_count = input(Strings.GET_GRANTS_INPUT)
        try:
            grant_count = int(grant_count)
            is_grant_count_valid = True
        except:
            print(Strings.NOT_A_NUM_ERROR)
    return grant_count


def get_stock_ticker_from_user() -> str:
    is_stock_valid = False
    stock_ticker = ""
    while not is_stock_valid:
        stock_ticker = input(Strings.GET_STOCK_INPUT_MSG)
        stock_ticker.upper()
        if stock_repo.is_ticker_symbol_valid(stock_ticker):
            is_stock_valid = True
        else:
            print(Strings.GET_STOCK_ERROR)
    return stock_ticker


def prompt_user_yes_or_no(yes_or_no_prompt: str) -> bool:
    while True:
        yes_or_no_input = input(yes_or_no_prompt)
        if yes_or_no_input == 'Y' or yes_or_no_input == 'y' or yes_or_no_input.lower() == 'yes':
            return True
        elif yes_or_no_input == 'N' or yes_or_no_input == 'n' or yes_or_no_input.lower() == 'no':
            return False
        else:
            print(Strings.YES_OR_NO_ERROR)

# Gets the X coordinate for a specific column
def get_x_coord_for_column(column: int) -> int:
    if column == 0:
        return 0
    elif column == 1:
        return 8
    else:
        return 8 + ((column - 1) * 18)


def curses_main(stdscr):

    stdscr.clear()

    draw_headers(stdscr)


    stdscr.refresh()

    # Any char will stop the program
    stdscr.getch()


def draw_headers(stdscr):
    max_grant_count = config_repo.get_stock_portfolio().get_max_grant_count()
    stdscr.addstr(0, get_x_coord_for_column(1), Strings.CURRENT)
    # Add the "Grant #" Headers
    for i in range(max_grant_count):
        grant_header_text = Strings.GRANT_HEADER % (i + 1)
        stdscr.addstr(0, get_x_coord_for_column(i + 2), grant_header_text)
    # Add the total Header
    stdscr.addstr(0, get_x_coord_for_column(max_grant_count + 2), Strings.TOTAL)


if __name__ == '__main__':
    # Hides the stack trace when you stop the program with control+c
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

    config_repo = ConfigRepository()
    stock_repo = StockRepository(ApiService(config_repo))

    # Look for command line arguments, if we find any, cancel execution
    process_arguments()
    if len(sys.argv) > 1:
        sys.exit()

    # Check is there is already a portfolio
    if len(config_repo.is_config_file_valid() and
           config_repo.get_stock_portfolio().get_all_stock_grants()) > 0:
        input(Strings.USING_PORTFOLIO_MSG)

    else:
        # Step 1 - Welcome Message!
        print(Strings.WELCOME_MSG)

        # Step 2 - Get Finnhub API Token
        get_api_token_from_user()

        # Step 3 - Get Stocks / Grants
        stock_portfolio = get_stock_portfolio_from_user()
        # Save the portfolio in the config file
        config_repo.save_stock_portfolio(stock_portfolio)

    # Todo: show a countdown timer and maybe some instructions on how to exit

    # This is where all the UI magic happens! View CursesSandboxes for some examples.
    wrapper(curses_main)
    log("Main done.")







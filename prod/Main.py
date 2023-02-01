import argparse
import signal
import sys
import curses
from _curses import curs_set
from curses import wrapper

from prod.network.ApiService import ApiService
from prod.objects.LiveStockInfo import LiveStockInfo
from prod.objects.StockGrant import StockGrant
from prod.objects.StockGrantCollection import StockGrantCollection
from prod.objects.StockPortfolio import StockPortfolio
from prod.repository.ConfigRepository import ConfigRepository
from prod.repository.StockRepository import StockRepository
from prod.resources import Strings
from prod.util import MathUtil
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
            if grant_price[0] == '$':
                grant_price = grant_price[1:]
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
    current_header_x = 8
    header_1_width = 20
    header_normal_padding = 25

    if column == 0:
        return 0
    elif column == 1:
        return current_header_x
    elif column == 2:
        return current_header_x + header_1_width
    else:
        return current_header_x + header_1_width + ((column - 2) * header_normal_padding)


def curses_main(stdscr):
    # Use the default terminal colors! Cool!
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # -1 for default color
    curses.init_pair(2, curses.COLOR_RED, -1)

    # Hide the cursor
    curs_set(0)

    portfolio = config_repo.get_stock_portfolio()

    stdscr.clear()

    draw_headers(stdscr)

    stdscr.refresh()

    # Create a dict of Windows and Ticker symbols and update it when live updates come in
    # This holds {TWTR: Window}, where the Window is the "View" that will be written to whenever a TWTR update happens.
    stock_window_dict = {}

    # Create windows for all the Stocks in the Portfolio
    window_row = 1
    for stock_grant_collection in portfolio.get_all_stock_grant_collections():
        ticker_symbol = stock_grant_collection.ticker
        width = curses.COLS - 1  # The entire width of the window
        # Window size = h, w.  Location = y, x
        stock_row_window = curses.newwin(1, width, window_row, 0)
        window_row += 1
        stock_window_dict[ticker_symbol] = stock_row_window

    stock_repo.listen_for_portfolio_updates(
        portfolio, lambda live_stock_update: update_ui_with_live_stock_info(portfolio, stock_window_dict, live_stock_update))

    # This line never seems to be hit...


def update_ui_with_live_stock_info(portfolio: StockPortfolio, stock_window_dict, update: LiveStockInfo):
    stock_window = stock_window_dict[update.ticker]
    stock_window.clear()
    update_stock_window_with_new_data(stock_window, update, portfolio)
    stock_window.refresh()


# Reminder, this is what it should look like.
#         Current          Grant 1             Grant 2             Total
# TWTR    $36.23  (2.4%)   $50,000 (-50.5%)    $20,000 (+23.3%)    $70,000 (-36.3%)
#
def update_stock_window_with_new_data(stock_window,
                                      stock_update: LiveStockInfo,
                                      stock_portfolio: StockPortfolio):
    GREEN = curses.color_pair(1)
    RED = curses.color_pair(2)

    ticker = stock_update.ticker

    stock_grant_collection = stock_portfolio.get_stock_grant_collection(ticker)

    # Add the ticker at the beginning
    stock_window.addstr(0, 0, f"{ticker}")

    # Add the Current Price / percent change
    current_price = round(stock_update.current_price, 2)
    percent_change = MathUtil.calculate_percent_change(stock_update.previous_close_price, current_price)
    percent_color = GREEN if percent_change >= 0 else RED
    stock_window.addstr(0, get_x_coord_for_column(1), "${:,.2f}".format(current_price))
    stock_window.addstr(0, get_x_coord_for_column(1) + 9, f"({format(percent_change, '.2f')} %)", percent_color)

    # Add the Grants
    stock_grant_column = 2
    for grant in stock_grant_collection.stock_grant_list:
        if grant.count == 0:
            continue
        current_grant_value = grant.count * stock_update.current_price
        current_grant_percent_change = MathUtil.calculate_grant_percent_change_2(stock_update.current_price, grant)
        percent_color = GREEN if current_grant_percent_change >= 0 else RED
        column_x_coord = get_x_coord_for_column(stock_grant_column)
        current_grant_value_str = "${:,.2f}".format(current_grant_value)
        stock_window.addstr(0, column_x_coord, current_grant_value_str)
        stock_window.addstr(0, column_x_coord + len(current_grant_value_str) + 1,
                            f"({format(current_grant_percent_change, '.2f')} %)", percent_color)
        stock_grant_column += 1

    # Add the Total Column
    max_grant_count = stock_portfolio.get_max_grant_count()
    if max_grant_count != 0:
        total_column = max_grant_count + 2
        total_grant_value = MathUtil.calculate_multi_grant_dollar_amount(stock_update.current_price,
                                                                         stock_grant_collection.stock_grant_list)
        total_grant_value_str = "${:,.2f}".format(total_grant_value)
        # This will change each vesting period, so prob not worth
        total_vest_periods_left = 16
        if total_grant_value > 0:
            next_vest_amount_str = total_grant_value/total_vest_periods_left
            total_grant_value_str += " (${:,.2f})".format(next_vest_amount_str)

        stock_window.addstr(0, get_x_coord_for_column(total_column), total_grant_value_str)


def draw_headers(stdscr):
    max_grant_count = config_repo.get_stock_portfolio().get_max_grant_count()
    stdscr.addstr(0, get_x_coord_for_column(1), Strings.CURRENT, curses.A_UNDERLINE)

    if max_grant_count == 0:
        return

    # Add the "Grant #" Headers
    for i in range(max_grant_count):
        grant_header_text = Strings.GRANT_HEADER % (i + 1)
        stdscr.addstr(0, get_x_coord_for_column(i + 2), grant_header_text, curses.A_UNDERLINE)
    # Add the total Header
    stdscr.addstr(0, get_x_coord_for_column(max_grant_count + 2), Strings.TOTAL, curses.A_UNDERLINE)


if __name__ == '__main__':
    # Hides the stack trace when you stop the program with control+c
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

    config_repo = ConfigRepository()
    stock_repo = StockRepository(ApiService(config_repo))

    # Look for command line arguments, if we find any, cancel execution
    process_arguments()
    if len(sys.argv) > 1:
        sys.exit()

    # Init the config file if it is not there
    if not config_repo.does_config_file_exist():
        log("Creating Empty Config File")
        config_repo.create_empty_config_file()

    # Check is there is already a portfolio
    if config_repo.is_config_file_valid() and len(config_repo.get_stock_portfolio().get_all_stock_grants()) > 0:
        print(Strings.USING_PORTFOLIO_MSG)

    else:
        # Step 1 - Welcome Message!
        print(Strings.WELCOME_MSG)

        # Step 2 - Get Finnhub API Token
        get_api_token_from_user()

        # Step 3 - Get Stocks / Grants
        stock_portfolio_from_user = get_stock_portfolio_from_user()
        # Save the portfolio in the config file
        config_repo.save_stock_portfolio(stock_portfolio_from_user)

    # Todo: show a countdown timer and maybe some instructions on how to exit
# Todo: Disabled for now as I know how to exit
#    input(Strings.START_STOCK_UI_MSG)

    # This is where all the UI magic happens! View CursesSandboxes for some examples.
    wrapper(curses_main)
    log("Main done.")

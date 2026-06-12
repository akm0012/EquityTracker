import argparse
import locale
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
from prod.util import ChartUtil
from prod.util import MathUtil
from prod.util.LogUtil import log

# Layout for the trailing visualizations, measured from the Total column.
GAUGE_OFFSET_FROM_TOTAL = 28
GAIN_OFFSET_FROM_GAUGE = 36
GAUGE_WIDTH = 10


class TickerSession:
    """Per-ticker data cached for the life of the session (since the app was opened)."""

    def __init__(self):
        self.day_high = 0.0
        self.day_low = 0.0
        self.open_price = 0.0
        self.previous_close = 0.0
        self.latest_price = 0.0

    def record(self, update: LiveStockInfo):
        # The day OHLC is only present on the initial REST quote; carry it forward.
        if update.day_high:
            self.day_high = update.day_high
        if update.day_low:
            self.day_low = update.day_low
        if update.open_price:
            self.open_price = update.open_price
        if update.previous_close_price:
            self.previous_close = update.previous_close_price

        price = update.current_price
        if price <= 0:
            return

        self.latest_price = price

        # Keep the day range honest as live ticks move beyond the morning quote.
        if self.day_high == 0 or price > self.day_high:
            self.day_high = price
        if self.day_low == 0 or price < self.day_low:
            self.day_low = price


def safe_addstr(window, y: int, x: int, text: str, attr: int = 0):
    """Write text but clip to the window so far-right visuals never crash a narrow terminal."""
    if not text:
        return
    max_y, max_x = window.getmaxyx()
    if y >= max_y or x < 0 or x >= max_x:
        return
    available = max_x - x - 1
    if available <= 0:
        return
    try:
        window.addstr(y, x, text[:available], attr)
    except curses.error:
        pass


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


def parse_non_negative_int(raw_value: str) -> int:
    try:
        value = int(raw_value.strip())
    except ValueError:
        raise ValueError(Strings.NON_NEGATIVE_INT_ERROR)
    if value < 0:
        raise ValueError(Strings.NON_NEGATIVE_INT_ERROR)
    return value


def parse_positive_float(raw_value: str) -> float:
    normalized_value = raw_value.strip()
    if normalized_value.startswith('$'):
        normalized_value = normalized_value[1:]
    try:
        value = float(normalized_value.replace(",", ""))
    except ValueError:
        raise ValueError(Strings.POSITIVE_PRICE_ERROR)
    if value <= 0:
        raise ValueError(Strings.POSITIVE_PRICE_ERROR)
    return value


def normalize_optional_group(raw_value: str) -> str:
    group = raw_value.strip()
    if "," in group:
        raise ValueError(Strings.GROUP_LABEL_COMMA_ERROR)
    return group


def get_api_token_from_user():
    # If there is already a token, we can skip this.
    if config_repo.get_finnhub_api_key() != "":
        print(Strings.FINNHUB_TOKEN_EXIST)
        return

    is_token_valid = False
    while not is_token_valid:
        finnhub_api_token = input(Strings.FINNHUB_INPUT_MSG).strip()
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
    has_existing_grants_for_ticker = False
    while more_grants_to_add:
        # Get the grant number
        grant_count = get_grant_count_from_user()

        if grant_count == 0:
            stock_grant = StockGrant(stock_ticker, 0, 0.0, 0)
            print(Strings.ADDING_WATCH_ONLY_STOCK % stock_ticker)
            portfolio.add_stock_grant(stock_grant)
            return

        # Get price of stock for grant
        grant_price = get_grant_price(grant_count)

        # Get number of vests left for this Grant
        vests_left = get_num_of_vests_left_from_user()

        group = get_grant_group_from_user(stock_ticker, has_existing_grants_for_ticker)

        # Add stock grant to Portfolio
        stock_grant = StockGrant(stock_ticker, grant_count, grant_price, vests_left, group)
        print(f"Adding {stock_grant} to portfolio.")
        portfolio.add_stock_grant(stock_grant)
        has_existing_grants_for_ticker = True
        more_grants_to_add = prompt_user_yes_or_no(Strings.MORE_GRANTS_TO_ADD % stock_ticker)


def get_grant_price(grant_count) -> float:
    grant_price = 0.0
    if grant_count > 0:
        is_grant_price_valid = False
        while not is_grant_price_valid:
            grant_price = input(Strings.GET_GRANTS_COST_INPUT)
            try:
                grant_price = parse_positive_float(grant_price)
                is_grant_price_valid = True
            except ValueError as error:
                print(error)
    return grant_price


def get_num_of_vests_left_from_user() -> int:
    is_num_of_vests_valid = False
    vest_count = 0
    while not is_num_of_vests_valid:
        vest_count = input(Strings.GET_NUM_OF_VESTS_INPUT)
        try:
            vest_count = parse_non_negative_int(vest_count)
            is_num_of_vests_valid = True
        except ValueError as error:
            print(error)
    return vest_count


def get_grant_count_from_user() -> int:
    is_grant_count_valid = False
    grant_count = 0
    while not is_grant_count_valid:
        grant_count = input(Strings.GET_GRANTS_INPUT)
        try:
            grant_count = parse_non_negative_int(grant_count)
            is_grant_count_valid = True
        except ValueError as error:
            print(error)
    return grant_count


def get_grant_group_from_user(stock_ticker: str, has_existing_grants_for_ticker: bool = False) -> str:
    group_prompt = Strings.GET_GRANT_GROUP_INPUT if not has_existing_grants_for_ticker \
        else Strings.GET_ADDITIONAL_GRANT_GROUP_INPUT % stock_ticker
    while True:
        group = input(group_prompt)
        try:
            return normalize_optional_group(group)
        except ValueError as error:
            print(error)


def get_stock_ticker_from_user() -> str:
    is_stock_valid = False
    stock_ticker = ""
    while not is_stock_valid:
        stock_ticker = input(Strings.GET_STOCK_INPUT_MSG).strip().upper()
        if stock_repo.is_ticker_symbol_valid(stock_ticker):
            is_stock_valid = True
        else:
            print(Strings.GET_STOCK_ERROR)
    return stock_ticker


def prompt_user_yes_or_no(yes_or_no_prompt: str) -> bool:
    while True:
        yes_or_no_input = input(yes_or_no_prompt).strip()
        if yes_or_no_input == "":
            return True
        if yes_or_no_input == 'Y' or yes_or_no_input == 'y' or yes_or_no_input.lower() == 'yes':
            return True
        elif yes_or_no_input == 'N' or yes_or_no_input == 'n' or yes_or_no_input.lower() == 'no':
            return False
        else:
            print(Strings.YES_OR_NO_ERROR)


def render_portfolio_summary(portfolio: StockPortfolio, config_path: str) -> str:
    summary_lines = [
        Strings.SAVED_PORTFOLIO_MSG % config_path,
        "",
        Strings.PORTFOLIO_SUMMARY_HEADER,
    ]

    for grant in portfolio.get_all_stock_grants():
        if grant.count == 0:
            summary_lines.append(Strings.PORTFOLIO_SUMMARY_WATCH_ONLY % grant.ticker)
            continue

        grant_summary = Strings.PORTFOLIO_SUMMARY_GRANT % (
            grant.ticker,
            grant.count,
            grant.price,
            grant.vests_left)
        if grant.group:
            grant_summary += Strings.PORTFOLIO_SUMMARY_GROUP % grant.group
        summary_lines.append(grant_summary)

    return "\n".join(summary_lines)


def print_setup_summary(portfolio: StockPortfolio):
    print(render_portfolio_summary(portfolio, config_repo.get_config_file_location()))


def prompt_start_tracker() -> bool:
    return prompt_user_yes_or_no(Strings.START_TRACKER_PROMPT)


def print_config_parse_errors(parse_errors: list[str]):
    for parse_error in parse_errors:
        print(Strings.CONFIG_ROW_PARSE_ERROR % parse_error)


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


# X coordinate of the day-range gauge, just past the Total column.
def get_gauge_x(max_grant_count: int) -> int:
    return get_x_coord_for_column(max_grant_count + 2) + GAUGE_OFFSET_FROM_TOTAL


# X coordinate of the unrealized gain/loss column, just past the gauge.
def get_gain_x(max_grant_count: int) -> int:
    return get_gauge_x(max_grant_count) + GAIN_OFFSET_FROM_GAUGE


def curses_main(stdscr):
    # Use the default terminal colors! Cool!
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # -1 for default color
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)

    # Hide the cursor
    curs_set(0)

    portfolio = config_repo.get_stock_portfolio()

    stdscr.clear()

    draw_headers(stdscr)

    stdscr.refresh()

    # Pair each row's grant collection with its own window. We key by row (not ticker)
    # because a single ticker can span multiple rows when grants are split into groups.
    row_windows = []  # list of (StockGrantCollection, window)

    # Create windows for all the rows in the Portfolio
    window_row = 1
    for stock_grant_collection in portfolio.get_all_stock_grant_collections():
        width = curses.COLS - 1  # The entire width of the window
        # Window size = h, w.  Location = y, x
        stock_row_window = curses.newwin(1, width, window_row, 0)
        window_row += 1
        row_windows.append((stock_grant_collection, stock_row_window))

    # A blank line then a footer row for the portfolio-wide totals (if there's room).
    footer_window = None
    if window_row + 1 < curses.LINES:
        footer_window = curses.newwin(1, curses.COLS - 1, window_row + 1, 0)

    # A connection status line below the footer (if there's room).
    status_window = None
    if window_row + 2 < curses.LINES:
        status_window = curses.newwin(1, curses.COLS - 1, window_row + 2, 0)

    # Cached per-ticker session data (price history, day range, latest price...).
    ticker_state = {}

    stock_repo.listen_for_portfolio_updates(
        portfolio,
        lambda live_stock_update: update_ui_with_live_stock_info(
            portfolio, row_windows, ticker_state, footer_window, live_stock_update),
        lambda status: draw_status(status_window, status))

    # This line never seems to be hit...


def update_ui_with_live_stock_info(portfolio: StockPortfolio, row_windows, ticker_state,
                                   footer_window, update: LiveStockInfo):
    session = ticker_state.setdefault(update.ticker, TickerSession())
    session.record(update)

    # A price update is per-ticker, so refresh every row that tracks this ticker.
    for stock_grant_collection, stock_window in row_windows:
        if stock_grant_collection.ticker != update.ticker:
            continue
        stock_window.clear()
        update_stock_window_with_new_data(stock_window, update, stock_grant_collection, portfolio, session)
        stock_window.refresh()

    # Refresh the portfolio total footer with every ticker's latest known price.
    if footer_window is not None:
        draw_footer(footer_window, portfolio, ticker_state)


# Reminder, this is what it should look like.
#         Current          Grant 1             Grant 2             Total
# TWTR    $36.23  (2.4%)   $50,000 (-50.5%)    $20,000 (+23.3%)    $70,000 (-36.3%)
#
def update_stock_window_with_new_data(stock_window,
                                      stock_update: LiveStockInfo,
                                      stock_grant_collection: StockGrantCollection,
                                      stock_portfolio: StockPortfolio,
                                      session: TickerSession):
    GREEN = curses.color_pair(1)
    RED = curses.color_pair(2)

    ticker = stock_update.ticker

    # Add the ticker at the beginning
    safe_addstr(stock_window, 0, 0, f"{ticker}")

    # Add the Current Price / percent change
    current_price = round(stock_update.current_price, 2)
    percent_change = MathUtil.calculate_percent_change(stock_update.previous_close_price, current_price)
    percent_color = GREEN if percent_change >= 0 else RED
    safe_addstr(stock_window, 0, get_x_coord_for_column(1), "${:,.2f}".format(current_price))
    safe_addstr(stock_window, 0, get_x_coord_for_column(1) + 9, f"({format(percent_change, '.2f')} %)", percent_color)

    # Add the Grants
    stock_grant_column = 2
    for grant in stock_grant_collection.stock_grant_list:
        if grant.count == 0:
            continue
        current_grant_value = grant.count * stock_update.current_price
        current_grant_percent_change = MathUtil.calculate_grant_percent_change_2(stock_update.current_price, grant)
        grant_color = GREEN if current_grant_percent_change >= 0 else RED
        column_x_coord = get_x_coord_for_column(stock_grant_column)
        current_grant_value_str = "${:,.2f}".format(current_grant_value)
        safe_addstr(stock_window, 0, column_x_coord, current_grant_value_str)
        safe_addstr(stock_window, 0, column_x_coord + len(current_grant_value_str) + 1,
                    f"({format(current_grant_percent_change, '.2f')} %)", grant_color)
        stock_grant_column += 1

    # Add the Total Column
    max_grant_count = stock_portfolio.get_max_grant_count()
    if max_grant_count != 0:
        total_column = max_grant_count + 2
        # Totals are scoped to this row's grants only, so split rows vest independently.
        total_grant_value = stock_grant_collection.get_total_value(stock_update.current_price)
        total_grant_value_str = "${:,.2f}".format(total_grant_value)

        if total_grant_value > 0:
            next_vest_amount_str = stock_grant_collection.get_next_vest_value(current_price)
            total_grant_value_str += " (${:,.2f})".format(next_vest_amount_str)

        safe_addstr(stock_window, 0, get_x_coord_for_column(total_column), total_grant_value_str)

    # Day range gauge: where today's price sits between its low and high.
    gauge_str = ChartUtil.render_range_gauge(session.day_low, session.day_high, current_price, GAUGE_WIDTH)
    safe_addstr(stock_window, 0, get_gauge_x(max_grant_count), gauge_str)

    # Unrealized gain/loss: how much this row's grants are up/down since they were granted.
    if not stock_grant_collection.is_tracking_stock_only:
        unrealized_gain = stock_grant_collection.get_unrealized_gain(stock_update.current_price)
        gain_color = GREEN if unrealized_gain >= 0 else RED
        gain_arrow = "▲" if unrealized_gain >= 0 else "▼"
        gain_str = "{} ${:,.2f}".format(gain_arrow, abs(unrealized_gain))
        safe_addstr(stock_window, 0, get_gain_x(max_grant_count), gain_str, gain_color)


def draw_headers(stdscr):
    max_grant_count = config_repo.get_stock_portfolio().get_max_grant_count()
    safe_addstr(stdscr, 0, get_x_coord_for_column(1), Strings.CURRENT, curses.A_UNDERLINE)

    if max_grant_count != 0:
        # Add the "Grant #" Headers
        for i in range(max_grant_count):
            grant_header_text = Strings.GRANT_HEADER % (i + 1)
            safe_addstr(stdscr, 0, get_x_coord_for_column(i + 2), grant_header_text, curses.A_UNDERLINE)
        # Add the total Header
        safe_addstr(stdscr, 0, get_x_coord_for_column(max_grant_count + 2), Strings.TOTAL, curses.A_UNDERLINE)

    # Header for the day range gauge (shown for grants and watch-only rows).
    safe_addstr(stdscr, 0, get_gauge_x(max_grant_count), Strings.DAY_RANGE, curses.A_UNDERLINE)
    # The gain/loss column only applies to rows that actually hold grants.
    if max_grant_count != 0:
        safe_addstr(stdscr, 0, get_gain_x(max_grant_count), Strings.GAIN_LOSS, curses.A_UNDERLINE)


def draw_footer(footer_window, stock_portfolio: StockPortfolio, ticker_state):
    GREEN = curses.color_pair(1)
    RED = curses.color_pair(2)

    price_by_ticker = {ticker: state.latest_price
                       for ticker, state in ticker_state.items() if state.latest_price}
    prev_close_by_ticker = {ticker: state.previous_close
                            for ticker, state in ticker_state.items() if state.previous_close}

    total_value = stock_portfolio.get_total_portfolio_value(price_by_ticker)
    if total_value <= 0:
        return  # Watch-only portfolio: nothing to total up.

    day_change = stock_portfolio.get_total_day_change(price_by_ticker, prev_close_by_ticker)

    footer_window.clear()
    total_text = Strings.PORTFOLIO_TOTAL.format(total_value)
    safe_addstr(footer_window, 0, 0, total_text, curses.A_BOLD)

    change_sign = "+" if day_change >= 0 else "-"
    change_text = Strings.PORTFOLIO_DAY_CHANGE.format(change_sign, abs(day_change))
    change_color = GREEN if day_change >= 0 else RED
    safe_addstr(footer_window, 0, len(total_text), change_text, change_color)
    footer_window.refresh()


def draw_status(status_window, status_key):
    if status_window is None:
        return

    GREEN = curses.color_pair(1)
    RED = curses.color_pair(2)
    YELLOW = curses.color_pair(3)

    status_colors = {
        Strings.CONN_STATUS_CONNECTING: YELLOW,
        Strings.CONN_STATUS_LIVE: GREEN,
        Strings.CONN_STATUS_RECONNECTING: YELLOW,
        Strings.CONN_STATUS_DISCONNECTED: RED,
    }
    status_text = Strings.CONN_STATUS_TEXT.get(status_key, status_key)
    status_color = status_colors.get(status_key, 0)

    status_window.clear()
    safe_addstr(status_window, 0, 0, status_text, status_color)
    status_window.refresh()


if __name__ == '__main__':
    # Hides the stack trace when you stop the program with control+c
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

    # Use the terminal's locale so curses can render the unicode gauge/arrow glyphs.
    locale.setlocale(locale.LC_ALL, "")

    config_repo = ConfigRepository()
    stock_repo = StockRepository(ApiService(config_repo))

    config_repo.ensure_config_file()

    # Look for command line arguments, if we find any, cancel execution
    process_arguments()
    if len(sys.argv) > 1:
        sys.exit()

    portfolio, parse_errors = config_repo.get_stock_portfolio_with_errors()
    print_config_parse_errors(parse_errors)
    has_api_token = config_repo.get_finnhub_api_key() != ""
    has_portfolio = len(portfolio.get_all_stock_grants()) > 0

    # Check is there is already a portfolio
    if has_api_token and has_portfolio:
        print(Strings.USING_PORTFOLIO_MSG)

    else:
        # Step 1 - Welcome Message!
        print(Strings.WELCOME_MSG)

        # Step 2 - Get Finnhub API Token
        if not has_api_token:
            get_api_token_from_user()

        if not has_portfolio:
            # Step 3 - Get Stocks / Grants
            portfolio = get_stock_portfolio_from_user()
            # Save the portfolio in the config file
            config_repo.save_stock_portfolio(portfolio)
            print_setup_summary(portfolio)
            if not prompt_start_tracker():
                sys.exit()

    # Todo: show a countdown timer and maybe some instructions on how to exit
# Todo: Disabled for now as I know how to exit
#    input(Strings.START_STOCK_UI_MSG)

    # This is where all the UI magic happens! View CursesSandboxes for some examples.
    wrapper(curses_main)
    log("Main done.")

HELP_DESC = "This program is a lightweight way to keep an eye on your stock watch list and see how your equity grants " \
            "are performing."
ARG_TOKEN_HELP = "Sets the Finnhub API token. You can create a free token here: https://finnhub.io/dashboard."
ARG_RESET_HELP = "Removes all the stocks and equity amounts."
ARG_NUKE_HELP = "Nuke from orbit. Resets the entire config file. You will lose your API Token and Stock list."

WELCOME_MSG = "\nWelcome! 👋🏼 This simple app will help you keep track of current stock prices and any stock grants you may have. 📈\n" \
              "But first, we need to go through a simple setup...\n"
USING_PORTFOLIO_MSG = "It looks like you already have a stock portfolio set up. If you would like to add, edit, or " \
                      "remove any stocks or grants please use the command line arguments or edit the config.ini file " \
                      "directly.\n"

START_STOCK_UI_MSG = "To quit the application, press 'Ctrl + C'. Press any key to start..."

FINNHUB_INPUT_MSG = "You will need a free API Token from Finnhub. You can get one here: https://finnhub.io/dashboard.\n" \
                    "Once you have your free Finnhub Token, enter it here: "
FINNHUB_TOKEN_OK = "Finnhub Token has been validated and saved."
FINNHUB_TOKEN_ERROR = "Finnhub Token is not valid please try again..."
FINNHUB_TOKEN_EXIST = "Looks like you already have a Finnhub token! If you want to change it, check the '-h' " \
                      "documentation.\n"

GET_STOCK_MSG = "Now that we have your API Token, let's add some stocks and stock grants to your portfolio."
GET_STOCK_INPUT_MSG = "Enter in a stock ticker (I.E. AAPL): "
GET_STOCK_ERROR = "That stock symbol is not valid. Please try again..."

GET_GRANTS_INPUT = "Enter the number of shares in this grant (0 to watch this stock only): "
GET_NUM_OF_VESTS_INPUT = "Enter in your number of vests left (I.E. 4 year vest evenly would be 16): "

GET_GRANTS_COST_INPUT = "Enter the price the stock was granted at: "
GET_GRANT_GROUP_INPUT = "Optional group label (usually leave blank; use a label to show this grant on its own row): "
GET_ADDITIONAL_GRANT_GROUP_INPUT = "Optional group label for this %s grant (Enter combines it with matching blank-label grants): "

MORE_STOCKS_TO_ADD = "Do you want to add any more stocks? (Y/n): "
MORE_GRANTS_TO_ADD = "Do you want to add any more stock grants for %s? (Y/n): "

YES_OR_NO_ERROR = "Sorry, I didn't recognize that. Please enter, 'Y' for yes, and 'n' for no."
NOT_A_NUM_ERROR = "That's not a valid number. Please try again..."
NON_NEGATIVE_INT_ERROR = "Please enter a whole number greater than or equal to 0."
POSITIVE_PRICE_ERROR = "Please enter a grant price greater than 0."
GROUP_LABEL_COMMA_ERROR = "Group labels cannot contain commas."
ADDING_WATCH_ONLY_STOCK = "Adding %s as a watch-only stock."
CONFIG_ROW_PARSE_ERROR = "Skipping malformed config row: %s"
SAVED_PORTFOLIO_MSG = "\nSaved portfolio to %s"
PORTFOLIO_SUMMARY_HEADER = "Portfolio:"
PORTFOLIO_SUMMARY_WATCH_ONLY = "- %s: watch only"
PORTFOLIO_SUMMARY_GRANT = "- %s: %s shares @ $%.2f, %s vests left"
PORTFOLIO_SUMMARY_GROUP = ', group "%s"'
START_TRACKER_PROMPT = "\nStart live tracker now? (Y/n): "

# Curses Strings
CURRENT = "Current"
GRANT_HEADER = "Grant %s"
TOTAL = "Total"
DAY_RANGE = "Day Range"
GAIN_LOSS = "Gain/Loss"
PORTFOLIO_TOTAL = "Portfolio: ${:,.2f}"
PORTFOLIO_DAY_CHANGE = " ({}${:,.2f} today)"

# Connection status keys emitted by the network layer (see ApiService).
CONN_STATUS_CONNECTING = "connecting"
CONN_STATUS_LIVE = "live"
CONN_STATUS_RECONNECTING = "reconnecting"
CONN_STATUS_DISCONNECTED = "disconnected"

# Display text for each connection status key.
CONN_STATUS_TEXT = {
    CONN_STATUS_CONNECTING: "○ connecting…",
    CONN_STATUS_LIVE: "● live",
    CONN_STATUS_RECONNECTING: "○ reconnecting…",
    CONN_STATUS_DISCONNECTED: "✕ disconnected",
}

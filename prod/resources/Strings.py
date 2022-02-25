HELP_DESC = "This program is a light weight way to keep an eye on your Stock watch list and see how your equity grants " \
            "are preforming."
ARG_TOKEN_HELP = "Sets the Finnhub API token. You can create a free token here: https://finnhub.io/dashboard."
ARG_RESET_HELP = "Removes all the stocks and equity amounts."
ARG_NUKE_HELP = "Nuke from orbit. Resets the entire config file. You will lose your API Token and Stock list."

WELCOME_MSG = "\nWelcome! 👋🏼 This simple app will help you keep track of current stock prices and any stock grants you may have. 📈\n" \
              "But first, we need to go through a simple set up...\n"
USING_PORTFOLIO_MSG = "It looks like you already have a stock portfolio set up. If you would like to add, edit, or " \
                      "remove any stocks or grants please use the command line arguments or edit the config.ini file " \
                      "directly.\n"

START_STOCK_UI_MSG = "To quit the application, press 'Ctrl + c'. Press any key to start..."

FINNHUB_INPUT_MSG = "You will need a free API Token from Finnhub. You can get one here: https://finnhub.io/dashboard.\n" \
                    "Once you have your free Finhub Token, enter it here: "
FINNHUB_TOKEN_OK = "Finnhub Token has been validated and saved."
FINNHUB_TOKEN_ERROR = "Finnhub Token is not valid please try again..."
FINNHUB_TOKEN_EXIST = "Looks like you already have a Finnhub token! If you want to change it, check the '-h' " \
                      "documentation.\n"

GET_STOCK_MSG = "Now that we have your API Token, let's add some stocks and stock grants to your portfolio."
GET_STOCK_INPUT_MSG = "Enter in a stock ticker (I.E. TWTR): "
GET_STOCK_ERROR = "That stock symbol is not valid. Please try again..."

GET_GRANTS_INPUT = "Enter in your number of grants (0 if no grants): "

GET_GRANTS_COST_INPUT = "Enter the price the stock was granted at: "

MORE_STOCKS_TO_ADD = "Do you want to add any more stocks? (Y/n): "
MORE_GRANTS_TO_ADD = "Do you want to add any more stock grants for %s? (Y/n): "

YES_OR_NO_ERROR = "Sorry, I didn't recognize that. Please enter, 'Y' for yes, and 'n' for no."
NOT_A_NUM_ERROR = "That's not a valid number. Please try again..."

# Curses Strings
CURRENT = "Current"
GRANT_HEADER = "Grant %s"
TOTAL = "Total"


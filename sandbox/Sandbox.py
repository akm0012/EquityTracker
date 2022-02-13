import os
import sys
from prod.Colors import TextStyles
from prod.objects.StockGrant import StockGrant
from prod.objects.StockGrantCollection import StockGrantCollection
from prod.objects.StockPortfolio import StockPortfolio
from prod.repository.ConfigRepository import ConfigRepository

print("Hello World!")
print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "../config.ini"
abs_file_path = os.path.join(script_dir, rel_path)

configRepo = ConfigRepository()
# configExist = configRepo.does_config_file_exist()
# is_config_file_valid = configRepo.is_config_file_valid()
# print("Is config valid: " + str(is_config_file_valid))
# configRepo.write_finnhub_api_key("Woohoo!")
configRepo.create_empty_config_file()

stock_grant_1 = StockGrant("appl", 10, 100.50)
stock_grant_2 = StockGrant("twtr", 100, 36.50)
stock_grant_3 = StockGrant("twtr", 200, 50.50)

portfolio = StockPortfolio()

twtr_stock_grant_collection = StockGrantCollection("twtr")
twtr_stock_grant_collection.add_stock_grant(stock_grant_2)
twtr_stock_grant_collection.add_stock_grant(stock_grant_3)

appl_stock_grant_collection = StockGrantCollection("appl")
appl_stock_grant_collection.add_stock_grant(stock_grant_1)

portfolio.add_stock_grant_collection(twtr_stock_grant_collection)
portfolio.add_stock_grant_collection(appl_stock_grant_collection)

print(portfolio)

stockTicker = input("What Stock would you like to track? >> ")
print("You entered " + stockTicker)

print(TextStyles.OKGREEN + "Warning: No active frommets remain. Continue?" + TextStyles.ENDC)
print(f"{TextStyles.WARNING}Warning: No active frommets remain. Continue?{TextStyles.ENDC}")
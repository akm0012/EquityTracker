"""
This class reads/writes the config file.
"""
import os
from os.path import exists
import configparser

from prod.objects.StockGrant import StockGrant
from prod.objects.StockPortfolio import StockPortfolio


class ConfigRepository:
    API_TOKENS_SECTION = "API_TOKENS"
    FINN_HUB_API_KEY = "FINN_HUB_API_KEY"
    DATABASE_SECTION = "DATABASE"
    NO_KEY = "NO_KEY"

    config_file_location = ""

    def __init__(self):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../../config.ini"
        self.config_file_location = os.path.join(script_dir, rel_path)

    def does_config_file_exist(self) -> bool:
        file_exist = exists(self.config_file_location)
        return file_exist

    def is_config_file_valid(self) -> bool:
        if not self.does_config_file_exist():
            raise FileNotFoundError("Config file can not be found.")

        # Make sure the Config has all the right sections
        config = configparser.ConfigParser()
        config.read(self.config_file_location)
        if config.sections().__len__() != 2:
            return False
        if not config.has_section(self.API_TOKENS_SECTION):
            return False
        if not config.has_section(self.DATABASE_SECTION):
            return False

        # Make sure there is an API Key
        api_tokens_key = config.get(self.API_TOKENS_SECTION, self.FINN_HUB_API_KEY, fallback=self.NO_KEY)
        if api_tokens_key == self.NO_KEY:
            return False

        return True

    """
    Creates a config.ini file that looks like this: 
    ----------
    [API_TOKENS]
    finn_hub_api_key = 

    [DATABASE]
    ----------
    """
    def create_empty_config_file(self):
        config = configparser.ConfigParser()

        config.add_section(self.API_TOKENS_SECTION)
        config[self.API_TOKENS_SECTION][self.FINN_HUB_API_KEY] = ""
        config.add_section(self.DATABASE_SECTION)

        with open(self.config_file_location, 'w') as configfile:
            config.write(configfile)

    def delete_config_file(self) -> bool:
        if self.does_config_file_exist():
            os.remove(self.config_file_location)
            return True
        return False

    def get_finnhub_api_key(self) -> str:
        config = configparser.ConfigParser()
        config.read(self.config_file_location)
        return config.get(self.API_TOKENS_SECTION, self.FINN_HUB_API_KEY)

    def write_finnhub_api_key(self, api_key: str):
        config = configparser.ConfigParser()
        config.read(self.config_file_location)
        config[self.API_TOKENS_SECTION][self.FINN_HUB_API_KEY] = api_key
        with open(self.config_file_location, 'w') as configfile:
            config.write(configfile)

    def get_stock_portfolio(self) -> StockPortfolio:
        config = configparser.ConfigParser()
        config.read(self.config_file_location)

        database_section = config[self.DATABASE_SECTION]

        stock_portfolio = StockPortfolio()

        for stock in database_section:
            stock_ini_str = database_section[stock]
            stock_grant = StockGrant.create_from_config_ini(stock_ini_str)
            stock_portfolio.add_stock_grant(stock_grant)

        return stock_portfolio

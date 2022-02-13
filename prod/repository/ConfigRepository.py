"""
This class is reads/writes the config file.
"""
import os
from os.path import exists
import configparser


class ConfigRepository:

    config_file_location = ""

    def __init__(self):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../../config.ini"
        self.config_file_location = os.path.join(script_dir, rel_path)

    def read_ini(self, file_path: str):
        config = configparser.ConfigParser()
        config.read(file_path)
        for section in config.sections():
            for key in config[section]:
                print((key, config[section][key]))

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
        if not config.has_section("API_TOKENS"):
            return False
        if not config.has_section("DATABASE"):
            return False

        return True

    def get_finnhub_api_key(self) -> str:
        #todo: Read this from a file instead
        return ""
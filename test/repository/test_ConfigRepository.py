import os
from unittest import TestCase

from prod.repository.ConfigRepository import ConfigRepository


class TestConfigRepository(TestCase):

    # region does_config_file_exist tests

    def test_does_config_file_exist_true(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_1.ini")
        self.assertTrue(config_repo.does_config_file_exist())

    def test_does_config_file_exist_false(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("not_a_file.ini")
        self.assertFalse(config_repo.does_config_file_exist())

    # endregion

    # region is_config_file_valid tests

    def test_is_config_file_valid_no_file_found(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("not_a_file.ini")
        try:
            config_repo.is_config_file_valid()
        except FileNotFoundError as myException:
            self.assertTrue(myException.args[0].startswith("Config file can not be found."))

    def test_is_config_file_valid_no_sections(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_2.ini")
        self.assertFalse(config_repo.is_config_file_valid())

    def test_is_config_file_valid_too_many_sections(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_3.ini")
        self.assertFalse(config_repo.is_config_file_valid())

    def test_is_config_file_valid_no_api_token(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_4.ini")
        self.assertFalse(config_repo.is_config_file_valid())

    def test_is_config_file_valid_no_database(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_5.ini")
        self.assertFalse(config_repo.is_config_file_valid())

    def test_is_config_file_valid_no_api_token_value(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_6.ini")
        self.assertFalse(config_repo.is_config_file_valid())

    def test_is_config_file_valid_true_1(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_1.ini")
        self.assertTrue(config_repo.is_config_file_valid())

    def test_is_config_file_valid_true_2(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_7.ini")
        self.assertTrue(config_repo.is_config_file_valid())

    # endregion

    # region get_finnhub_api_key tests

    def test_get_finnhub_api_key_empty(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_7.ini")
        self.assertEqual(config_repo.get_finnhub_api_key(), "")

    def test_get_finnhub_api_key_normal(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_1.ini")
        self.assertEqual(config_repo.get_finnhub_api_key(), "api_key_test")

    # endregion

    # region create_empty_config_file tests

    def test_create_empty_config_file(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("empty_config_file.ini")

        # Make sure the file is not there
        self.assertFalse(config_repo.does_config_file_exist())

        # Create the empty config file
        config_repo.create_empty_config_file()

        # Make sure it's there
        self.assertTrue(config_repo.does_config_file_exist())

        # Make sure it's valid
        self.assertTrue(config_repo.is_config_file_valid())

        # Clean up, delete the file
        self.assertTrue(config_repo.delete_config_file())

    # endregion

    # region get_stock_portfolio

    def test_get_stock_portfolio_0(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_1.ini")

        test_portfolio = config_repo.get_stock_portfolio()

        port_dict = test_portfolio.stock_grant_collection_dict

        twtr_stock_grants = port_dict.get("TWTR")
        self.assertEqual(twtr_stock_grants.ticker, "TWTR")
        self.assertEqual(twtr_stock_grants.stock_grant_list[0].ticker, "TWTR")
        self.assertEqual(twtr_stock_grants.stock_grant_list[0].count, 100)
        self.assertEqual(twtr_stock_grants.stock_grant_list[0].price, 36.50)
        self.assertEqual(twtr_stock_grants.stock_grant_list[1].ticker, "TWTR")
        self.assertEqual(twtr_stock_grants.stock_grant_list[1].count, 200)
        self.assertEqual(twtr_stock_grants.stock_grant_list[1].price, 46.50)

        appl_stock_grants = port_dict.get("APPL")
        self.assertEqual(appl_stock_grants.ticker, "APPL")
        self.assertEqual(appl_stock_grants.stock_grant_list[0].ticker, "APPL")
        self.assertEqual(appl_stock_grants.stock_grant_list[0].count, 50)
        self.assertEqual(appl_stock_grants.stock_grant_list[0].price, 100.50)

    # endregion

    @staticmethod
    def __get_path_to_test_file(test_file_name: str) -> str:
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../test_config_files/" + test_file_name
        return os.path.join(script_dir, rel_path)

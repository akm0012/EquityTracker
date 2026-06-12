import os
import tempfile
from unittest import TestCase

from prod.objects.StockGrant import StockGrant
from prod.objects.StockPortfolio import StockPortfolio
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

    # region ensure_config_file tests

    def test_ensure_config_file_creates_missing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_repo = ConfigRepository()
            config_repo.config_file_location = os.path.join(temp_dir, "config.ini")

            config_repo.ensure_config_file()

            self.assertTrue(config_repo.does_config_file_exist())
            self.assertTrue(config_repo.is_config_file_valid())
            self.assertEqual("", config_repo.get_finnhub_api_key())

    def test_ensure_config_file_repairs_missing_api_tokens(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.ini")
            with open(config_path, "w") as config_file:
                config_file.write("[DATABASE]\nSTOCK_1 = AAPL,10,100.00,4\n")

            config_repo = ConfigRepository()
            config_repo.config_file_location = config_path

            config_repo.ensure_config_file()

            self.assertTrue(config_repo.is_config_file_valid())
            self.assertEqual("", config_repo.get_finnhub_api_key())
            self.assertEqual(1, len(config_repo.get_stock_portfolio().get_all_stock_grants()))

    def test_ensure_config_file_repairs_missing_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.ini")
            with open(config_path, "w") as config_file:
                config_file.write("[API_TOKENS]\nFINN_HUB_API_KEY = api_key_test\n")

            config_repo = ConfigRepository()
            config_repo.config_file_location = config_path

            config_repo.ensure_config_file()

            self.assertTrue(config_repo.is_config_file_valid())
            self.assertEqual("api_key_test", config_repo.get_finnhub_api_key())
            self.assertEqual(0, len(config_repo.get_stock_portfolio().get_all_stock_grants()))

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

    def test_save_finnhub_api_key_creates_missing_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_repo = ConfigRepository()
            config_repo.config_file_location = os.path.join(temp_dir, "config.ini")

            config_repo.save_finnhub_api_key("new_key")

            self.assertTrue(config_repo.does_config_file_exist())
            self.assertEqual("new_key", config_repo.get_finnhub_api_key())

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

    def test_get_stock_portfolio_with_errors_skips_malformed_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.ini")
            with open(config_path, "w") as config_file:
                config_file.write("[API_TOKENS]\n")
                config_file.write("FINN_HUB_API_KEY = api_key_test\n\n")
                config_file.write("[DATABASE]\n")
                config_file.write("STOCK_1 = AAPL,10,100.00,4\n")
                config_file.write("STOCK_2 = BROKEN,10\n")

            config_repo = ConfigRepository()
            config_repo.config_file_location = config_path

            portfolio, errors = config_repo.get_stock_portfolio_with_errors()

            self.assertEqual(1, len(portfolio.get_all_stock_grants()))
            self.assertEqual("AAPL", portfolio.get_all_stock_grants()[0].ticker)
            self.assertEqual(1, len(errors))
            self.assertIn("stock_2", errors[0])

    # endregion

    # region clear_stocks tests

    def test_clear_stocks_repairs_missing_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.ini")
            with open(config_path, "w") as config_file:
                config_file.write("[API_TOKENS]\nFINN_HUB_API_KEY = api_key_test\n")

            config_repo = ConfigRepository()
            config_repo.config_file_location = config_path

            config_repo.clear_stocks()

            self.assertTrue(config_repo.is_config_file_valid())
            self.assertEqual(0, len(config_repo.get_stock_portfolio().get_all_stock_grants()))

    # endregion

    # region Integration Tests

    def test_full_creation_0(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("full_creation_1.ini")

        # Delete the file if it's there!
        config_repo.delete_config_file()

        # Create 3 stocks
        stock_grant_1 = StockGrant("APPL", 60, 200.50, 10)
        stock_grant_2 = StockGrant("TWTR", 600, 66.50, 0)
        stock_grant_3 = StockGrant("TWTR", 700, 70.50, 0)

        # Add the Stocks to a Portfolio
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(stock_grant_1)
        portfolio.add_stock_grant(stock_grant_2)
        portfolio.add_stock_grant(stock_grant_3)

        # Sanity check Portfolio
        self.assertEqual(len(portfolio.stock_grant_collection_dict), 2)

        # Write the portfolio to a config file
        config_repo.save_stock_portfolio(portfolio)

        # Read them into a new Portfolio
        portfolio2 = config_repo.get_stock_portfolio()

        portfolio2_stock_list = portfolio2.get_all_stock_grants()
        portfolio2_stock_1 = portfolio2_stock_list[0]
        portfolio2_stock_2 = portfolio2_stock_list[1]
        portfolio2_stock_3 = portfolio2_stock_list[2]

        # Make sure they all the data is correct
        self.assertEqual(stock_grant_1.ticker, portfolio2_stock_1.ticker)
        self.assertEqual(stock_grant_1.count, portfolio2_stock_1.count)
        self.assertEqual(stock_grant_1.price, portfolio2_stock_1.price)
        self.assertEqual(stock_grant_1.vests_left, portfolio2_stock_1.vests_left)

        self.assertEqual(stock_grant_2.ticker, portfolio2_stock_2.ticker)
        self.assertEqual(stock_grant_2.count, portfolio2_stock_2.count)
        self.assertEqual(stock_grant_2.price, portfolio2_stock_2.price)
        self.assertEqual(stock_grant_2.vests_left, portfolio2_stock_2.vests_left)

        self.assertEqual(stock_grant_3.ticker, portfolio2_stock_3.ticker)
        self.assertEqual(stock_grant_3.count, portfolio2_stock_3.count)
        self.assertEqual(stock_grant_3.price, portfolio2_stock_3.price)
        self.assertEqual(stock_grant_3.vests_left, portfolio2_stock_3.vests_left)

        config_repo.delete_config_file()

    def test_save_stock_portfolio_removes_stale_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.ini")
            with open(config_path, "w") as config_file:
                config_file.write("[API_TOKENS]\n")
                config_file.write("FINN_HUB_API_KEY = api_key_test\n\n")
                config_file.write("[DATABASE]\n")
                config_file.write("STOCK_1 = AAPL,10,100.00,4\n")
                config_file.write("STOCK_2 = RDDT,20,200.00,4\n")

            config_repo = ConfigRepository()
            config_repo.config_file_location = config_path

            portfolio = StockPortfolio()
            portfolio.add_stock_grant(StockGrant("AAPL", 5, 90.00, 2))
            config_repo.save_stock_portfolio(portfolio)

            saved_grants = config_repo.get_stock_portfolio().get_all_stock_grants()
            self.assertEqual(1, len(saved_grants))
            self.assertEqual("AAPL", saved_grants[0].ticker)
            self.assertEqual(5, saved_grants[0].count)

    # endregion

    @staticmethod
    def __get_path_to_test_file(test_file_name: str) -> str:
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../test_config_files/" + test_file_name
        return os.path.join(script_dir, rel_path)

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
        self.assertEquals(config_repo.get_finnhub_api_key(), "")

    def test_get_finnhub_api_key_normal(self):
        config_repo = ConfigRepository()
        config_repo.config_file_location = self.__get_path_to_test_file("test_config_1.ini")
        self.assertEquals(config_repo.get_finnhub_api_key(), "api_key_test")

    # endregion

    def __get_path_to_test_file(self, test_file_name: str) -> str:
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "../test_config_files/" + test_file_name
        return os.path.join(script_dir, rel_path)

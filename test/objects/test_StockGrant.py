from unittest import TestCase

from prod.objects.StockGrant import StockGrant


class TestStockGrant(TestCase):

    def test_get_config_ini_str_0(self):
        stock_grant = StockGrant("TWTR", 100, 36.50, 10)
        self.assertEqual(stock_grant.get_config_ini_str(), "TWTR,100,36.50,10")

    def test_get_config_ini_str_1(self):
        stock_grant = StockGrant("", 0, 0, 0)
        self.assertEqual(stock_grant.get_config_ini_str(), ",0,0.00,0")

    def test_get_config_ini_str_2(self):
        stock_grant = StockGrant("appl", 10000, 5000.01,16)
        self.assertEqual(stock_grant.get_config_ini_str(), "APPL,10000,5000.01,16")

    def test_get_config_ini_str_with_group(self):
        stock_grant = StockGrant("RDDT", 399, 147.86, 2, "b")
        self.assertEqual(stock_grant.get_config_ini_str(), "RDDT,399,147.86,2,b")

    def test_create_from_config_ini_no_group(self):
        stock_grant = StockGrant.create_from_config_ini("RDDT,357,216.99,2")
        self.assertEqual(stock_grant.ticker, "RDDT")
        self.assertEqual(stock_grant.count, 357)
        self.assertEqual(stock_grant.price, 216.99)
        self.assertEqual(stock_grant.vests_left, 2)
        self.assertEqual(stock_grant.group, "")

    def test_create_from_config_ini_with_group(self):
        stock_grant = StockGrant.create_from_config_ini("RDDT,399,147.86,2,b")
        self.assertEqual(stock_grant.ticker, "RDDT")
        self.assertEqual(stock_grant.count, 399)
        self.assertEqual(stock_grant.price, 147.86)
        self.assertEqual(stock_grant.vests_left, 2)
        self.assertEqual(stock_grant.group, "b")

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

from unittest import TestCase

from prod.objects.StockGrant import StockGrant
from prod.objects.StockPortfolio import StockPortfolio


class TestStockGrant(TestCase):

    def test_get_max_grant_count_0(self):
        stock_grant_1 = StockGrant("mfst", 0, 0, 0)
        stock_grant_2 = StockGrant("qppl", 0, 0, 0)
        stock_grant_3 = StockGrant("qppl", 0, 0, 0)

        portfolio = StockPortfolio()

        portfolio.add_stock_grant(stock_grant_1)
        portfolio.add_stock_grant(stock_grant_2)
        portfolio.add_stock_grant(stock_grant_3)

        self.assertEqual(0, portfolio.get_max_grant_count())

    def test_get_max_grant_count_1(self):
        stock_grant_1 = StockGrant("mfst", 1, 1, 0)
        stock_grant_2 = StockGrant("qppl", 0, 0, 0)
        stock_grant_3 = StockGrant("qppl", 0, 0, 0)

        portfolio = StockPortfolio()

        portfolio.add_stock_grant(stock_grant_1)
        portfolio.add_stock_grant(stock_grant_2)
        portfolio.add_stock_grant(stock_grant_3)

        self.assertEqual(1, portfolio.get_max_grant_count())

    def test_get_max_grant_count_2(self):
        stock_grant_1 = StockGrant("mfst", 0, 0, 0)
        stock_grant_2 = StockGrant("qppl", 1, 1, 0)
        stock_grant_3 = StockGrant("qppl", 2, 2, 0)

        portfolio = StockPortfolio()

        portfolio.add_stock_grant(stock_grant_1)
        portfolio.add_stock_grant(stock_grant_2)
        portfolio.add_stock_grant(stock_grant_3)

        self.assertEqual(2, portfolio.get_max_grant_count())

    def test_get_max_grant_count_3(self):
        stock_grant_1 = StockGrant("mfst", 1, 1, 0)
        stock_grant_2 = StockGrant("qppl", 1, 1, 0)
        stock_grant_3 = StockGrant("qppl", 2, 2, 0)

        portfolio = StockPortfolio()

        portfolio.add_stock_grant(stock_grant_1)
        portfolio.add_stock_grant(stock_grant_2)
        portfolio.add_stock_grant(stock_grant_3)

        self.assertEqual(2, portfolio.get_max_grant_count())


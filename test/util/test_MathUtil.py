from unittest import TestCase

from prod.objects.StockGrant import StockGrant
from prod.util.MathUtil import calculate_percent_change, calculate_grant_percent_change, \
    calculate_multi_grant_percent_change, calculate_multi_grant_dollar_change, calculate_grant_dollar_change


class MathUtilTests(TestCase):
    def test_calculate_percent_change(self):
        expected = 100
        actual = calculate_percent_change(50, 100)
        self.assertEqual(expected, actual)

    def test_calculate_percent_change_2(self):
        expected = 0
        actual = calculate_percent_change(50, 50)
        self.assertEqual(expected, actual)

    def test_calculate_percent_change_3(self):
        expected = -50
        actual = calculate_percent_change(100, 50)
        self.assertEqual(expected, actual)

    def test_calculate_grant_percent_change(self):
        current_share_price = 60.00
        grant_price = 50.00
        shares = 2000

        expected = 20
        actual = calculate_grant_percent_change(current_share_price,
                                                shares,
                                                grant_price)
        self.assertEqual(expected, actual)

    def test_calculate_grant_percent_change_2(self):
        current_share_price = 60.00
        grant_price = 70.00
        shares = 100

        expected = -14.29
        actual = calculate_grant_percent_change(current_share_price,
                                                shares,
                                                grant_price)
        self.assertEqual(expected, actual)

    def test_calculate_grant_dollar_change(self):
        current_share_price = 60.00
        grant_price = 50.00
        shares = 2000

        expected = 20000
        actual = calculate_grant_dollar_change(current_share_price,
                                                shares,
                                                grant_price)
        self.assertEqual(expected, actual)

    def test_calculate_grant_dollar_change(self):
        current_share_price = 60.00
        grant_price = 70.00
        shares = 100

        expected = -1000
        actual = calculate_grant_dollar_change(current_share_price,
                                                shares,
                                                grant_price)
        self.assertEqual(expected, actual)

    def test_calculate_multi_grant_percent_change(self):
        current_share_price = 60.00

        grant_1 = StockGrant("TWTR", 2000, 50)
        grant_2 = StockGrant("TWTR", 100, 70)

        expected = 17.76
        actual = calculate_multi_grant_percent_change(current_share_price, [grant_1, grant_2])

        self.assertEqual(expected, actual)

    def test_calculate_multi_grant_dollar_change(self):
        current_share_price = 60.00

        grant_1 = StockGrant("TWTR", 2000, 50)
        grant_2 = StockGrant("TWTR", 100, 70)

        expected = 19000
        actual = calculate_multi_grant_dollar_change(current_share_price, [grant_1, grant_2])

        self.assertEqual(expected, actual)

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

    def test_same_ticker_no_group_combines_into_one_row(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 357, 216.99, 2))
        portfolio.add_stock_grant(StockGrant("RDDT", 399, 147.86, 2))

        collections = list(portfolio.get_all_stock_grant_collections())
        self.assertEqual(1, len(collections))
        self.assertEqual(2, len(collections[0].stock_grant_list))

    def test_same_ticker_different_group_splits_into_separate_rows(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 357, 216.99, 2))
        portfolio.add_stock_grant(StockGrant("RDDT", 399, 147.86, 2, "b"))

        collections = list(portfolio.get_all_stock_grant_collections())
        self.assertEqual(2, len(collections))
        # Each row holds exactly one grant
        self.assertEqual(1, len(collections[0].stock_grant_list))
        self.assertEqual(1, len(collections[1].stock_grant_list))
        # Both rows still track the same ticker
        self.assertEqual("RDDT", collections[0].ticker)
        self.assertEqual("RDDT", collections[1].ticker)

    def test_split_rows_dedupe_ticker_for_subscriptions(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 357, 216.99, 2))
        portfolio.add_stock_grant(StockGrant("RDDT", 399, 147.86, 2, "b"))

        self.assertEqual(["RDDT"], list(portfolio.get_all_stock_ticker_symbols()))

    def test_unrealized_gain_positive(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("AAPL", 100, 50.0, 4))
        collection = list(portfolio.get_all_stock_grant_collections())[0]
        # 100 shares up $10 each.
        self.assertAlmostEqual(1000.0, collection.get_unrealized_gain(60.0))

    def test_unrealized_gain_negative(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("AAPL", 100, 70.0, 4))
        collection = list(portfolio.get_all_stock_grant_collections())[0]
        # 100 shares down $10 each.
        self.assertAlmostEqual(-1000.0, collection.get_unrealized_gain(60.0))

    def test_unrealized_gain_combines_grants_on_same_row(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 357, 216.99, 2))
        portfolio.add_stock_grant(StockGrant("RDDT", 399, 147.86, 2))
        collection = list(portfolio.get_all_stock_grant_collections())[0]
        expected = 357 * (166.56 - 216.99) + 399 * (166.56 - 147.86)
        self.assertAlmostEqual(expected, collection.get_unrealized_gain(166.56))

    def test_total_portfolio_value_sums_across_tickers(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 100, 50.0, 2))
        portfolio.add_stock_grant(StockGrant("AAPL", 10, 100.0, 4))

        prices = {"RDDT": 166.56, "AAPL": 310.0}
        expected = 100 * 166.56 + 10 * 310.0
        self.assertAlmostEqual(expected, portfolio.get_total_portfolio_value(prices))

    def test_total_portfolio_value_skips_unknown_prices(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 100, 50.0, 2))
        portfolio.add_stock_grant(StockGrant("AAPL", 10, 100.0, 4))

        # AAPL has no price yet, so only RDDT counts.
        prices = {"RDDT": 166.56}
        self.assertAlmostEqual(100 * 166.56, portfolio.get_total_portfolio_value(prices))

    def test_total_portfolio_value_handles_split_rows(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 357, 216.99, 2))
        portfolio.add_stock_grant(StockGrant("RDDT", 399, 147.86, 2, "b"))

        prices = {"RDDT": 166.56}
        self.assertAlmostEqual((357 + 399) * 166.56, portfolio.get_total_portfolio_value(prices))

    def test_total_day_change(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 100, 50.0, 2))
        portfolio.add_stock_grant(StockGrant("AAPL", 10, 100.0, 4))

        prices = {"RDDT": 110.0, "AAPL": 90.0}
        prev_close = {"RDDT": 100.0, "AAPL": 100.0}
        # RDDT: +$10/share * 100 = +1000; AAPL: -$10/share * 10 = -100
        self.assertAlmostEqual(900.0, portfolio.get_total_day_change(prices, prev_close))

    def test_total_day_change_skips_missing_previous_close(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 100, 50.0, 2))

        prices = {"RDDT": 110.0}
        self.assertAlmostEqual(0.0, portfolio.get_total_day_change(prices, {}))

    def test_next_vest_value_is_scoped_per_row(self):
        # The original bug: two grants with independent schedules incorrectly summed
        # both grants' next vest. Splitting onto separate rows scopes each calculation.
        current_price = 166.56

        # Combined (old behavior): both grants share one row
        combined = StockPortfolio()
        combined.add_stock_grant(StockGrant("RDDT", 357, 216.99, 2))
        combined.add_stock_grant(StockGrant("RDDT", 399, 147.86, 2))
        combined_row = list(combined.get_all_stock_grant_collections())[0]
        expected_combined = (357 * current_price) / 2 + (399 * current_price) / 2
        self.assertAlmostEqual(expected_combined, combined_row.get_next_vest_value(current_price))

        # Split: grant 2 on its own row vests independently
        split = StockPortfolio()
        split.add_stock_grant(StockGrant("RDDT", 357, 216.99, 2))
        split.add_stock_grant(StockGrant("RDDT", 399, 147.86, 2, "b"))
        rows = list(split.get_all_stock_grant_collections())
        self.assertAlmostEqual((357 * current_price) / 2, rows[0].get_next_vest_value(current_price))
        self.assertAlmostEqual((399 * current_price) / 2, rows[1].get_next_vest_value(current_price))


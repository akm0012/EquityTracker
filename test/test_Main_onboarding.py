from unittest import TestCase
from unittest.mock import patch

from prod.Main import get_grant_group_from_user, get_stock_grants_from_user, normalize_optional_group, \
    parse_non_negative_int, parse_positive_float, prompt_user_yes_or_no, render_portfolio_summary
from prod.objects.StockGrant import StockGrant
from prod.objects.StockPortfolio import StockPortfolio
from prod.resources import Strings


class MainOnboardingTests(TestCase):

    # region parse_non_negative_int

    def test_parse_non_negative_int_accepts_zero(self):
        self.assertEqual(0, parse_non_negative_int("0"))

    def test_parse_non_negative_int_accepts_positive_int(self):
        self.assertEqual(42, parse_non_negative_int(" 42 "))

    def test_parse_non_negative_int_rejects_negative_int(self):
        with self.assertRaises(ValueError) as error:
            parse_non_negative_int("-1")
        self.assertEqual(Strings.NON_NEGATIVE_INT_ERROR, str(error.exception))

    def test_parse_non_negative_int_rejects_text(self):
        with self.assertRaises(ValueError) as error:
            parse_non_negative_int("ten")
        self.assertEqual(Strings.NON_NEGATIVE_INT_ERROR, str(error.exception))

    # endregion

    # region parse_positive_float

    def test_parse_positive_float_accepts_plain_price(self):
        self.assertEqual(12.34, parse_positive_float("12.34"))

    def test_parse_positive_float_accepts_dollar_prefix_and_commas(self):
        self.assertEqual(1234.56, parse_positive_float("$1,234.56"))

    def test_parse_positive_float_rejects_zero(self):
        with self.assertRaises(ValueError) as error:
            parse_positive_float("0")
        self.assertEqual(Strings.POSITIVE_PRICE_ERROR, str(error.exception))

    def test_parse_positive_float_rejects_text(self):
        with self.assertRaises(ValueError) as error:
            parse_positive_float("nope")
        self.assertEqual(Strings.POSITIVE_PRICE_ERROR, str(error.exception))

    # endregion

    # region normalize_optional_group

    def test_normalize_optional_group_strips_whitespace(self):
        self.assertEqual("b", normalize_optional_group(" b "))

    def test_normalize_optional_group_allows_blank(self):
        self.assertEqual("", normalize_optional_group("   "))

    def test_normalize_optional_group_rejects_commas(self):
        with self.assertRaises(ValueError) as error:
            normalize_optional_group("a,b")
        self.assertEqual(Strings.GROUP_LABEL_COMMA_ERROR, str(error.exception))

    # endregion

    def test_prompt_user_yes_or_no_defaults_blank_to_yes(self):
        with patch("builtins.input", return_value=""):
            self.assertTrue(prompt_user_yes_or_no("Start? "))

    def test_get_grant_group_reprompts_when_group_has_comma(self):
        with patch("builtins.input", side_effect=["bad,label", "good"]), patch("builtins.print"):
            self.assertEqual("good", get_grant_group_from_user("RDDT"))

    def test_get_stock_grants_from_user_adds_watch_only_stock_without_extra_prompts(self):
        portfolio = StockPortfolio()

        with patch("builtins.input", side_effect=["0"]), patch("builtins.print"):
            get_stock_grants_from_user(portfolio, "AAPL")

        grants = portfolio.get_all_stock_grants()
        self.assertEqual(1, len(grants))
        self.assertEqual("AAPL", grants[0].ticker)
        self.assertEqual(0, grants[0].count)
        self.assertEqual(0.0, grants[0].price)
        self.assertEqual(0, grants[0].vests_left)
        self.assertEqual("", grants[0].group)

    def test_get_stock_grants_from_user_adds_grouped_grant(self):
        portfolio = StockPortfolio()

        with patch("builtins.input", side_effect=["100", "$50.25", "4", "b", "n"]), patch("builtins.print"):
            get_stock_grants_from_user(portfolio, "RDDT")

        grants = portfolio.get_all_stock_grants()
        self.assertEqual(1, len(grants))
        self.assertEqual("RDDT", grants[0].ticker)
        self.assertEqual(100, grants[0].count)
        self.assertEqual(50.25, grants[0].price)
        self.assertEqual(4, grants[0].vests_left)
        self.assertEqual("b", grants[0].group)

    def test_render_portfolio_summary_includes_config_grants_groups_and_watch_only_rows(self):
        portfolio = StockPortfolio()
        portfolio.add_stock_grant(StockGrant("RDDT", 357, 216.99, 2, "a"))
        portfolio.add_stock_grant(StockGrant("AAPL", 0, 0, 0))

        summary = render_portfolio_summary(portfolio, "/tmp/config.ini")

        self.assertIn("Saved portfolio to /tmp/config.ini", summary)
        self.assertIn("Portfolio:", summary)
        self.assertIn('- RDDT: 357 shares @ $216.99, 2 vests left, group "a"', summary)
        self.assertIn("- AAPL: watch only", summary)

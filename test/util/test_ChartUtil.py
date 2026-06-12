from unittest import TestCase

from prod.util.ChartUtil import render_range_gauge


class ChartUtilTests(TestCase):

    # region render_range_gauge

    def test_render_range_gauge_unknown_range_is_empty(self):
        self.assertEqual("", render_range_gauge(0, 0, 0))
        self.assertEqual("", render_range_gauge(100, 100, 100))

    def test_render_range_gauge_marker_at_low(self):
        result = render_range_gauge(160.0, 170.0, 160.0, width=10)
        bar = result.split("▕")[1].split("▏")[0]
        self.assertEqual("●", bar[0])
        self.assertEqual("─", bar[-1])

    def test_render_range_gauge_marker_at_high(self):
        result = render_range_gauge(160.0, 170.0, 170.0, width=10)
        bar = result.split("▕")[1].split("▏")[0]
        self.assertEqual("●", bar[-1])

    def test_render_range_gauge_marker_in_middle(self):
        result = render_range_gauge(0.0, 10.0, 5.0, width=11)
        bar = result.split("▕")[1].split("▏")[0]
        self.assertEqual(5, bar.index("●"))

    def test_render_range_gauge_clamps_out_of_range_price(self):
        # A live price above today's high should clamp to the end, not overflow the bar.
        result = render_range_gauge(160.0, 170.0, 999.0, width=10)
        bar = result.split("▕")[1].split("▏")[0]
        self.assertEqual(1, bar.count("●"))
        self.assertEqual("●", bar[-1])

    def test_render_range_gauge_includes_endpoints(self):
        result = render_range_gauge(160.12, 171.40, 166.0, width=10)
        self.assertIn("$160.12", result)
        self.assertIn("$171.40", result)

    # endregion

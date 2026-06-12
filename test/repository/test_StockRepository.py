from unittest import TestCase

from prod.network.ApiService import ApiService, UnknownStockError
from prod.objects.StockInfo import StockInfo
from prod.repository.StockRepository import StockRepository
from prod.resources import Strings


def _make_stock_info(ticker: str) -> StockInfo:
    return StockInfo(ticker, {
        "c": 100.0, "d": 1.0, "dp": 1.0, "h": 101.0,
        "l": 99.0, "o": 100.0, "pc": 99.0, "t": 1,
    })


class _StubApiService:
    """Minimal stand-in for ApiService so we can test StockRepository without the network."""

    def __init__(self, raise_error: Exception = None):
        self.raise_error = raise_error
        self.calls = []
        self.listen_call = None

    def get_stock(self, ticker: str, api_token: str = "") -> StockInfo:
        self.calls.append((ticker, api_token))
        if self.raise_error is not None:
            raise self.raise_error
        return _make_stock_info(ticker)

    def listen_for_stock_updates(self, ticker_list, yesterday_price_dict, callback, status_callback=None):
        # Don't actually open a socket; just record how we were invoked.
        self.listen_call = (ticker_list, yesterday_price_dict, callback, status_callback)


class StockRepositoryTests(TestCase):

    def test_is_finnhub_api_key_valid_true(self):
        repo = StockRepository(_StubApiService())
        self.assertTrue(repo.is_finnhub_api_key_valid("good-key"))

    def test_is_finnhub_api_key_valid_false_on_unknown_stock_error(self):
        # A bad token surfaces as UnknownStockError; this used to escape and crash setup.
        repo = StockRepository(_StubApiService(raise_error=UnknownStockError("bad token")))
        self.assertFalse(repo.is_finnhub_api_key_valid("bad-key"))

    def test_is_finnhub_api_key_valid_false_on_key_error(self):
        repo = StockRepository(_StubApiService(raise_error=KeyError("c")))
        self.assertFalse(repo.is_finnhub_api_key_valid("bad-key"))

    def test_is_ticker_symbol_valid_true(self):
        repo = StockRepository(_StubApiService())
        self.assertTrue(repo.is_ticker_symbol_valid("AAPL"))

    def test_is_ticker_symbol_valid_false(self):
        repo = StockRepository(_StubApiService(raise_error=UnknownStockError("nope")))
        self.assertFalse(repo.is_ticker_symbol_valid("NOPE"))

    # region connection status plumbing

    def test_listen_emits_connecting_and_seeds_initial_prices(self):
        api = _StubApiService()
        repo = StockRepository(api)
        statuses = []
        prices = []

        repo.listen_for_stock_price_updates(["AAPL", "MSFT"], prices.append, statuses.append)

        # The user sees a "connecting" status before any prices arrive.
        self.assertEqual([Strings.CONN_STATUS_CONNECTING], statuses)
        # One initial REST quote per ticker is pushed to the price callback.
        self.assertEqual(2, len(prices))

    def test_listen_forwards_status_callback_to_websocket(self):
        api = _StubApiService()
        repo = StockRepository(api)

        def status_cb(_status):
            pass

        repo.listen_for_stock_price_updates(["AAPL"], lambda _p: None, status_cb)

        # The same status callback must reach the websocket listener so live/reconnect updates show.
        self.assertIsNotNone(api.listen_call)
        self.assertIs(status_cb, api.listen_call[3])

    def test_websocket_close_reports_reconnecting(self):
        statuses = []
        ApiService.__on_close__(None, 1000, "bye", statuses.append)
        self.assertEqual([Strings.CONN_STATUS_RECONNECTING], statuses)

    def test_websocket_error_reports_reconnecting(self):
        statuses = []
        ApiService.__on_web_socket_error__(None, Exception("boom"), statuses.append)
        self.assertEqual([Strings.CONN_STATUS_RECONNECTING], statuses)

    # endregion

import websocket

from prod.network.ApiService import ApiService
from prod.repository.ConfigRepository import ConfigRepository


# Example:
# onMessage: {"data":[{"c":["1","24","12"],"p":168.645,"s":"AAPL","t":1644878285748,"v":1},{"c":["1","24","12"],"p":168.645,"s":"AAPL","t":1644878285748,"v":1}],"type":"trade"}
def on_message(ws, message):
    print(f"onMessage: {message}")


def on_error(ws, error):
    print(f"onError: {error}")


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"aapl"}')
    # ws.send('{"type":"subscribe","symbol":"AMZN"}')
    # ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
    # ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')


def on_stock_update(new_value):
    print(new_value)


if __name__ == "__main__":
    ApiService(ConfigRepository()).listen_for_stock_updates(["twtr"], lambda msg: print(msg))
    # -----

    # ApiService(ConfigRepository()).listen_for_stock_updates(["appl"], lambda x: on_stock_update(x))
    # ApiService(ConfigRepository()).listen_for_stock_updates(["appl"], on_stock_update)

    # -----
    # websocket.enableTrace(True)
    # ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={ConfigRepository().get_finnhub_api_key()}",
    #                             on_message=lambda ws, message: print(message),
    #                             on_error=on_error,
    #                             on_close=on_close)
    # ws.on_open = on_open
    # ws.run_forever()

# if __name__ == "__main__":
#     websocket.enableTrace(False)
#     ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={ConfigRepository().get_finnhub_api_key()}",
#                                 on_message=on_message,
#                                 on_error=on_error,
#                                 on_close=on_close)
#     ws.on_open = on_open
#     ws.run_forever()

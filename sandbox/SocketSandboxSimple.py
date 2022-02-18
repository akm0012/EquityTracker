from prod.network.ApiService import ApiService
from prod.objects.LiveStockInfo import LiveStockInfo
from prod.repository.ConfigRepository import ConfigRepository
from prod.repository.StockRepository import StockRepository
from prod.util.LogUtil import log


def process_stock_update(live_stock_update: LiveStockInfo):
    print(f"{live_stock_update.ticker} was just updated!")
    print(f"New price is {live_stock_update.current_price}!")


if __name__ == "__main__":
    stock_repo = StockRepository(ApiService(ConfigRepository()))
    log(stock_repo.listen_for_stock_price_updates(["twtr", "aapl"], lambda live_stock_update: print(live_stock_update)))

    # ApiService(ConfigRepository()).listen_for_stock_updates(["twtr", "aapl"], lambda update: process_stock_update(update))


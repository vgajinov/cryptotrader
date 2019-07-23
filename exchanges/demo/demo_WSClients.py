import os
import sys
import time
import logging
from exchanges.WS.binance import BinanceWSClient
from exchanges.WS.bitfinex import BitfinexWSClient


# Ticker
# ---------------------------------------------------------------------------------

class Ticker:
    header = ['BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE',
              'DAY_CH_PERC', 'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW']
    fmt = "{:^15}" * len(header)
    client_name = ''
    ticker = []

    def _show_header(self):
        os.system('clear')
        print()
        header_string = '*' * 50 + '\n   TESTING:   {0} {1}\n' + '*' * 50 + '\n'
        print(header_string.format(self.client_name, 'Ticker'))
        print(self.fmt.format(*self.header))

    def show(self):
        self._show_header()
        print(self.fmt.format(*self.ticker))

    def handle_updates(self, sender, data):
        self.ticker = data
        self.show()

    def test(self, client, symbol):
        self.client_name = client.name()
        handle, snapshot = client.subscribe_ticker(symbol, update_handler=self.handle_updates)
        if snapshot:
            self.handle_updates(None, snapshot)
        time.sleep(10)
        client.unsubscribe(handle, update_handler=self.handle_updates)


# All tickers
# ---------------------------------------------------------------------------------

class AllTickers:
    header = ['PAIR', 'BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE',
              'DAY_CH_PERC', 'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW']
    fmt = "{:^15}" * len(header)
    client_name = ''
    tickers = []

    def _show_header(self):
        os.system('clear')
        print()
        header_string = '*' * 50 + '\n   TESTING:   {0} {1}\n' + '*' * 50 + '\n'
        print(header_string.format(self.client_name, 'All Tickers'))
        print(self.fmt.format(*self.header))

    def show(self):
        self._show_header()
        for ticker in self.tickers[:20]:
            print(self.fmt.format(*ticker))


    def handle_updates(self, sender, data):
        self.tickers = data
        self.show()


    def test(self, client):
        self.client_name = client.name()
        handle, snapshot = client.subscribe_all_tickers(update_handler=self.handle_updates)
        if snapshot:
            self.handle_updates(None, snapshot)
        time.sleep(10)
        client.unsubscribe(handle, update_handler=self.handle_updates)


# Order book
# ---------------------------------------------------------------------------------

class OrderBook:
    header = ['PRICE', 'AMOUNT']
    fmt = "{:^15}" * len(header)
    client_name = ''
    bids = {}
    asks = {}

    def _show_header(self):
        os.system('clear')
        print()
        header_string = '*' * 50 + '\n   TESTING:   {0} {1}\n' + '*' * 50 + '\n'
        print(header_string.format(self.client_name, 'Order Book'))
        print(self.fmt.format(*self.header))


    def show(self):
        self._show_header()
        for price, amount in reversed(list(self.asks.items())[0:15]):
            print(self.fmt.format(price, round(amount, 8)))
        print('-' * 40)
        for price, amount in reversed(list(self.bids.items())[-15:]):
            print(self.fmt.format(price, round(amount, 8)))


    def handle_updates(self, sender, data):
        self.bids, self.asks = data['bids'], data['asks']
        self.show()


    def test(self, client, symbol):
        self.client_name = client.name()
        handle, snapshot = client.subscribe_order_book(symbol, update_handler=self.handle_updates)
        if snapshot:
            self.handle_updates(None, snapshot)
        time.sleep(10)
        client.unsubscribe(handle, update_handler=self.handle_updates)


# Trades
# ---------------------------------------------------------------------------------

class Trades:
    header = ['TIMESTAMP', 'AMOUNT', 'PRICE']
    fmt = "{:^15}" * len(header)
    client_name = ''
    trades = []

    def _show_header(self):
        os.system('clear')
        print()
        header_string = '*' * 50 + '\n   TESTING:   {0} {1}\n' + '*' * 50 + '\n'
        print(header_string.format(self.client_name, 'Trades [last 20]'))
        print(self.fmt.format(*self.header))

    def show(self):
        self._show_header()
        for trade in self.trades[-20:]:
            print(self.fmt.format(*trade))


    def handle_updates(self, sender, data):
        update_type, update = data
        if update_type == 'snapshot':
            self.trades = update
        elif update_type == 'update':
            self.trades.append(update)
        else:
            # not valid update
            pass
        self.show()


    def test(self, client, symbol):
        self.client_name = client.name()
        handle, snapshot = client.subscribe_trades(symbol, update_handler=self.handle_updates)
        if snapshot:
            self.handle_updates(None, snapshot)
        time.sleep(10)
        client.unsubscribe(handle, update_handler=self.handle_updates)


# Candles
# ---------------------------------------------------------------------------------

class Candles:
    header = ['MTS', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
    fmt = "{:^15}" * len(header)
    client_name = ''
    candles = []

    def _show_header(self):
        os.system('clear')
        print()
        header_string = '*' * 50 + '\n   TESTING:   {0} {1}\n' + '*' * 50 + '\n'
        print(header_string.format(self.client_name, 'Candles [1m]'))
        print(self.fmt.format(*self.header))

    def show(self):
        self._show_header()
        for candle in self.candles[-20:]:
            print(self.fmt.format(*candle))


    def handle_updates(self, sender, data):
        update_type, update = data
        if update_type == 'snapshot':
            print(update)
            self.candles = update
        elif update_type == 'update':
            self.candles[-1] = update
        elif update_type == 'add':
            self.candles.append(update)
        else:
            # not valid update
            pass
        self.show()


    def test(self, client, symbol):
        self.client_name = client.name()
        handle, snapshot = client.subscribe_candles(symbol, update_handler=self.handle_updates)
        if snapshot:
            self.handle_updates(None, snapshot)
        time.sleep(10)
        client.unsubscribe(handle, update_handler=self.handle_updates)


# INFO handler
# ---------------------------------------------------------------------------------
def info_handler(sender, data):
    print(data)


# Orders
# ---------------------------------------------------------------------------------

class UserOrders:
    header = ['ID', 'TIMESTAMP', 'SYMBOL', 'TYPE', 'SIDE', 'PRICE', 'AMOUNT', 'FILED_PERCENT', 'TOTAL']
    fmt = "{:^15}" * len(header)
    client_name = ''
    orders = []

    def _show_header(self):
        os.system('clear')
        print()
        header_string = '*' * 50 + '\n   TESTING:   {0} {1}\n' + '*' * 50 + '\n'
        print(header_string.format(self.client_name, 'User Orders'))
        print(self.fmt.format(*self.header))

    def show(self):
        self._show_header()
        for order in self.orders:
            print(self.fmt.format(*order))

    def handle_updates(self, sender, data):
        self.orders = data
        self.show()

    def test(self, client):
        self.client_name = client.name()
        self._show_header()
        handle = client.subscribe_user_orders(update_handler=self.handle_updates)
        time.sleep(10)
        client.unsubscribe(handle, update_handler=self.handle_updates)


# User trades
# ---------------------------------------------------------------------------------

class UserTrades:
    header = ['TIMESTAMP', 'SYMBOL', 'TYPE', 'SIDE', 'PRICE', 'AMOUNT', 'FILED', 'TOTAL', 'STATUS']
    fmt = "{:^15}" * len(header)
    client_name = ''
    trades = []

    def _show_header(self):
        os.system('clear')
        print()
        header_string = '*' * 50 + '\n   TESTING:   {0} {1}\n' + '*' * 50 + '\n'
        print(header_string.format(self.client_name, 'User Trades'))
        print(self.fmt.format(*self.header))

    def show(self):
        self._show_header()
        for trade in self.trades:
            print(self.fmt.format(*trade))

    def handle_updates(self, sender, data):
        self.trades = data
        self.show()

    def test(self, client):
        self.client_name = client.name()
        self._show_header()
        handle = client.subscribe_user_trades(update_handler=self.handle_updates)
        time.sleep(10)
        client.unsubscribe(handle, update_handler=self.handle_updates)


# Balances
# ---------------------------------------------------------------------------------

class UserBalances:
    header = ['ASSET', 'BALANCE']
    fmt = "{:^15}" * len(header)
    client_name = ''
    balances = {}

    def _show_header(self):
        os.system('clear')
        print()
        header_string = '*' * 50 + '\n   TESTING:   {0} {1}\n' + '*' * 50 + '\n'
        print(header_string.format(self.client_name, 'User Balances'))
        print(self.fmt.format(*self.header))

    def show(self):
        self._show_header()
        for key, value in self.balances.items():
            if float(value) > 0:
                print(self.fmt.format(key, value))

    def handle_updates(self, sender, data):
        self.balances = data
        self.show()

    def test(self, client):
        self.client_name = client.name()
        self._show_header()
        handle = client.subscribe_balances(update_handler=self.handle_updates)
        time.sleep(30)
        client.unsubscribe(handle, update_handler=self.handle_updates)


# =================================================================================
# Demos
# =================================================================================

def demo_public_channels(client):
    client.connect(info_handler)

    if client.name() == 'Binance':
        symbol = 'BTCUSDT'
        AllTickers().test(client)
        time.sleep(3)
    else:
        symbol = 'BTCUSD'
    Ticker().test(client, symbol)
    time.sleep(3)
    OrderBook().test(client, symbol)
    time.sleep(3)
    Trades().test(client, symbol)
    time.sleep(3)
    Candles().test(client, symbol)
    time.sleep(3)

    client.disconnect()
    time.sleep(5)


# Test multiple channel subscriptions
def demo_multiple_subscriptions(client):
    # add a stdout handler to a client logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    client.logger.addHandler(handler)

    os.system('clear')
    header_string = '*' * 100 + '\n   TESTING:   {0} {1}\n' + '*' * 100 + '\n\n'
    print(header_string.format('Multiple channel subscriptions via websocket for ', client.name()))

    client.connect(info_handler)
    print('\nSubscribing to Ticker:\n' + '-'*100)
    client.subscribe_ticker('LTCBTC')
    time.sleep(1)
    print('\nSubscribing to Candles:\n' + '-' * 100)
    client.subscribe_candles('LTCBTC', '1m')
    time.sleep(1)
    print('\nSubscribing to Trades:\n' + '-' * 100)
    client.subscribe_trades('LTCBTC')
    time.sleep(1)
    print('\nSubscribing to Order Book:\n' + '-' * 100)
    client.subscribe_order_book('LTCBTC')
    time.sleep(5)
    print('\nDisconnecting ...\n' + '-' * 100)
    client.disconnect()
    time.sleep(5)


# Test multiple listeners on the same channel
def demo_multiple_listeners(client):
    class SimpleTicker(Ticker):
        def handle_updates(self, sender, data):
            self.ticker = data

    # add a stdout handler to a client logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    client.logger.addHandler(handler)

    os.system('clear')
    header_string = '*' * 100 + '\n   TESTING:   {0} {1}\n' + '*' * 100 + '\n\n'
    print(header_string.format('Multiple listeners on a Ticker channel for ', client.name()))

    ticker1 = SimpleTicker()
    ticker2 = SimpleTicker()
    ticker3 = SimpleTicker()

    print('\nNew subscriber to a Ticker:\n' + '-' * 100)
    handle1, _ = client.subscribe_ticker('LTCBTC', update_handler=ticker1.handle_updates)
    time.sleep(5)
    print('\nNew subscriber to a Ticker:\n' + '-' * 100)
    handle2, _ = client.subscribe_ticker('LTCBTC', update_handler=ticker2.handle_updates)
    time.sleep(5)
    print('\nNew subscriber to a Ticker:\n' + '-' * 100)
    handle3, _ = client.subscribe_ticker('LTCBTC', update_handler=ticker3.handle_updates)
    time.sleep(5)

    print('\nUNSUBSCRIBING ...\n' + '-' * 100)
    client.unsubscribe(handle1, update_handler=ticker1.handle_updates)
    client.unsubscribe(handle2, update_handler=ticker2.handle_updates)
    client.unsubscribe(handle3, update_handler=ticker3.handle_updates)
    time.sleep(3)

    print('\nDisconnecting:\n' + '-' * 100)
    client.disconnect()
    time.sleep(3)

    print("\nSTATE OF TICKERS:\n" + '-' * 100)
    print(ticker1.fmt.format(*ticker1.header))
    print(ticker1.fmt.format(*ticker1.ticker))
    print(ticker2.fmt.format(*ticker2.ticker))
    print(ticker3.fmt.format(*ticker3.ticker))


# Test authenticated channels
def demo_authenticated(client, key_file):
    client.connect(info_handler)
    client.authenticate(key_file=key_file)

    UserOrders().test(client)
    UserTrades().test(client)
    UserBalances().test(client)

    client.disconnect()
    time.sleep(3)


if __name__ == '__main__':
    choices  = "Choose which demo to run:\n"
    choices += "  (1) demo Binance public channels\n"
    choices += "  (2) demo Bitfinex public channels\n"
    choices += "  (3) demo multiple subscriptions - Binance\n"
    choices += "  (4) demo multiple subscriptions - Bitfinex\n"
    choices += "  (5) demo multiple channel listeners - Binance\n"
    choices += "  (6) demo multiple channel listeners - Bitfinex\n"
    choices += "  (7) demo authenticated channels - Binance\n"
    choices += "  (8) demo authenticated channels - Bitfinex\n"
    print(choices)
    choice = -1
    while choice not in [1, 2, 3, 4, 5, 6, 7, 8]:
        try:
            choice = int(input("Your choice: "))
        except:
            pass

    if choice == 1:
        demo_public_channels(client=BinanceWSClient())
    elif choice == 2:
        demo_public_channels(client=BitfinexWSClient())
    elif choice == 3:
        demo_multiple_subscriptions(client=BinanceWSClient())
    elif choice == 4:
        demo_multiple_subscriptions(client=BitfinexWSClient())
    elif choice == 5:
        demo_multiple_listeners(client=BinanceWSClient())
    elif choice == 6:
        demo_multiple_listeners(client=BitfinexWSClient())
    elif choice == 7:
        path = input("Full path to Binance key file: ")
        demo_authenticated(BinanceWSClient(), path)
    elif choice == 8:
        path = input("Full path to Bitfinex key file: ")
        demo_authenticated(BitfinexWSClient(), path)
    else:
        print("Wrong choice given!")

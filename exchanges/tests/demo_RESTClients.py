from exchanges.REST.bitfinex import BitfinexRESTClient
from exchanges.REST.binance import  BinanceRESTClient
from exchanges.exception import ExchangeException


# =============================================================================
# Test Binance
# =============================================================================

def test_binance():
    binance = BinanceRESTClient()

    print('='*100)
    print('   TESTING Binance public endpoints')
    print('=' * 100)
    print()

    print('STATUS\n' + '-'*30)
    print(binance.ping())
    print()
    print('SERVER TIME\n' + '-'*30)
    print(binance.server_time())
    print()
    print('SYMBOLS\n' + '-'*30)
    print(binance.symbols())
    print()
    print('SYMBOL DETAILS\n' + '-'*30)
    print(binance.symbols_details()['BNBBTC'])
    print()

    print('TICKER\n' + '-'*30)
    print(binance.ticker('bnbbtc'))
    print()
    print('ALL TICKERS (only showing the ones starting with A)\n' + '-'*30)
    res = binance.all_tickers()
    for k in res.keys():
        if k.startswith('A'):
            print(k, res[k])
    print()

    print('ORDER BOOK\n' + '-'*30)
    res = binance.order_book('bnbbtc', limit=10)
    for r in res:
        print(r)
        for i in res[r]:
            print(i)
    print()

    print('TRADES\n' + '-'*30)
    res = binance.trades('bnbbtc', limit=10)
    for r in res: print(r)
    print()

    print('CANDLES\n' + '-'*30)
    res = binance.candles('bnbbtc', '1m', limit=10)
    for r in res: print(r)
    print()

    print('HISTORIC CANDLES\n' + '-'*30)
    res = binance.historical_candles('bnbbtc', '1m', start_time=1519862400000, end_time=1519863300000)
    for r in res: print(r)
    print()


def test_binance_authenticated(file_path):
    # 1. Make sure to update the key file before running these tests
    # 2. Set the prices so that they do not get filled (i.e. buy price bellow current price)
    binance = BinanceRESTClient(key_file=file_path)
    assert binance.authenticated

    print('='*100)
    print('   TESTING Binance authenticated endpoints')
    print('=' * 100)
    print()

    print()
    print('SERVER TIME\n' + '-'*30)
    print(binance.server_time())
    print()
    print('BALANCES\n' + '-'*30)
    print(binance.balance()['BTC'])
    print()
    print('MY TRADES\n' + '-'*30)
    print(binance.user_trades('BNBBTC', limit=10))

    print()
    print('PLACE LIMIT ORDER\n' + '-'*30)
    order1 = binance.place_limit_order('buy', 'bnbbtc', 1, 0.0010655)
    print(order1)
    print()
    print('PLACE LIMIT ORDER\n' + '-'*30)
    order2 = binance.place_limit_order('buy', 'trxbtc', 1000, 0.00000085)
    print(order2)
    print()
    print('PLACE LIMIT ORDER\n' + '-'*30)
    order3 = binance.place_limit_order('buy', 'bnbbtc', 1, 0.00113)
    print(order3)

    print()
    print('GET A SINGLE ORDER STATUS\n' + '-'*30)
    res = binance.order(order1['orderId'], 'BNBBTC')
    for r in res.items(): print(r)
    print()
    print('GET ALL OPEN ORDERS\n' + '-'*30)
    res = binance.open_orders()
    for r in res: print(r)
    print()
    print('GET ALL OPEN ORDERS FOR A SYMBOL\n' + '-'*30)
    res = binance.open_orders_for(order1['symbol'])
    for r in res: print(r)
    print()
    print('GET ALL ORDERS FOR A SYMBOL\n' + '-'*30)
    res = binance.all_orders(order1['symbol'], limit=10)
    for r in res: print(r)
    print()
    print('GET ALL ORDERS STARTING FROM THE FIRST ORDER\n' + '-'*30)
    res = binance.all_orders_since(order1['symbol'], order1['orderId'])
    for r in res: print(r)

    print()
    print('CANCEL ORDER\n' + '-'*30)
    print(binance.cancel_order(order1['orderId'], order1['symbol']))
    print()
    print('CANCEL ORDER\n' + '-'*30)
    print(binance.cancel_order(order2['orderId'], order2['symbol']))
    print()
    print('CANCEL ORDER\n' + '-'*30)
    print(binance.cancel_order(order3['orderId'], order3['symbol']))


def test_binance_listen_key(file_path):
    binance = BinanceRESTClient(key_file=file_path)

    print()
    print('CREATE LISTEN KEY\n' + '-'*30)
    listen_key = binance.create_listen_key()['listenKey']
    print(binance.create_listen_key())
    print()

    print()
    print('PING LISTEN KEY\n' + '-'*30)
    print(binance.ping_listen_key(listen_key))
    print()

    print()
    print('CLOSE LISTEN KEY\n' + '-'*30)
    print(binance.close_listen_key(listen_key))
    print()


# =============================================================================
# Test Bitfinex
# =============================================================================

def test_bitfinex():
    bitfinex  = BitfinexRESTClient()

    print('='*100)
    print('   TESTING Bitfinex public endpoints')
    print('=' * 100)
    print()

    print('STATUS\n' + '-' * 30)
    print(bitfinex.ping())
    print()

    print('SYMBOLS\n' + '-' * 30)
    print(bitfinex.symbols())
    print()
    print('SYMBOLS DETAILS\n' + '-' * 30)
    print(bitfinex.symbols_details()['BTCUSD'])
    print()

    print('TICKER\n' + '-' * 30)
    print(bitfinex.ticker('btcusd'))
    print()
    print('TICKERS\n' + '-' * 30)
    print(bitfinex.tickers(['BTCUSD', 'LTCBTC', 'ETHBTC']))
    print()
    print('ALL TICKERS (only showing btc tickers)\n' + '-' * 30)
    res = bitfinex.all_tickers()
    for k in res.keys():
        if k.startswith('BTC'):
            print(k, res[k])
    print()

    print('ORDER BOOK\n' + '-' * 30)
    res = bitfinex.order_book('BTCUSD', len=25)
    for r in res.keys():
        print(r)
        for i in res[r][:10]:
            print(i)
    print()

    print('TRADES\n' + '-' * 30)
    res = bitfinex.trades('BTCUSD', limit_trades=10)
    for r in res: print(r)
    print()

    print('CANDLES\n' + '-'*30)
    res = bitfinex.candles('BTCUSD', '1m', limit=10)
    for r in res: print(r)
    print()

    print('HISTORIC CANDLES\n' + '-'*30)
    res = bitfinex.historical_candles('BTCUSD', '1m', start_time=1519862400000, end_time=1519863300000)
    for r in res: print(r)
    print()


def test_bitfinex_authenticated(file_path):
    # 1. Make sure to update the key file before running these tests
    # 2. Set the prices so that they do not get filled (i.e. buy price bellow current price)
    try:
        bitfinex = BitfinexRESTClient(key_file=file_path)
        assert bitfinex.authenticated

        print()
        print('='*100)
        print('   TESTING Bitfinex authenticated endpoints')
        print('=' * 100)
        print()

        print()
        print('BALANCES\n' + '-'*30)
        res = bitfinex.balance()
        for r in res.items():
            print(r)

        print()
        print('MY TRADES\n' + '-'*30)
        res = bitfinex.user_trades('btcusd', limit_trades=10)
        for r in res: print(r)
        print()
        print('GET ALL ORDERS (history)\n' + '-'*30)
        res = bitfinex.all_orders(None, limit=10)
        for r in res: print(r)
        print()
        print('GET ALL ORDERS FOR A SYMBOL (history - not active orders)\n' + '-'*30)
        res = bitfinex.all_orders('BTCUSD', limit=10)
        for r in res: print(r)

        print()
        print('PLACE LIMIT ORDER\n' + '-'*30)
        order1 = bitfinex.place_limit_order('sell', 'btcusd', 0.005, 123000)
        print(order1)
        print()
        print('PLACE LIMIT ORDER\n' + '-'*30)
        order2 = bitfinex.place_limit_order('buy', 'ltcbtc', 0.1, 0.000002)
        print(order2)
        print()
        print('PLACE LIMIT ORDER\n' + '-'*30)
        order3 = bitfinex.place_limit_order('buy', 'ethbtc', 0.1, 0.0001)
        print(order3)

        print()
        print('GET A SINGLE ORDER STATUS\n' + '-'*30)
        res = bitfinex.order(order1['orderId'], None)
        for r in res.items(): print(r)
        print()
        print('GET ALL OPEN ORDERS\n' + '-'*30)
        res = bitfinex.open_orders()
        for r in res: print(r)

        print()
        print('CANCEL ORDER\n' + '-'*30)
        print(bitfinex.cancel_order(order1['orderId'], order1['symbol']))
        print()
        print('CANCEL ALL\n' + '-'*30)
        print(bitfinex.cancel_all_orders())

        print()
        print('PLACE LIMIT ORDER\n' + '-'*30)
        order1 = bitfinex.place_limit_order('sell', 'btcusd', 0.005, 123000)
        print(order1)
        print()
        print('PLACE LIMIT ORDER\n' + '-'*30)
        order2 = bitfinex.place_limit_order('buy', 'ltcbtc', 0.1, 0.000002)
        print(order2)
        print()
        print('CANCEL MULTIPLE ORDERS\n' + '-'*30)
        print(bitfinex.cancel_multiple_orders([order1['orderId'], order2['orderId']]))
        print()
        print('GET ALL OPEN ORDERS\n' + '-'*30)
        res = bitfinex.open_orders()
        for r in res: print(r)
        print()
    except ExchangeException as e:
        print(e)


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    choices = "Demo REST clients:\n"
    choices += "Choose which demo to run:\n"
    choices += "  (1) demo Binance public channels\n"
    choices += "  (2) demo Binance authenticated channels\n"
    choices += "  (3) demo Binance listen key\n"
    choices += "  (4) demo Bitfinex public channels\n"
    choices += "  (5) demo Bitfinex authenticated channels\n"
    print(choices)
    choice = -1
    while choice not in [1, 2, 3, 4, 5]:
        try:
            choice = int(input("Your choice: "))
        except:
            pass

    if choice == 1:
        test_binance()
    elif choice == 2:
        path = input("Full path to Binance key file: ")
        test_binance_authenticated(path)
    elif choice == 3:
        path = input("Full path to Binance key file: ")
        test_binance_listen_key(path)
    elif choice == 4:
        test_bitfinex()
    elif choice == 5:
        path = input("Full path to Bitfinex key file: ")
        test_bitfinex_authenticated(path)
    else:
        print("Wrong choice given!")

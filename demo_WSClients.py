import os
import time
from pydispatch import dispatcher
from exchanges.WS.binance import BinanceWSClient
from exchanges.WS.bitfinex import BitfinexWSClient


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


getch = _GetchUnix()


# Ticker
# ---------------------------------------------------------------------------------

def showTicker(ticker):
    print('*' * 50 + '\n   TESTING:    Ticker\n' + '*' * 50 + '\n')
    fmt = "{:^14}" * (10)
    print( fmt.format('BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE', 'DAY_CH_PERC',
                      'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW') )
    print(fmt.format(*ticker))


# listener for ticker updates
def handleTicker(sender, data):
    os.system('clear')
    showTicker(data)


def testTicker(client):
    handle = client.subscribe_ticker('LTCBTC', update_handler=handleTicker)
    time.sleep(10)
    client.unsubscribe(handle, update_handler=handleTicker)


# All tickers
# ---------------------------------------------------------------------------------

def showAllTickers(tickers):
    os.system('clear')
    print('*' * 50 + '\n   TESTING:    All Tickers (showing 20)\n' + '*' * 50 + '\n')
    fmt = "{:^14}" * (11)
    print( fmt.format('PAIR', 'BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE', 'DAY_CH_PERC',
                      'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW') )
    for ticker in tickers[:20]:
        print(fmt.format(*ticker))


# listener for all ticker updates
def handleAllTickers(sender, data):
    showAllTickers(data)


def testAllTickers(client):
    handle = client.subscribe_all_tickers(update_handler=handleAllTickers)
    time.sleep(10)
    client.unsubscribe(handle, update_handler=handleAllTickers)


# Order book
# ---------------------------------------------------------------------------------

def showBook(bids, asks):
    os.system('clear')
    print ('*'*50 + '\n   TESTING:    OrderBook\n' + '*'*50 + '\n')
    print ("{:^15}{:^15}\n".format('PRICE', 'AMOUNT'))
    for price, amount in reversed(list(asks.items())[0:15]):
        print ("{:>15}{:>15}".format(price, round(-amount, 8)))
    print('-'*40)
    for price, amount in reversed(list(bids.items())[-15:]):
        print("{:>15}{:>15}".format(price, round(amount, 8)))


# listener for book updates
def handleBook(sender, data):
    showBook(data['bids'], data['asks'])


def testBook(client):
    handle = client.subscribe_order_book('LTCBTC', update_handler=handleBook)
    time.sleep(10)
    client.unsubscribe(handle, update_handler=handleBook)


# Trades
# ---------------------------------------------------------------------------------

def showTrades(trades):
    os.system('clear')
    print('*' * 50 + '\n   TESTING:    Trades\n' + '*' * 50 + '\n')
    print ("{:^15}{:^15}{:^15}\n".format('TIMESTAMP', 'AMOUNT', 'PRICE'))
    for trade in trades:
        print("{:>15}{:>15}{:>15}".format(*trade))


# listener for trade updates
def handleTrades(sender, data):
    showTrades(data)


def testTrades(client):
    handle = client.subscribe_trades('LTCBTC', update_handler=handleTrades)
    time.sleep(10)
    client.unsubscribe(handle, update_handler=handleTrades)


# Candles
# ---------------------------------------------------------------------------------

def showCandles(candles):
    os.system('clear')
    print('*' * 50 + '\n   TESTING:    Candles [1m]\n' + '*' * 50 + '\n')
    header = ['MTS', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']
    fmt = "{:^15}" * (len(header))
    print( fmt.format(*header) )
    for candle in candles[-20:]:
        print(fmt.format(*candle))


# listener for candle updates
def handleCandles(sender, data):
    showCandles(data)


def testCandles(client):
    handle = client.subscribe_candles('LTCBTC', update_handler=handleCandles)
    time.sleep(5)
    client.unsubscribe(handle, update_handler=handleCandles)


# INFO handler
# ---------------------------------------------------------------------------------
def info_handler(sender, data):
    print(data)


# Orders
# ---------------------------------------------------------------------------------

def showOrders(orders):
    os.system('clear')
    print()
    print('*' * 50 + '\n   TESTING:    Orders\n' + '*' * 50 + '\n')
    header = ['ID', 'TIMESTAMP', 'SYMBOL', 'TYPE', 'SIDE', 'PRICE', 'AMOUNT', 'FILED_PERCENT', 'TOTAL']
    fmt = "{:^15}" * (len(header))
    print( fmt.format(*header) )
    for order in orders:
        print(fmt.format(*order))


# listener for candle updates
def handleOrders(sender, data):
    showOrders(data)


def testOrders(client):
    os.system('clear')
    print('*' * 50 + '\n   TESTING:    Orders\n' + '*' * 50 + '\n')
    handle = client.subscribe_user_orders(update_handler=handleOrders)
    time.sleep(30)
    client.unsubscribe(handle, update_handler=handleOrders)


# User trades
# ---------------------------------------------------------------------------------

def showUserTrades(trades):
    os.system('clear')
    print('*' * 50 + '\n   TESTING:    User Trades\n' + '*' * 50 + '\n')
    header = ['TIMESTAMP', 'SYMBOL', 'TYPE', 'SIDE', 'PRICE', 'AMOUNT', 'FILED', 'TOTAL', 'STATUS']
    fmt = "{:^15}" * (len(header))
    print( fmt.format(*header) )
    for trade in trades:
        print(fmt.format(*trade))


# listener for candle updates
def handleUserTrades(sender, data):
    showUserTrades(data)


def testUserTrades(client):
    os.system('clear')
    print('*' * 50 + '\n   TESTING:    User Trades\n' + '*' * 50 + '\n')
    handle = client.subscribe_user_trades(update_handler=handleUserTrades)
    time.sleep(30)
    client.unsubscribe(handle, update_handler=handleUserTrades)


# Balances
# ---------------------------------------------------------------------------------

def showBalances(balances):
    os.system('clear')
    print('*' * 50 + '\n   TESTING:    Balances\n' + '*' * 50 + '\n')
    header = ['ASSET', 'BALANCE']
    fmt = "{:^15}" * (len(header))
    print( fmt.format(*header) )
    for key, value in balances.items():
        if float(value) > 0:
            print(fmt.format(key, value))


# listener for candle updates
def handleBalances(sender, data):
    showBalances(data)


def testBalances(client):
    os.system('clear')
    print('*' * 50 + '\n   TESTING:    Balances\n' + '*' * 50 + '\n')
    handle = client.subscribe_balances(update_handler=handleBalances)
    time.sleep(30)
    client.unsubscribe(handle, update_handler=handleBalances)


# =================================================================================
# Demos
# =================================================================================

def demoBinance():
    client = BinanceWSClient()
    client.connect(info_handler)

    testAllTickers(client)
    time.sleep(3)
    testTicker(client)
    time.sleep(3)
    testBook(client)
    time.sleep(3)
    testTrades(client)
    time.sleep(3)
    testCandles(client)
    time.sleep(3)

    client.disconnect()


def demoBitfinex():
    client = BitfinexWSClient()
    client.connect(info_handler)

    testTicker(client)
    time.sleep(3)
#    testBook(client)
#    time.sleep(3)
#    testTrades(client)
#    time.sleep(3)
#    testCandles(client)
#    time.sleep(3)

    client.disconnect()



# Test multiple subscriptions and disconnect
def demoMultiSubscriptions(client):
    client.connect(info_handler)
    client.subscribe_ticker('LTCBTC')
    time.sleep(1)
    client.subscribe_candles('LTCBTC', '1m')
    time.sleep(1)
    client.subscribe_trades('LTCBTC')
    time.sleep(1)
    client.subscribe_order_book('LTCBTC')
    time.sleep(5)
    client.disconnect()



def demoMultiListeners(client):

    def handleTicker1(sender, data):
        print()
        print('#### Listener 1 ####')
        showTicker(data)

    def handleTicker2(sender, data):
        print()
        print('#### Listener 2 ####')
        showTicker(data)

    client.connect(info_handler)
    handle = client.subscribe_ticker('LTCBTC', update_handler=handleTicker1)
    time.sleep(10)
    handle2 = client.subscribe_ticker('LTCBTC', update_handler=handleTicker2)
    time.sleep(20)
    client.unsubscribe(handle, update_handler=handleTicker1)
    client.unsubscribe(handle2, update_handler=handleTicker2)
    client.disconnect()


def demoAuthenticated(client, keyFile):
    client.connect(info_handler)
    client.authenticate(key_file=keyFile)

    testOrders(client)
    # testUserTrades(client)
    # testBalances(client)

    client.disconnect()


# =================================================================================
# Demo runs
# =================================================================================

# demoBinance()
demoBitfinex()

# demoMultiSubscriptions(client=BitfinexWSClient())
# demoMultiSubscriptions(client=BinanceWSClient())

# demoMultiListeners(client=BitfinexWSClient())
# demoMultiListeners(client=BinanceWSClient())

# demoAuthenticated(BitfinexWSClient(), '/home/vladimir/work/keys/bitfinex.key')
# demoAuthenticated(BinanceWSClient(), '/home/vladimir/work/keys/binance.key')
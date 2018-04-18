# Import Built-ins
import os
import time

# Import Third-Party
from pydispatch import dispatcher

# Import Homebrew
from exchanges.WS.binance import BinanceWSClient


# Ticker
# ---------------------------------------------------------------------------------

def showTicker(ticker):
   os.system('clear')
   print('*' * 50 + '\n   TESTING:    Ticker\n' + '*' * 50 + '\n')
   fmt = "{:^14}" * (10)
   print( fmt.format('BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE', 'DAY_CH_PERC',
                     'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW') )
   print(fmt.format(*ticker))

# listener for trade updates
def handleTicker(sender, data):
   showTicker(data)


def testTicker(client):
   handle = client.subscribe_ticker('TRXBTC')
   dispatcher.connect(handleTicker, signal=handle, sender='binance')
   time.sleep(10)
   dispatcher.disconnect(handleTicker, signal=handle, sender='binance')
   client.unsubscribe(handle)


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

# listener for trade updates
def handleAllTickers(sender, data):
   showAllTickers(data)

def testAllTickers(client):
   handle = client.subscribe_all_tickers()
   dispatcher.connect(handleAllTickers, signal=handle, sender='binance')
   time.sleep(10)
   dispatcher.disconnect(handleTicker, signal=handle, sender='binance')
   client.unsubscribe(handle)

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
   handle = client.subscribe_order_book('ETHBTC', update_handler=handleBook)
   # dispatcher.connect(handleBook, signal=handle, sender='binance')
   time.sleep(10)
   dispatcher.disconnect(handleBook, signal=handle, sender='binance')
   client.unsubscribe(handle)
   client.unsubscribe('test')
   dispatcher.disconnect(handleBook, signal=handle, sender='binance')


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
   handle = client.subscribe_trades('ETHBTC')
   dispatcher.connect(handleTrades, signal=handle, sender='binance')
   time.sleep(10)
   dispatcher.disconnect(handleTrades, signal=handle, sender='binance')
   client.unsubscribe(handle)


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

# listener for trade updates
def handleCandles(sender, data):
   showCandles(data)

def testCandles(client):
   handle = client.subscribe_candles('TRXBTC')
   dispatcher.connect(handleCandles, signal=handle, sender='binance')
   time.sleep(5)
   dispatcher.disconnect(handleCandles, signal=handle, sender='binance')
   client.unsubscribe(handle)





# TESTS
# ---------------------------------------------------------------------------------

# create the client
client = BinanceWSClient()
client.connect()

# testTicker(client)
# time.sleep(3)
#
# testAllTickers(client)
# time.sleep(3)

testBook(client)
time.sleep(3)

# testTrades(client)
# time.sleep(3)
#
# testCandles(client)
# time.sleep(3)

client.disconnect()


# Test multiple subscriptions and disconnect
# client.connect()
# client.subscribe('candles', {'pair': 'TRXBTC'})
# time.sleep(1)
# client.subscribe('candles', {'pair': 'ETHBTC'})
# time.sleep(1)
# client.subscribe('book', {'pair': 'TRXBTC'})
# time.sleep(5)
# client.disconnect()




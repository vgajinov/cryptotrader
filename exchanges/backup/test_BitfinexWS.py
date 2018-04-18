# Import Built-ins
import os
import time

# Import Third-Party
from pydispatch import dispatcher

# Import Homebrew
from exchanges.WS.bitfinex import BitfinexWSClient




# Ticker
# ---------------------------------------------------------------------------------

def showTicker(ticker):
   os.system('clear')
   print('Ticker\n')
   fmt = "{:^14}" * (10)
   print( fmt.format('BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE', 'DAY_CH_PERC',
                     'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW') )
   fmt = "{:^14}" * (10)
   print(fmt.format(*ticker))

# listener for trade updates
def handleTicker(sender, data):
   showTicker(data)


def testTicker(client):
   os.system('clear')
   chanId = client.subscribe_ticker('BTCUSD')
   dispatcher.connect(handleTicker, signal=chanId, sender='bitfinex')
   time.sleep(10)
   dispatcher.disconnect(handleTicker, signal=chanId, sender='bitfinex')
   client.unsubscribe(chanId)
   time.sleep(3)


# Order book
# ---------------------------------------------------------------------------------

def showBook(bids, asks):
   os.system('clear')
   print ('OrderBook\n')
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
   chanId = client.subscribe_order_book('BTCUSD', prec='P1', len=10, update_handler=handleBook)
   dispatcher.connect(handleBook, signal=chanId, sender='bitfinex')
   time.sleep(10)
   dispatcher.disconnect(handleBook, signal=chanId, sender='bitfinex')
   client.unsubscribe(chanId)


# Trades
# ---------------------------------------------------------------------------------

def showTrades(trades):
   os.system('clear')
   print ('Trades\n')
   print ("{:^15}{:^15}{:^15}\n".format('ORDER_ID', 'AMOUNT', 'PRICE'))
   for trade in trades[-10:]:
      print("{:>15}{:>15}{:>15}".format(*trade))


# listener for trade updates
def handleTrades(sender, data):
   showTrades(data)


def testTrades(client):
   chanId = client.subscribe_trades('BTCUSD')
   dispatcher.connect(handleTrades, signal=chanId, sender='bitfinex')
   time.sleep(10)
   dispatcher.disconnect(handleTrades, signal=chanId, sender='bitfinex')
   client.unsubscribe(chanId)


# Candles
# ---------------------------------------------------------------------------------

def showCandles(candles):
   os.system('clear')
   header = ['MTS', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']
   print('Candles\n')
   fmt = "{:^15}" * (len(header))
   print( fmt.format(*header) )
   for candle in candles[-10:]:
      print(fmt.format(*candle))

# listener for trade updates
def handleCandles(sender, data):
   showCandles(data)

def testCandles(client):
   chanId = client.subscribe_candles('BTCUSD', '1m')
   dispatcher.connect(handleCandles, signal=chanId, sender='bitfinex')
   time.sleep(10)
   dispatcher.disconnect(handleCandles, signal=chanId, sender='bitfinex')
   client.unsubscribe(chanId)

#'candles_BTCUSD'


# TESTS
# ---------------------------------------------------------------------------------

# create the client
client = BitfinexWSClient()
client.connect()

# testTicker(client)
# time.sleep(2)

testBook(client)
time.sleep(2)

# testTrades(client)
# time.sleep(2)
#
# testCandles(client)
# time.sleep(2)



client.disconnect()


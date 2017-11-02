import os, sys
import time
from datetime import datetime
from pydispatch import dispatcher
import bitfinex_v2_WebSockets



# RawBook
# ---------------------------------------------------------------------------------

# client.subscribe('raw_book', {'pair':"BTCUSD"})


# Order book
# ---------------------------------------------------------------------------------

#client.subscribe('book', {'pair': "BTCUSD", 'prec': "P0"})

def showBook(bids, asks):
   os.system('clear')
   print ('OrderBook\n')
   print ("{:^15}{:^15}\n".format('PRICE', 'AMOUNT'))
   for price, amount in list(asks.items())[-15:]:
      print ("{:>15}{:>15}".format(price, round(-amount, 8)))
   print('-'*40)
   for price, amount in list(bids.items())[:15]:
      print("{:>15}{:>15}".format(price, round(amount, 8)))


# listener for book updates
def handleBook(sender, bids, asks):
   showBook(bids, asks)


def testBook(client):
   dispatcher.connect(handleBook, signal='book_BTCUSD', sender='bitfinex')
   time.sleep(10)
   dispatcher.disconnect(handleBook, signal='book_BTCUSD', sender='bitfinex')


# Trades
# ---------------------------------------------------------------------------------

#client.subscribe('trades', {'pair':"BTCUSD"})

def showTrades(trades):
   os.system('clear')
   print ('Trades\n')
   print ("{:^15}{:^15}{:^15}\n".format('ORDER_ID', 'PRICE', 'AMOUNT'))
   for trade in trades:
      print("{:>15}{:>15}{:>15}".format(*trade))


# listener for trade updates
def handleTrades(sender, trades):
   showTrades(trades)


def testTrades(client):
   trades = client.getTrades('BTCUSD')
   if trades:
      handleTrades('bitfinex', trades.getTrades)
   dispatcher.connect(handleTrades, signal='trades_BTCUSD', sender='bitfinex')
   time.sleep(10)
   dispatcher.disconnect(handleTrades, signal='trades_BTCUSD', sender='bitfinex')


# Ticker
# ---------------------------------------------------------------------------------

# client.subscribe('ticker', {'pair': "BTCUSD"})

def showTicker(ticker):
   os.system('clear')
   print('Ticker\n')
   fmt = "{:^14}" * (10)
   print( fmt.format('BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE', 'DAY_CH_PERC',
                     'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW') )
   fmt = "{:^14}" * (10)
   print(fmt.format(*ticker))

# listener for trade updates
def handleTicker(sender, ticker):
   showTicker(ticker)


def testTicker(client):
   os.system('clear')
   ticker = client.getTicker('BTCUSD')
   if ticker:
      handleTicker('bitfinex', ticker)
   dispatcher.connect(handleTicker, signal='ticker_BTCUSD', sender='bitfinex')
   time.sleep(20)
   dispatcher.disconnect(handleTicker, signal='ticker_BTCUSD', sender='bitfinex')



# Candles
# ---------------------------------------------------------------------------------

# client.subscribe('candles', {'pair': "BTCUSD", 'scale': "1m"})

def showCandles(candles):
   os.system('clear')
   header = ['MTS', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']
   print('Candles\n')
   fmt = "{:^15}" * (len(header))
   print( fmt.format(*header) )
   for candle in candles:
      print(fmt.format(*candle))

# listener for trade updates
def handleCandles(sender, candles):
   showCandles(candles)

def testCandles(client):
   candles = client.getCandles('BTCUSD')
   if candles:
      handleCandles('bitfinex', candles.getCandles)
   dispatcher.connect(handleCandles, signal='candles_BTCUSD', sender='bitfinex')
   time.sleep(10)
   dispatcher.disconnect(handleCandles, signal='candles_BTCUSD', sender='bitfinex')



# TESTS
# ---------------------------------------------------------------------------------

# create the client
client = bitfinex_v2_WebSockets.BitfinexWSClient()
client.connect()

#testBook(client)
#time.sleep(2)

#testTrades(client)
#time.sleep(2)

#testTicker(client)
#time.sleep(2)

testCandles(client)
time.sleep(2)



client.disconnect()




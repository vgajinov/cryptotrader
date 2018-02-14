import os, sys
import time
from datetime import datetime
from pydispatch import dispatcher
import binance_Websocket



# Order book
# ---------------------------------------------------------------------------------

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
   dispatcher.connect(handleBook, signal='book_ethbtc', sender='binance')
   client.subscribe('book', {'pair': 'ETHBTC'})
   time.sleep(10)
   dispatcher.disconnect(handleBook, signal='book_ethbtc', sender='binance')


# Trades
# ---------------------------------------------------------------------------------

# client.subscribe('trades', {'pair':"BTCUSD"})

def showTrades(trades):
   os.system('clear')
   print ('Trades\n')
   print ("{:^15}{:^15}{:^15}{:^15}\n".format('ORDER_ID', 'TIMESTAMP', 'AMOUNT', 'PRICE'))
   for trade in trades:
      print("{:>15}{:>15}{:>15}{:^15}".format(*trade))


# listener for trade updates
def handleTrades(sender, trades):
   showTrades(trades)


def testTrades(client):
   dispatcher.connect(handleTrades, signal='trades_ethbtc', sender='binance')
   client.subscribe('trades', {'pair': 'ETHBTC'})
   time.sleep(10)
   dispatcher.disconnect(handleTrades, signal='trades_ethbtc', sender='binance')


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
   dispatcher.connect(handleCandles, signal='candles_trxbtc', sender='binance')
   client.subscribe('candles', {'pair': 'TRXBTC'})
   time.sleep(10)
   dispatcher.disconnect(handleCandles, signal='candles_trxbtc', sender='binance')


# Ticker
# ---------------------------------------------------------------------------------

# client.subscribe('ticker', {'pair': "BTCUSD"})

def showTicker(ticker):
   os.system('clear')
   print('Ticker\n')
   fmt = "{:^14}" * (10)
   print( fmt.format('BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE', 'DAY_CH_PERC',
                     'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW') )
   print(fmt.format(*ticker))

# listener for trade updates
def handleTicker(sender, ticker):
   showTicker(ticker)


def testTicker(client):
   dispatcher.connect(handleTicker, signal='ticker_trxbtc', sender='binance')
   client.subscribe('ticker', {'pair': 'TRXBTC'})
   time.sleep(10)
   dispatcher.disconnect(handleTicker, signal='ticker_trxbtc', sender='binance')

# All tickers
def showAllTickers(tickers):
   os.system('clear')
   print('Tickers\n')
   fmt = "{:^14}" * (11)
   print( fmt.format('PAIR', 'BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE', 'DAY_CH_PERC',
                     'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW') )
   for ticker in tickers:
      print(fmt.format(*ticker))

# listener for trade updates
def handleAllTickers(sender, tickers):
   showAllTickers(tickers)

def testAllTickers(client):
   dispatcher.connect(handleAllTickers, signal='ticker_all', sender='binance')
   client.subscribe('ticker', {'pair': 'ALL'})
   time.sleep(10)
   dispatcher.disconnect(handleTicker, signal='ticker_all', sender='binance')


# TESTS
# ---------------------------------------------------------------------------------

# create the client
client = binance_Websocket.BinanceWSClient()
client.connect()

#testBook(client)
#time.sleep(2)

#testTrades(client)
#time.sleep(2)

testCandles(client)
time.sleep(2)

#testTicker(client)
#time.sleep(2)

#testAllTickers(client)
#time.sleep(2)

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




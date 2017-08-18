import os, sys
import time
from datetime import datetime


import bitfinex_v1_REST

# symbol to query the order book
symbol = 'btcusd'

# create the client
client = bitfinex_v1_REST.Client()


def Test_getTicker():
   time.sleep(1)
   # get latest ticker
   ticker = client.ticker(symbol)
   print ('\nTesting: get Ticker\n', '-' * 50)
   print ("Last Ticker at %s" % (datetime.now()))
   print (ticker)


def Test_getStats():
   time.sleep(1)
   stats = client.stats(symbol)
   print ('\nTesting: get Stats\n', '-' * 50)
   print (stats)


def Test_getFundingbook():
   time.sleep(1)
   fbook = client.lendbook('BTC')
   print ('\nTesting: get FundingBook\n', '-' * 50)
   print (fbook)


def Test_getOrderbook():
   time.sleep(1)
   # set the parameters to limit the number of bids or asks
   parameters = {'limit_asks': 5, 'limit_bids': 5}

   # get the order book
   orders = client.order_book(symbol, parameters)

   print ('\nTesting: get Orderbook\n', '-' * 50)
   for order_type in orders:
      print(order_type)
      for order in orders[order_type]:
         print (order['price'], order['amount'])


def Test_getTrades():
   time.sleep(1)
   parameters = {'timestamp': 1502026534, 'limit_trades': 10}
   trades = client.trades(symbol, parameters)
   print ('\nTesting: get Trades\n', '-' * 50)
   print(trades)


def Test_getLends():
   time.sleep(1)
   parameters = {'timestamp': 1502026534, 'limit_lends': 10}
   lends = client.lends('BTC', parameters)
   print ('\nTesting: get FundingBook\n', '-' * 50)
   print(lends)


def Test_getSymbols():
   time.sleep(1)
   symb = client.symbols()
   print ('\nTesting: get Symbols\n', '-' * 50)
   print (symb)


def Test_getSymbolDetails():
   time.sleep(1)
   fbook = client.symbols_details()
   print ('\nTesting: get SymbolDetails\n', '-' * 50)
   print (fbook)


def TestPublicAPI():
   # clear the display, and update values
   os.system('clear')
   Test_getTicker()
   Test_getStats()
   Test_getFundingbook()
   Test_getOrderbook()
   Test_getTrades()
   Test_getLends()
   Test_getSymbols()
   Test_getSymbolDetails()


TestPublicAPI()

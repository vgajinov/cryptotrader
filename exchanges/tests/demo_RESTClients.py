# Import Homebrew
from exchanges.REST.bitfinex import BitfinexRESTClient
from exchanges.REST.binance import  BinanceRESTClient



# =============================================================================
# Test Binance
# =============================================================================

def testBinance():
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
   res = binance.historical_candles('bnbbtc', '1m', startTime=1519862400000, endTime=1519863300000)
   for r in res: print(r)
   print()



def testBinanceAuth():
   # 1. Make sure to update the key file before running these tests
   # 2. Set the prices so that they do not get filled (i.e. buy price bellow current price)
   binance = BinanceRESTClient(key_file='binance.key')

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
   print(binance.my_trades('BNBBTC', limit=10))

   print()
   print('PLACE LIMIT ORDER\n' + '-'*30)
   order1 = binance.place_limit_order('buy', 'bnbbtc', 1, 0.0010655)
   print(order1)
   print()
   print('PLACE LIMIT ORDER\n' + '-'*30)
   order2 = binance.place_limit_order('buy', 'trxbtc', 1000, 0.00000280)
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

   # This order will be executed immediately
   # print()
   # print('PLACE MARKET ORDER\n' + '-'*30)
   # morder = binance.place_market_order('buy', 'bnbbtc', 1)
   # print(morder)
   # print()
   # print('GET A SINGLE ORDER STATUS\n' + '-'*30)
   # res = binance.order(morder['orderId'], 'BNBBTC')
   # for r in res.items(): print(r)

   # These order types do not seem to work!
   #
   # print()
   # print('PLACE STOP-LOSS-LIMIT ORDER\n' + '-'*30)
   # order = binance.place_stoploss_order('buy', 'trxbtc', 1000, 0.00000280)
   # print(order)
   # print()
   # print('PLACE STOP-LOSS-LIMIT ORDER\n' + '-'*30)
   # order = binance.place_stoplosslimit_order('buy', 'trxbtc', 1000, 0.00000280, 0.00000275)
   # print(order)




# =============================================================================
# Test Bitfinex
# =============================================================================

def testBitfinex():
   bitfinex  = BitfinexRESTClient(key_file='bitfinex.key')

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
   print(bitfinex.symbols_details()['btcusd'])
   print()

   print('TICKER\n' + '-' * 30)
   print(bitfinex.ticker('btcusd'))
   print()
   print('TICKERS\n' + '-' * 30)
   print(bitfinex.tickers(['btcusd','ltcbtc','ethbtc']))
   print()
   print('ALL TICKERS (only showing btc tickers)\n' + '-' * 30)
   res = bitfinex.all_tickers()
   for k in res.keys():
      if k.startswith('btc'):
         print(k, res[k])
   print()

   print('ORDER BOOK\n' + '-' * 30)
   res = bitfinex.order_book('btcusd', len=25)
   for r in res.keys():
      print(r)
      for i in res[r][:10]:
         print(i)
   print()

   print('TRADES\n' + '-' * 30)
   res = bitfinex.trades('btcusd', limit_trades=10)
   for r in res: print(r)
   print()

   print('CANDLES\n' + '-'*30)
   res = bitfinex.candles('btcusd', '1m', limit=10)
   for r in res: print(r)
   print()
   print('HISTORIC CANDLES\n' + '-'*30)
   res = bitfinex.historical_candles('btcusd', '1m', startTime=1519862400000, endTime=1519863300000)
   for r in res: print(r)
   print()



def testBitfinexAuth():
   # 1. Make sure to update the key file before running these tests
   # 2. Set the prices so that they do not get filled (i.e. buy price bellow current price)
   bitfinex = BitfinexRESTClient(key_file='bitfinex.key')

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
   res = bitfinex.my_trades('btcusd', limit_trades=10)
   for r in res:
      print(r)


   print()
   print('PLACE LIMIT ORDER\n' + '-'*30)
   order1 = bitfinex.place_limit_order('sell', 'btcusd', 0.01, 123000)
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
   print('GET ALL ORDERS (history)\n' + '-'*30)
   res = bitfinex.all_orders(None, limit=10)
   for r in res: print(r)

   # TODO: implement from V2
   # print()
   # print('GET ALL OPEN ORDERS FOR A SYMBOL\n' + '-'*30)
   # res = bitfinex.open_orders(order1['symbol'])
   # for r in res: print(r)
   # print()
   # print('GET ALL ORDERS FOR A SYMBOL (history)\n' + '-'*30)
   # res = bitfinex.all_orders(order1['symbol'], order1['orderId'])
   # for r in res: print(r)


   print()
   print('CANCEL ORDER\n' + '-'*30)
   print(bitfinex.cancel_order(order1['orderId'], order1['symbol']))
   print()
   print('CANCEL ALL\n' + '-'*30)
   print(bitfinex.cancel_all_orders())


   print()
   print('PLACE LIMIT ORDER\n' + '-'*30)
   order1 = bitfinex.place_limit_order('sell', 'btcusd', 0.01, 123000)
   print(order1)
   print()
   print('PLACE LIMIT ORDER\n' + '-'*30)
   order2 = bitfinex.place_limit_order('buy', 'ltcbtc', 0.1, 0.000002)
   print(order2)
   print()
   print('CANCEL MULTIPLE ORDERS\n' + '-'*30)
   print(bitfinex.cancel_multiple_orders([order1['orderId'], order2['orderId']]))




# testBinance()
# testBitfinex()

#testBinanceAuth()
testBitfinexAuth()


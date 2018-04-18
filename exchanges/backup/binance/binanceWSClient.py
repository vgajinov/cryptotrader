import websocket
import ssl
import json
import traceback
import logging
import threading
from pydispatch import dispatcher
from collections import OrderedDict, deque

from exchanges.exchangeWSClient import ExchangeWSClient
from exchanges.binance.binanceRESTClient import binanceRESTClient

# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d-%m %H:%M',
                    filename='./binance_websocket.log',
                    filemode='w')
logger = logging.getLogger('binance_websocket')


# All endpoints of /api and /wapi are under https://api.binance.com
# All endpoints return either a JSON object or array.
# Data is returned in ascending order. Oldest first, newest last.
# All time and timestamp related fields are in milliseconds.
#
# Error codes
# ----------------------
#
# HTTP 4XX return codes are used for for malformed requests; the issue is on the sender's side.
# HTTP 5XX return codes are used for internal errors; the issue is on Binance's side.
# HTTP 504 return code is used when the API successfully sent the message but not get a response within the timeout period. It is important to NOT treat this as a failure; the execution status is UNKNOWN and could have been a success.
# Any endpoint can retun an ERROR; the error payload is as follows:
# {
#   "code": -1121,
#   "msg": "Invalid symbol."
# }
# Specific error codes and messages defined in another document.
#
# Terminology
# ----------------------
# base asset      refers to the asset that is the quantity of a symbol.
# quoate asset    refers to the asset that is the price of a symbol.
#
#
# ENUM definitions
# ----------------------
#
# Symbol type:
#   SPOT
#
# Order status:
#   NEW
#   PARTIALLY_FILLED
#   FILLED
#   CANCELED
#   PENDING_CANCEL
#   REJECTED
#   EXPIRED
#
# Order types:
#   LIMIT
#   MARKET
#
# Order side:
#   BUY
#   SELL
#
# Time in force:
#   GTC
#   IOC
#
# Kline intervals:
#   1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
#
# Websocekts
# ----------------------
# The base endpoint is: wss://stream.binance.com:9443
# Streams can be access either in a single raw stream or a combined stream
# Raw streams are accessed at /ws/<streamName>
# Combined streams are accessed at /stream?streams=<streamName1>/<streamName2>/<streamName3>
# Combined stream events are wrapped as follows: {"stream":"<streamName>","data":<rawPayload>}
# All symbols for streams are lowercase
# A single connection to stream.binance.com is only valid for 24 hours; expect to be disconnected at the 24 hour mark.



# SSL connection
WEBSOCKET_URI = 'wss://stream.binance.com:9443/ws/'
REST_URI      = 'https://api.binance.com'

SYMBOLS = ["btcusd"]  # ,"ltcusd"] #,"ltcbtc","ethusd","ethbtc","bchbtc","bcheth"]


# ==========================================================================================
#   OrderBook
# ==========================================================================================

class binanceOrderBook:
   """
      [ PRICE, COUNT, AMOUNT ]
      when count > 0 then you have to add or update the price level
           if amount > 0 then add/update bids
           if amount < 0 then add/update asks
      when count = 0 then you have to delete the price level.
           if amount = 1 then remove from bids
           if amount = -1 then remove from asks
   """

   def __init__(self, name, bids, asks):
      self.name = name
      self.asks = {}
      self.bids = {}
      for bid in bids:
         price = float(bid[0])
         amount = float(bid[1])
         self.bids[price] = amount
      for ask in asks:
         price = float(ask[0])
         amount = float(ask[1])
         self.asks[price] = -amount
      self._publish()

   def updateBook(self, bids, asks):
      for bid in bids:
         price = float(bid[0])
         quantity = float(bid[1])
         if quantity == 0.0:
            if self.bids.get(price, None):
               self.bids.pop(price)
            elif self.asks.get(price, None):
               self.asks.pop(price)
         else:
            self.bids[price] = quantity
      for ask in asks:
         price = float(ask[0])
         quantity = float(ask[1])
         if quantity == 0.0:
            if self.bids.get(price, None):
               self.bids.pop(price)
            elif self.asks.get(price, None):
               self.asks.pop(price)
         else:
            self.asks[price] = -quantity
      self._publish()

   def _sortBook(self):
      bids = OrderedDict(reversed(sorted(self.bids.items(), key=lambda t: t[0])))
      asks = OrderedDict(reversed(sorted(self.asks.items(), key=lambda t: t[0])))
      return bids, asks

   def _publish(self):
      # send updated book to listeners
      bids, asks = self._sortBook()
      dispatcher.send(signal=self.name, sender='binance', bids=bids, asks=asks)

   @property
   def getBidsAsks(self):
      return self._sortBook()


# ==========================================================================================
#   Trades
# ==========================================================================================

class binanceTrades:
   # Updates are in the form of a list [ ID, MTS, AMOUNT, PRICE ]
   def __init__(self, name):
      self.name = name
      self.trades = deque(maxlen=60)

   def update(self, trade):
      self.trades.append([ trade['t'], trade['T'], trade['q'], trade['p'] ])
      self._publish()

   def _publish(self):
      # send updated data to listeners
      dispatcher.send(signal=self.name, sender='binance', trades=list(self.trades))

   @property
   def getTrades(self):
      return list(self.trades)


# ==========================================================================================
#   Candles
# ==========================================================================================

class binanceCandles:
   # Updates are in the form of a list [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
   # Direction of updates in the list is from the most recent to the least recent
   def __init__(self, name, candles):
      print(name)
      self.name = name
      self.candles = deque([candle[0:6] for candle in candles])
      self._publish()

   def update(self, candle):
      last = self.candles.pop()
      if candle[0] > last[0]:
         # add new candle
         self.candles.append(last)
         self.candles.append(candle)
         self._publish()
      elif candle[0] == last[0]:
         # update last candle
         self.candles.append(candle)
         self._publish()
      else:
         # bitfinex sometimes also send old candles. We just ignore it.
         self.candles.append(last)

   def _publish(self):
      # send updated book to listeners
      dispatcher.send(signal=self.name, sender='binance', candles=list(self.candles))

   @property
   def getCandles(self):
      return list(self.candles)


# ==========================================================================================
#   Client
# ==========================================================================================

class BinanceWSClient(ExchangeWSClient):
   name = 'Binance'
   # channel data
   book    = {}
   trades  = {}
   tickers = {}
   candles = {}
   subscriptions = {}  # stream -> thread
   threadData    = {}  # thread -> (updateHandler, dataHandler)
   connections   = {}  # thread -> websocket


   def __init__(self):
      self.channels = {
         'book'   : self.subscribeToBook,
         'trades' : self.subscribeToTrades,
         'ticker' : self.subscribeToTicker,
         'candles': self.subscribeToCandles
      }


   def _subscribe(self, stream, updateHandler, dataHandler):
      # start websocket listener thread
      thread = threading.Thread(target=self._connect, name=stream)  # , args=(stream)
      self.subscriptions[stream] = thread
      self.threadData[thread] = (updateHandler, dataHandler)
      thread.start()


   # Methods used by connection threads
   # ---------------------------------------------------------------------------------

   def _connect(self):
      logger.info('Connecting to websocket API ...')
      stream = threading.current_thread().getName()
      #websocket.enableTrace(True)
      self.ws = websocket.WebSocketApp(WEBSOCKET_URI + stream,
                                       on_message=self.on_message,
                                       on_error=self.on_error,
                                       on_close=self.on_close)
      self.ws.on_open = self.on_open
      self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  # TODO see if you can solve this using ssl


   def on_open(self, ws):
      self.connections[threading.current_thread()] = ws
      logger.info('Websocket connection open.')

   def on_close(self, ws):
      logger.info('Websocket connection closed.')

   def on_error(self, ws, error):
      try:
         err = json.loads(error)
         print('Error {} : {}'.format(err['code'], err['msg']))
      except:
         print(error)

   def on_message(self, ws, message):
      # Websocket client returns message as string. Convert it to json
      msg = json.loads(message)
      try:
         currThread = threading.current_thread()
         updateHandler, dataHandler = self.threadData[currThread]
         updateHandler(dataHandler, msg)
      except Exception as inst:
         print(type(inst))      # the exception instance
         print(inst)             # __str__ allows args to be printed directly
         print(traceback.format_exc())


   # Public methods
   # ---------------------------------------------------------------------------------

   def connect(self):
      pass

   def disconnect(self):
      for stream, thread in list(self.subscriptions.items()):
         self.unsubscribe(stream)
         thread.join()

   def subscribe(self, channel, parameters={}):
      subscribeHandler = self.channels[channel]
      return subscribeHandler(parameters)

   def unsubscribe(self, stream):
      thread = self.subscriptions.pop(stream)  # remove subscription
      self.threadData.pop(thread)              # remove the thread data
      socket = self.connections.pop(thread)    # remove connection
      socket.close()
      # to avoid blocking the parent thread does not call join here




   # ===============================================================================
   # Channels
   # ===============================================================================

   # Order Book
   # ---------------------------------------------------------------------------------

      """
      // request
       wss://stream.binance.com:9443/ws/[symbol in lower case]@depth   
       (e.g. wss://stream.binance.com:9443/ws/ethbtc@depth)

      // response
      {
         "e": "depthUpdate",        // event type
         "E": 1499404630606,        // event time
         "s": "ETHBTC",             // symbol
         "U": 157,                  // First update ID in event
         "u": 160,                  // Final update ID in event
         "b": [                     // bids
            [
               "0.10376590",        // price (need to update the quantity on this price)
               "59.15767010",       // quantity
               []                   // can be ignored
            ],
         ],
         "a": [                     // asks
            [
               "0.10376586",        // price (need to upate the quantity on this price)
               "159.15767010",      // quantity
               []                   // can be ignored
            ],
            [
               "0.10490700",
               "0.00000000",        //quantitiy=0 means remove this level
               []
            ]
         ]
      }
      
      How to manage a local order book correctly :
      
      Open a stream to wss://stream.binance.com:9443/ws/bnbbtc@depth
      Buffer the events you receive from the stream
      Get a depth snapshot from **https://www.binance.com/api/v1/depth?symbol=BNBBTC&limit=1000"
      Drop any event where u is <= lastUpdateId in the snapshot
      The first processed should have U <= lastUpdateId+1 AND u >= lastUpdateId+1
      While listening to the stream, each new event's U should be equal to the previous event's u+1
      The data in each event is the absolute quantity for a price level
      If the quantity is 0, remove the price level
      Receiving an event that removes a price level that is not in your local order book can happen and is normal.
      limit : default 100; max 1000. Valid limits:[5, 10, 20, 50, 100, 500, 1000]
      """

   def subscribeToBook(self, params={}):
      pair = params.get('pair', "ETHBTC")
      pair = pair.lower()
      stream = pair + '@depth'
      if self.subscriptions.get(stream, None):
         return

      logger.info('Subscribing to order book for {} ...'.format(pair.upper()))

      # Get a depth snapshot using the rest api
      # TODO check for errors from rest api
      #initBookData = BinanceRestAPI().orderBook(pair)
      initBookData = binanceRESTClient(None, None).get_order_book(symbol=pair.upper())
      book = binanceOrderBook('book_' + pair, initBookData['bids'], initBookData['asks'])
      self.book[pair] = book

      # subscribe to book. Arguments are update handler and order book object
      self._subscribe(stream, self.BookUpdate, book)
      return stream


   def BookUpdate(self, book, msg):
      asks = msg['a']
      bids = msg['b']
      book.updateBook(bids, asks)


   def getOrderBook(self, pair):
      return self.book.get(pair, None)


   # Trades
   # ---------------------------------------------------------------------------------

      """
      // request
      wss://stream.binance.com:9443/ws/[symbol in lower case]@trade 
      (e.g. wss://stream.binance.com:9443/ws/ethbtc@aggTrade)

      // response
      {
        "e": "trade",     // Event type
        "E": 123456789,   // Event time
        "s": "BNBBTC",    // Symbol
        "t": 12345,       // Trade ID
        "p": "0.001",     // Price
        "q": "8.156",     // Quantity
        "b": 88,          // Buyer order Id
        "a": 50,          // Seller order Id
        "T": 123456785,   // Trade time
        "m": true,        // Is the buyer the market maker?
        "M": true         // Ignore.
      }
      """

   def subscribeToTrades(self, params={}):
      pair = params.get('pair', "BTCUSD")
      pair = pair.lower()
      stream = pair + '@trade'
      if self.subscriptions.get(stream, None):
         return

      logger.info('Subscribing to trades for {} ...'.format(pair.upper()))

      trades = binanceTrades('trades_' + pair)
      self.trades[pair] = trades

      # subscribe to trade updates. Arguments are update handler and trades object
      self._subscribe(stream, self.TradesUpdate, trades)
      return stream


   def TradesUpdate(self, trades, msg):
      trades.update(msg)

   def getTrades(self, pair):
      return self.trades.get(pair, None)



   # Candles
   # ---------------------------------------------------------------------------------

      """
      // request
      wss://stream.binance.com:9443/ws/[symbol in lower case]@kline_[interval] 
      (e.g. wss://stream.binance.com:9443/ws/ethbtc@kline_1m)

      // response
      {
         "e": "kline",                    // event type
         "E": 1499404907056,              // event time
         "s": "ETHBTC",                   // symbol
         "k": {
               "t": 1499404860000,        // start time of this bar
               "T": 1499404919999,        // end time of this bar
               "s": "ETHBTC",             // symbol
               "i": "1m",                 // interval
               "f": 77462,                // first trade id
               "L": 77465,                // last trade id
               "o": "0.10278577",         // open
               "c": "0.10278645",         // close
               "h": "0.10278712",         // high
               "l": "0.10278518",         // low
               "v": "17.47929838",        // volume
               "n": 4,                    // number of trades
               "x": false,                // whether this bar is final
               "q": "1.79662878",         // quote volume
               "V": "2.34879839",         // taker buy base asset volume
               "Q": "0.24142166",         // taker buy quote asset volume
               "B": "13279784.01349473"   // can be ignored
              }
      }
      """

   def subscribeToCandles(self, params={}):
      pair = params.get('pair', "BTCUSD")
      pair = pair.lower()
      timeframe = params.get('scale', '1m')
      valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h',
                          '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
      if timeframe not in valid_timeframes:
         raise ValueError("timeframe must be any of %s" % valid_timeframes)

      stream = pair + '@kline_' + timeframe
      if self.subscriptions.get(stream, None):
         return

      logger.info('Subscribing to candles for {} - {} ...'.format(pair.upper(), timeframe))

      # Get candle snapshot using the rest api
      # TODO rest API will return None in case of error. How should we handle this
      initCandleData = binanceRESTClient(None, None).get_klines(symbol=pair.upper(), interval=timeframe)
      candles = binanceCandles('candles_' + pair, initCandleData)
      self.candles[pair] = candles

      # subscribe to candle updates. Arguments are update handler and candle storage object
      self._subscribe(stream, self.CandlesUpdate, candles)
      return stream


   def CandlesUpdate(self, candles, msg):
      candles.update([ msg['k']['t'], msg['k']['o'], msg['k']['h'], msg['k']['l'], msg['k']['c'], msg['k']['v'] ])

   def getCandles(self, pair):
      return self.candles.get(pair, None)



   # Ticker
   # ---------------------------------------------------------------------------------

      """
      Single Ticker:

      Stream Name: <symbol>@ticker

      // request
      wss://stream.binance.com:9443/ws/[symbol in lower case]@ticker 
      (e.g. wss://stream.binance.com:9443/ws/ethbtc@kline_1m)

      Payload:
      
      {
        "e": "24hrTicker",  // Event type
        "E": 123456789,     // Event time
        "s": "BNBBTC",      // Symbol
        "p": "0.0015",      // Price change
        "P": "250.00",      // Price change percent
        "w": "0.0018",      // Weighted average price
        "x": "0.0009",      // Previous day's close price
        "c": "0.0025",      // Current day's close price
        "Q": "10",          // Close trade's quantity
        "b": "0.0024",      // Best bid price
        "B": "10",          // Bid bid quantity
        "a": "0.0026",      // Best ask price
        "A": "100",         // Best ask quantity
        "o": "0.0010",      // Open price
        "h": "0.0025",      // High price
        "l": "0.0010",      // Low price
        "v": "10000",       // Total traded base asset volume
        "q": "18",          // Total traded quote asset volume
        "O": 0,             // Statistics open time
        "C": 86400000,      // Statistics close time
        "F": 0,             // First trade ID
        "L": 18150,         // Last trade Id
        "n": 18151          // Total number of trades
      }
      
      All Market Tickers Stream:
      
      24hr Ticker statistics for all symbols in an array pushed every second

      Stream Name: !ticker@arr

      Payload:
      
      [
        {
          // Same as for single ticker
        }
      ]
      
      Generally, ticker should return 
         [BID, BID_SIZE, ASK, ASK_SIZE, DAILY_CHANGE, DAILY_CHANGE_PERC, LAST_PRICE, VOLUME, HIGH, LOW]
      """

   def subscribeToTicker(self, params={}):
      pair = params.get('pair', "BTCUSD")
      pair = pair.lower()
      if pair == 'all':
         stream = '!ticker@arr'
         if not self.subscriptions.get(stream, None):
            # subscribe to trade updates. Arguments are update handler and trades object
            logger.info('Subscribing to all pairs tickers')
            self._subscribe(stream, self.AllTickersUpdate, 'ticker_all')
      else:
         stream = pair + '@ticker'
         if not self.subscriptions.get(stream, None):
            # subscribe to trade updates. Arguments are update handler and trades object
            logger.info('Subscribing to ticker for {} ...'.format(pair.upper()))
            self._subscribe(stream, self.TickerUpdate, 'ticker_' + pair)

      return stream


   def TickerUpdate(self, name, msg):
      ticker = [msg[key] for key in ['b', 'B', 'a', 'A', 'p', 'P', 'c', 'v', 'h', 'l']]
      dispatcher.send(signal=name, sender='binance', ticker=ticker)


   def AllTickersUpdate(self, name, msg):
      ticker = []
      for tck in msg:
         ticker.append([tck[key] for key in ['s', 'b', 'B', 'a', 'A', 'p', 'P', 'c', 'v', 'h', 'l']])
      dispatcher.send(signal=name, sender='binance', tickers=ticker)
import websocket
import ssl
import json
import traceback
import threading
from pydispatch import dispatcher
from collections import OrderedDict, deque

from exchanges.WS.api import *
from exchanges.REST.binance import BinanceRESTClient



# ==========================================================================================
#   Ticker
# ==========================================================================================

class BinanceTicker(ChannelData):
   def __init__(self, name):
      super(BinanceTicker, self).__init__()
      self.name = name
      self.data = []

   def update(self, data):
      self.data = [float(data[key]) for key in ['b', 'B', 'a', 'A', 'p', 'P', 'c', 'v', 'h', 'l']]
      self._publish()

   def _publish(self):
      dispatcher.send(signal=self.name, sender='binance', data=self.data)


# ==========================================================================================
#   All Tickers
# ==========================================================================================

class BinanceAllTickers(ChannelData):
   def __init__(self, name):
      super(BinanceAllTickers, self).__init__()
      self.name = name
      self.data = []

   def update(self, data):
      self.data = []
      for tck in data:
         self.data.append([tck['s']] + [float(tck[key]) for key in ['b', 'B', 'a', 'A', 'p', 'P', 'c', 'v', 'h', 'l']])
      self._publish()

   def _publish(self):
      dispatcher.send(signal=self.name, sender='binance', data=self.data)

# ==========================================================================================
#   OrderBook
# ==========================================================================================

class BinanceOrderBook(ChannelData):
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
      super(BinanceOrderBook, self).__init__()
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

   def update(self, bids, asks):
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
      bids = OrderedDict(sorted(self.bids.items(), key=lambda t: t[0]))
      asks = OrderedDict(sorted(self.asks.items(), key=lambda t: t[0]))
      return bids, asks

   def _publish(self):
      # send updated book to listeners
      bids, asks = self._sortBook()
      dispatcher.send(signal=self.name, sender='binance', data={'bids':bids, 'asks':asks})



# ==========================================================================================
#   Trades
# ==========================================================================================

class BinanceTrades(ChannelData):
   def __init__(self, name, trades):
      super(BinanceTrades, self).__init__()
      self.name = name
      self.trades = deque(maxlen=TRADE_QUEUE_SIZE)
      trades = trades[-TRADE_QUEUE_SIZE:]
      for trade in trades:
         if trade[-1] == 'sell':
            amount = -float(trade[2])
         else:
            amount = float(trade[2])
         self.trades.append([int(trade[0]), amount, float(trade[1])])
      self._publish()

   def update(self, trade):
      if trade['m']:
         amount = -float(trade['q'])  # sell
      else:
         amount = float(trade['q'])   # buy
      self.trades.append([ int(trade['T']), amount, float(trade['p']) ])
      self._publish()

   def _publish(self):
      # send updated data to listeners
      dispatcher.send(signal=self.name, sender='binance', data=list(self.trades))



# ==========================================================================================
#   Candles
# ==========================================================================================

class BinanceCandles(ChannelData):
   # Updates are in the form of a list [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
   # Direction of updates in the list is from the most recent to the least recent
   def __init__(self, name, candles):
      super(BinanceCandles, self).__init__()
      self.name = name
      self.candles = deque([ [int(candle[0])] + [float(c) for c in candle[1:6]] for candle in candles ])
      self._publish()

   def update(self, candle):
      last = self.candles.pop()
      candle = [int(candle[0])] + [float(c) for c in candle[1:]]
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
         self.candles.append(last)

   def _publish(self):
      # send updated book to listeners
      dispatcher.send(signal=self.name, sender='binance', data=list(self.candles))



# ==========================================================================================
#   Client
# ==========================================================================================

WEBSOCKET_URI = 'wss://stream.binance.com:9443/ws/'
REST_URI      = 'https://api.binance.com'


class BinanceWSClient(WSClientAPI):
   def __init__(self, key_file=None):
      super(BinanceWSClient, self).__init__()
      self._data = {}           # stream -> data
      self._subscriptions = {}  # stream -> thread
      self._connections = {}    # thread -> websocket

      # authenticated streams
      self.authenticated = False
      self._listenKey = None
      self._key = None
      self._secret = None
      self._keyFile = None
      self._orders = []
      self._trades = []
      self._balances = {}

   @staticmethod
   def name():
      return 'Binance'

   def _connect(self):
      stream = threading.current_thread().getName()
      self.logger.info('Connecting to websocket for stream %s' % stream)
      # websocket.enableTrace(True)
      self.ws = websocket.WebSocketApp(WEBSOCKET_URI + stream,
                                       on_message=self._on_message,
                                       on_error=self._on_error,
                                       on_close=self._on_close)
      self.ws.on_open = self._on_open
      self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  # TODO see if you can solve this using ssl
      self.logger.info('Thread exit for {}'.format(stream))

   def _reconnect(self):
      self._connect()

   def _subscribe(self, stream):
      # start websocket listener thread
      self.logger.info('Starting a new thread for {}'.format(stream))
      thread = threading.Thread(target=self._connect, name=stream)  # , args=(stream)
      thread.deamon = True
      self._subscriptions[stream] = thread
      thread.start()

   def _log_active_threads(self):
      threads = [thr.getName() for thr in threading.enumerate()]
      self.logger.info(('ACTIVE THREADS: {}'.format(','.join(threads))))

   # Websocket handlers
   # ---------------------------------------------------------------------------------

   def _on_open(self, ws):
      stream = threading.current_thread().getName()
      self._connections[threading.current_thread()] = ws
      self.logger.info('Websocket connection open for {}'.format(stream))

   def _on_close(self, ws):
      stream = threading.current_thread().getName()
      self.logger.info('Websocket connection closed for {}'.format(stream))

   def _on_error(self, ws, error):
      self.logger.info('Websocket error:')
      try:
         err = json.loads(error)
         self.logger.info('Error {} : {}'.format(err['code'], err['msg']))
         dispatcher.send(signal='info', sender='binance', data={'error': err['msg]']})
      except:
         self.logger.info(error)
         dispatcher.send(signal='info', sender='binance', data={'error': error})


   def _on_message(self, ws, message):
      # Websocket client returns message as string. Convert it to json
      msg = json.loads(message)
      try:
         self._channel_update(msg)
      except Exception as inst:
         self.logger.info(type(inst))              # the exception instance
         self.logger.info(inst)                    # __str__ allows args to be printed directly
         self.logger.info(traceback.format_exc())


   def _channel_update(self, msg):
      stream = threading.current_thread().getName()
      # TICKER
      if 'ticker' in stream:
         self._data[stream].update(msg)
      # ORDER BOOK
      elif 'depth' in stream:
         self._data[stream].update(bids=msg['b'], asks=msg['a'])
      # TRADES
      elif 'trade' in stream:
         self._data[stream].update(msg)
      # CANDLES
      elif 'kline' in stream:
         self._data[stream].update([msg['k']['t'], msg['k']['o'], msg['k']['h'],
                                    msg['k']['l'], msg['k']['c'], msg['k']['v']])
      # AUTHENTICATED
      elif self._listenKey == stream:
         self._handle_auth_update(msg)
      else:
         self.logger.info('Update not handled for stream {}'.format(stream))
         self.logger.info('Message:\n{}'.format(msg))


   # Public interface methods
   # ---------------------------------------------------------------------------------

   def connect(self, info_handler=None):
      # register a handler for recieving info and error messages from websocket thread
      self._info_handler = info_handler
      dispatcher.connect(info_handler, signal='info', sender='binance')

   def disconnect(self):
      self.logger.info('Disconnecting ...')
      for stream, thread in self._subscriptions.items():
         try:
            self._connections[thread].close()
            self.logger.info('Unsubscribed from %s' % stream)
            thread.join()
         except KeyError:
            self.logger.info('No subscription for stream %s' % stream)

      self._data.clear()
      self._connections.clear()
      self._subscriptions.clear()

      if self._info_handler is not None:
         dispatcher.disconnect(self._info_handler, signal='info', sender='binance')
      for d in dispatcher.getAllReceivers(sender='binance'):
         d.disconnect()

      self._stop_logger()


   def subscribe(self, channel, **kwargs):
      if channel == 'ticker':
         return self.subscribe_ticker(**kwargs)
      elif channel == 'book':
         return self.subscribe_book(**kwargs)
      elif channel == 'trades':
         return self.subscribe_trades(**kwargs)
      elif channel == 'candles':
         return self.subscribe_candles(**kwargs)
      else:
         return None

   def unsubscribe(self, stream, update_handler=None):
      if update_handler is not None:
         try:
            self.logger.info('Removing listener for %s ...' % stream)
            dispatcher.disconnect(update_handler, signal=stream, sender='binance')
         except dispatcher.errors.DispatcherKeyError as e:
            self.logger.info(e)

      # unsubscribe if no one is listening
      if dispatcher.getReceivers(sender='binance', signal=stream) == []:
         self.logger.info('Unsubscribing from %s ...' % stream)
         try:
            self._data.pop(stream)                    # remove data object
            thread = self._subscriptions.pop(stream)  # remove subscription
            socket = self._connections.pop(thread)    # remove connection
            socket.close()                            # this will terminate the thread
            self.logger.info('Unsubscribed from %s' % stream)
            # parent thread does not call join here to avoid blocking
         except KeyError:
            self.logger.info('No subscription for stream %s' % stream)


   # Channels
   # ---------------------------------------------------------------------------------

   def _publish_channel_data(self, stream):
      try:
         chanId = self._data[stream]
         self._data[chanId].publish()
      except KeyError:
         pass


   def subscribe_ticker(self, symbol, update_handler=None):
      stream = symbol.lower() + '@ticker'

      if update_handler is not None:
         dispatcher.connect(update_handler, signal=stream, sender='binance')

      if self._subscriptions.get(stream, None) is None:
         self.logger.info('Subscribing to ticker for {} ...'.format(symbol.upper()))
         self._data[stream] = BinanceTicker(stream)
         self._subscribe(stream)
      else:
         self.logger.info('Already subscribed to %s candles' % symbol.lower())
         self._publish_channel_data(stream)

      return stream


   def subscribe_all_tickers(self, update_handler=None):
      stream = '!ticker@arr'

      if update_handler is not None:
         dispatcher.connect(update_handler, signal=stream, sender='binance')

      if self._subscriptions.get(stream, None) is None:
         self.logger.info('Subscribing to all pairs tickers')
         self._data[stream] = BinanceAllTickers(stream)
         self._subscribe(stream)
      else:
         self.logger.info('Already subscribed to all tickers')
         self._publish_channel_data(stream)

      return stream


   def subscribe_order_book(self, symbol, update_handler=None, **kwargs):
      symbol = symbol.lower()
      stream = symbol + '@depth'

      if update_handler is not None:
         dispatcher.connect(update_handler, signal=stream, sender='binance')

      if self._subscriptions.get(stream, None) is None:
         self.logger.info('Subscribing to order book for {} ...'.format(symbol))
         # Get a depth snapshot using the rest api
         initBookData = BinanceRESTClient().order_book(symbol)
         if initBookData is None:
            initBookData = {'bids':[], 'asks':[]}
         self._data[stream] = BinanceOrderBook(stream, initBookData['bids'], initBookData['asks'])
         self._subscribe(stream)
      else:
         self.logger.info('Already subscribed to %s book' % symbol)
         self._publish_channel_data(stream)

      return stream


   def subscribe_trades(self, symbol, update_handler=None):
      symbol = symbol.lower()
      stream = symbol + '@trade'

      if update_handler is not None:
         dispatcher.connect(update_handler, signal=stream, sender='binance')

      if self._subscriptions.get(stream, None) is None:
         self.logger.info('Subscribing to trades for {} ...'.format(symbol))

         initTradeData = BinanceRESTClient().trades(symbol.lower())
         if initTradeData is None:
            initTradeData = []

         self._data[stream] = BinanceTrades(stream, initTradeData)
         self._subscribe(stream)
      else:
         self.logger.info('Already subscribed to %s trades' % symbol)
         self._publish_channel_data(stream)

      return stream


   def subscribe_candles(self, symbol, interval='1m', update_handler=None):
      valid_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h',
                         '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
      if interval not in valid_intervals:
         raise ValueError("interval must be any of %s" % valid_intervals)

      stream = symbol.lower() + '@kline_' + interval

      if update_handler is not None:
         dispatcher.connect(update_handler, signal=stream, sender='binance')

      if self._subscriptions.get(stream, None) is None:
         self.logger.info('Subscribing to candles for {} - {} ...'.format(symbol.upper(), interval))
         # Get candle snapshot using the rest api
         initCandleData = BinanceRESTClient().candles(symbol.lower(), interval=interval)
         if initCandleData is None:
            initCandleData = []
         self._data[stream] = BinanceCandles(stream, initCandleData)
         self._subscribe(stream)
      else:
         self.logger.info('Already subscribed to %s candles' % symbol)
         self._publish_channel_data(stream)

      return stream


   # Authenticated Channels
   # ---------------------------------------------------------------------------------

   def authenticate(self, key=None, secret=None, keyFile=None):
      self._key = key
      self._secret = secret
      self._keyFile = keyFile

      self.logger.info('Authenticating ...')
      restClient = BinanceRESTClient(key=key, secret=secret, key_file=keyFile)
      ret = restClient.create_listen_key()
      try:
         self._listenKey = ret['listenKey']
         self.logger.info('Authentication successful')
      except:
         self.logger.info('Authentication failed')
         return False

      # get a snapshot of open orders
      openOrders = restClient.open_orders()
      if openOrders is not None:
         for order in openOrders:
            orderId = int(order['orderId'])
            timestamp = int(order['timestamp'])
            symbol = order['symbol']
            orderType = order['type']
            side = order['side']
            price = float(order['price'])
            amount = float(order['amount'])
            filled = float(order['filled'])
            total = price * amount
            percFilled = '{:.2f}'.format(100 * filled / amount)

            self._orders.append([orderId, timestamp, symbol, orderType, side, price, amount, percFilled, total])

      # get a snapshot of balances
      self._balances = restClient.balance()
      if self._balances is None:
         self._balances = {}

      self._subscribe(self._listenKey)

      self.authenticated = True
      return True


   def subscribe_user_orders(self, update_handler):
      self.logger.info('Subscribing to orders channel')
      dispatcher.connect(update_handler, signal='orders', sender='binance')
      if self._orders:
         dispatcher.send(signal='orders', sender='binance', data=list(reversed(self._orders)))
      return 'orders'

   def subscribe_user_trades(self, update_handler):
      self.logger.info('Subscribing to user trades channel')
      dispatcher.connect(update_handler, signal='user_trades', sender='binance')
      return 'user_trades'

   def subscribe_balances(self, update_handler):
      self.logger.info('Subscribing to balances channel')
      dispatcher.connect(update_handler, signal='balances', sender='binance')
      if self._balances:
         dispatcher.send(signal='balances', sender='binance', data=self._balances)
      return 'balances'


   def _handle_auth_update(self, msg):
      if msg['e'] == 'outboundAccountInfo':
         self._handle_balance_update(msg)
      elif msg['e'] == 'executionReport':
         if msg['x'] == 'REJECTED':
            dispatcher.send(signal='info', sender='binance', data=msg['r'])
         else:
            self._handle_order_update(msg)
      else:
         self.logger.info('Unknown user stream event: {}'.format(msg['event']))


   def _handle_order_update(self, msg):
      orderId    = int(msg['i'])
      timestamp  = int(msg['T'])
      symbol     = msg['s']
      orderType  = msg['o'].lower()
      side       = msg['S']
      price      = float(msg['p'])
      amount     = float(msg['q'])
      filled     = float(msg['z'])
      total      = price * amount
      percFilled = '{:.2f}'.format(100 * filled / amount)
      status     = msg['x'].lower()
      if status == 'trade':
         status = 'executed'
      isActive   = msg['x'] == 'NEW'


      orderUpdate = [orderId, timestamp, symbol, orderType, side, price, amount, percFilled, total]
      tradeUpdate = [timestamp, symbol, orderType, side, price, amount, filled, total, status]

      if isActive:
         # is it an update of existing order
         isNewOrder = True
         for i, order in enumerate(self._orders):
            if order[0] == orderId:
               isNewOrder = False
               self._orders[i] = orderUpdate
               break
         if isNewOrder:
            self._orders.append(orderUpdate)
         dispatcher.send(signal='orders', sender='binance', data=list(reversed(self._orders)))
      else:
         # delete from orders
         for i, order in enumerate(self._orders):
            if order[0] == orderId:
               del self._orders[i]
               dispatcher.send(signal='orders', sender='binance', data=list(reversed(self._orders)))
         # add to trades
         self._trades.append(tradeUpdate)
         dispatcher.send(signal='user_trades', sender='binance', data=list(reversed(self._trades)))


   def _handle_balance_update(self, msg):
      for wallet in msg['B']:
         self._balances[wallet['a']] = wallet['f']
      dispatcher.send(signal='balances', sender='binance', data=self._balances)






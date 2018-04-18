import websocket
import json
import time
import traceback
from threading import Thread
from pydispatch import dispatcher
from collections import OrderedDict, deque
from abc import ABC, abstractmethod

from exchanges.WS.api import *



# ==========================================================================================
#   Ticker
# ==========================================================================================

class BitfinexTicker(ChannelData):
   def __init__(self, name, ticker):
      super(BitfinexTicker, self).__init__()
      self.name = name
      self.data = [float(x) for x in ticker]
      self._publish()

   def update(self, ticker):
      self.data = [float(x) for x in ticker]
      self._publish()

   def _publish(self):
      dispatcher.send(signal=self.name, sender='bitfinex', data=self.data)

# ==========================================================================================
#   OrderBook
# ==========================================================================================

class BitfinexOrderBook:
   """
      [ PRICE, COUNT, AMOUNT ]
      when count > 0 then you have to add or update the price level
           if amount > 0 then add/update bids
           if amount < 0 then add/update asks
      when count = 0 then you have to delete the price level.
           if amount = 1 then remove from bids
           if amount = -1 then remove from asks
   """
   def __init__(self, name, orders):
      self.name = name
      self.asks = {}
      self.bids = {}
      for order in orders:
         price  = float(order[0])
         amount = float(order[2])
         if amount > 0:
            self.bids[price] = amount
         else:
            self.asks[price] = amount
      self._publish()


   def update(self, update):
      price  = float(update[0])
      count  = int(update[1])
      amount = float(update[2])
      if count > 0:
         if amount > 0:
            self.bids[price] = amount
         else:
            self.asks[price] = amount
      else:
         if amount == 1:
            if self.bids.get(price, None):
               self.bids.pop(price)
         elif amount == -1:
            if self.asks.get(price, None):
               self.asks.pop(price)
      self._publish()

   def _sortBook(self):
      bids = OrderedDict( sorted(self.bids.items(), key=lambda t: t[0]) )
      asks = OrderedDict( sorted(self.asks.items(), key=lambda t: t[0]) )
      return bids, asks

   def _publish(self):
      # send updated book to listeners
      bids, asks = self._sortBook()
      dispatcher.send(signal=self.name, sender='bitfinex', data={'bids':bids, 'asks':asks})


# ==========================================================================================
#   Trades
# ==========================================================================================

class BitfinexTrades:
   # Updates are in the form of a list [ ID, MTS, AMOUNT, PRICE ]
   def __init__(self, name, trades):
      self.name = name
      self.trades = deque(maxlen=60)
      for trade in trades:
         self.trades.append(trade[1:])
      self._publish()

   def update(self, trade):
      self.trades.append(trade[1:])
      self._publish()

   def _publish(self):
      # send updated book to listeners
      dispatcher.send(signal=self.name, sender='bitfinex', data=list(self.trades))



# ==========================================================================================
#   Candles
# ==========================================================================================

class BitfinexCandles:
   # Updates are in the form of a list [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
   # Direction of updates in the list is from the most recent to the least recent
   def __init__(self, name, candles):
      self.name = name
      for i in range(len(candles)):
         # TODO: improve this swapping, i.e. use numpy
         close = candles[i][2]
         candles[i][2] = candles[i][3]
         candles[i][3] = candles[i][4]
         candles[i][4] = close
      self.candles = deque(list(reversed(candles)))
      self._publish()

   def update(self, candle):
      close = candle[2]
      candle[2] = candle[3]
      candle[3] = candle[4]
      candle[4] = close
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
      dispatcher.send(signal=self.name, sender='bitfinex', data=list(self.candles))



# ==========================================================================================
#   Client
# ==========================================================================================

class BitfinexWSClient(WSClientAPI):
   def __init__(self):
      super(BitfinexWSClient, self).__init__()
      self._thread = None
      self._ws = None
      self._connected = False
      self._subscriptions  = {}   # subsriptions : channelId -> channelName
      self._data = {}             # channelId -> channel data

   @staticmethod
   def name():
      return 'Bitfinex'

   def _get_channel_ID(self, chanName):
      chanId = None
      for key, value in self._subscriptions.items():
         if value == chanName:
            chanId = key
      return chanId


   def _connect(self):
      self.logger.info ('Connecting to bitfinex websocket API ...')
      #websocket.enableTrace(True)
      self._ws = websocket.WebSocketApp('wss://api.bitfinex.com/ws/2',
                                        on_message=self._on_message,
                                        on_error=self._on_error,
                                        on_close=self._on_close)
      self._ws.on_open = self._on_open
      self._ws.run_forever()

   def _reconnect(self):
      self._connect()
      self._resubscribe_all()

   def _unsubscribe_all(self):
      for chanId in self._subscriptions.keys():
         self.logger.info('Unsubscribing from %s ...' % self._subscriptions[chanId])
         self._ws.send(json.dumps({"event": "unsubscribe", "chanId": chanId}))

   def _resubscribe_all(self):
      subscriptions = self._subscriptions.keys()
      self._subscriptions.clear()
      for chan in subscriptions:
         ch = chan.split('_')
         if len(ch) == 3:
            self.subscribe(ch[0], symbol=ch[1], interval=ch[2])
         else:
            self.subscribe(ch[0], symbol=ch[1])


   # Websocket handlers
   # ---------------------------------------------------------------------------------

   def _on_open(self, ws):
      self._connected = True
      self.logger.info('Bitfinex websocket connection open.')

   def _on_close(self, ws):
      self.logger.info('Bitfinex websocket connection closed.')

   def _on_error(self, ws, error):
      self.logger.info('Bitfinex websocket error:')
      self.logger.info(error)
      dispatcher.send(signal='info', sender='bitfinex', data={ 'error' : error})

   def _on_message(self, ws, message):
      # Websocket client returns message as string. Convert it to json
      msg = json.loads(message)

      try:
         # EVENT MESSAGE
         if type(msg) is dict:
            event = msg['event']
            if event == 'hb':
               pass
            elif event == 'pong':
               self.logger.info('Pong received.')
            elif event == 'error':
               dispatcher.send(signal='info', sender='bitfinex', data={'error' : msg['msg']})
               self.logger.info('Error ' + str(msg['code']) + ' : ' + str(msg['msg']))
            elif event == 'info':
               if 'version' in msg.keys():
                  self.logger.info('WS API version ' + str(msg['version']))
               elif 'code' in msg.keys():
                  self.logger.info('Received code' + str(msg['code']) + ' : ' + msg['msg'])
                  if   msg['code'] == 20051 :
                     dispatcher.send(signal='info', sender='bitfinex', data={'info' : 'reconnect'})
                     self._reconnect()
                  elif msg['code'] == 20060 :
                     dispatcher.send(signal='info', sender='bitfinex', data={'info' : 'pause'})
                     self._unsubscribe_all()
                  elif msg['code'] == 20061 :
                     dispatcher.send(signal='info', sender='bitfinex', data={'info' : 'unpause'})
                     self._resubscribe_all()
            elif event == 'subscribed':
               self._channel_subscribed(msg)
            elif event == 'unsubscribed':
               self._data.pop(msg['chanId'])                       # remove data object
               chanName = self._subscriptions.pop(msg['chanId'])   # remove subscription
               self.logger.info('Unsubscribed from channel %s' % chanName)
            else:
               self.logger.info('Unhandled WS event!')

         # CHANNEL UPDATE
         else:
            self._update_channel(msg)

      except Exception as inst:
         self.logger.info(type(inst))              # the exception instance
         self.logger.info(inst)                    # __str__ allows args to be printed directly
         self.logger.info(traceback.format_exc())


   def _channel_subscribed(self, msg):
      channel = msg['channel']
      if channel == 'ticker':
         symbol = msg['pair']
         self._subscriptions[msg['chanId']] = 'ticker_' + symbol
         self.logger.info('New subscription to ticker for %s' % symbol)
      elif channel == 'book':
         symbol = msg['symbol'][1:]
         prec = msg['prec']
         freq = msg['freq']
         self._subscriptions[msg['chanId']] = 'book_' + symbol + '_' + prec + '_' + freq
         self.logger.info('New subscription to order book channel for %s' % symbol)
      elif channel == 'trades':
         symbol = msg['symbol'][1:]
         self._subscriptions[msg['chanId']] = 'trades_' + symbol
         self.logger.info('New subscription to trades channel for %s' % symbol)
      elif channel == 'candles':
         symbol = msg['key'].split(':')[-1][1:].upper()
         interval = msg['key'].split(':')[1]
         self._subscriptions[msg['chanId']] = 'candles_' + symbol + '_' + interval
         self.logger.info('New subscription to candles channel for %s' % symbol)
      else:
         self.logger.info('No channel handler for channel - ' + channel)
         dispatcher.send(signal='info', sender='bitfinex', data={ 'error' : 'No channel handler for channel - ' + channel})


   def _update_channel(self, msg):
      if 'hb' in msg:
         return

      chanId = msg[0]
      chanName = self._subscriptions[chanId]
      data = msg[1]
      if self._data.get(chanId, None) is None:
         # snapshot message
         if chanName.startswith('ticker'):
            #dispatcher.send(signal=chanName, sender='bitfinex', data=[float(x) for x in msg[1]])
            self._data[chanId] = BitfinexTicker(chanName, data)
         elif chanName.startswith('book'):
            self._data[chanId] = BitfinexOrderBook(chanName, data)
         elif chanName.startswith('trades'):
            self._data[chanId] = BitfinexTrades(chanName, data)
         elif chanName.startswith('candles'):
            self._data[chanId] = BitfinexCandles(chanName, data)
      else:
         # update
         if chanName.startswith('trades'):
            self._data[chanId].update(msg[2])
         else:
            self._data[chanId].update(data)


   # Public interface methods
   # ---------------------------------------------------------------------------------

   def connect(self, info_handler=None):
      def run():
         self._connect()

      # start websocket listener thread
      self._thread = Thread(target=run)
      self._thread.start()

      # register a handler for recieving info and error messages from websocket thread
      self._info_handler = info_handler
      dispatcher.connect(info_handler, signal='info', sender='bitfinex')

      # halt the calling thread until the connection is up
      while not self._connected:
         time.sleep(1)

   def disconnect(self):
      self._unsubscribe_all()
      self._subscriptions.clear()
      self._data.clear()

      # close connection and wait for the thread to terminate
      if self._ws is not None:
         self._ws.close()
      self._thread.join()
      self._thread = None
      self._ws = None
      self._connected = False

      # disconnect all listeners
      for d in dispatcher.getAllReceivers(sender='bitfinex'):
         d.disconnect()

   def subscribe(self, channel, **kwargs):
      if channel == 'ticker':
         return self.subscribe_ticker(**kwargs)
      elif channel == 'book':
         return self.subscribe_order_book(**kwargs)
      elif channel == 'trades':
         return self.subscribe_trades(**kwargs)
      elif channel == 'candles':
         return self.subscribe_candles(**kwargs)
      else:
         return None

   def unsubscribe(self, chanName, update_handler=None):
      chanId = self._get_channel_ID(chanName)
      if chanId is None:
         self.logger.info('Not subscribed to %s' % chanName)
         return

      # remove listener
      if update_handler is not None:
         try:
            self.logger.info('Removing listener for %s ...' % chanName)
            dispatcher.disconnect(update_handler, signal=chanName, sender='bitfinex')
         except dispatcher.errors.DispatcherKeyError as e:
            self.logger.info(e)

      # unsubscribe if no one is listening
      if dispatcher.getReceivers(sender='bitfinex', signal=chanName) == []:
         self.logger.info('Unsubscribing from %s ...' % chanName)
         self._ws.send(json.dumps({"event": "unsubscribe", "chanId": chanId}))



   # Channels
   # ---------------------------------------------------------------------------------

   def subscribe_ticker(self, symbol, update_handler=None):
      symbol = symbol.upper()
      chanName = 'ticker_' + symbol

      if update_handler is not None:
         dispatcher.connect(update_handler, signal=chanName, sender='bitfinex')

      if chanName not in self._subscriptions.values():
         self.logger.info('Subscribing to ticker %s ...' % symbol)
         self._ws.send(json.dumps({"event": "subscribe", "channel": "ticker", "symbol": symbol}))
      else:
         self.logger.info('Already subscribed to %s ticker' % symbol)
         try:
            chanId = self._get_channel_ID(chanName)
            if chanId is None:
               self._data[chanId].publish()
         except KeyError:
            pass

      return chanName


   def subscribe_order_book(self, symbol, update_handler=None, **kwargs):
      symbol = symbol.upper()
      prec = kwargs.get('prec', 'P0')
      freq = kwargs.get('freq', 'F0')
      len  = kwargs.get('len', '25')
      if prec not in ['P0','P1','P2','P3']:
         prec = 'P0'
      if freq not in ['F0','F1']:
         freq = 'F0'
      if len not in ['25','100']:
         len = '25'

      chanName = 'book_' + symbol + '_' + prec + '_' + freq

      if update_handler is not None:
         dispatcher.connect(update_handler, signal=chanName, sender='bitfinex')

      if chanName not in self._subscriptions.values():
         self.logger.info('Subscribing to order book for %s ...' % symbol)
         self._ws.send(json.dumps({"event": "subscribe", "channel": "book", "symbol": symbol,
                                  "prec": prec, "freq": freq, "len": len}))
      else:
         self.logger.info('Already subscribed to %s order book' % symbol)
         try:
            chanId = self._get_channel_ID(chanName)
            if chanId is None:
               self._data[chanId].publish()
         except KeyError:
            pass

      return chanName


   def subscribe_trades(self, symbol, update_handler=None):
      symbol = symbol.upper()
      chanName = 'trades_' + symbol

      if update_handler is not None:
         dispatcher.connect(update_handler, signal=chanName, sender='bitfinex')

      if chanName not in self._subscriptions.values():
         self.logger.info('Subscribing to trades for %s ...' % symbol)
         self._ws.send(json.dumps({"event": "subscribe", "channel": "trades", "symbol": symbol}))
      else:
         self.logger.info('Already subscribed to trades channel for %s' % symbol)
         try:
            chanId = self._get_channel_ID(chanName)
            if chanId is None:
               self._data[chanId].publish()
         except KeyError:
            pass

      return chanName


   def subscribe_candles(self, symbol, interval='1m', update_handler=None):
      symbol = symbol.upper()
      valid_intervals = ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D', '1M']
      if interval not in valid_intervals:
         raise ValueError("interval must be any of %s" % valid_intervals)

      chanName = 'candles_' + symbol + '_' + interval

      if update_handler is not None:
         dispatcher.connect(update_handler, signal=chanName, sender='bitfinex')

      if chanName not in self._subscriptions.values():
         self.logger.info('Subscribing to %s candels for %s ...' % (interval, symbol))
         self._ws.send(json.dumps({"event": "subscribe", "channel": "candles", "key": 'trade:' + interval + ':t' + symbol}))
      else:
         self.logger.info('Already subscribed to %s candles' % symbol)
         try:
            chanId = self._get_channel_ID(chanName)
            if chanId is not None:
               self._data[chanId].publish()
         except KeyError:
            pass

      return chanName






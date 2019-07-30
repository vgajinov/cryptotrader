import websocket
import json
import hashlib
import hmac
import time
from threading import Thread
from pydispatch import dispatcher
from collections import OrderedDict, deque

from exchanges.exception import *
from exchanges.WS.api import *


# ==========================================================================================
#   Ticker
# ==========================================================================================

class BitfinexTicker(ChannelData):
    """Bitfinex per-channel ticker"""

    def __init__(self, name, ticker):
        """Initialize a new ticker tracker
        :param name:   ticker name (i.e. 'ticker_' + symbol)
        :param ticker: ticker data from the exchange
        :raises: WSException
        Transform all the ticker data to floats and sends it to listeners
        """
        super(BitfinexTicker, self).__init__()
        self.name = name
        try:
            self.data = [float(x) for x in ticker]
        except Exception as e:
            raise WSException("Error initializing ticker channel {}: {}".format(name, e))
        self._publish()

    def update(self, ticker):
        """Update the ticker
        :param ticker:  a new ticker received from exchange via websocket
        :return: None
        :raises: WSException
        Updates all listeners via dispatcher.
        """
        try:
            self.data = [float(x) for x in ticker]
        except Exception as e:
            raise WSException("Error updating ticker channel {}: {}".format(self.name, e))
        self._publish()

    def snapshot(self):
        """Get the current snapshot of the ticker"""
        return self.data

    def _publish(self):
        """Send ticker to listeners"""
        dispatcher.send(signal=self.name, sender='bitfinex', data=self.data)


# ==========================================================================================
#   OrderBook
# ==========================================================================================

class BitfinexOrderBook(ChannelData):
    """Bitfinex per-channel order book.
    Bitfinex sends the data in the form of a list of orders,
    where each order is in the form of:
        [ PRICE, COUNT, AMOUNT ]
    when count > 0 then we have to add or update the price level
        if amount > 0 then add/update bids
        if amount < 0 then add/update asks
    when count = 0 then we have to delete the price level.
        if amount = 1 then remove from bids
        if amount = -1 then remove from asks
    """
    def __init__(self, name, orders):
        """Initialize a new order book
        :param name:   channel name (i.e. 'book_' + symbol + '_' + prec + '_' + freq)
        :param orders: order book data from the exchange
        :raises: WSException
        A new dictionary of bids and asks is created and sent to all listener via dispatcher
        """
        super(BitfinexOrderBook, self).__init__()
        self.name = name
        self.asks = {}
        self.bids = {}
        try:
            for order in orders:
                price  = float(order[0])
                amount = float(order[2])
                if amount > 0:
                    self.bids[price] = amount
                else:
                    self.asks[price] = -amount
        except Exception as e:
            raise WSException("Error initializing order book channel {}: {}".format(self.name, e))
        self._publish()


    def update(self, update):
        """Update the order book
        :param update:  an update received from exchange via websocket
        :return: None
        :raises WSException
        When the internal order book dictionary is updated
        all listeners are also updated via dispatcher.
        """
        try:
            price  = float(update[0])
            count  = int(update[1])
            amount = float(update[2])
            if count > 0:
                if amount > 0:
                    self.bids[price] = amount
                else:
                    self.asks[price] = -amount
            else:
                if amount == 1:
                    if self.bids.get(price, None):
                        self.bids.pop(price)
                elif amount == -1:
                    if self.asks.get(price, None):
                        self.asks.pop(price)
        except Exception as e:
            raise WSException("Error updating order book channel {}: {}".format(self.name, e))
        self._publish()

    def snapshot(self):
        """Get the latest snapshot of the order book"""
        bids, asks = self._sort_book()
        return {'bids': bids, 'asks': asks}

    def _sort_book(self):
        """Create two ordered lists, one for asks and the other for bids
        :return: (OrderedDict, OrderedDict)
        """
        bids = OrderedDict( sorted(self.bids.items(), key=lambda t: t[0]) )
        asks = OrderedDict( sorted(self.asks.items(), key=lambda t: t[0]) )
        return bids, asks

    def _publish(self):
        """Sends updated book to listeners"""
        bids, asks = self._sort_book()
        dispatcher.send(signal=self.name, sender='bitfinex', data={'bids': bids, 'asks': asks})


# ==========================================================================================
#   Trades
# ==========================================================================================

class BitfinexTrades(ChannelData):
    """Bitfinex per-channel trades.
    Updates are in the form of a list [ ID, MTS, AMOUNT, PRICE ]
    """
    def __init__(self, name, trades):
        """Initializes a new trades object
        :param name:   channel name (i.e. 'trades_' + symbol)
        :param trades: trades for a symbol from the exchange
        :raises WSException
        """
        super(BitfinexTrades, self).__init__()
        self.name = name
        self.trades = deque(maxlen=self.MAX_TRADES)
        try:
            for trade in trades:
                self.trades.append(trade[1:])
        except Exception as e:
            raise WSException("Error initializing trades channel {}: {}".format(self.name, e))
        # publish full list of trades
        dispatcher.send(signal=self.name, sender='bitfinex', data=('snapshot', list(self.trades)))

    def update(self, trade):
        """Update trades
        :param trade:  an update received from exchange via websocket
        :return: None
        :raises WSException
        Also update all listeners.
        """
        try:
            self.trades.appendleft(trade[1:])
        except Exception as e:
            raise WSException("Error updating trades channel {}: {}".format(self.name, e))
        dispatcher.send(signal=self.name, sender='bitfinex', data=('update', trade[1:]))

    def snapshot(self):
        """Get the current snapshot of the trades"""
        return 'snapshot', list(self.trades)


# ==========================================================================================
#   Candles
# ==========================================================================================

class BitfinexCandles(ChannelData):
    """Bitfinex per-channel candles
    1. Updates are in the form of a list [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
    so it is necessary to transform them into a standard ohlc form - [MTS, OPEN, HIGH, LOW, CLOSE, VOLUME].
    2. The order of received updates in the list is from the most recent to the least recent.
    We maintain the opposite order.
    """
    def __init__(self, name, candles):
        """Initializes a new candles object
        :param name:   channel name (i.e. 'candles_' + symbol)
        :param candles: a candles snapshot received from the exchange
        :raises WSException
        Keeps candles in a deque with size limited to MAX_CANDLES elements (just a safety).
        """
        super(BitfinexCandles, self).__init__()
        self.name = name
        try:
            for candle in candles:
                # make all values float except for the timestamp.
                # Bitfinex will send rounded price as int (i.e., 92.0 as 92)
                for i in range(1,len(candle)):
                    candle[i] = float(candle[i])
                # swap columns 3->2 4->3 2->4
                candle[2], candle[3] = candle[3], candle[2]
                candle[3], candle[4] = candle[4], candle[3]
            self.candles = deque(list(reversed(candles)), maxlen=self.MAX_CANDLES)
        except Exception as e:
            raise WSException("Error initializing candles channel {}: {}".format(self.name, e))
        dispatcher.send(signal=self.name, sender='bitfinex', data=('snapshot', list(self.candles)))

    def update(self, candle):
        """Update the candles
        :param candle:  a candle update received from exchange via websocket
        :return: None
        :raises WSException
        The new candle has to be compared with the last that we keep in order
        to see if we need to update the last we have or add a new one.
        """
        try:
            # swap the order of candle data
            candle[2], candle[3] = candle[3], candle[2]
            candle[3], candle[4] = candle[4], candle[3]
            # compare the timestamps of the last and new candle
            if candle[0] > self.candles[-1][0]:
                # add new candle
                self.candles.append(candle)
                dispatcher.send(signal=self.name, sender='bitfinex', data=('add', candle))
            elif candle[0] == self.candles[-1][0]:
                # update last candle
                self.candles[-1] = candle
                dispatcher.send(signal=self.name, sender='bitfinex', data=('update', candle))
            else:
                # bitfinex sometimes sends old candles. We just ignore it.
                return
        except Exception as e:
            raise WSException("Error updating candles channel {}: {}".format(self.name, e))

    def snapshot(self):
        """Get the current snapshot of the candles"""
        return 'snapshot', list(self.candles)


# ==========================================================================================
#   Client
# ==========================================================================================

class BitfinexWSClient(WSClientAPI):
    """Websocket client for Bitfinex

    - Client should be used via factory.
    - It implements common websocket api WSClientAPI,
      which means that only those calls should be used by a user.
    - The updates are propagated to a user code asynchronously via dispatcher.
      User is supposed to provide a callback handler that should handle
      the updates in the user space. Subscribe methods return the channel name
      and the initial data (useful to reduce communication cost for candles and trades)
    - Public channels are subscribed as requested.
    - Private channels are subscribed automatically after successful authentication.
    - All websocket communication is logged.
    """
    def __init__(self):
        """Creates Bitfinex websocket client"""
        super(BitfinexWSClient, self).__init__()
        self._thread = None         # socket thread
        self._ws = None             # websocket
        self._connected = False
        self._subscriptions  = {}   # subscriptions : channel_id -> channel_name
        self._data = {}             # channel_id -> channel data

        # authenticated channels
        self.authenticated = False
        self._key = None
        self._secret = None
        self._orders = []
        self._trades = []
        self._balances = {}

    @staticmethod
    def name():
        return 'Bitfinex'


    def _get_channel_id(self, channel_name):
        """Finds the channel ID for a given channel name.
        :param channel_name:   the name of the channel
        :return str           channel ID
        """
        channel_id = None
        for key, value in self._subscriptions.items():
            if value == channel_name:
                channel_id = key
        return channel_id


    def _connect(self):
        """Create a websocket connection to Bitfinex.
        Uses Bitfinex API version 2.
        """
        self.logger.info('Connecting to bitfinex websocket API ...')
        # websocket.enableTrace(True)
        self._ws = websocket.WebSocketApp('wss://api.bitfinex.com/ws/2',
                                          on_message=self._on_message,
                                          on_error=self._on_error,
                                          on_close=self._on_close)
        self._ws.on_open = self._on_open
        self._ws.run_forever()


    def _reconnect(self):
        """Reconnect to a websocket and resubscribe to all used channels.
        This method is intended to be used in case a websocket connection is dropped.
        """
        self._connect()
        self._resubscribe_all()


    def _unsubscribe_all(self):
        """Unsubscribe from all subscribed channels."""
        for chanId in self._subscriptions.keys():
            self.logger.info('Unsubscribing from %s ...' % self._subscriptions[chanId])
            self._ws.send(json.dumps({"event": "unsubscribe", "chanId": chanId}))


    def _resubscribe_all(self):
        """Renew subscription to all the channels used before the connection was dropped."""
        subscriptions = self._subscriptions.keys()
        self._subscriptions.clear()
        for chan in subscriptions:
            ch = chan.split('_')
            if len(ch) == 3:
                self.subscribe(ch[0], symbol=ch[1], interval=ch[2])
            else:
                self.subscribe(ch[0], symbol=ch[1])
        if self.authenticated is True:
            self.authenticated = False
            self.authenticate(key=self._key, secret=self._secret)


    # Websocket handlers
    # ---------------------------------------------------------------------------------

    def _on_open(self):
        self._connected = True
        self.logger.info('Bitfinex websocket connection open.')

    def _on_close(self):
        self.logger.info('Bitfinex websocket connection closed.')

    def _on_error(self, error):
        """Handles the error message received from the websocket.
        Logs the message and sends the error notification to listeners
        via dispatcher using 'info' signal.
        """
        self.logger.error('Bitfinex websocket error:')
        self.logger.error(error)
        dispatcher.send(signal='info', sender='bitfinex', data={'error': error})

    def _on_message(self, message):
        """Handles regular messages received from the websocket.
        :param message:   a message from the websocket
        :return None
        :raises ExchangeException

        This method is where most of the messages are decoded and handled
        according to their specific intent: event messages, update messages,
        info and error messages and so on.

        Bitfinex error codes:
            10000 : Unknown event
            10001 : Unknown pair
            10305 : Reached limit of open channels
            10300 : Subscription failed (generic)
            10301 : Already subscribed
            10302 : Unknown channel
            10400 : Subscription failed (generic)
            10401 : Not subscribed
        """

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
                    dispatcher.send(signal='info', sender='bitfinex', data={'error': msg['msg']})
                    self.logger.info('Error ' + str(msg['code']) + ' : ' + str(msg['msg']))
                elif event == 'info':
                    if 'version' in msg.keys():
                        self.logger.info('WS API version ' + str(msg['version']))
                    elif 'code' in msg.keys():
                        self.logger.info('Received code' + str(msg['code']) + ' : ' + msg['msg'])
                        if   msg['code'] == 20051:
                            dispatcher.send(signal='info', sender='bitfinex', data={'info': 'reconnecting'})
                            self._reconnect()
                        elif msg['code'] == 20060:
                            dispatcher.send(signal='info', sender='bitfinex', data={'info': 'pause'})
                            self._unsubscribe_all()
                        elif msg['code'] == 20061:
                            dispatcher.send(signal='info', sender='bitfinex', data={'info': 'unpause'})
                            self._resubscribe_all()
                elif event == 'subscribed':
                    self._channel_subscribed(msg)
                elif event == 'unsubscribed':
                    self._data.pop(msg['chanId'])                               # remove data object
                    channel_name = self._subscriptions.pop(msg['chanId'])       # remove subscription
                    self.logger.info('Unsubscribed from channel %s' % channel_name)
                elif event == 'auth':
                    if msg['status'] == 'OK':
                        self.authenticated = True
                        self.userId = msg['userId']
                        self.logger.info('Authenticated - userId %s' % self.userId)
                    else:
                        dispatcher.send(signal='info', sender='bitfinex', data={'error': 'Authentication FAILED!'})
                        self.logger.info('Authentication FAILED : %s' % msg['code'])
                else:
                    self.logger.info('Unhandled WS event!')

            # CHANNEL UPDATE
            else:
                channel_id = msg[0]
                if channel_id == 0:   # Account info always uses channel_id 0
                    self._update_auth_channel(msg)
                else:
                    self._update_channel(msg)

        except Exception as e:
            # a more specific exception message is provided in the exception itself.
            raise ExchangeException(self.name(), '', data=msg, orig_exception=e, logger=self.logger)


    def _channel_subscribed(self, msg):
        """Handles subscription notification messages received from websocket.
        :param msg:     a confirmation subscription message
        :returns None
        :raises Exception
        """
        try:
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
                dispatcher.send(signal='info', sender='bitfinex',
                                data={ 'error': 'No channel handler for channel - ' + channel})
        except Exception as e:
            ex_msg = 'Exception caught while processing subscription confirmation message:\n{}\n{}'.format(msg, e)
            raise(type(e), ex_msg)


    def _update_channel(self, msg):
        """Handles updates from public channels.
        :param msg:     update message
        :returns None
        :raises Exception
        """
        # return if this is just a channel heartbeat
        if 'hb' in msg:
            return

        try:
            channel_id = msg[0]
            channel_name = self._subscriptions[channel_id]
            data = msg[1]
            if self._data.get(channel_id, None) is None:
                # snapshot message
                if channel_name.startswith('ticker'):
                    self._data[channel_id] = BitfinexTicker(channel_name, data)
                elif channel_name.startswith('book'):
                    self._data[channel_id] = BitfinexOrderBook(channel_name, data)
                elif channel_name.startswith('trades'):
                    self._data[channel_id] = BitfinexTrades(channel_name, data)
                elif channel_name.startswith('candles'):
                    self._data[channel_id] = BitfinexCandles(channel_name, data)
            else:
                # update
                if channel_name.startswith('trades'):
                    self._data[channel_id].update(msg[2])
                else:
                    self._data[channel_id].update(data)
        except Exception as e:
            ex_msg = 'Exception caught while processing public channel update message:\n{}\n{}'.format(msg, e)
            raise(type(e), ex_msg)


    def _update_auth_channel(self, msg):
        """Handles updates from authenticated (private) channels.
        :param msg:     update message
        :returns None
        :raises Exception
        """
        try:
            self.logger.info('AUTH: {}'.format(msg[1]))
            if msg[1] == 'os':
                self._handle_order_update(msg[2])
            elif msg[1] == 'on' or msg[1] == 'ou' or msg[1] == 'oc':
                self._handle_order_update([msg[2]])
            elif msg[1] == 'tu':
                self._handle_user_trades(msg[2])
            elif msg[1] == 'ws':
                self._handle_balance_update(msg[2])
            elif msg[1] == 'wu':
                self._handle_balance_update([msg[2]])
        except Exception as e:
            ex_msg = 'Exception caught while processing private channel update message:\n{}\n{}'.format(msg, e)
            raise(type(e), ex_msg)


    # Public interface methods
    # ---------------------------------------------------------------------------------

    def connect(self, info_handler=None):
        """Connects to the exchange via websocket stream.
        :param info_handler:   a callback handler for info messages
        :returns None
        Info messages cover any information that is not related to concrete data from the exchange,
        but rather about the protocol or various exchange events, such as maintenance, or connection issues.
        """
        # start websocket listener thread
        self._thread = Thread(target=self._connect)
        self._thread.daemon = True
        self._thread.start()

        # register a handler for receiving info and error messages from websocket thread
        self._info_handler = info_handler
        dispatcher.connect(info_handler, signal='info', sender='bitfinex')

        # halt the calling thread until the connection is up
        while not self._connected:
            time.sleep(1)


    def disconnect(self):
        """Disconnects a client from the exchange.
        This method first unsubscribes a client from all subscribed channels,
        then it closes the websocket connection and waits for the socket thread to terminate.
        Next, it disconnects all listeners from the dispatcher for this client,
        and finally it stops the logger.
        """
        self._unsubscribe_all()
        self._subscriptions.clear()
        self._data.clear()

        # close connection
        if self._ws:
            self._ws.close()
            self._ws = None
            self._connected = False

        # wait for the thread to terminate
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None

        # disconnect all listeners
        for d in dispatcher.getAllReceivers(sender='bitfinex'):
            d.disconnect()

        self._stop_logger()


    def subscribe(self, channel, **kwargs):
        """Generic method for subscribing to a channel on the exchange.
        :param channel:  a concrete channel to subscribe to
        :param kwargs:   Arbitrary keyword arguments. Depend on the specific exchange.
        :returns str:    channel name that is used as a handle for a stream.
        :raises: ExchangeException
        A channel must be one of the following: ticker, book, trades or candles
        A remainder of the arguments is passed directly to concrete methods
        for subscribing to a given channel.
        """
        if channel == 'ticker':
            return self.subscribe_ticker(**kwargs)
        elif channel == 'book':
            return self.subscribe_order_book(**kwargs)
        elif channel == 'trades':
            return self.subscribe_trades(**kwargs)
        elif channel == 'candles':
            return self.subscribe_candles(**kwargs)
        else:
            raise ExchangeException(self.name(), 'Unrecognized channel requested. ' +
                                    'A channel must be one of the following: ticker, book, trades or candles')


    def unsubscribe(self, channel_name, update_handler=None):
        """Generic method to unsubscribe from the channel.
        :param channel_name:    a name of the channel
        :param update_handler:  Arbitrary keyword arguments. Depend on the specific exchange.
        The method first removes the listener from a dispatcher and then sends
        an unsubscribe message to a websocket.
        """
        # remove listener
        if update_handler is not None:
            try:
                self.logger.info('Removing listener for %s ...' % channel_name)
                dispatcher.disconnect(update_handler, signal=channel_name, sender='bitfinex')
            except dispatcher.errors.DispatcherKeyError:
                exc_msg = 'Tried to remove unrecognized listener while unsubscribing ' + \
                        'from a channel {}'.format(channel_name)
                self.logger.info(exc_msg)

        # authenticated channels all have channel_id 0 and are automatically subscribed
        if channel_name in ['orders', 'user_trades', 'balances']:
            return

        # get the channel_id of public channels
        channel_id = self._get_channel_id(channel_name)
        if channel_id is None:
            self.logger.info('Not subscribed to %s' % channel_name)
            return

        # unsubscribe if no one is listening
        if not dispatcher.getReceivers(sender='bitfinex', signal=channel_name):
            self.logger.info('Unsubscribing from %s ...' % channel_name)
            self._ws.send(json.dumps({"event": "unsubscribe", "chanId": channel_id}))


    # Public Channels
    # ---------------------------------------------------------------------------------

    def _handle_subscription(self, channel_name, payload, channel_type, symbol, update_handler=None):
        """Handles a common part of subscribing to a public channel
        :param channel_name:    a name of the channel to subscribe to
        :param payload:         a json object to send to a websocket
        :param channel_type:    one of 'ticker', 'book', 'trades' or 'candles'
        :param symbol:          a trading pair for which we request a subscription
        :param update_handler:  a callback to be used for updates by a dispatcher.
        :return: None
        This method registers a listener to a dispatcher for a given channel,
        sends the payload to a websocket.
        """
        if update_handler:
            dispatcher.connect(update_handler, signal=channel_name, sender='bitfinex')

        if channel_name not in self._subscriptions.values():
            self.logger.info('Subscribing to {} for {} ...'.format(channel_type, symbol))
            self._ws.send(payload)
        else:
            self.logger.info('Already subscribed to {} for {}.'.format(channel_type, symbol))
            channel_id = self._get_channel_id(channel_name)
            if channel_id:
                return self._data[channel_id].snapshot()
        return None


    def subscribe_ticker(self, symbol, update_handler=None):
        """Subscribe to ticker channel.
        :param symbol:            A string that represents a ticker symbol (pair).
        :param update_handler:  A callback handler that should handle the asynchronous update of a ticker.
        :return: A tuple of a string that represents a stream (channel) identifier and a snapshot.
        :raises ExchangeException
        """
        try:
            symbol = symbol.upper()
            channel_name = 'ticker_' + symbol
            payload = json.dumps({ "event": "subscribe",
                                   "channel": "ticker",
                                   "symbol": symbol  })
            ret = self._handle_subscription(channel_name, payload, 'ticker', symbol, update_handler)
            return channel_name, ret
        except Exception as e:
            raise ExchangeException(self.name(), 'Exception while trying to subscribe to a ticker',
                                    orig_exception=e, logger=self.logger)


    def subscribe_order_book(self, symbol, update_handler=None, **kwargs):
        """Subscribe to order book channel.
        :param symbol:          A symbol for a ticker (pair).
        :param update_handler:  A callback handler that should handle the asynchronous update of the order book.
        :param kwargs:          Additional parameters that differ between exchanges.
        :return: A tuple of a string that represents a stream (channel) identifier and a snapshot.
        :raises ExchangeException
        """
        try:
            symbol = symbol.upper()
            prec   = kwargs.get('prec', 'P0')
            freq   = kwargs.get('freq', 'F0')
            length = kwargs.get('len', '25')
            if prec not in ['P0', 'P1', 'P2', 'P3']: prec = 'P0'
            if freq not in ['F0', 'F1']: freq = 'F0'
            if length not in ['25', '100']: length = '25'

            channel_name = 'book_' + symbol + '_' + prec + '_' + freq
            payload = json.dumps({ "event":   "subscribe",
                                   "channel": "book",
                                   "symbol":   symbol,
                                   "prec":     prec,
                                   "freq":     freq,
                                   "len":      length
                                   })
            ret = self._handle_subscription(channel_name, payload, 'order book', symbol, update_handler)
            return channel_name, ret
        except Exception as e:
            raise ExchangeException(self.name(), 'Exception while trying to subscribe to an order book',
                                    orig_exception=e, logger=self.logger)


    def subscribe_trades(self, symbol, update_handler=None):
        """Subscribe to the channel for trades.
        :param symbol:          A symbol for a ticker (pair).
        :param update_handler:  A callback handler that should handle the asynchronous update of trades.
        :return: A tuple of a string that represents a stream (channel) identifier and a snapshot.
        :raises ExchangeException
        """
        try:
            symbol = symbol.upper()
            channel_name = 'trades_' + symbol
            payload = json.dumps({ "event": "subscribe",
                                   "channel": "trades",
                                   "symbol": symbol  })
            ret = self._handle_subscription(channel_name, payload, 'trades', symbol, update_handler)
            return channel_name, ret
        except Exception as e:
            raise ExchangeException(self.name(), 'Exception while trying to subscribe to a channel for trades',
                                    orig_exception=e, logger=self.logger)


    def subscribe_candles(self, symbol, interval='1m', update_handler=None):
        """Subscribe to the channel for candles.
        :param symbol:          A symbol for a ticker (pair).
        :param interval         Time interval for a candle.
        :param update_handler:  A callback handler that should handle the asynchronous update of trades.
        :return: A tuple of a string that represents a stream (channel) identifier and a snapshot.
        :raises ExchangeException
        """
        symbol = symbol.upper()
        valid_intervals = ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D', '1M']
        if interval not in valid_intervals:
            raise ExchangeException(self.name(), f'Unsupported candle interval. Must be one of {valid_intervals}')

        try:
            channel_name = 'candles_' + symbol + '_' + interval
            payload = json.dumps({ "event": "subscribe",
                                   "channel": "candles",
                                   "key": 'trade:' + interval + ':t' + symbol
                                   })
            ret = self._handle_subscription(channel_name, payload, 'candles', symbol, update_handler)
            return channel_name, ret
        except Exception as e:
            raise ExchangeException(self.name(), 'Exception while trying to subscribe to a channel for candles',
                                    orig_exception=e, logger=self.logger)


    # Authenticated Channels
    # ---------------------------------------------------------------------------------

    def authenticate(self, key=None, secret=None, key_file=None):
        """Authenticate a user.
        :param key:        User's public key.
        :param secret:     User's private key.
        :param key_file:   A ke file with public and private keys.
        :return True if authentication was successful
        If key file is provided, it will override values provided via key and secret
        """
        if key_file:
            with open(key_file, 'r') as f:
                self._key = f.readline().strip()
                self._secret = f.readline().strip()
        else:
            if key and secret:
                self._key = key
                self._secret = secret
        if not self._key or not self._secret:
            return False

        nonce = str(int(time.time() * 10000000))
        auth_string = 'AUTH' + nonce
        auth_sig = hmac.new(self._secret.encode(), auth_string.encode(), hashlib.sha384).hexdigest()

        self.logger.info('Authenticating ...')
        self._ws.send(json.dumps({'event':        'auth',
                                  'apiKey':       self._key,
                                  'authSig':      auth_sig,
                                  'authPayload':  auth_string,
                                  'authNonce':    nonce,
                                  'filter':       ['trading', 'balance', 'wallet']
                                  }))
        return True


    def subscribe_user_orders(self, update_handler):
        """Subscribe to user orders channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of user orders.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        """
        self.logger.info('Subscribing to orders channel')
        dispatcher.connect(update_handler, signal='orders', sender='bitfinex')
        if self._orders:
            dispatcher.send(signal='orders', sender='bitfinex', data=list(reversed(self._orders)))
        return 'orders'

    def subscribe_user_trades(self, update_handler):
        """Subscribe to user trades channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of user trades.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        """
        self.logger.info('Subscribing to user trades channel')
        dispatcher.connect(update_handler, signal='user_trades', sender='bitfinex')
        if self._trades:
            dispatcher.send(signal='user_trades', sender='bitfinex', data=list(reversed(self._trades)))
        return 'user_trades'

    def subscribe_balances(self, update_handler):
        """Subscribe to balances channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of user balances.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        """
        self.logger.info('Subscribing to balances channel')
        dispatcher.connect(update_handler, signal='balances', sender='bitfinex')
        if self._balances:
            dispatcher.send(signal='balances', sender='bitfinex', data=self._balances)
        return 'balances'


    def _handle_order_update(self, orders):
        """Handles order updates received from a websocket
        :param orders   a list of orders
        :returns None
        Processes received order updates and sends them to listeners via dispatcher.
        """
        for order in orders:
            id         = order[0]
            timestamp  = order[5]
            symbol     = order[3][1:]
            price      = order[16]
            amount     = abs(order[7])
            filled     = amount - abs(order[6])
            total      = price * amount
            active     = order[13] == 'ACTIVE' or order[13].startswith('PARTIALLY FILLED')
            canceled   = 'CANCELED' in order[13]
            side       = 'Buy' if order[7] > 0 else 'Sell'
            percFilled = '{:.2f}'.format(100 * filled / amount)

            if 'LIMIT' in order[8]:
                order_type = 'limit'
            elif 'MARKET' in order[8]:
                order_type = 'market'
            elif 'TRAILING STOP' in order[8]:
                order_type = 'trailing stop'
            elif 'STOP' in order[8]:
                order_type = 'stop'
            elif 'FOK' in order[8]:
                order_type = 'fok'

            order_update = [id, timestamp, symbol, order_type, side, price, amount, percFilled, total]

            # is it an update of existing order
            is_new_order = True
            for i, ord in enumerate(self._orders):
                if ord[0] == id:
                    is_new_order = False
                    if active:
                        self._orders[i] = order_update
                    else:
                        del self._orders[i]
                    break

            # is it a new order
            if active and is_new_order:
                self._orders.append(order_update)

            if canceled:
                trade_update = [timestamp, symbol, order_type, side, price, amount, filled, total, 'cancelled']
                self._trades.append(trade_update)
                dispatcher.send(signal='user_trades', sender='bitfinex', data=list(reversed(self._trades)))

        # publish orders
        dispatcher.send(signal='orders', sender='bitfinex', data=list(reversed(self._orders)))


    def _handle_user_trades(self, trade):
        """Handles trade updates received from a websocket
        :param trade   a single trade update
        :returns None
        Processes received trade update and sends it to listeners via dispatcher.
        """
        timestamp  = trade[2]
        symbol     = trade[1][1:]
        price      = trade[5]
        amount     = abs(trade[4])
        filled     = amount
        total      = price * amount
        side       = 'Buy' if trade[4] > 0 else 'Sell'
        status     = 'executed'

        if 'LIMIT' in trade[6]:
            order_type = 'limit'
        elif 'MARKET' in trade[6]:
            order_type = 'market'
        elif 'TRAILING STOP' in trade[6]:
            order_type = 'trailing stop'
        elif 'STOP' in trade[6]:
            order_type = 'stop'
        elif 'FOK' in trade[6]:
            order_type = 'fok'

        trade_update = [timestamp, symbol, order_type, side, price, amount, filled, total, status]
        self._trades.append(trade_update)
        dispatcher.send(signal='user_trades', sender='bitfinex', data=list(reversed(self._trades)))


    def _handle_balance_update(self, balances):
        """Handles balance updates received from a websocket
        :param balances   a list of balances
        :returns None
        Processes received balance updates and sends them to listeners via dispatcher.
        """
        for balance in balances:
            if balance[0] != 'exchange':
                continue
            currency = balance[1].upper()
            available_balance = balance[2]
            self._balances[currency] = available_balance

        dispatcher.send(signal='balances', sender='bitfinex', data=self._balances)


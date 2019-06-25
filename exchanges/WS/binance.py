import websocket
import ssl
import json
import threading
from pydispatch import dispatcher
from collections import OrderedDict, deque

from exchanges.WS.api import WSClientAPI, ChannelData
from exchanges.REST.binance import BinanceRESTClient
from exchanges.exception import *


# ==========================================================================================
#   Ticker
# ==========================================================================================

class BinanceTicker(ChannelData):
    """Binance per-channel ticker"""

    def __init__(self, name):
        """Initialize a new ticker tracker
        :param name:   ticker name (i.e. 'ticker_' + symbol)
        Sets the name of the ticker and sets data to empty list.
        """
        super(BinanceTicker, self).__init__()
        self.name = name
        self.data = []

    def update(self, ticker):
        """Update the ticker
        :param ticker:  a new ticker received from exchange via websocket
        :return: None
        :raises: WSException
        Updates all listeners via dispatcher.
        """
        self.data = [float(ticker[key]) for key in ['b', 'B', 'a', 'A', 'p', 'P', 'c', 'v', 'h', 'l']]
        dispatcher.send(signal=self.name, sender='binance', data=self.data)

    def snapshot(self):
        """Get the current snapshot of the ticker"""
        return self.data


# ==========================================================================================
#   All Tickers
# ==========================================================================================

class BinanceAllTickers(ChannelData):
    """Binance specific channel that returns tickers for all symbols traded on the exchange."""

    def __init__(self, name):
        """Initialize a new tracker for all-symbols tickers
        :param name:   ticker name (i.e. 'ticker_' + symbol)
        Sets the name of the ticker data handler and sets data to empty list.
        Adds a symbol as a first element of the ticker list.
        """
        super(BinanceAllTickers, self).__init__()
        self.name = name
        self.data = []

    def update(self, tickers):
        """Update all tickers
        :param tickers:  a new ticker received from exchange via websocket
        :return: None
        :raises: WSException
        Updates all listeners via dispatcher.
        """
        self.data = []
        for tickers in tickers:
            self.data.append([tickers['s']] +
                             [float(tickers[key]) for key in ['b', 'B', 'a', 'A', 'p', 'P', 'c', 'v', 'h', 'l']])
        dispatcher.send(signal=self.name, sender='binance', data=self.data)

    def snapshot(self):
        """Get the current snapshot of the ticker"""
        return self.data


# ==========================================================================================
#   OrderBook
# ==========================================================================================

class BinanceOrderBook(ChannelData):
    """Binance per-channel order book."""

    def __init__(self, name, snapshot):
        """Initialize a new order book
        :param name:      channel name (i.e. 'book_' + symbol + '_' + prec + '_' + freq)
        :param snapshot:  data to initialize the order book
        :raises: WSException
        A new dictionary of bids and asks is created and sent to all listener via dispatcher
        Binance snapshot is obtained using the REST api request.
        It has the following form:
            {
                "bids" : [ [price (str), amount (str)], .... ]
                "asks" : [ [price (str), amount (str)], .... ]
            }

        Since the snapshot is obtained using the REST api we do not need to publish the snapshot.
        The users, including the one that first subscribes to the channel, get the snapshot
        directly via the subscribe method.
        """
        super(BinanceOrderBook, self).__init__()
        self.name = name
        self.asks = {}
        self.bids = {}
        self.lastUpdateId = snapshot.get('lastUpdateId', 0)
        try:
            self.bids = {float(bid[0]): float(bid[1]) for bid in snapshot['bids']}
            self.asks = {float(ask[0]): float(ask[1]) for ask in snapshot['asks']}
        except Exception as e:
            raise WSException("Error initializing order book channel {}: {}".format(self.name, e))
        # self._publish()

    def update(self, update):
        """Update the order book
        :param update:  an update received from exchange via websocket
        :return: None
        :raises WSException
        When the internal order book dictionary is updated all listeners are also updated via dispatcher.
        """
        # Drop any event where 'u' (final update ID in event) is <= lastUpdateId
        if update['u'] <= self.lastUpdateId:
            return
        self.lastUpdateId = update['u']

        try:
            for bid in update['b']:
                price = float(bid[0])
                quantity = float(bid[1])
                if quantity == 0.0:
                    if self.bids.get(price, None):
                        self.bids.pop(price)
                    # elif self.asks.get(price, None):
                    #    self.asks.pop(price)
                else:
                    self.bids[price] = quantity
            for ask in update['a']:
                price = float(ask[0])
                quantity = float(ask[1])
                if quantity == 0.0:
                    if self.asks.get(price, None):
                        self.asks.pop(price)
                    # elif self.bids.get(price, None):
                    #    self.bids.pop(price)
                else:
                    self.asks[price] = quantity
        except Exception as e:
            raise WSException("Error updating order book channel {}: {}".format(self.name, e))
        self._publish()

    def snapshot(self):
        """Get the latest snapshot of the order book"""
        bids, asks = self._sort_book()
        return {'bids': bids, 'asks': asks}

    def _sort_book(self):
        """Get the latest snapshot of the order book"""
        bids = OrderedDict(sorted(self.bids.items(), key=lambda t: t[0]))
        asks = OrderedDict(sorted(self.asks.items(), key=lambda t: t[0]))
        return bids, asks

    def _publish(self):
        """Sends updated book to listeners"""
        bids, asks = self._sort_book()
        dispatcher.send(signal=self.name, sender='binance', data={'bids': bids, 'asks': asks})


# ==========================================================================================
#   Trades
# ==========================================================================================

class BinanceTrades(ChannelData):
    """Binance per-channel trades."""
    def __init__(self, name, trades):
        """Initializes a new trades object
        :param name:   channel name (i.e. 'trades_' + symbol)
        :param trades: trades for a symbol from the exchange
        :raises WSException
        The snapshot of the trades is obtained by using the REST api,
        which returns the trades in the form of a list of
            [ TIMESTAMP, PRICE, AMOUNT, 'sell' or 'buy' ]
        We return it in the form of
            [ TIMESTAMP, AMOUNT, PRICE ]
        where the amount is negative if it was a sell order.

        Since the snapshot is obtained using the REST api we do not need to publish the snapshot.
        The users, including the one that first subscribes to the channel, get the snapshot
        directly via the subscribe method.
        """
        super(BinanceTrades, self).__init__()
        self.name = name
        self.trades = deque(maxlen=self.MAX_TRADES)
        trades = trades[-self.MAX_TRADES:]
        try:
            for trade in trades:
                self.trades.appendleft([int(trade[0]),
                                        -float(trade[2]) if trade[-1] == 'sell' else float(trade[2]),
                                        float(trade[1])])
        except Exception as e:
            raise WSException("Error initializing trades channel {}: {}".format(self.name, e))
        # dispatcher.send(signal=self.name, sender='binance', data=('snapshot', list(self.trades)))

    def update(self, trade):
        """Update trades
        :param trade:  an update received from exchange via websocket
        :return: None
        :raises WSException
        Also updates all listeners.
        The updates are dictionary objects:
            {
                "e": "trade",     // Event type
                "E": 123456789,   // Event time
                "s": "BNBBTC",    // Symbol
                "t": 12345,       // Trade ID
                "p": "0.001",     // Price
                "q": "100",       // Quantity
                "b": 88,          // Buyer order ID
                "a": 50,          // Seller order ID
                "T": 123456785,   // Trade time
                "m": true,        // Is the buyer the market maker?
                "M": true         // Ignore
            }
        """
        try:
            self.trades.appendleft( [int(trade['T']),
                                     -float(trade['q']) if trade['m'] else float(trade['q']),
                                     float(trade['p'])] )
        except Exception as e:
            raise WSException("Error initializing trades channel {}: {}".format(self.name, e))
        dispatcher.send(signal=self.name, sender='binance', data=('update', self.trades[0]))


    def snapshot(self):
        """Get the current snapshot of the trades"""
        return 'snapshot', list(self.trades)


# ==========================================================================================
#   Candles
# ==========================================================================================

class BinanceCandles(ChannelData):
    """Binance per-channel candles
    1. Snapshot is received using the REST api and is a list of candles:
        [
          [
            1499040000000,      # Open time
            "0.01634790",       # Open
            "0.80000000",       # High
            "0.01575800",       # Low
            "0.01577100",       # Close
            "148976.11427815",  # Volume
            1499644799999,      # Close time
            "2434.19055334",    # Quote asset volume
            308,                # Number of trades
            "1756.87402397",    # Taker buy base asset volume
            "28.46694368",      # Taker buy quote asset volume
            "17928899.62484339" # Ignore.
          ]
        ]
    So we just take the first 6 items of each candle to retain a standard ohlc form
        [MTS, OPEN, HIGH, LOW, CLOSE, VOLUME].
    2. The order of received updates in the list is from the oldest to the most recent candle.
    """
    def __init__(self, name, candles):
        """Initializes a new candles object
        :param name:   channel name (i.e. 'candles_' + symbol)
        :param candles: a candles snapshot received from the exchange
        :raises WSException
        Keeps candles in a deque with size limited to MAX_CANDLES elements (just a safety).
        Since the snapshot is obtained using the REST api we do not need publish the snapshot.
        The users, including the one that first subscribes to the channel, get the snapshot
        directly via the subscribe method.
        """
        super(BinanceCandles, self).__init__()
        self.name = name
        try:
            self.candles = deque([ [int(candle[0])] + [float(c) for c in candle[1:6]] for candle in candles ],
                                 maxlen=self.MAX_CANDLES)
        except Exception as e:
            raise WSException("Error initializing candles channel {}: {}".format(self.name, e))
        # dispatcher.send(signal=self.name, sender='binance', data=('snapshot', list(self.candles)))

    def update(self, update):
        """Update the candles
        :param update:  a candle update received from exchange via websocket
        :return: None
        :raises WSException
        The new candle has to be compared with the last that we keep in order
        to see if we need to update the last we have or add a new one.
        The format of the candle update is this:
            {
              "e": "kline",     # Event type
              "E": 123456789,   # Event time
              "s": "BNBBTC",    # Symbol
              "k": {
                "t": 123400000, # Kline start time
                "T": 123460000, # Kline close time
                "s": "BNBBTC",  # Symbol
                "i": "1m",      # Interval
                "f": 100,       # First trade ID
                "L": 200,       # Last trade ID
                "o": "0.0010",  # Open price
                "c": "0.0020",  # Close price
                "h": "0.0025",  # High price
                "l": "0.0015",  # Low price
                "v": "1000",    # Base asset volume
                "n": 100,       # Number of trades
                "x": false,     # Is this kline closed?
                "q": "1.0000",  # Quote asset volume
                "V": "500",     # Taker buy base asset volume
                "Q": "0.500",   # Taker buy quote asset volume
                "B": "123456"   # Ignore
              }
            }
        """
        try:
            candle = [int(update['k']['t']),
                      float(update['k']['o']),
                      float(update['k']['h']),
                      float(update['k']['l']),
                      float(update['k']['c']),
                      float(update['k']['v'])]

            if candle[0] > self.candles[-1][0]:
                # add new candle
                self.candles.append(candle)
                dispatcher.send(signal=self.name, sender='binance', data=('add', candle))
            elif candle[0] == self.candles[-1][0]:
                # update last candle
                self.candles[-1] = candle
                dispatcher.send(signal=self.name, sender='binance', data=('update', candle))
            else:
                # in case we got some stale update just ignore it.
                return
        except Exception as e:
            raise WSException("Error updating candles channel {}: {}".format(self.name, e))

    def snapshot(self):
        """Get the current snapshot of the candles"""
        return 'snapshot', list(self.candles)


# ==========================================================================================
#   Client
# ==========================================================================================

WEBSOCKET_URI = 'wss://stream.binance.com:9443/ws/'
REST_URI      = 'https://api.binance.com'


class BinanceWSClient(WSClientAPI):
    """Websocket client for Binance

    - Client should be used via factory.
    - It implements common websocket api WSClientAPI,
      which means that only those calls should be used by a user.
    - The updates are propagated to a user code asynchronously via dispatcher.
      User is supposed to provide a callback handler that should handle
      the updates in the user space. Subscribe methods return the channel name
      and the initial data (useful to reduce communication cost for candles and trades)
    - Public channels are subscribed as requested.
    - Private channels are subscribed automatically after successful authentication.
    - Each channel is handled by a separate dedicated thread. Since Binance does not have
      a subscription handshake protocol, channels are subscribed as soon as we send a request
      for a particular stream. That means that each thread work on the dedicated websocket.
    - All websocket communication is logged.
    """
    def __init__(self):
        """Creates Binance websocket client"""
        super(BinanceWSClient, self).__init__()
        self._data = {}           # stream -> data
        self._subscriptions = {}  # stream -> thread
        self._connections = {}    # stream -> websocket

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
        """Create a websocket connection to Bitfinex."""
        stream = threading.current_thread().getName()
        self.logger.info('Connecting to websocket for stream %s' % stream)
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp(WEBSOCKET_URI + stream,
                                         on_message=self._on_message,
                                         on_error=self._on_error,
                                         on_close=self._on_close)
        ws.on_open = self._on_open
        self._connections[stream] = ws
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  # TODO see if we can solve this using ssl
        self.logger.info('Thread exit for {}'.format(stream))

    def _reconnect(self):
        """Reconnect to a websocket and resubscribe to all used channels.
        This method is intended to be used in case a websocket connection is dropped.
        All the stream should be reconnected automatically.
        """
        self._connect()

    def _subscribe(self, stream):
        """Starts a websocket listener thread for a given stream.
        The name of the thread is the name of the stream it handles.
        """
        self.logger.info('Starting a new thread for {}'.format(stream))
        thread = threading.Thread(target=self._connect, name=stream)
        thread.daemon = True
        self._subscriptions[stream] = thread
        thread.start()

    def _log_active_threads(self):
        """A helper method to log all active threads."""
        threads = [thr.getName() for thr in threading.enumerate()]
        self.logger.info(('ACTIVE THREADS: {}'.format(','.join(threads))))


    # Websocket handlers
    # ---------------------------------------------------------------------------------

    def _on_open(self):
        stream = threading.current_thread().getName()
        self.logger.info('Websocket connection open for {}'.format(stream))

    def _on_close(self):
        stream = threading.current_thread().getName()
        self.logger.info('Websocket connection closed for {}'.format(stream))

    def _on_error(self, error):
        """Handles the error message received from the websocket.
        :param error:  error message
        :raises ExchangeException
        Logs the message and sends the error notification to listeners
        via dispatcher using 'info' signal.
        """
        self.logger.info('Websocket error:')
        try:
            err = json.loads(error)
            self.logger.info('Error {} : {}'.format(err['code'], err['msg']))
            dispatcher.send(signal='info', sender='binance', data={'error': err['msg]']})
        except json.decoder.JSONDecodeError as e:
            raise ExchangeException(self.name(), 'Exception caught while decoding json object from a websocket!',
                                    data=error, orig_exception=e, logger=self.logger)


    def _on_message(self, message):
        """Handles regular messages (updates) received from the websocket.
        :param message:   a message from the websocket
        :return None
        :raises ExchangeException
        """
        msg = json.loads(message)
        try:
            stream = threading.current_thread().getName()
            # TICKER, ORDER BOOK, TRADES or CANDLES
            if 'ticker' in stream or \
                    'depth' in stream or \
                    'trade' in stream or \
                    'kline' in stream:
                self._data[stream].update(msg)
            # AUTHENTICATED
            elif self._listenKey == stream:
                self._handle_auth_update(msg)
            else:
                self.logger.info('Update not handled for stream {}'.format(stream))
                self.logger.info('Message:\n{}'.format(msg))
        except KeyError:
            pass
        except Exception as e:
            raise ExchangeException(self.name(), 'Exception caught while handling a websocket channel message',
                                    data=msg, orig_exception=e, logger=self.logger)


    # Public interface methods
    # ---------------------------------------------------------------------------------

    def connect(self, info_handler=None):
        """Connects to the exchange via websocket stream.
        :param info_handler:   a callback handler for info messages
        :returns None
        In Binance case there no connection establishing; as soon as we send a request for a given stream
        are connected to it. Establishing a connection is handled when starting a stream dedicated thread.
        this method only registers a common info handler for messages related to the protocol or various
        exchange events, such as maintenance, or connection issues.
        """
        self._info_handler = info_handler
        dispatcher.connect(info_handler, signal='info', sender='binance')

    def disconnect(self):
        """Disconnects a client from the exchange.
        This method first unsubscribes a client from all subscribed channels,
        closes the websocket connections and waits for the each socket thread to terminate.
        Next, it disconnects all listeners from the dispatcher for this client,
        and finally it stops the logger.
        """
        self.logger.info('Disconnecting ...')
        for stream, thread in list(self._subscriptions.items()):
            try:
                self.unsubscribe(stream)
                thread.join()
            except KeyError:
                self.logger.info('No subscription for stream %s' % stream)

        self._data.clear()
        self._connections.clear()
        self._subscriptions.clear()

        if self._info_handler:
            dispatcher.disconnect(self._info_handler, signal='info', sender='binance')
        # there should be no listeners at this point but make sure that we do a clean up
        for d in dispatcher.getAllReceivers(sender='binance'):
            d.disconnect()

        self._stop_logger()


    def subscribe(self, channel, **kwargs):
        """Generic method for subscribing to a stream on the exchange.
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


    def unsubscribe(self, stream, update_handler=None):
        """Generic method to unsubscribe from the channel.
        :param stream:          a name of the channel
        :param update_handler:  arbitrary keyword arguments. Depend on the specific exchange.
        The method first removes the listener from a dispatcher and then sends
        an unsubscribe message to a websocket if there are no more listeners on a stream.
        """
        if update_handler:
            try:
                self.logger.info(f'Removing listener for {stream} ...')
                dispatcher.disconnect(update_handler, signal=stream, sender='binance')
            except dispatcher.errors.DispatcherKeyError as e:
                self.logger.error(e)

        # unsubscribe if no one is listening
        if not dispatcher.getReceivers(sender='binance', signal=stream):
            self.logger.info(f'Unsubscribing from {stream} ...')
            try:
                self._data.pop(stream)                    # remove data object
                self._subscriptions.pop(stream)           # remove subscription
                socket = self._connections.pop(stream)    # remove connection
                socket.close()                            # this will terminate the thread
                self.logger.info(f'Unsubscribed from {stream}')
                # parent thread does not call join here to avoid blocking
            except KeyError:
                self.logger.error(f'No subscription for stream {stream}')


    # Public Channels
    # ---------------------------------------------------------------------------------

    def subscribe_ticker(self, symbol, update_handler=None):
        """Subscribe to ticker channel.
        :param symbol:            A string that represents a ticker symbol (pair).
        :param update_handler:  A callback handler that should handle the asynchronous update of a ticker.
        :return: A tuple of a string that represents a stream (channel) identifier and a snapshot.
        :raises ExchangeException
        """
        try:
            stream = symbol.lower() + '@ticker'

            if update_handler:
                dispatcher.connect(update_handler, signal=stream, sender='binance')

            if stream not in self._subscriptions:
                self.logger.info(f'Subscribing to ticker for {symbol} ...')
                self._data[stream] = BinanceTicker(stream)
                self._subscribe(stream)
                return stream, None
            else:
                self.logger.info(f'Already subscribed to {symbol} candles')
                return stream, self._data[stream].snapshot()
        except Exception as e:
            raise ExchangeException(self.name(), 'Exception while trying to subscribe to a ticker',
                                    orig_exception=e, logger=self.logger)


    def subscribe_all_tickers(self, update_handler=None):
        """Subscribe to all tickers channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of a ticker.
        :return: A tuple of a string that represents a stream (channel) identifier and a snapshot.
        :raises ExchangeException
        """
        try:
            stream = '!ticker@arr'

            if update_handler:
                dispatcher.connect(update_handler, signal=stream, sender='binance')

            if stream not in self._subscriptions:
                self.logger.info('Subscribing to all pairs tickers')
                self._data[stream] = BinanceAllTickers(stream)
                self._subscribe(stream)
                return stream, None
            else:
                self.logger.info('Already subscribed to all tickers')
                return stream, self._data[stream].snapshot()
        except Exception as e:
            raise ExchangeException(self.name(), 'Exception while trying to subscribe to all tickers',
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
            symbol = symbol.lower()
            stream = symbol + '@depth'

            if update_handler is not None:
                dispatcher.connect(update_handler, signal=stream, sender='binance')

            if stream not in self._subscriptions:
                self.logger.info(f'Subscribing to order book for {symbol} ...')
                # Get a depth snapshot using the rest api
                init_book_data = BinanceRESTClient().order_book(symbol)
                if not init_book_data:
                    init_book_data = {'bids': [], 'asks': []}
                self._data[stream] = BinanceOrderBook(stream, init_book_data)
                self._subscribe(stream)
            else:
                self.logger.info(f'Already subscribed to {symbol} book')

            return stream, self._data[stream].snapshot()

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
            symbol = symbol.lower()
            stream = symbol + '@trade'

            if update_handler:
                dispatcher.connect(update_handler, signal=stream, sender='binance')

            if stream not in self._subscriptions:
                self.logger.info(f'Subscribing to trades for {symbol} ...')
                # get trades snapshot using the REST api
                init_trade_data = BinanceRESTClient().trades(symbol.lower())
                if init_trade_data is None:
                    init_trade_data = []
                self._data[stream] = BinanceTrades(stream, init_trade_data)
                self._subscribe(stream)
            else:
                self.logger.info(f'Already subscribed to {symbol} trades')

            return stream, self._data[stream].snapshot()

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
        valid_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h',
                           '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        if interval not in valid_intervals:
            raise ExchangeException(self.name(), f'Unsupported candle interval. Must be one of {valid_intervals}')

        try:
            stream = symbol.lower() + '@kline_' + interval

            if update_handler is not None:
                dispatcher.connect(update_handler, signal=stream, sender='binance')

            if stream not in self._subscriptions:
                self.logger.info(f'Subscribing to {interval} candles for {symbol} ...')
                # Get candle snapshot using the rest api
                init_candle_data = BinanceRESTClient().candles(symbol.lower(), interval=interval)
                if init_candle_data is None:
                    init_candle_data = []
                self._data[stream] = BinanceCandles(stream, init_candle_data)
                self._subscribe(stream)
            else:
                self.logger.info(f'Already subscribed to {symbol} candles')

            return stream, self._data[stream].snapshot()

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
        self._key = key
        self._secret = secret
        self._keyFile = key_file

        self.logger.info('Authenticating ...')
        rest_client = BinanceRESTClient(key=key, secret=secret, key_file=key_file)
        ret = rest_client.create_listen_key()
        try:
            self._listenKey = ret['listenKey']
            self.logger.info('Authentication successful')
        except:
            self.logger.info('Authentication failed')
            return False

        # get a snapshot of open orders
        open_orders = rest_client.open_orders()
        if open_orders is not None:
            for order in open_orders:
                order_id   = int(order['orderId'])
                timestamp  = int(order['timestamp'])
                symbol     = order['symbol']
                order_type = order['type']
                side       = order['side']
                price      = float(order['price'])
                amount     = float(order['amount'])
                filled     = float(order['filled'])
                total      = price * amount
                percent_filled = '{:.2f}'.format(100 * filled / amount)

                self._orders.append(
                    [order_id, timestamp, symbol, order_type, side, price, amount, percent_filled, total])

        # get a snapshot of balances
        self._balances = rest_client.balance()
        if self._balances is None:
            self._balances = {}

        self._subscribe(self._listenKey)

        self.authenticated = True
        return True


    def subscribe_user_orders(self, update_handler):
        """Subscribe to user orders channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of user orders.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        """
        self.logger.info('Subscribing to orders channel')
        dispatcher.connect(update_handler, signal='orders', sender='binance')
        if self._orders:
            dispatcher.send(signal='orders', sender='binance', data=list(reversed(self._orders)))
        return 'orders'

    def subscribe_user_trades(self, update_handler):
        """Subscribe to user trades channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of user trades.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        """
        self.logger.info('Subscribing to user trades channel')
        dispatcher.connect(update_handler, signal='user_trades', sender='binance')
        return 'user_trades'

    def subscribe_balances(self, update_handler):
        """Subscribe to balances channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of user balances.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        """
        self.logger.info('Subscribing to balances channel')
        dispatcher.connect(update_handler, signal='balances', sender='binance')
        if self._balances:
            dispatcher.send(signal='balances', sender='binance', data=self._balances)
        return 'balances'


    def _handle_auth_update(self, msg):
        """Handles updates for authenticated streams received from a websocket
        :param msg     an update message
        :returns None
        Processes received order updates and sends them to listeners via dispatcher.
        """
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
        """Handles order updates received from a websocket
        :param msg      order update message
        :returns None
        Processes received order updates and sends them to listeners via dispatcher.
        """
        order_id   = int(msg['i'])
        timestamp  = int(msg['T'])
        symbol     = msg['s']
        order_type = msg['o'].lower()
        side       = msg['S']
        price      = float(msg['p'])
        amount     = float(msg['q'])
        filled     = float(msg['z'])
        total      = price * amount
        percent_filled = '{:.2f}'.format(100 * filled / amount)
        status     = msg['x'].lower()
        if status == 'trade':
            status = 'executed'
        is_active   = msg['x'] == 'NEW'

        order_update = [order_id, timestamp, symbol, order_type, side, price, amount, percent_filled, total]
        trade_update = [timestamp, symbol, order_type, side, price, amount, filled, total, status]

        if is_active:
            # is it an update of existing order
            is_new_order = True
            for i, order in enumerate(self._orders):
                if order[0] == order_id:
                    is_new_order = False
                    self._orders[i] = order_update
                    break
            if is_new_order:
                self._orders.append(order_update)
            dispatcher.send(signal='orders', sender='binance', data=list(reversed(self._orders)))
        else:
            # delete from orders
            for i, order in enumerate(self._orders):
                if order[0] == order_id:
                    del self._orders[i]
                    dispatcher.send(signal='orders', sender='binance', data=list(reversed(self._orders)))
            # add to trades
            self._trades.append(trade_update)
            dispatcher.send(signal='user_trades', sender='binance', data=list(reversed(self._trades)))


    def _handle_balance_update(self, msg):
        """Handles balance updates received from a websocket
        :param msg      a balance update message
        :returns None
        Processes received balance updates and sends them to listeners via dispatcher.
        """
        for wallet in msg['B']:
            self._balances[wallet['a']] = wallet['f']
        dispatcher.send(signal='balances', sender='binance', data=self._balances)






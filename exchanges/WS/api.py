import logging
from abc import ABC, abstractmethod

TRADE_QUEUE_SIZE = 100  # deque size for trades


class WSClientAPI(ABC):
    """ Abstract base class for websocket based clients """

    def __init__(self):
        super(WSClientAPI, self).__init__()
        self._init_logger()
        self._info_handler = None

    def __str__(self):
        return self.name()

    def _init_logger(self):
        """Create a logger for a client"""
        self.logger = logging.getLogger('WSClientAPILogger')
        self.logger.setLevel(logging.DEBUG)
        self.logger_handler = logging.FileHandler(self.__class__.__name__ + '.log')
        self.logger_handler.setLevel(logging.DEBUG)
        self.logger_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                                  datefmt='%d-%m %H:%M:%S')
        self.logger_handler.setFormatter(self.logger_formatter)
        self.logger.addHandler(self.logger_handler)

    def _stop_logger(self):
        """Terminate the logger"""
        self.logger_handler.flush()
        self.logger_handler.close()
        self.logger.removeHandler(self.logger_handler)
        self.logger = None

    # @staticmethod
    @abstractmethod
    def name(self):
        """Return the name of the exchange.
        This is used by the WSClientFactory and is NOT the name of the class,
        but is defined by the class implementation.
        """
        pass

    @abstractmethod
    def connect(self, info_handler=None):
        """Connect to the exchange via websocket stream.
        :param info_handler   a callback handler for info messages
        Info messages cover any information that is not related to concrete data from the exchange,
        but rather about the protocol or various exchange events, such as maintenance, or connection issues.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the exchange."""
        pass

    @abstractmethod
    def subscribe(self, channel, **kwargs):
        """Generic method to subscribe to a channel of an exchange.
        :param channel:  a concrete channel to subscribe to
        :param kwargs: Arbitrary keyword arguments. Depend on the specific exchange.
        """
        pass

    @abstractmethod
    def unsubscribe(self, channel, update_handler=None):
        """Generic method to unsubscribe from the channel.
        :param channel:         id of the channel to unsubscribe from
        :param update_handler:  a handler used by a listener to receive updates from dispatcher.
        A channel must be one of the following: ticker, book, trades or candles.
        A remainder of the arguments is passed directly to concrete methods
        for subscribing to a given channel.
        """
        pass

    @abstractmethod
    def subscribe_ticker(self, symbol, update_handler=None):
        """Subscribe to ticker channel.
        :param symbol:            A string that represents a ticker symbol (pair).
        :param update_handler:  A callback handler that should handle the asynchronous update of a ticker.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        :raises ExchangeException
        Data is returned by dispatcher via update_handler in the following format:
           [ BID, BID_SIZE, ASK, ASK_SIZE, DAY_CHANGE, DAY_CHANGE_PERCENT, LAST_PRICE, VOLUME, HIGH, LOW ]
        Return type:
           [ all floats ]
        """
        pass

    @abstractmethod
    def subscribe_order_book(self, symbol, update_handler=None, **kwargs):
        """Subscribe to order book channel.
        :param symbol:          A symbol for a ticker (pair).
        :param update_handler:  A callback handler that should handle the asynchronous update of the order book.
        :param kwargs:          Additional parameters that differ between exchanges.
        :raises ExchangeException
        Data is returned by dispatcher as a dictionary with two keys: bids and asks,
            {'bids': bids, 'asks': asks}
        where bids and asks are OrderedDict objects ordered by the price from low to high.
        The format is:
           { PRICE (float) : AMOUNT (float) }
        """
        pass

    @abstractmethod
    def subscribe_trades(self, symbol, update_handler=None):
        """Subscribe to the channel for trades.
        :param symbol:          A symbol for a ticker (pair).
        :param update_handler:  A callback handler that should handle the asynchronous update of trades.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        :raises ExchangeException
        Data is returned by dispatcher as a (type, data) tuple,
        where the type informs the user how he should treat the data.
        Type can be one of these two options:
            ('snapshot', list(trades))    data is a a complete snapshot
            ('update', new_trade)         data is an update of the most recent trade
        The format of a single trade is a list:
            [ TIMESTAMP, AMOUNT, PRICE ]  -> [int, float, float]
        If the amount is negative, that was a sell order. Otherwise it was a buy order.
        The snapshot returns the trades in the order from the most recent to the least recent.
        """
        pass

    @abstractmethod
    def subscribe_candles(self, symbol, interval='1m', update_handler=None):
        """Subscribe to the channel fro candles.
        :param symbol:          A symbol for a ticker (pair).
        :param interval         Time interval for a candle.
        :param update_handler:  A callback handler that should handle the asynchronous update of trades.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        :raises ExchangeException
        Data is returned by dispatcher as a (type, data) tuple,
        where the type informs the user how he should treat the data.
        Type can be one of these three options:
            ('snapshot', list(candles))    data is a a complete snapshot
            ('add', candle)                data is a new candle
            ('update', candle)             data is an update of the last candle
        The format of a candle is a list:
            [ TIMESTAMP, OPEN, CLOSE, HIGH, LOW, VOLUME ] -> [int, float, float, float, float, float]
        """
        pass


    # ------------------------------------------------------------------------
    #    AUTHENTICATED CHANNELS
    # ------------------------------------------------------------------------

    @abstractmethod
    def authenticate(self, key=None, secret=None, key_file=None):
        """Authenticate a user.
        :param key:        User's public key.
        :param secret:     User's private key.
        :param key_file:   A ke file with public and private keys.
        :return True if authentication was successful
        If key file is provided, it will override values of provided via key and secret
        """
        pass

    @abstractmethod
    def subscribe_user_orders(self, update_handler):
        """Subscribe to user orders channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of user orders.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        Data is returned by dispatcher in the form of list of orders:
           [ ID, TIMESTAMP, SYMBOL, TYPE, SIDE, PRICE, AMOUNT, FILED%, TOTAL ]
        Return type:
           [ [int, int, string, string, string, float, float, string, float] ]
        """
        pass

    @abstractmethod
    def subscribe_user_trades(self, update_handler):
        """Subscribe to user trades channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of user trades.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        Data is returned by dispatcher in the form of list of trades:
           [ TIMESTAMP, SYMBOL, TYPE, SIDE, PRICE, AMOUNT, FILLED, TOTAL, STATUS ]
        Return type:
           [ [int, string, string, string, float, float, float, float, string] ]
        """
        pass

    @abstractmethod
    def subscribe_balances(self, update_handler):
        """Subscribe to balances channel.
        :param update_handler:  A callback handler that should handle the asynchronous update of user balances.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        Data is returned by dispatcher as a dictionary of balances:
           { currency : balance }
        Return type:
           { string : float }
        """
        pass


class ChannelData(ABC):
    """Abstract class for channel data.
    A data object for a specific channel is created only once
    and can update multiple listeners at the same time.
    When the first user of a given channel is subscribed,
    and once the snapshot is received from the websocket,
    a corresponding data object will be created for that channel.
    Since receiving the data from a websocket is asynchronous,
    the first user will be updated by sending entire snapshot
    via dispatcher. Subsequent subscribes will immediately get
    the snapshot from the data object as a return data from the
    subscribe method.

    Individual updates from the exchange are published to all listener,
    but the communication is kept to the minimum by avoiding to send
    the full data on every update.

    See the WSClientAPI subscribe methods description for the format
    of data returned by a dispatcher or a snapshot.
    """
    MAX_TRADES  = 100       # the maximum number of trades kept by trades data object
    MAX_CANDLES = 10000     # the maximum number of candles kept by candles data object

    def __init__(self):
        super(ChannelData, self).__init__()

    @abstractmethod
    def update(self, data):
        """Updates subscribers with channel updates.
        :param data: Data to be published (sent to subscribers).
        :raises WSException
        """
        pass

    @abstractmethod
    def snapshot(self):
        """Returns the current snapshot of the data.
        The intention is immediately provide the data if available to a user,
        """
        pass

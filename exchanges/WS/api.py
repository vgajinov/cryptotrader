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
    def subscribe(self, **kwargs):
        """Generic method to subscribe to a channel of an exchange.
        :param kwargs: Arbitrary keyword arguments. Depend on the specific exchange.
        """
        return None

    @abstractmethod
    def unsubscribe(self, **kwargs):
        """Generic method to unsubscribe from the channel.
        :param kwargs: Arbitrary keyword arguments. Depend on the specific exchange.
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
        return None

    @abstractmethod
    def subscribe_order_book(self, symbol, update_handler=None, **kwargs):
        """Subscribe to order book channel.
        :param symbol:          A symbol for a ticker (pair).
        :param update_handler:  A callback handler that should handle the asynchronous update of the order book.
        :param kwargs:          Additional parameters that differ between exchanges.
        :raises ExchangeException
        Data is returned by dispatcher as two ordered dictionaries, bids and asks,
        ordered by price from low to high. The format is
           { PRICE : AMOUNT }
        Return type:
           { float : float }
        """
        # TODO - Check if the order should be H -> L
        # TODO - Is it better to return list instead of ordered dict (it would be list of tuples)? Or numpy array???
        return None

    @abstractmethod
    def subscribe_trades(self, symbol, update_handler=None):
        """Subscribe to the channel for trades.
        :param symbol:          A symbol for a ticker (pair).
        :param update_handler:  A callback handler that should handle the asynchronous update of trades.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        :raises ExchangeException
        Data is returned by dispatcher as a list of trades:
            [ [ TIMESTAMP, AMOUNT, PRICE ], ... ]
        Return type:
           [ [int, float, float] ]
        """
        return None

    @abstractmethod
    def subscribe_candles(self, symbol, interval='1m', update_handler=None):
        """Subscribe to the channel fro candles.
        :param symbol:          A symbol for a ticker (pair).
        :param interval         Time interval for a candle.
        :param update_handler:  A callback handler that should handle the asynchronous update of trades.
        :return: A string that represents a stream (channel) identifier. Specific for each exchange.
        :raises ExchangeException
        Data is returned by dispatcher as a list of candles:
           [ TIMESTAMP, OPEN, CLOSE, HIGH, LOW, VOLUME ]
        Return type:
           numpy.array(int, float, float, float, float, float)
        """
        return None


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
        return False

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
        return None

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
        return None

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
        return None


class ChannelData(ABC):
    """Abstract class for channel data."""

    def __init__(self):
        super(ChannelData, self).__init__()

    @abstractmethod
    def _publish(self):
        """Sends channel updates via dispatcher.send call."""
        pass

    @abstractmethod
    def update(self, data):
        """Updates subscribers with channel updates.
        :param data: Data to be published (sent to subscribers).
        """
        pass

    def publish(self):
        """Can be used by a user to explicitly initiate a dispatcher to send the data.
        The intention is to provide a way for subscribers to initialize themselves by
        a data upon subscription and not to have to wait for a channel update to happen
        before doing so.
        """
        self._publish()

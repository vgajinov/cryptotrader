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
        # create the logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger_handler = logging.FileHandler(self.__class__.__name__ + '.log')
        self.logger_handler.setLevel(logging.DEBUG)
        self.logger_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                                  datefmt='%d-%m %H:%M:%S')
        self.logger_handler.setFormatter(self.logger_formatter)
        self.logger.addHandler(self.logger_handler)

    def _stop_logger(self):
        self.logger.removeHandler(self.logger_handler)
        self.logger = None

    # @staticmethod
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def connect(self, info_handler=None):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def subscribe(self, **kwargs):
        return None

    @abstractmethod
    def unsubscribe(self, **kwargs):
        pass

    """
    Subscribe to ticker channel. 
    Data is returned by dispatcher in the following format:
       [ BID, BID_SIZE, ASK, ASK_SIZE, DAY_CHANGE, DAY_CHANGE_PERCENT, LAST_PRICE, VOLUME, HIGH, LOW ]  
    Return type:
       [ all floats ] 
    """

    @abstractmethod
    def subscribe_ticker(self, pair, update_handler=None):
        return None

    # TODO - check if the order should be H -> L
    # TODO - see if it is better to return list instead of ordered dict (it would be list of tuples). Or numpy array???
    """
    Subscribe to order book channel. 
    Data is returned by dispatcher in as two ordered dictionaries, bids and asks,
    ordered by price from low to high. The format is
       { PRICE : AMOUNT }
    Return type:
       { float : float }   
    """

    @abstractmethod
    def subscribe_order_book(self, symbol, update_handler=None, **kwargs):
        return None

    """
    Subscribe to trade channel.
    Data is returned in the form of list of trades:
       [ 
         [ TIMESTAMP, AMOUNT, PRICE ],
         ...
       ]
    Return type:
       [ [int, float, float] ]
    """

    @abstractmethod
    def subscribe_trades(self, symbol, update_handler=None):
        return None

    """
    Subscribe to candles channel.
    Data is returned in the form of list of candles:
       [ TIMESTAMP, OPEN, CLOSE, HIGH, LOW, VOLUME ]
    Return type:
       numpy.array(int, float, float, float, float, float)
    """

    @abstractmethod
    def subscribe_candles(self, symbol, interval='1m', update_handler=None):
        return None

    """
    AUTHENTHICATED CHANNELS
    ------------------------------------------------------------------------
    """

    """
    Authenticate a user 
    """

    @abstractmethod
    def authenticate(self, key=None, secret=None, key_file=None):
        return False

    """
    Subscribe to user orders channel.
    Data is returned in the form of list of orders:
       [ ID, TIMESTAMP, SYMBOL, TYPE, SIDE, PRICE, AMOUNT, FILED%, TOTAL ]
    Return type:
       [ [int, int, string, string, string, float, float, string, float] ]
    """

    @abstractmethod
    def subscribe_user_orders(self, update_handler):
        return None

    """
    Subscribe to user trades channel.
    Data is returned in the form of list of trades:
       [ TIMESTAMP, SYMBOL, TYPE, SIDE, PRICE, AMOUNT, FILLED, TOTAL, STATUS ]
    Return type:
       [ [int, string, string, string, float, float, float, float, string] ]
    """

    @abstractmethod
    def subscribe_user_trades(self, update_handler):
        return None

    """
    Subscribe to balances channel.
    Data is returned in the form of dictionary of balances:
       { currency : balance }
    Return type:
       { string : float }
    """

    @abstractmethod
    def subscribe_balances(self, update_handler):
        return None


"""
Abstract class for channel data 
"""


class ChannelData(ABC):
    def __init__(self):
        super(ChannelData, self).__init__()

    @abstractmethod
    def _publish(self):
        pass

    @abstractmethod
    def update(self, data):
        pass

    def publish(self):
        self._publish()

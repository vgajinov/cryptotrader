# Import built-Ins
import logging
import time
from abc import ABC, abstractmethod
from urllib.parse import urljoin
from os.path import join
# Import third-Party
import requests
# Import internal
from exchanges.REST.response import APIResponse


class RESTClientAPI(ABC):
    """Abstract base class for REST based clients.
    Provides methods to interact with exchange APIs,
    such as sending queries and signing authenticated messages.
    """

    def __init__(self, uri, api_version=None, key=None, secret=None, key_file=None,
                 timeout=5, log=logging.getLogger('RESTClientAPILogger')):
        """Create a REST client object.
        :param uri: string address for api (i.e. https://api.kraken.com/
        :param api_version: version, as required to query an endpoint
        :param key: API access key
        :param secret: API secret
        """
        self._key = key
        self._secret = secret
        if key_file:
            self._load_key(key_file)
        self._uri = uri
        self._version = api_version if api_version else ''
        self.timeout = timeout
        self._log = log
        self._log.debug("Initialized %s client for URI: %s; " % (self.name(), self._uri))


    def __str__(self):
        return self.name()

    @abstractmethod
    def name(self):
        """Return the name of the exchange.
        This is used by the RESTClientFactory and is NOT the name of the class,
        but is defined by the class implementation.
        NOTE: Must be implemented as classmethod or staticmethod for the purpose of logging
        """
        pass

    @staticmethod
    def _nonce():
        """Creates a Nonce value for signature generation
        :return: Nonce value as a string
        """
        return str(round(100000 * time.time()) * 2)

    @staticmethod
    def _api_request(*args, **kwargs):
        """ Wrapper which converts a requests.Response into our custom APIResponse object.
        :param args:
        :param kwargs:
        :return:
        """
        r = requests.request(*args, **kwargs)
        return APIResponse(r)

    def _load_key(self, path):
        """Load key and secret from file.
        :param path: path to file with first two lines for a key and secret respectively
        """
        with open(path, 'r') as f:
            self._key = f.readline().strip()
            self._secret = f.readline().strip()

    def _query(self, method_verb, endpoint, authenticate=False, *args, **kwargs):
        """Makes a query to an exchange. Defaults to unauthenticated query.
        :param method_verb:    valid request type (PUT, GET, POST etc)
        :param endpoint:       endpoint path for the resource to query.
        :param authenticate:   Flag to determine whether or not a signature is required.
        :param args:           Optional args for requests.request()
        :param kwargs:         Optional kwargs for self.sign() and requests.request()
        :return: request.response() object
        """
        if self._version:
            endpoint_path = join(self._version, endpoint)
        else:
            endpoint_path = endpoint

        url = urljoin(self._uri, endpoint_path)
        if authenticate:  # sign off kwargs and url before sending request
            url, request_kwargs = self._sign(url, endpoint, endpoint_path, method_verb, *args, **kwargs)
        else:
            request_kwargs = kwargs

        self._log.debug("Making a request to: %s, kwargs: %s", url, request_kwargs)
        req = self._api_request(method_verb, url, timeout=self.timeout, **request_kwargs)
        self._log.debug("%s request made to %s, with body %s. Status code %s",
                        req.request.method, req.request.url, req.request.body, req.status_code)
        return req

    @abstractmethod
    def _sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        """Dummy Signature creation method. Override this in child.
        :param url: self.uri + self.version + endpoint
        :param endpoint: api endpoint to call (i.e. 'Depth')
        :param endpoint_path: self.version + endpoint (i.e. '0/Depth')
        :param method_verb: valid request type (PUT, GET, POST etc)
        :return: A tuple of url as a string and a dictionary of parameters
        URL is required to be returned, as some Signatures use the url for
        sig generation, and api calls made must match the address exactly.
        """
        url = self._uri
        return url, {'params': {'test_param': "authenticated_test_user"}}


    # public endpoints
    # ------------------------------------------------------------------

    @abstractmethod
    def ping(self):
        pass

    @abstractmethod
    def quote_currencies(self):
        """Get a list of base (quote) currencies.
        :return: List of quote currencies : ['USD', 'BTC', ...]
        """
        pass

    @abstractmethod
    def symbols(self):
        """Get a list of all the symbols supported by an exchange.
        :return: List of symbols : ['BTCUSD', "LTCBTC', ...]
        """
        pass

    @abstractmethod
    def symbols_details(self):
        """Get info about symbols.
        :return: Non-standard dictionaries per symbol. The minimum subset of keys should be:
                    { 'precision', 'minAmount' }
        """
        pass

    @abstractmethod
    def candle_intervals(self):
        """Get the list of valid candle intervals (exchange specific).
        :return: List of intervals : ['1m','3m','5m', ... ]
        """
        pass

    @abstractmethod
    def ticker(self, symbol, **kwargs):
        """Get a ticker for a given symbol.
        :param symbol:  A symbol (pair) for a ticker.
        :param kwargs:  Additional keyword arguments.
        :return: List of ticker data.
        The format for the ticker data is:
            [bidPrice, askPrice, high, low, lastPrice, volume, priceChange, priceChangePercent]
        """
        pass

    @abstractmethod
    def all_tickers(self,**kwargs):
        """Get all tickers.
        :param kwargs:  Additional keyword arguments.
        :return: Dictionary of symbol:ticker pairs.
        { symbol : [bidPrice, askPrice, high, low, lastPrice, volume, priceChange, priceChangePercent] }
        """
        pass

    @abstractmethod
    def order_book(self, symbol, **kwargs):
        """Get order book.
        :param symbol:  A symbol (pair) for the order book query.
        :param kwargs:  Exchange specific additional parameters.
        :return: A dictionary with bids and asks in the form of lists
                    { 'bids' : [ [price, amount], ...] ]
                      'asks' : [ [price, amount], ...] ] }
        """
        pass

    @abstractmethod
    def trades(self, symbol, **kwargs):
        """Get the recen ttrades for a given symbol.
        :param symbol:  A symbol (pair) to query for info about trades.
        :param kwargs:  Exchange specific additional parameters
        :return: A list of trade data:
                    [ [timestamp, price, amount, type='buy' or 'sell'], ... ]
        """
        pass

    @abstractmethod
    def candles(self, symbol, interval='1m', **kwargs):
        """Get candle data for a given symbol and specified candle interval.
        :param symbol:    A symbol (pair) to query for candle data.
        :param interval:  Time interval for a candle.
        :param kwargs:    Exchange specific additional parameters.
        :return: List of candles data:
                    [ [timestamp, open, high, low, close, volume], ... ]
        """
        pass

    @abstractmethod
    def historical_candles(self, symbol, interval, start_time, end_time, **kwargs):
        """Get historical candle data fro a given time period.
        :param symbol:      A symbol (pair) to query for candle history.
        :param interval:    Time interval for a candle.
        :param start_time:  Start time of the history period.
        :param end_time:    End time of the history period.
        :param kwargs:      Exchange specific additional parameters.
        :return: List of candles for the time period between startTime and endTime
        """
        pass


    # private endpoints
    # ------------------------------------------------------------------

    @abstractmethod
    def place_market_order(self, side, symbol, size, **kwargs):
        """Place order to execute at a current market price.
        :param side:    BUY or SELL string.
        :param symbol:  The symbol for which we are placing an order.
        :param size:    The amount of an order to place.
        :param kwargs:  Exchange specific additional parameters.
        :return:
        """
        pass

    @abstractmethod
    def place_limit_order(self, side, symbol, size, price, **kwargs):
        """Place order to execute at a given price.
        :param side:    BUY or SELL string.
        :param symbol:  The symbol for which we are placing an order.
        :param size:    The amount of an order to place.
        :param price:   The requested price for the order.
        :param kwargs:  Exchange specific additional parameters.
        :return:
        """
        pass

    @abstractmethod
    def order(self, order_id, symbol, **kwargs):
        """Query a given order.
        :param order_id:  The id of an order on the exchange.
        :param symbol:    The symbol used by an order.
        :param kwargs:    Exchange specific additional parameters.
        :return:
        """
        pass

    @abstractmethod
    def open_orders(self, **kwargs):
        """Get all open orders.
        :param kwargs:  Exchange specific additional parameters.
        :return:
        """
        pass

    @abstractmethod
    def all_orders(self, symbol, **kwargs):
        """Get all orders for a given symbol.
        :param symbol:  A trading symbol (pair).
        :param kwargs:  Exchange specific additional parameters.
        :return:
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id, symbol, **kwargs):
        """Cancel an order.
        :param order_id:  An id of an order to cancel.
        :param symbol:    A trading symbol (pair).
        :param kwargs:    Exchange specific additional parameters.
        :return:
        """
        pass

    @abstractmethod
    def my_trades(self, symbol, **kwargs):
        """Get all trades executed by a user for a given symbol.
        :param symbol:  A trading symbol (pair).
        :param kwargs:  Exchange specific additional parameters.
        :return:
        """
        pass

    @abstractmethod
    def balance(self, **kwargs):
        """Get user balances.
        :param kwargs:  Exchange specific parameters.
        :return:
        """
        pass


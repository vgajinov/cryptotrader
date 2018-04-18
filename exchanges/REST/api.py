# Import Built-Ins
import logging
import time
from abc import ABCMeta, abstractmethod
from urllib.parse import urljoin
from os.path import join

# Import Third-Party
import requests

# Import Homebrew
from exchanges.REST.response import APIResponse


"""
ABC for Exchange APIs
"""
class RESTClientAPI(metaclass=ABCMeta):
   """
   Base Class for API ojects. Provides basic methods to interact
   with exchange APIs, such as sending queries and signing messages to pass
   authentication.
   """

   def __init__(self, uri, api_version=None, key=None, secret=None, key_file=None,
                timeout=5, log=logging.getLogger(__name__)):
      """
      Create API Client object.
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


   '''
   PROTECTED METHODS
   '''

   def _load_key(self, path):
      """
      Load key and secret from file.
      :param path: path to file with first two lines are key, secret respectively
      """
      with open(path, 'r') as f:
         self._key = f.readline().strip()
         self._secret = f.readline().strip()

   def _nonce(self):
      """
      Creates a Nonce value for signature generation
      :return:
      """
      return str(round(100000 * time.time()) * 2)

   @staticmethod
   def _api_request(*args, **kwargs):
      """
      Wrapper which converts a requests.Response into our custom APIResponse
      object
      :param args:
      :param kwargs:
      :return:
      """
      r = requests.request(*args, **kwargs)
      return APIResponse(r)

   @abstractmethod
   def _sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
      """
      Dummy Signature creation method. Override this in child.
      URL is required to be returned, as some Signatures use the url for
      sig generation, and api calls made must match the address exactly.
      param url: self.uri + self.version + endpoint (i.e https://api.kraken/0/Depth)
      param endpoint: api endpoint to call (i.e. 'Depth')
      param endpoint_path: self.version + endpoint (i.e. '0/Depth')
      param method_verb: valid request type (PUT, GET, POST etc)
      param return:
      """
      url = self._uri

      return url, {'params': {'test_param': "authenticated_chimichanga"}}

   def _query(self, method_verb, endpoint, authenticate=False, *args, **kwargs):
      """
      Queries exchange using given data. Defaults to unauthenticated query.
      :param method_verb: valid request type (PUT, GET, POST etc)
      :param endpoint: endpoint path for the resource to query, sans the url &
                       API version (i.e. '/btcusd/ticker/').
      :param authenticate: Bool to determine whether or not a signature is
                           required.
      :param args: Optional args for requests.request()
      :param kwargs: Optional Kwargs for self.sign() and requests.request()
      :return: request.response() obj
      """
      if self._version:
         endpoint_path = join(self._version, endpoint)
      else:
         endpoint_path = endpoint

      url = urljoin(self._uri, endpoint_path)
      if authenticate:  # sign off kwargs and url before sending request
         url, request_kwargs = self._sign(url, endpoint, endpoint_path,
                                         method_verb, *args, **kwargs)
      else:
         request_kwargs = kwargs

      self._log.debug("Making request to: %s, kwargs: %s", url, request_kwargs)
      r = self._api_request(method_verb, url, timeout=self.timeout,
                           **request_kwargs)
      self._log.debug("%s request made to %s, with body %s. Status code %s",
                      r.request.method, r.request.url, r.request.body, r.status_code)
      return r


   '''
   PUBLIC INTERFACE
   '''

   @abstractmethod
   def name(self):
      pass

   # public endpoints
   # ------------------------------------------------------------------

   @abstractmethod
   def ping(self):
      pass

   @abstractmethod
   def symbols(self):
      pass

   @abstractmethod
   def ticker(self, pair, **kwargs):
      pass

   @abstractmethod
   def all_tickers(self,**kwargs):
      pass

   @abstractmethod
   def order_book(self, pair, **kwargs):
      pass

   @abstractmethod
   def trades(self, pair, **kwargs):
      pass

   @abstractmethod
   def candles(self, pair, interval='1m', **kwargs):
      pass

   @abstractmethod
   def historical_candles(self, pair, interval, startTime, endTime, **kwargs):
      pass


   # private endpoints
   # ------------------------------------------------------------------

   @abstractmethod
   def place_market_order(self, side, pair, size, **kwargs):
      pass

   @abstractmethod
   def place_limit_order(self, side, pair, size, price, **kwargs):
      pass

   @abstractmethod
   def order(self, order_id, symbol, **kwargs):
      pass

   @abstractmethod
   def open_orders(self, **kwargs):
      pass

   @abstractmethod
   def all_orders(self, symbol, **kwargs):
      pass

   @abstractmethod
   def cancel_order(self, order_id, symbol, **kwargs):
      pass

   @abstractmethod
   def my_trades(self, symbol, **kwargs):
      pass

   @abstractmethod
   def balance(self, **kwargs):
      pass


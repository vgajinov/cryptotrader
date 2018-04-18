# Import Built-ins
import logging
import json
import hashlib
import hmac
import base64

# Import Homebrew
from exchanges.REST.api import APIClient
from exchanges.REST.response import return_api_response
from exchanges.REST.formatterBase import Formatter

log = logging.getLogger(__name__)


# ===============================================================================
#    Bitfinex response formatter
# ===============================================================================

class BtfxFormatter(Formatter):

   @staticmethod
   def ticker(data, *args, **kwargs):
      return [ data['bid'], data['ask'], data['high'], data['low'], data['last_price'],
               data['volume'], None, None ]





   @staticmethod
   def order_book(data, *args, **kwargs):
      return { 'bids' : [ [i['price'], i['amount']] for i in data['bids']],
               'asks' : [ [i['price'], i['amount']] for i in data['asks']] }

   @staticmethod
   def trades(data, *args, **kwargs):
      return [ [t['timestamp'], t['price'], t['amount'], t['type']] for t in data]



   @staticmethod
   def order(data, *args, **kwargs):
      try:
         return data['order_id']
      except KeyError:
         return False

   @staticmethod
   def cancel(data, *args, **kwargs):
      return True if 'message' not in data else False

   @staticmethod
   def order_status(data, *args, **kwargs):
      return data['is_live']

# alias BitfinexFormatter
fmt = BtfxFormatter


# ===============================================================================
#    Bitfinex API client
# ===============================================================================

class BitfinexREST(APIClient):
   def __init__(self, key=None, secret=None, api_version='v1',
                url='https://api.bitfinex.com', timeout=5, log=log):
      super(BitfinexREST, self).__init__(url, api_version=api_version,
                                         key=key, secret=secret,
                                         timeout=timeout, log=log)

   def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
      try:
         req = kwargs['params']
      except KeyError:
         req = {}
      if self.version == 'v1':
         req['request'] = endpoint_path
         req['nonce'] = self.nonce()

         js = json.dumps(req)
         data = base64.standard_b64encode(js.encode('utf8'))
      else:
         data = '/api/' + endpoint_path + self.nonce() + json.dumps(req)
      h = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384)
      signature = h.hexdigest()
      headers = {"X-BFX-APIKEY": self.key,
                 "X-BFX-SIGNATURE": signature,
                 "X-BFX-PAYLOAD": data}
      if self.version == 'v2':
         headers['content-type'] = 'application/json'

      return url, {'headers': headers}


# ===============================================================================
#    Bitfinex interface
# ===============================================================================

class Bitfinex(BitfinexREST):
   def __init__(self, key='', secret='', key_file=''):
      super(Bitfinex, self).__init__(key, secret)
      if key_file:
         self.load_key(key_file)

   def public_query(self, endpoint, **kwargs):
      return self.query('GET', endpoint, **kwargs)

   def private_query(self, endpoint, **kwargs):
      return self.query('POST', endpoint, authenticate=True, **kwargs)


   """
   Standardized Methods
   """

   @return_api_response(fmt.ticker, log)
   def ticker(self, pair, **kwargs):
      return self.public_query('pubticker/%s' % pair, params=kwargs)

   def all_tickers(self):
      return { symbol:self.ticker(symbol) for symbol in self.symbols() }

   @return_api_response(fmt.order_book, log)
   def order_book(self, pair, **kwargs):
      return self.public_query('book/%s' % pair, params=kwargs)

   @return_api_response(fmt.trades, log)
   def trades(self, pair, **kwargs):
      return self.public_query('trades/%s' % pair, params=kwargs)




   def _place_order(self, pair, size, price, side, replace, **kwargs):
      q = {'symbol': pair, 'amount': size, 'price': price, 'side': side,
           'type': 'exchange limit'}
      q.update(kwargs)
      if replace:
         return self.private_query('order/cancel/replace', params=q)
      else:
         return self.private_query('order/new', params=q)

   @return_api_response(fmt.order, log)
   def bid(self, pair, price, size, replace=False, **kwargs):
      return self._place_order(pair, size, price, 'buy', replace=replace,
                               **kwargs)

   @return_api_response(fmt.order, log)
   def ask(self, pair, price, size, replace=False, **kwargs):
      return self._place_order(pair, str(size), str(price), 'sell',
                               replace=replace, **kwargs)

   @return_api_response(fmt.cancel, log)
   def cancel_order(self, order_id, all=False, **kwargs):

      q = {'order_id': int(order_id)}
      q.update(kwargs)
      if not all:
         return self.private_query('order/cancel', params=q)
      else:
         endpoint = 'order/cancel/all'
         return self.private_query(endpoint)

   @return_api_response(fmt.order_status, log)
   def order(self, order_id, **kwargs):
      q = {'order_id': order_id}
      q.update(kwargs)
      return self.private_query('order/status', params=q)

   @return_api_response(fmt.balance, log)
   def balance(self, **kwargs):
      return self.private_query('balances', params=kwargs)

   @return_api_response(fmt.withdraw, log)
   def withdraw(self, size, tar_addr, **kwargs):
      q = {'withdraw_type': kwargs.pop('withdraw_type'),
           'walletselected': kwargs.pop('walletselected'),
           'amount': size, 'address': tar_addr}
      q.update(kwargs)
      return self.private_query('withdraw', params=q)

   @return_api_response(fmt.deposit, log)
   def deposit_address(self, **kwargs):
      q = {}
      q.update(kwargs)
      return self.private_query('deposit/new', params=kwargs)


   """
   Exchange Specific Methods
   """

   @return_api_response(None, log)
   def symbols(self, details=False):
      if details:
         return self.public_query('symbols_details')
      else:
         return self.public_query('symbols')



   @return_api_response(None, log)
   def statistics(self, pair):
      return self.public_query('stats/%s' % pair)

   @return_api_response(None, log)
   def funding_book(self, currency, **kwargs):
      return self.public_query('lendbook/%s' % currency, params=kwargs)

   @return_api_response(None, log)
   def lends(self, currency, **kwargs):
      return self.public_query('lends/%s' % currency, params=kwargs)



   @return_api_response(None, log)
   def fees(self):
      return self.private_query('account_infos')

   @return_api_response(None, log)
   def orders(self):
      return self.private_query('orders')

   @return_api_response(None, log)
   def balance_history(self, currency, **kwargs):
      q = {'currency': currency}
      q.update(kwargs)
      return self.private_query('history/movements', params=q)

   @return_api_response(None, log)
   def trade_history(self, pair, since, **kwargs):
      q = {'symbol': pair, 'timestamp': since}
      q.update(kwargs)
      return self.private_query('mytrades', params=q)

   @return_api_response(None, log)
   def positions(self):
      return self.private_query('positions')

   @return_api_response(None, log)
   def credits(self):
      return self.private_query('credits')

   @return_api_response(None, log)
   def new_offer(self, currency, amount, rate, period, direction, **kwargs):
      q = {'currency': currency, 'amount': amount, 'rate': rate, 'period': period, 'period': direction}
      q.update(kwargs)
      return self.private_query('offer/new', params=q)

   @return_api_response(None, log)
   def cancel_offer(self, id, **kwargs):
      q = {'id': id}
      q.update(kwargs)
      return self.private_query('offer/cancel', params=q)

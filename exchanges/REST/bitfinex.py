# Import Built-ins
import logging
import json
import hashlib
import hmac
import base64

# Import Homebrew
from exchanges.REST.api import RESTClientAPI
from exchanges.REST.response import return_api_response
from exchanges.REST.formatterBase import Formatter


# create the logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logger_handler = logging.FileHandler('BitfinexRESTClient.log')
logger_handler.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d-%m %H:%M:%S')
logger_handler.setFormatter(logger_formatter)
log.addHandler(logger_handler)


# ===============================================================================
#    Bitfinex response formatter
# ===============================================================================

class BitfinexFormatter(Formatter):


   @staticmethod
   def echo(data, *args, **kwargs):
      return data

   @staticmethod
   def symbols(data, *args, **kwargs):
      return  data

   @staticmethod
   def symbols_details(data, *args, **kwargs):
      return {d['pair'].upper(): {'precision': d['price_precision'],
                                  'minAmount': d['minimum_order_size'],
                                  'maxAmount': d['maximum_order_size']}
              for d in data}

   @staticmethod
   def ticker(data, *args, **kwargs):
      return [ data[0], data[2], data[8], data[9], data[6], data[7], data[4], data[5] ]

   @staticmethod
   def tickers(data, *args, **kwargs):
      return { d[0][1:].upper():[d[1], d[3], d[9], d[10], d[7], d[8], d[5], 100*d[6]] for d in data }

   @staticmethod
   def order_book(data, *args, **kwargs):
      return { 'bids' : [ [i['price'], i['amount']] for i in data['bids']],
               'asks' : [ [i['price'], i['amount']] for i in data['asks']] }

   @staticmethod
   def trades(data, *args, **kwargs):
      return [ [t['timestamp'], t['price'], t['amount'], t['type']] for t in data]

   @staticmethod
   def candles(data, *args, **kwargs):
      return reversed([ [d[0], d[1], d[3], d[4], d[2], d[5]] for d in data])

   @staticmethod
   def order(data, *args, **kwargs):
      try:
         return { 'symbol': data['symbol'],
                  'orderId': data['id'],
                  'price': data['price'],
                  'amount': data['original_amount'],
                  'filled': data['executed_amount'],
                  'type': 'LIMIT' if data['type']=='exchange limit' else
                          'MARKET' if data['type']=='exchange market' else
                          'STOP-LOSS' if data['type'] == 'exchange stop' else
                          'TRAILING STOP-LOSS',
                  'side': data['side'],
                  'timestamp': data['timestamp'],
                  'status': 'LIVE' if data['is_live'] else
                            'CANCELED' if data['is_cancelled'] else
                            'EXECUTED'
                 }
      except KeyError:
         return False

   @staticmethod
   def order_status(data, *args, **kwargs):
      try:
         return { 'symbol': data['symbol'],
                  'orderId': data['id'],
                  'price': data['price'],
                  'stopPrice': data['price'],
                  'amount': data['original_amount'],
                  'filled': data['executed_amount'],
                  'type': 'LIMIT' if data['type']=='exchange limit' else
                          'MARKET' if data['type']=='exchange market' else
                          'STOP-LOSS' if data['type'] == 'exchange stop' else
                          'TRAILING STOP-LOSS',
                  'side': data['side'],
                  'timestamp': data['timestamp'],
                  'status': 'LIVE' if data['is_live'] else
                            'CANCELED' if data['is_cancelled'] else
                            'EXECUTED'
                 }
      except KeyError:
         return False

   @staticmethod
   def multi_order_status(data, *args, **kwargs):
         return [ BitfinexFormatter.order_status(d) for d in data]

   @staticmethod
   def cancel(data, *args, **kwargs):
      if type(data) is dict:
         if 'is_cancelled' in data or 'result' in data:
            return True
      return False

   @staticmethod
   def my_trades(data, *args, **kwargs):
      return [{'orderId': d['order_id'], 'price': d['price'], 'amount': d['amount'],
               'fee': d['fee_amount'], 'feeAsset': d['fee_currency'], 'side': d['type']} for d in data]

   @staticmethod
   def balance(data, *args, **kwargs):
      return { d['currency'] : d['available'] for d in data if d['type']=='exchange'}


# alias BitfinexFormatter
fmt = BitfinexFormatter


# ===============================================================================
#    Bitfinex REST API client
# ===============================================================================

class BitfinexRESTClient(RESTClientAPI):
   def __init__(self, key=None, secret=None, key_file=None, api_version=None,
                url='https://api.bitfinex.com', timeout=5, log=log):
      super(BitfinexRESTClient, self).__init__(url, api_version=api_version, key=key, secret=secret,
                                               key_file=key_file, timeout=timeout, log=log)


   @staticmethod
   def name():
      return 'Bitfinex'


   def _sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
      data = None
      try:
         req = kwargs['params']
      except KeyError:
         req = {}
      if 'v1' in endpoint:
         req['request'] = endpoint_path
         req['nonce'] = self._nonce()
         js = json.dumps(req)
         data = base64.standard_b64encode(js.encode('utf-8'))
      else:
         data = '/api/' + endpoint_path + self._nonce() + json.dumps(req)


      h = hmac.new(self._secret.encode('utf-8'), data, hashlib.sha384)
      signature = h.hexdigest()

      headers = {
         "X-BFX-APIKEY": self._key,
         "X-BFX-SIGNATURE": signature,
         "X-BFX-PAYLOAD": data
      }
      if 'v2' in endpoint:
         headers['content-type'] = 'application/json'

      return url, {'headers': headers}


   def _public_query(self, endpoint, **kwargs):
      return self._query('GET', endpoint, **kwargs)

   def _private_query(self, endpoint, **kwargs):
      return self._query('POST', endpoint, authenticate=True, **kwargs)


   """
   Standardized Methods
   """

   # public
   # ------------------------------------------------------------------

   def ping(self):
      return self.status()[0] == 1

   def quote_currencies(self):
      return ['USD', 'BTC', 'EUR', 'JPY', 'GBP', 'ETH']

   @return_api_response(fmt.symbols, log)
   def symbols(self):
      return self._public_query('/v1/symbols')

   @classmethod
   def candle_intervals(self):
      return ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D', '1M']

   @return_api_response(fmt.ticker, log)
   def ticker(self, pair, **kwargs):
      return self._public_query('/v2/ticker/t%s' % pair.upper(), params=kwargs)

   def all_tickers(self, **kwargs):
      symbols = self.symbols()
      return self.tickers(symbols)

   @return_api_response(fmt.order_book, log)
   def order_book(self, pair, **kwargs):
      return self._public_query('/v1/book/%s' % pair, params=kwargs)

   @return_api_response(fmt.trades, log)
   def trades(self, pair, **kwargs):
      return self._public_query('/v1/trades/%s' % pair, params=kwargs)

   @return_api_response(fmt.candles, log)
   def candles(self, pair, interval='1m', **kwargs):
      if interval not in self.candle_intervals():
         interval ='1m'
      return self._public_query('/v2/candles/trade:%s:t%s/hist' % (interval, pair.upper()), params=kwargs)

   def historical_candles(self, pair, interval, startTime, endTime, **kwargs):
      return self.candles(pair, interval, start=startTime, end=endTime, **kwargs)



   # MARGIN ORDERS: “market” / “limit” / “stop” / “trailing-stop” / “fill-or-kill”
   # NORMAL ORDERS: “exchange market” / “exchange limit” / “exchange stop” /
   #                “exchange trailing-stop” / “exchange fill-or-kill”

   def _place_order(self, type, side, pair, size, price, stopPrice, **kwargs):
      q = {'type': type, 'side': side.lower(), 'symbol': pair.upper(), 'amount': str(size)}
      if price:
         q['price'] = format(price, '.8f')
      if stopPrice:
         q['stopPrice'] = format(stopPrice, '.8f')
      q.update(kwargs)
      return self._private_query('/v1/order/new', params=q)

   @return_api_response(fmt.order, log)
   def place_market_order(self, side, pair, size, **kwargs):
      # price should be a random positive number, we use 1
      return self._place_order('exchange market', side, pair, size, 1, None, **kwargs)

   @return_api_response(fmt.order, log)
   def place_limit_order(self, side, pair, size, price, **kwargs):
      return self._place_order('exchange limit', side, pair, size, price, None, **kwargs)




   @return_api_response(fmt.order_status, log)
   def order(self, order_id, symbol, **kwargs):
      q = {'order_id': order_id}
      q.update(kwargs)
      return self._private_query('/v1/order/status', params=q)

   @return_api_response(fmt.multi_order_status, log)
   def open_orders(self, **kwargs):
      return self._private_query('/v1/orders')

   @return_api_response(fmt.multi_order_status, log)
   def all_orders(self, symbol, **kwargs):
      q= {}
      q.update(kwargs)
      return self._private_query('/v1/orders/hist', params=q)

   @return_api_response(fmt.cancel, log)
   def cancel_order(self, order_id, symbol, **kwargs):
      q = {'order_id': int(order_id)}
      q.update(kwargs)
      return self._private_query('/v1/order/cancel', params=q)


   @return_api_response(fmt.my_trades, log)
   def my_trades(self, symbol, **kwargs):
      q = {'symbol': symbol}
      q.update(kwargs)
      return self._private_query('/v1/mytrades', params=q)

   @return_api_response(fmt.balance, log)
   def balance(self, **kwargs):
      return self._private_query('/v1/balances', params=kwargs)



   """
   Exchange Specific Methods
   """

   @return_api_response(fmt.echo, log)
   def status(self):
      return self._public_query('/v2/platform/status')

   @return_api_response(fmt.symbols_details, log)
   def symbols_details(self):
      return self._public_query('/v1/symbols_details')

   @return_api_response(fmt.tickers, log)
   def tickers(self, pairs, **kwargs):
      pairList = ','.join( ['t'+ p.upper() for p in pairs] )
      return self._public_query('/v2/tickers?symbols=%s' % pairList, params=kwargs)



   @return_api_response(fmt.order, log)
   def place_stoploss_order(self, side, pair, size, stopPrice, **kwargs):
      return self._place_order('exchange stop', side, pair, size, stopPrice, None, **kwargs)

   @return_api_response(fmt.order, log)
   def place_trailing_stoploss_order(self, side, pair, size, stopPrice, **kwargs):
      return self._place_order('exchange trailing-stop', side, pair, size, stopPrice, None, **kwargs)

   @return_api_response(fmt.cancel, log)
   def cancel_multiple_orders(self, order_ids, **kwargs):
      q = {'order_ids': order_ids}
      q.update(kwargs)
      return self._private_query('/v1/order/cancel/multi', params=q)

   @return_api_response(fmt.cancel, log)
   def cancel_all_orders(self, **kwargs):
      return self._private_query('/v1/order/cancel/all')





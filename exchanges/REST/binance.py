# Import Built-ins
import logging
import hashlib
import hmac
import time

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
#    Binance response formatter
# ===============================================================================

class BinanceFormatter(Formatter):

   @staticmethod
   def server_time(data, *args, **kwargs):
      return data['serverTime']

   @staticmethod
   def symbols(data, *args, **kwargs):
      return  [ d['symbol'] for d in data['symbols'] ]

   @staticmethod
   def symbols_details(data, *args, **kwargs):
      return {d['symbol'].upper(): {'precision': d['baseAssetPrecision'],
                                    'minAmount': d['filters'][1]['minQty'],
                                    'baseAsset': d['baseAsset'],
                                    'quoteAsset': d['quoteAsset'],
                                    'quotePrecision': d['quotePrecision'],
                                    'orderTypes': d['orderTypes'],
                                    'minPrice': d['filters'][0]['minPrice']}
              for d in data['symbols']}


   @staticmethod
   def ticker(data, *args, **kwargs):
      return [data['bidPrice'], data['askPrice'], data['highPrice'], data['lowPrice'], data['lastPrice'],
              data['volume'], data['priceChange'], data['priceChangePercent']]

   @staticmethod
   def tickers(data, *args, **kwargs):
      return {d['symbol']: [d['bidPrice'], d['askPrice'], d['highPrice'], d['lowPrice'], d['lastPrice'],
                            d['volume'], d['priceChange'], d['priceChangePercent']] for d in data}

   @staticmethod
   def order_book(data, *args, **kwargs):
      return { 'bids' : [ i[:2] for i in data['bids']],
               'asks' : [ i[:2] for i in data['asks']] }

   @staticmethod
   def trades(data, *args, **kwargs):
      return [ [t['time'], t['price'], t['qty'], 'sell' if t['isBuyerMaker'] else 'buy'] for t in data]

   @staticmethod
   def candles(data, *args, **kwargs):
      return [ d[:6] for d in data]
      # we could find the rest of data useful: number of trades, buy volume, sell volume

   @staticmethod
   def order(data, *args, **kwargs):
      # Order status can be one of these:
      #   NEW, PARTIALLY_FILLED, FILLED, CANCELED, REJECTED, EXPIRED
      try:
         return { 'symbol': data['symbol'],
                  'orderId': data['orderId'],
                  'price': data['price'],
                  'amount': data['origQty'],
                  'filled': data['executedQty'],
                  'type': data['type'],
                  'side': data['side'],
                  'timestamp': data['transactTime'],
                  'status': 'LIVE' if data['status']=='NEW' or data['status']=='PARTIALLY_FILLED' else
                            'EXECUTED' if data['status']=='FILLED' else
                            'CANCELED'
                 }
      except KeyError:
         return False


   @staticmethod
   def order_status(data, *args, **kwargs):
      try:
         return { 'symbol': data['symbol'],
                  'orderId': data['orderId'],
                  'price': data['price'],
                  'stopPrice': data['stopPrice'],
                  'amount': data['origQty'],
                  'filled': data['executedQty'],
                  'type': data['type'],
                  'side': data['side'],
                  'timestamp': data['time'],
                  'status': 'LIVE' if data['status']=='NEW' or data['status']=='PARTIALLY_FILLED' else
                            'EXECUTED' if data['status']=='FILLED' else
                            'CANCELED'
                 }
      except KeyError:
         return False

   @staticmethod
   def multi_order_status(data, *args, **kwargs):
         return [ BinanceFormatter.order_status(d) for d in data]

   @staticmethod
   def cancel(data, *args, **kwargs):
      return True

   @staticmethod
   def balance(data, *args, **kwargs):
      try:
         tmp = data['balances']
      except KeyError as e:
         print('BAD RESPONSE')
         return {}
      return { d['asset'] : d['free'] for d in data['balances'] }

   @staticmethod
   def my_trades(data, *args, **kwargs):
      return [ {'orderId':d['orderId'], 'price':d['price'], 'amount':d['qty'],
                'fee':d['commission'], 'feeAsset':d['commissionAsset'],
                'side': 'buy' if d['isBuyer'] else 'sell'} for d in data ]

   @staticmethod
   def historical_trades(data, *args, **kwargs):
      return [ [t['time'], t['price'], t['qty'], 'sell' if t['isBuyerMaker'] else 'buy'] for t in data]


# alias for the formatter
fmt = BinanceFormatter


# ===============================================================================
#    Binance REST API client
# ===============================================================================


class BinanceRESTClient(RESTClientAPI):
   def __init__(self, key=None, secret=None, key_file=None, api_version=None,
                url='https://api.binance.com', timeout=5, log=log):
      super(BinanceRESTClient, self).__init__(url, api_version=api_version, key=key, secret=secret,
                                              key_file=key_file, timeout=timeout, log=log)


   @staticmethod
   def name():
      return 'Binance'


   def _sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
      try:
         req = kwargs['params']
      except KeyError:
         req = {}

      # Convert params to a list with signature as last element
      params = []
      for key, value in req.items():
         params.append((key, value))

      # add recieve window time to compensate for clocks being out of sync
      params.append(('recvWindow', 60000))
      # add timestamp (required)
      params.append( ('timestamp', int((time.time()) * 1000)) )

      # generate  and add signature
      query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in params])
      h = hmac.new(self._secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
      signature = h.hexdigest()
      params.append(('signature', signature))

      headers = {'Accept': 'application/json',
                 'User-Agent': 'binance/python',
                 'X-MBX-APIKEY': self._key}

      return url, {'headers': headers, 'params': params}


   def _public_query(self, endpoint, **kwargs):
      return self._query('GET', endpoint, **kwargs)

   def _private_query(self, method, endpoint, **kwargs):
      return self._query(method, endpoint, authenticate=True, **kwargs)


   """
   Standardized Methods
   """

   # public
   # ------------------------------------------------------------------

   def ping(self):
      return self._public_query('/api/v1/ping').ok

   def quote_currencies(self):
      return ['BTC', 'ETH', 'BNB', 'USDT']

   @return_api_response(fmt.symbols, log)
   def symbols(self):
      return self._public_query('/api/v1/exchangeInfo')

   @return_api_response(fmt.symbols_details, log)
   def symbols_details(self):
      return self._public_query('/api/v1/exchangeInfo')

   @classmethod
   def candle_intervals(self):
      return ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']

   @return_api_response(fmt.ticker, log)
   def ticker(self, pair, **kwargs):
      return self._public_query('/api/v1/ticker/24hr?symbol=%s' % pair.upper(), params=kwargs)

   @return_api_response(fmt.tickers, log)
   def all_tickers(self, **kwargs):
      return self._public_query('/api/v1/ticker/24hr', params=kwargs)

   @return_api_response(fmt.order_book, log)
   def order_book(self, pair, **kwargs):
      return self._public_query('/api/v1/depth?symbol=%s' % pair.upper(), params=kwargs)

   @return_api_response(fmt.trades, log)
   def trades(self, pair, **kwargs):
      return self._public_query('/api/v1/trades?symbol=%s' % pair.upper(), params=kwargs)

   @return_api_response(fmt.candles, log)
   def candles(self, pair, interval='1m', **kwargs):
      if interval not in self.candle_intervals():
         interval ='1m'
      return self._public_query('/api/v1/klines?symbol=%s&interval=%s' % (pair.upper(), interval), params=kwargs)

   def historical_candles(self, pair, interval, startTime, endTime, **kwargs):
      return self.candles(pair, interval, startTime=startTime, endTime=endTime, **kwargs)

   # private
   # ------------------------------------------------------------------

   # Order types:  LIMIT, MARKET, STOP_LOSS, STOP_LOSS_LIMIT,
   #               TAKE_PROFIT, TAKE_PROFIT_LIMIT, LIMIT_MAKER

   def _place_order(self, type, side, pair, size, price, stopPrice, **kwargs):
      q = {'type': type, 'side': side.upper(), 'symbol': pair.upper(), 'quantity': size}
      if price:
         q['price'] = format(price, '.8f')
      if stopPrice:
         q['stopPrice'] = format(stopPrice, '.8f')

      q.update(kwargs)
      return self._private_query('POST', '/api/v3/order', params=q)

   @return_api_response(fmt.order, log)
   def place_market_order(self, side, pair, size, **kwargs):
      return self._place_order('MARKET', side, pair, size, None, None, **kwargs)

   @return_api_response(fmt.order, log)
   def place_limit_order(self, side, pair, size, price, **kwargs):
      return self._place_order('LIMIT', side, pair, size, price, None, timeInForce='GTC', **kwargs)


   @return_api_response(fmt.order_status, log)
   def order(self, order_id, symbol, **kwargs):
      q = {'symbol': symbol, 'orderId': int(order_id)}
      q.update(kwargs)
      return self._private_query('GET', '/api/v3/order', params=q)

   @return_api_response(fmt.multi_order_status, log)
   def open_orders(self, **kwargs):
      q = {}
      q.update(kwargs)
      return self._private_query('GET', '/api/v3/openOrders', params=q)

   @return_api_response(fmt.multi_order_status, log)
   def all_orders(self, symbol, **kwargs):
      q = {'symbol': symbol}
      q.update(kwargs)
      return self._private_query('GET', '/api/v3/allOrders', params=q)

   @return_api_response(fmt.cancel, log)
   def cancel_order(self, order_id, symbol, **kwargs):
      q = {'symbol': symbol, 'orderId': int(order_id)}
      q.update(kwargs)
      return self._private_query('DELETE', '/api/v3/order', params=q)


   @return_api_response(fmt.my_trades, log)
   def my_trades(self, symbol, **kwargs):
      q = {'symbol': symbol}
      q.update(kwargs)
      return self._private_query('GET', '/api/v3/myTrades', params=q)

   @return_api_response(fmt.balance, log)
   def balance(self, **kwargs):
      return self._private_query('GET', '/api/v3/account', params=kwargs)



   """
   Exchange Specific Methods
   """

   @return_api_response(fmt.server_time, log)
   def server_time(self):
      return self._public_query('/api/v1/time')

   @return_api_response(fmt.multi_order_status, log)
   def open_orders_for(self, symbol, **kwargs):
      q = {'symbol': symbol}
      q.update(kwargs)
      return self._private_query('GET', '/api/v3/openOrders', params=q)

   @return_api_response(fmt.multi_order_status, log)
   def all_orders_since(self, symbol, order_id, **kwargs):
      q = {'symbol': symbol}
      if order_id:
         q['orderId'] = int(order_id)  # return all orders starting from this one
      q.update(kwargs)
      return self._private_query('GET', '/api/v3/allOrders', params=q)




   # These order types are in documentation, but they don't seem to work
   #
   # @return_api_response(fmt.order, log)
   # def place_stoploss_order(self, side, pair, size, stopPrice, **kwargs):
   #    return self._place_order('STOP_LOSS', side, pair, size, None, stopPrice, **kwargs)
   #
   # @return_api_response(fmt.order, log)
   # def place_stoplosslimit_order(self, side, pair, size, price, stopPrice, **kwargs):
   #    return self._place_order('STOP_LOSS_LIMIT', side, pair, size, price, stopPrice, timeInForce='GTC', **kwargs)
   #
   # @return_api_response(fmt.order, log)
   # def place_takeprofit_order(self, side, pair, size, stopPrice,  **kwargs):
   #    return self._place_order('TAKE_PROFIT', side, pair, size, None, stopPrice, **kwargs)
   #
   # @return_api_response(fmt.order, log)
   # def place_takeprofitlimit_order(self, side, pair, size, price, stopPrice,  **kwargs):
   #    return self._place_order('TAKE_PROFIT_LIMIT', side, pair, size, price, stopPrice, timeInForce='GTC', **kwargs)

   # This is failing ...  401 Client Error: Unauthorized for url: ...
   # @return_api_response(fmt.historical_trades, log)
   # def historical_trades(self, pair, **kwargs):
   #    return self.public_query('/api/v1/historicalTrades?symbol=%s' % pair.upper(), params=kwargs)








import logging
import hashlib
import hmac
import time

from exchanges.REST.api import RESTClientAPI
from exchanges.REST.response import response_formatter
from exchanges.REST.formatterBase import Formatter

# Location of the Binance API documentation:
# https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md


# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_handler = logging.FileHandler('BinanceRESTClient.log')
logger_handler.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d-%m %H:%M:%S')
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)


# ===============================================================================
#    Binance response formatter
# ===============================================================================

class BinanceFormatter(Formatter):

    @staticmethod
    def server_time(data, *args, **kwargs):
        return data['serverTime']

    @staticmethod
    def symbols(data, *args, **kwargs):
        return [d['symbol'] for d in data['symbols']]


    @staticmethod
    def symbols_details(data, *args, **kwargs):
        # create a temporary dictionary for each symbol as a key,
        # where values are dictionaries of filters with filter name as the key.
        filters = {d['symbol']: {f['filterType']: f for f in d['filters']} for d in data['symbols']}
        return {d['symbol'].upper(): {'precision':      d['baseAssetPrecision'],
                                      'minAmount':      filters[d['symbol']]['LOT_SIZE']['minQty'],
                                      'minPrice':       filters[d['symbol']]['PRICE_FILTER']['minPrice'],
                                      'baseAsset':      d['baseAsset'],
                                      'quoteAsset':     d['quoteAsset'],
                                      'quotePrecision': d['quotePrecision'],
                                      'orderTypes':     d['orderTypes'],
                                      'status':         d['status']}
                for d in data['symbols']}


    @staticmethod
    def ticker(data, *args, **kwargs):
        return [data['bidPrice'],
                data['askPrice'],
                data['highPrice'],
                data['lowPrice'],
                data['lastPrice'],
                data['volume'],
                data['priceChange'],
                data['priceChangePercent']]


    @staticmethod
    def tickers(data, *args, **kwargs):
        return {d['symbol']: [d['bidPrice'],
                              d['askPrice'],
                              d['highPrice'],
                              d['lowPrice'],
                              d['lastPrice'],
                              d['volume'],
                              d['priceChange'],
                              d['priceChangePercent']]
                for d in data}


    @staticmethod
    def order_book(data, *args, **kwargs):
        return {'bids': data['bids'],
                'asks': data['asks']}


    @staticmethod
    def trades(data, *args, **kwargs):
        return [[ t['time'],
                  t['price'],
                  t['qty'],
                  'sell' if t['isBuyerMaker'] else 'buy'
                ] for t in data]


    @staticmethod
    def candles(data, *args, **kwargs):
        # we could find the rest of data useful: number of trades, buy volume, sell volume
        return [d[:6] for d in data]


    @staticmethod
    def order(data, *args, **kwargs):
        # Order status can be one of these:
        #   NEW, PARTIALLY_FILLED, FILLED, CANCELED, REJECTED, EXPIRED
        try:
            return {'symbol':     data['symbol'],
                    'orderId':    data['orderId'],
                    'price':      data['price'],
                    'amount':     data['origQty'],
                    'filled':     data['executedQty'],
                    'type':       data['type'],
                    'side':       data['side'],
                    'timestamp':  data['transactTime'],
                    'status':     'LIVE' if data['status'] == 'NEW' or data['status'] == 'PARTIALLY_FILLED' else
                                  'EXECUTED' if data['status'] == 'FILLED' else
                                  'CANCELED'
                    }
        except KeyError:
            return False


    @staticmethod
    def order_status(data, *args, **kwargs):
        try:
            return {'symbol':     data['symbol'],
                    'orderId':    data['orderId'],
                    'price':      data['price'],
                    'stopPrice':  data['stopPrice'],
                    'amount':     data['origQty'],
                    'filled':     data['executedQty'],
                    'type':       data['type'],
                    'side':       data['side'],
                    'timestamp':  data['time'],
                    'status':     'LIVE' if data['status'] == 'NEW' or data['status'] == 'PARTIALLY_FILLED' else
                                  'EXECUTED' if data['status'] == 'FILLED' else
                                  'CANCELED'
                    }
        except KeyError:
            return {}


    @staticmethod
    def multi_order_status(data, *args, **kwargs):
        return [BinanceFormatter.order_status(d) for d in data]


    @staticmethod
    def cancel(data, *args, **kwargs):
        return True


    @staticmethod
    def balance(data, *args, **kwargs):
        return {d['asset']: d['free'] for d in data['balances']}


    @staticmethod
    def my_trades(data, *args, **kwargs):
        return [{'orderId': d['orderId'],
                 'price': d['price'],
                 'amount': d['qty'],
                 'fee': d['commission'],
                 'feeAsset': d['commissionAsset'],
                 'side': 'buy' if d['isBuyer'] else 'sell'}
                for d in data]


    @staticmethod
    def historical_trades(data, *args, **kwargs):
        return [[ t['time'],
                  t['price'],
                  t['qty'],
                  'sell' if t['isBuyerMaker'] else 'buy']
                for t in data]


# ===============================================================================
#     Binance REST API client
# ===============================================================================

class BinanceRESTClient(RESTClientAPI):
    def __init__(self, key=None, secret=None, key_file=None, api_version=None,
                 url='https://api.binance.com', timeout=5, log=logger):
        super(BinanceRESTClient, self).__init__(url, api_version=api_version, key=key, secret=secret,
                                                key_file=key_file, timeout=timeout, log=log)
        self.authenticated = key_file is not None or key is not None and secret is not None


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

        if 'userDataStream' in endpoint:
            # body = params
            headers = {
                'X-MBX-APIKEY': self._key,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            return url, {'headers': headers, 'params': params}

        # add receive window time to compensate for clocks being out of sync
        params.append(('recvWindow', 60000))
        # add timestamp (required)
        params.append(('timestamp', int(round(time.time() * 1000))))

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


    # ------------------------------------------------------------------
    #     Public Methods
    # ------------------------------------------------------------------

    def ping(self):
        return self._public_query('/api/v1/ping').ok


    def quote_currencies(self):
        return ['BTC', 'ETH', 'BNB', 'USDT']


    @response_formatter(BinanceFormatter.symbols, logger)
    def symbols(self):
        return self._public_query('/api/v1/exchangeInfo')


    @response_formatter(BinanceFormatter.symbols_details, logger)
    def symbols_details(self):
        return self._public_query('/api/v1/exchangeInfo')


    @classmethod
    def candle_intervals(self):
        return ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']


    @response_formatter(BinanceFormatter.ticker, logger)
    def ticker(self, pair, **kwargs):
        return self._public_query('/api/v1/ticker/24hr?symbol=%s' % pair.upper(), params=kwargs)


    @response_formatter(BinanceFormatter.tickers, logger)
    def all_tickers(self, **kwargs):
        return self._public_query('/api/v1/ticker/24hr', params=kwargs)


    @response_formatter(BinanceFormatter.order_book, logger)
    def order_book(self, pair, **kwargs):
        return self._public_query('/api/v1/depth?symbol=%s' % pair.upper(), params=kwargs)


    @response_formatter(BinanceFormatter.trades, logger)
    def trades(self, pair, **kwargs):
        return self._public_query('/api/v1/trades?symbol=%s' % pair.upper(), params=kwargs)


    @response_formatter(BinanceFormatter.candles, logger)
    def candles(self, pair, interval='1m', **kwargs):
        if interval not in self.candle_intervals():
            interval = '1m'
        return self._public_query('/api/v1/klines?symbol=%s&interval=%s' % (pair.upper(), interval), params=kwargs)


    def historical_candles(self, pair, interval, start_time, end_time, **kwargs):
        return self.candles(pair, interval, startTime=start_time, endTime=end_time, **kwargs)


    # ------------------------------------------------------------------
    #     Private Methods
    # ------------------------------------------------------------------

    # Order types:  LIMIT, MARKET, STOP_LOSS, STOP_LOSS_LIMIT,
    #               TAKE_PROFIT, TAKE_PROFIT_LIMIT, LIMIT_MAKER

    def _place_order(self, type, side, pair, size, price, stopPrice, **kwargs):
        params = {'type': type, 'side': side.upper(), 'symbol': pair.upper(), 'quantity': size}
        if price:
            params['price'] = format(price, '.8f')
        if stopPrice:
            params['stopPrice'] = format(stopPrice, '.8f')

        params.update(kwargs)
        return self._private_query('POST', '/api/v3/order', params=params)


    @response_formatter(BinanceFormatter.order, logger)
    def place_market_order(self, side, pair, size, **kwargs):
        return self._place_order('MARKET', side, pair, size, None, None, **kwargs)


    @response_formatter(BinanceFormatter.order, logger)
    def place_limit_order(self, side, pair, size, price, **kwargs):
        return self._place_order('LIMIT', side, pair, size, price, None, timeInForce='GTC', **kwargs)


    @response_formatter(BinanceFormatter.order_status, logger)
    def order(self, order_id, symbol, **kwargs):
        params = {'symbol': symbol, 'orderId': int(order_id)}
        params.update(kwargs)
        return self._private_query('GET', '/api/v3/order', params=params)


    @response_formatter(BinanceFormatter.multi_order_status, logger)
    def open_orders(self, **kwargs):
        params = {}
        params.update(kwargs)
        return self._private_query('GET', '/api/v3/openOrders', params=params)


    @response_formatter(BinanceFormatter.multi_order_status, logger)
    def all_orders(self, symbol, **kwargs):
        params = {'symbol': symbol}
        params.update(kwargs)
        return self._private_query('GET', '/api/v3/allOrders', params=params)


    @response_formatter(BinanceFormatter.cancel, logger)
    def cancel_order(self, order_id, symbol, **kwargs):
        params = {'symbol': symbol, 'orderId': int(order_id)}
        params.update(kwargs)
        return self._private_query('DELETE', '/api/v3/order', params=params)


    @response_formatter(BinanceFormatter.my_trades, logger)
    def user_trades(self, symbol, **kwargs):
        params = {'symbol': symbol}
        params.update(kwargs)
        return self._private_query('GET', '/api/v3/myTrades', params=params)


    @response_formatter(BinanceFormatter.balance, logger)
    def balance(self, **kwargs):
        return self._private_query('GET', '/api/v3/account', params=kwargs)


    # -----------------------------------------------------
    #    Exchange Specific Methods
    # -----------------------------------------------------

    @response_formatter(BinanceFormatter.server_time, logger)
    def server_time(self):
        return self._public_query('/api/v1/time')


    @response_formatter(BinanceFormatter.multi_order_status, logger)
    def open_orders_for(self, symbol, **kwargs):
        params = {'symbol': symbol}
        params.update(kwargs)
        return self._private_query('GET', '/api/v3/openOrders', params=params)


    @response_formatter(BinanceFormatter.multi_order_status, logger)
    def all_orders_since(self, symbol, order_id, **kwargs):
        params = {'symbol': symbol}
        if order_id:
            params['orderId'] = int(order_id)  # return all orders starting from this one
        params.update(kwargs)
        return self._private_query('GET', '/api/v3/allOrders', params=params)


    @response_formatter(BinanceFormatter.forward, logger)
    def create_listen_key(self):
        return self._private_query('POST', '/api/v1/userDataStream')


    @response_formatter(BinanceFormatter.forward, logger)
    def ping_listen_key(self, listenKey):
        return self._private_query('PUT', '/api/v1/userDataStream', params={'listenKey': listenKey})


    @response_formatter(BinanceFormatter.forward, logger)
    def close_listen_key(self, listenKey):
        return self._private_query('DELETE', '/api/v1/userDataStream', params={'listenKey': listenKey})

    # These order types are in documentation, but they don't seem to work
    #
    # @return_api_response(BinanceFormatter.order, log)
    # def place_stoploss_order(self, side, pair, size, stopPrice, **kwargs):
    #    return self._place_order('STOP_LOSS', side, pair, size, None, stopPrice, **kwargs)
    #
    # @return_api_response(BinanceFormatter.order, log)
    # def place_stoplosslimit_order(self, side, pair, size, price, stopPrice, **kwargs):
    #    return self._place_order('STOP_LOSS_LIMIT', side, pair, size, price, stopPrice, timeInForce='GTC', **kwargs)
    #
    # @return_api_response(BinanceFormatter.order, log)
    # def place_takeprofit_order(self, side, pair, size, stopPrice,  **kwargs):
    #    return self._place_order('TAKE_PROFIT', side, pair, size, None, stopPrice, **kwargs)
    #
    # @return_api_response(BinanceFormatter.order, log)
    # def place_takeprofitlimit_order(self, side, pair, size, price, stopPrice,  **kwargs):
    #    return self._place_order('TAKE_PROFIT_LIMIT', side, pair, size, price, stopPrice, timeInForce='GTC', **kwargs)

    # This is failing ...  401 Client Error: Unauthorized for url: ...
    # @return_api_response(BinanceFormatter.historical_trades, log)
    # def historical_trades(self, pair, **kwargs):
    #    return self.public_query('/api/v1/historicalTrades?symbol=%s' % pair.upper(), params=kwargs)


    # NOT IMPLEMENTED:
    # -------------------------------------------------------------------------------------
    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
    #
    # Should be checking for the request limits (error codes) to avoid beining banned. See LIMITS in docs.
    #
    #
    # AGGREGATE TRADES LIST:
    # ---------------------------
    # https://api.binance.com/api/v1/aggTrades
    #
    #
    # symbol    STRING
    # fromId    LONG      ID to get aggregate trades from INCLUSIVE.
    # startTime LONG      Timestamp in ms to get aggregate trades from INCLUSIVE.
    # endTime   LONG      Timestamp in ms to get aggregate trades until INCLUSIVE.
    # limit     INT       Default 500; max 1000.
    #
    # [
    #   {
    #     "a": 26129,         // Aggregate tradeId
    #     "p": "0.01633102",  // Price
    #     "q": "4.70443515",  // Quantity
    #     "f": 27781,         // First tradeId
    #     "l": 27781,         // Last tradeId
    #     "T": 1498793709153, // Timestamp
    #     "m": true,          // Was the buyer the maker?
    #     "M": true           // Was the trade the best price match?
    #   }
    # ]
    #
    #
    # CURRENT AVERAGE PRICE
    # ---------------------------
    #
    # https://api.binance.com/api/v3/avgPrice
    # https://api.binance.com/api/v3/avgPrice?BTCUSDT
    #
    # {
    #   "mins": 5,
    #   "price": "9.35751834"
    # }
    #
    #
    # SYMBOL ORDER BOOK TICKER
    # ---------------------------
    #
    # https://api.binance.com/api/v3/ticker/bookTicker
    # https://api.binance.com/api/v3/ticker/bookTicker?BTCUSDT
    #
    # {
    #   "symbol": "LTCBTC",
    #   "bidPrice": "4.00000000",
    #   "bidQty": "431.00000000",
    #   "askPrice": "4.00000200",
    #   "askQty": "9.00000000"
    # }
    #
    # or a list for all symbols
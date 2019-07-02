import logging
import json
import hashlib
import hmac
import base64

from exchanges.REST.api import RESTClientAPI
from exchanges.REST.response import response_formatter
from exchanges.REST.formatterBase import Formatter


# create the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_handler = logging.FileHandler('BitfinexRESTClient.log')
logger_handler.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d-%m %H:%M:%S')
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)


# ===============================================================================
#    Bitfinex response formatter
# ===============================================================================

class BitfinexFormatter(Formatter):

    @staticmethod
    def symbols(data, *args, **kwargs):
        return [symbol.upper() for symbol in data]

    @staticmethod
    def symbols_details(data, *args, **kwargs):
        # this hack is for the sole reason that Bitfinex API lacks any notion
        # of what base asset and quote asset are. We need to deduce it ourselves.
        # We use the fact that the exchange object is passed as the first argument in args
        qc = args[0].quote_currencies()
        return {d['pair'].upper(): {'precision':  d['price_precision'],
                                    'minAmount':  d['minimum_order_size'],
                                    'baseAsset':  d['pair'].upper().strip(
                                                     [curr for curr in qc if d['pair'].upper().endswith(curr)][-1]
                                                  ),
                                    'quoteAsset': [curr for curr in qc if d['pair'].upper().endswith(curr)][-1],
                                    'maxAmount':  d['maximum_order_size'],
                                    'status':     'TRADING'}
                for d in data}

    @staticmethod
    def ticker(data, *args, **kwargs):
        return [ data[0], data[2], data[8], data[9], data[6], data[7], data[4], data[5] ]

    @staticmethod
    def tickers(data, *args, **kwargs):
        return { d[0][1:].upper(): [d[1], d[3], d[9], d[10], d[7], d[8], d[5], 100*d[6]] for d in data }

    @staticmethod
    def order_book(data, *args, **kwargs):
        return { 'bids': [ [i['price'], i['amount']] for i in data['bids']],
                 'asks': [ [i['price'], i['amount']] for i in data['asks']] }

    @staticmethod
    def trades(data, *args, **kwargs):
        return [ [t['timestamp'],
                  t['price'],
                  t['amount'],
                  t['type']]
                 for t in data]

    @staticmethod
    def candles(data, *args, **kwargs):
        return list(reversed([ [d[0], d[1], d[3], d[4], d[2], d[5]] for d in data]))

    @staticmethod
    def order(data, *args, **kwargs):
        return { 'symbol':    data['symbol'],
                 'orderId':   data['id'],
                 'price':     data['price'],
                 'amount':    data['original_amount'],
                 'filled':    data['executed_amount'],
                 'type':      'LIMIT' if data['type'] == 'exchange limit' else
                              'MARKET' if data['type'] == 'exchange market' else
                              'STOP-LOSS' if data['type'] == 'exchange stop' else
                              'TRAILING STOP-LOSS',
                 'side':      data['side'],
                 'timestamp': data['timestamp'],
                 'status':    'LIVE' if data['is_live'] else
                              'CANCELED' if data['is_cancelled'] else
                              'EXECUTED'
                 }

    @staticmethod
    def order_status(data, *args, **kwargs):
        return { 'symbol':     data['symbol'],
                 'orderId':    data['id'],
                 'price':      data['price'],
                 'stopPrice':  data['price'],
                 'amount':     data['original_amount'],
                 'filled':     data['executed_amount'],
                 'type':       'LIMIT' if data['type'] == 'exchange limit' else
                               'MARKET' if data['type'] == 'exchange market' else
                               'STOP-LOSS' if data['type'] == 'exchange stop' else
                               'TRAILING STOP-LOSS',
                 'side':       data['side'],
                 'timestamp':  data['timestamp'],
                 'status':     'LIVE' if data['is_live'] else
                               'CANCELED' if data['is_cancelled'] else
                               'EXECUTED'
                 }


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
        return [{ 'orderId':  d['order_id'],
                  'price':    d['price'],
                  'amount':   d['amount'],
                  'fee':      d['fee_amount'],
                  'feeAsset': d['fee_currency'],
                  'side':     d['type']}
                for d in data]

    @staticmethod
    def balance(data, *args, **kwargs):
        return { d['currency']: d['available'] for d in data if d['type'] == 'exchange'}


# ===============================================================================
#    Bitfinex REST API client
# ===============================================================================

class BitfinexRESTClient(RESTClientAPI):
    def __init__(self, key=None, secret=None, key_file=None, api_version=None,
                 url='https://api.bitfinex.com', timeout=5, log=logger):
        super(BitfinexRESTClient, self).__init__(url, api_version=api_version, key=key, secret=secret,
                                                 key_file=key_file, timeout=timeout, log=log)
        self.authenticated = key_file is not None or key is not None and secret is not None


    @staticmethod
    def name():
        return 'Bitfinex'


    def _sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
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


    # ------------------------------------------------------------------
    #     Public Methods
    # ------------------------------------------------------------------

    def ping(self):
        return self.status()[0] == 1

    def quote_currencies(self):
        return ['USD', 'BTC', 'EUR', 'JPY', 'GBP', 'ETH', 'UST', 'EOS', 'XLM', 'DAI', 'USTF0', 'XCH']

    @response_formatter(BitfinexFormatter.symbols, logger)
    def symbols(self):
        return self._public_query('/v1/symbols')

    @response_formatter(BitfinexFormatter.symbols_details, logger)
    def symbols_details(self):
        return self._public_query('/v1/symbols_details')

    @classmethod
    def candle_intervals(cls):
        return ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D', '7D', '14D', '1M']

    @response_formatter(BitfinexFormatter.ticker, logger)
    def ticker(self, pair, **kwargs):
        return self._public_query('/v2/ticker/t%s' % pair.upper(), params=kwargs)

    def all_tickers(self, **kwargs):
        symbols = self.symbols()
        return self.tickers(symbols)

    @response_formatter(BitfinexFormatter.order_book, logger)
    def order_book(self, pair, **kwargs):
        return self._public_query('/v1/book/%s' % pair, params=kwargs)

    @response_formatter(BitfinexFormatter.trades, logger)
    def trades(self, pair, **kwargs):
        return self._public_query('/v1/trades/%s' % pair, params=kwargs)

    @response_formatter(BitfinexFormatter.candles, logger)
    def candles(self, pair, interval='1m', **kwargs):
        if interval not in self.candle_intervals():
            interval ='1m'
        return self._public_query('/v2/candles/trade:%s:t%s/hist' % (interval, pair.upper()), params=kwargs)

    def historical_candles(self, pair, interval, start_time, end_time, **kwargs):
        return self.candles(pair, interval, start=start_time, end=end_time, **kwargs)


    # ------------------------------------------------------------------
    #     Private Methods
    # ------------------------------------------------------------------

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

    @response_formatter(BitfinexFormatter.order, logger)
    def place_market_order(self, side, pair, size, **kwargs):
        # price should be a random positive number, we use 1
        return self._place_order('exchange market', side, pair, size, 1, None, **kwargs)

    @response_formatter(BitfinexFormatter.order, logger)
    def place_limit_order(self, side, pair, size, price, **kwargs):
        return self._place_order('exchange limit', side, pair, size, price, None, **kwargs)

    @response_formatter(BitfinexFormatter.order_status, logger)
    def order(self, order_id, symbol, **kwargs):
        q = {'order_id': order_id}
        q.update(kwargs)
        return self._private_query('/v1/order/status', params=q)

    @response_formatter(BitfinexFormatter.multi_order_status, logger)
    def open_orders(self, **kwargs):
        return self._private_query('/v1/orders')

    @response_formatter(BitfinexFormatter.multi_order_status, logger)
    def all_orders(self, symbol, **kwargs):
        q = {}
        q.update(kwargs)
        return self._private_query('/v1/orders/hist', params=q)

    @response_formatter(BitfinexFormatter.cancel, logger)
    def cancel_order(self, order_id, symbol, **kwargs):
        q = {'order_id': int(order_id)}
        q.update(kwargs)
        return self._private_query('/v1/order/cancel', params=q)


    @response_formatter(BitfinexFormatter.my_trades, logger)
    def my_trades(self, symbol, **kwargs):
        q = {'symbol': symbol}
        q.update(kwargs)
        return self._private_query('/v1/mytrades', params=q)

    @response_formatter(BitfinexFormatter.balance, logger)
    def balance(self, **kwargs):
        return self._private_query('/v1/balances', params=kwargs)


    # -----------------------------------------------------
    #    Exchange Specific Methods
    # -----------------------------------------------------

    @response_formatter(BitfinexFormatter.forward, logger)
    def status(self):
        return self._public_query('/v2/platform/status')

    @response_formatter(BitfinexFormatter.tickers, logger)
    def tickers(self, pairs, **kwargs):
        pair_list = ','.join( ['t' + p.upper() for p in pairs] )
        return self._public_query('/v2/tickers?symbols=%s' % pair_list, params=kwargs)

    @response_formatter(BitfinexFormatter.order, logger)
    def place_stoploss_order(self, side, pair, size, stop_price, **kwargs):
        return self._place_order('exchange stop', side, pair, size, stop_price, None, **kwargs)

    @response_formatter(BitfinexFormatter.order, logger)
    def place_trailing_stoploss_order(self, side, pair, size, stop_price, **kwargs):
        return self._place_order('exchange trailing-stop', side, pair, size, stop_price, None, **kwargs)

    @response_formatter(BitfinexFormatter.cancel, logger)
    def cancel_multiple_orders(self, order_ids, **kwargs):
        q = {'order_ids': order_ids}
        q.update(kwargs)
        return self._private_query('/v1/order/cancel/multi', params=q)

    @response_formatter(BitfinexFormatter.cancel, logger)
    def cancel_all_orders(self, **kwargs):
        return self._private_query('/v1/order/cancel/all')


    # NOT IMPLEMENTED:
    # -------------------------------------------------------------------------------------
    # https://docs.bitfinex.com/reference
    # https://docs.bitfinex.com/v2/reference
    #
    #
    # V1 STATS
    # ---------------------------
    #
    # https://api.bitfinex.com/v1/stats/<symbol>
    # https://api.bitfinex.com/v1/stats/BTCUSD
    #
    # period	[integer]    Period covered in days
    # volume	[price]      Volume
    #
    # [{
    #   "period":1,
    #   "volume":"7967.96766158"
    # },{
    #   "period":7,
    #   "volume":"55938.67260266"
    # },{
    #   "period":30,
    #   "volume":"275148.09653645"
    # }]
    #
    #
    # V2 BOOKS
    # ---------------------------
    #
    # https://api-pub.bitfinex.com/v2/book/Symbol/Precision
    # https://api-pub.bitfinex.com/v2/book/tBTCUSD/P0
    #
    # PATH PARAMS
    # Symbol
    # Precision    Level of price aggregation (P0, P1, P2, P3, P4, R0)    P0
    #
    # QUERY PARAMS
    #
    # len          Number of price points ("25", "100")                   25
    #
    # [
    #   [
    #     PRICE,
    #     COUNT,
    #     AMOUNT
    #   ]
    # ]
    #
    #
    # Margin related:
    # ---------------------------
    # FUNDINGBOOK:  https://api.bitfinex.com/v1/lendbook/<currency>
    # LENDS:        https://api.bitfinex.com/v1/lends/<currency>
    # V2 STATS:     https://api-pub.bitfinex.com/v2/stats1/Key:Size:Symbol/Section

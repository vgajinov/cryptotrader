import unittest
import logging
import os.path
from exchanges.REST.api import RESTClientAPI
from exchanges.WS.api import WSClientAPI


class DummyRESTClient(RESTClientAPI):
    def init(self, uri, api_version=None, key=None, secret=None, key_file=None,
             timeout=5, log=logging.getLogger(__name__)):
        super().__init__(uri, api_version, key, secret, key_file, timeout, log)

    def _sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs): pass
    def all_orders(self, symbol, **kwargs): pass
    def all_tickers(self,**kwargs): pass
    def balance(self, **kwargs): pass
    def cancel_order(self, order_id, symbol, **kwargs): pass
    def candle_intervals(self): pass
    def candles(self, symbol, interval='1m', **kwargs): pass
    def historical_candles(self, symbol, interval, start_time, end_time, **kwargs): pass
    def my_trades(self, symbol, **kwargs): pass
    def name(self): pass
    def open_orders(self, **kwargs): pass
    def order(self, order_id, symbol, **kwargs): pass
    def order_book(self, symbol, **kwargs): pass
    def ping(self): pass
    def place_limit_order(self, side, symbol, size, price, **kwargs): pass
    def place_market_order(self, side, symbol, size, **kwargs): pass
    def quote_currencies(self): pass
    def symbols(self): pass
    def symbols_details(self): pass
    def ticker(self, symbol, **kwargs): pass
    def trades(self, symbol, **kwargs): pass


class DummyWSClient(WSClientAPI):
    def __init__(self):
        super().__init__()

    def authenticate(self, key=None, secret=None, key_file=None): pass
    def connect(self, info_handler=None): pass
    def disconnect(self): pass
    def name(self): pass
    def subscribe(self, **kwargs): pass
    def subscribe_balances(self, update_handler): pass
    def subscribe_candles(self, symbol, interval='1m', update_handler=None): pass
    def subscribe_order_book(self, symbol, update_handler=None, **kwargs): pass
    def subscribe_ticker(self, symbol, update_handler=None): pass
    def subscribe_trades(self, symbol, update_handler=None): pass
    def subscribe_user_orders(self, update_handler): pass
    def subscribe_user_trades(self, update_handler): pass
    def unsubscribe(self, **kwargs): pass


class ApiClassesTestCase(unittest.TestCase):

    def test_REST_client_creation(self):
        self.assertRaises(TypeError, RESTClientAPI, 'http://testurl.com')
        self.assertRaises(TypeError, DummyRESTClient)
        try:
            cl = DummyRESTClient('http://testurl.com')
        except TypeError:
            self.fail('Instantiation of the concrete implementation of the abstract RESTClientAPI class failed!')
        self.assertEqual(cl._uri, 'http://testurl.com')
        self.assertIsNone(cl._key)
        self.assertIsNone(cl._secret)
        self.assertEqual(cl._version, '')
        self.assertEqual(cl.timeout, 5)
        self.assertIsNotNone(cl._log)
        self.assertEqual(cl._log.name, 'RESTClientAPILogger')

        cl2 = DummyRESTClient('http://testurl.com', key='userName', secret='abcd',
                              timeout=33, log=logging.getLogger('testLogger'), api_version='0.1.9')
        self.assertEqual(cl2._key, 'userName')
        self.assertEqual(cl2._secret, 'abcd')
        self.assertEqual(cl2.timeout, 33)
        self.assertEqual(cl2._version, '0.1.9')
        self.assertEqual(cl2._log.name, 'testLogger')

        file_path = os.path.dirname(os.path.relpath(__file__))
        cl3 = DummyRESTClient('http://testurl.com', key='userName', secret='abcd',
                              key_file=os.path.join(file_path, 'test.key'))
        self.assertEqual(cl3._key, 'storedUserName')
        self.assertEqual(cl3._secret, 'storedKeyABC')


    def test_WS_client_creation(self):
        self.assertRaises(TypeError, WSClientAPI)
        try:
            cl = DummyWSClient()
        except TypeError:
            self.fail('Instantiation of the concrete implementation of the abstract WSClientAPI class failed!')

        self.assertEqual(cl.logger.name, 'WSClientAPILogger')
        self.assertEqual(len(cl.logger.handlers), 1)
        self.assertTrue(cl.logger.handlers[0].baseFilename.endswith('DummyWSClient.log'))

        cl._stop_logger()
        self.assertIsNone(cl.logger)


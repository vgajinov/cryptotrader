import unittest
import json
import requests
import logging
from exchanges.REST.response import *
from exchanges.REST.formatterBase import Formatter
from exchanges.exception import ExchangeException


class DummyFormatter(Formatter):
    @staticmethod
    def symbols(data, *args, **kwargs):
        return [d['symbol'] for d in data['symbols']]


dummy_formatter = DummyFormatter()


class Dummy:
    @response_formatter(dummy_formatter.symbols)
    def request(self, response):
        return response

    def forward_response(self, response):
        return response

    def faulty_method(self):
        raise Exception('Dummy exception')


class ResponseDecoratorTestCase(unittest.TestCase):
    dummy = Dummy()
    response = requests.Response()
    logger = logging.getLogger('TestLogger')

    @classmethod
    def setUp(cls):
        cls.response.url = "http://dummy.test.com"
        cls.response.encoding = 'utf-8'

    def test_get_response_ok(self):
        self.assertEqual( get_response('DummyExchange', self.logger, self.dummy.forward_response, self.response),
                          self.response)

    def test_get_response_fail(self):
        self.assertRaises(ExchangeException, get_response, 'DummyExchange', None, self.dummy.faulty_method)

    def test_check_status_ok(self):
        # test correct response code 200 - OK
        self.response.status_code = 200
        try:
            check_status('DummyExchange', self.logger, self.response, self.dummy.forward_response)
        except:
            self.fail("Function 'check_status' threw exception for the Success status of the response")

    def test_check_status_bad_url(self):
        # test code 404 - Not Found
        self.response.status_code = 404
        self.assertRaises(ExchangeException, check_status,
                          'DummyExchange', None, self.response, self.dummy.forward_response)

    def test_check_status_bad_response(self):
        # test for bad response object (None)
        self.assertRaises(ExchangeException, check_status,
                          'DummyExchange', None, None, self.dummy.forward_response)

    def test_get_json_content_ok(self):
        self.response._content = b'{"symbol":"BTCUSD","priceChange":"-0.59740000","priceChangePercent":"-1.798"}'
        self.assertEqual(get_json_content("DummyExchange", None, self.response),
                         {'symbol': 'BTCUSD', 'priceChange': '-0.59740000', 'priceChangePercent': '-1.798'})

    def test_get_json_content_bad_json(self):
        self.response._content = b'{"symbol":}'
        self.assertRaises(ExchangeException, get_json_content, "DummyExchange", None, self.response)

    def test_format_data_ok(self):
        data = {"symbols": [{"symbol": "BTCUSD", "price": 2.34}, {"symbol": "XMRBTC", "price": 0.045}]}
        fmt = DummyFormatter()
        self.assertEqual(sorted(format_data("DummyExchange", None, data, fmt.symbols, self.dummy.forward_response)),
                         ["BTCUSD", "XMRBTC"])

    def test_format_data_bad_data(self):
        data = {"syms": [{"sym": "BTCUSD", "price": 2.34}, {"sym": "XMRBTC", "price": 0.045}]}
        fmt = DummyFormatter()
        self.assertRaises(ExchangeException, format_data, "DummyExchange",
                          None, data, fmt.symbols, self.dummy.forward_response)

    def test_format_data_no_formatter(self):
        data = {"symbol": "BTCUSD", "price": 2.34}
        self.assertEqual(format_data("DummyExchange", None, data, None, self.dummy.forward_response), data)

    def test_response_formatter_ok(self):
        self.response._content = b'{"symbols": [{"symbol": "BTCUSD", "price": 2.34}]}'
        self.response.status_code = 200   # OK
        self.assertEqual(self.dummy.request(self.response), ["BTCUSD"])


import unittest
from exchanges.exchangeRESTFactory import ExchangeRESTFactory
from exchanges.exchangeWSFactory import ExchangeWSFactory


class ExchangeFactoryTestCase(unittest.TestCase):

    def test_RESTFactory_get_exchanges(self):
        exchanges = ExchangeRESTFactory.get_exchanges()
        self.assertTrue(type(exchanges) is list)
        self.assertTrue('Binance' in exchanges)
        self.assertTrue('Bitfinex' in exchanges)

    def test_RESTFactory(self):
        self.assertIsNotNone(ExchangeRESTFactory.create_client('Binance'))
        self.assertEqual('Binance', ExchangeRESTFactory.create_client('Binance').name())
        self.assertIsNotNone(ExchangeRESTFactory.create_client('Bitfinex'))
        self.assertEqual('Bitfinex', ExchangeRESTFactory.create_client('Bitfinex').name())
        self.assertRaises(KeyError, ExchangeRESTFactory.create_client, 'NonExistent')

    def test_WSFactory_get_exchanges(self):
        exchanges = ExchangeWSFactory.get_exchanges()
        self.assertTrue(type(exchanges) is list)
        self.assertTrue('Binance' in exchanges)
        self.assertTrue('Bitfinex' in exchanges)

    def test_WSFactory(self):
        client = ExchangeWSFactory.create_client('Binance')
        self.assertIsNotNone(client)
        self.assertEqual('Binance', client.name())
        client.disconnect()
        client = ExchangeWSFactory.create_client('Bitfinex')
        self.assertIsNotNone(client)
        self.assertEqual('Bitfinex', client.name())
        client.disconnect()
        self.assertRaises(KeyError, ExchangeWSFactory.create_client, 'NonExistent')

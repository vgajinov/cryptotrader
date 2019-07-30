import unittest
from os import path
from exchanges.REST.bitfinex import BitfinexRESTClient
from exchanges.exception import ExchangeException

client = BitfinexRESTClient()


class BitfinexRESTPublicClientTestCase(unittest.TestCase):
    client = BitfinexRESTClient()

    def test_ping(self):
        self.assertTrue(self.client.ping())

    def test_quote_currencies(self):
        currencies = self.client.quote_currencies()
        self.assertIs(type(currencies), list)
        self.assertTrue('BTC' in currencies)
        self.assertTrue('USD' in currencies)

    def test_symbols(self):
        try:
            symbols = self.client.symbols()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(symbols), list)
        self.assertTrue('BTCUSD' in symbols)
        self.assertTrue('LTCBTC' in symbols)

    def test_symbols_details(self):
        try:
            symbols_details = self.client.symbols_details()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(symbols_details), dict)
        self.assertTrue('BTCUSD' in symbols_details)
        self.assertEqual(symbols_details['BTCUSD']['baseAsset'], 'BTC')
        self.assertEqual(symbols_details['BTCUSD']['quoteAsset'], 'USD')
        self.assertEqual(symbols_details['BTCUSD']['precision'], 5)

    def test_candle_intervals(self):
        try:
            intervals = self.client.candle_intervals()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(intervals), list)
        self.assertTrue('1m' in intervals)

    def test_ticker(self):
        try:
            ticker = self.client.ticker('BTCUSD')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(ticker), list)
        self.assertEqual(len(ticker), 8)

    def test_all_tickers(self):
        try:
            tickers = self.client.all_tickers()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(tickers), dict)
        self.assertTrue('BTCUSD' in tickers)
        self.assertIs(type(tickers['BTCUSD']), list)
        self.assertEqual(len(tickers['BTCUSD']), 8)

    def test_order_book(self):
        try:
            book = self.client.order_book('BTCUSD')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(book), dict)
        self.assertTrue('bids' in book)
        self.assertTrue('asks' in book)

    def test_trades(self):
        try:
            trades = self.client.trades('BTCUSD')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(trades), list)
        self.assertIs(type(trades[0]), list)
        self.assertEqual(len(trades[0]), 4)
        self.assertTrue('buy' in trades[0] or 'sell' in trades[0])

    def test_candles(self):
        # this also covers testing the historical_candles method
        try:
            candles = self.client.candles('BTCUSD', '1m', start=1560696720000, end=1560696780000)
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(candles), list)
        self.assertListEqual(candles[0], [1560696720000, 9261.33251778, 9269, 9260, 9269, 3.21300032])


class BitfinexRESTAuthenticatedClientTestCase(unittest.TestCase):
    client = None
    placed_orders = []

    @classmethod
    def setUpClass(cls) -> None:
        key_file = 'exchanges/api_keys/bitfinex.key'
        if not path.exists(key_file) or not path.isfile(key_file):
            print("Testing Bitfinex authenticated channels requires an API key!")
            print("Please, provide the key file named 'bitfinex.key' in the exchanges/api_keys folder.")
            raise unittest.SkipTest('Key file not found or invalid!')
        cls.client = BitfinexRESTClient(key_file=key_file)
        if not cls.client.authenticated:
            raise unittest.SkipTest('Authentication failed using given key file!')

    @classmethod
    def tearDownClass(cls) -> None:
        for order in cls.placed_orders:
            cls.client.cancel_order(order['orderId'], order['symbol'])

    def test_balances(self):
        balances = self.client.balance()
        self.assertIsNotNone(balances)
        self.assertIs(type(balances), dict)
        self.assertTrue('BTC' in balances.keys())
        self.assertTrue('USD' in balances.keys())

    def test_user_trades(self):
        try:
            self.client.user_trades()
            self.fail('Exception not raised for invalid call to user_trades!')
        except ExchangeException:
            pass
        trades = self.client.user_trades('BTCUSD', limit=10)
        self.assertIsNotNone(trades)
        self.assertIs(type(trades), list)
        self.assertIs(type(trades[0]), dict)
        self.assertTrue('orderId' in trades[0].keys())
        self.assertTrue('price' in trades[0].keys())
        self.assertTrue('amount' in trades[0].keys())
        self.assertTrue('side' in trades[0].keys())
        self.assertTrue(trades[0]['side'] == 'BUY' or trades[0]['side'] == 'SELL')

    def test_limit_order(self):
        try:
            order = self.client.place_limit_order('sell', 'btcusd', 0.001, 123000)
            self.placed_orders.append(order)
        except ExchangeException:
            self.fail('Placing limit order failed!')
        self.assertIsNotNone(order)
        self.assertIs(type(order), dict)
        self.assertTrue('orderId' in order)
        self.assertTrue('price' in order)
        self.assertTrue('amount' in order)
        self.assertTrue('side' in order)
        try:
            self.client.place_limit_order('buy', 'btcusd', 10000000000000, 0.0010655)
            self.fail('Exception not raised for invalid limit order amount!')
        except ExchangeException:
            pass
        try:
            self.client.place_limit_order('buy', 'btcusd', 1, -0.00000001)
            self.fail('Exception not raised for invalid limit order price!')
        except ExchangeException:
            pass

    def test_single_order_status(self):
        order = self.client.place_limit_order('sell', 'btcusd', 0.001, 123000)
        self.placed_orders.append(order)

        status = self.client.order(order['orderId'], 'BTCUSD')
        self.assertIsNotNone(status)
        self.assertIs(type(status), dict)
        self.assertTrue('symbol' in status)
        self.assertTrue('orderId' in status)
        self.assertTrue('price' in status)
        self.assertTrue('amount' in status)
        self.assertTrue('side' in status)
        self.assertTrue('type' in status)
        self.assertTrue('status' in status)
        self.assertTrue('timestamp' in status)
        self.assertEqual(status['symbol'], 'BTCUSD')
        self.assertEqual(status['orderId'], order['orderId'])
        self.assertEqual(status['price'], '123000.0')
        self.assertEqual(status['amount'], '0.001')
        self.assertEqual(status['type'], 'LIMIT')
        self.assertEqual(status['side'], 'SELL')
        self.assertEqual(status['status'], 'LIVE')

    def test_open_orders(self):
        order = self.client.place_limit_order('sell', 'btcusd', 0.001, 123000)
        self.placed_orders.append(order)

        orders = self.client.open_orders()
        self.assertIsNotNone(orders)
        self.assertIs(type(orders), list)
        self.assertGreaterEqual(len(orders), 1)
        self.assertIs(type(orders[0]), dict)
        self.assertTrue(order['orderId'] in [x['orderId'] for x in orders])

    def test_open_orders_for_symbol(self):
        order = self.client.place_limit_order('sell', 'btcusd', 0.001, 123000)
        self.placed_orders.append(order)

        orders = self.client.open_orders_for('BTCUSD')
        self.assertIsNotNone(orders)
        self.assertIs(type(orders), list)
        self.assertGreaterEqual(len(orders), 1)
        self.assertIs(type(orders[0]), dict)
        self.assertTrue(order['orderId'] in [x['orderId'] for x in orders])
        symbols = set([x['symbol'] for x in orders])
        self.assertEqual(len(symbols), 1)
        self.assertTrue('BTCUSD' in symbols)
        statuses = set([x['status'] for x in orders])
        self.assertEqual(len(statuses), 1)
        self.assertTrue('LIVE' in statuses, f'{statuses}\n{orders}')

    def test_all_orders(self):
        orders = self.client.all_orders('BTCUSD')
        self.assertIsNotNone(orders)
        self.assertIs(type(orders), list)
        self.assertGreaterEqual(len(orders), 1)
        self.assertIs(type(orders[0]), dict)
        symbols = set([x['symbol'] for x in orders])
        self.assertEqual(len(symbols), 1)
        self.assertTrue('BTCUSD' in symbols)

    def test_cancel_order(self):
        order = self.client.place_limit_order('sell', 'btcusd', 0.001, 123000)

        status = self.client.cancel_order(order['orderId'], order['symbol'])
        self.assertTrue(status)
        orders = self.client.open_orders()
        self.assertTrue(order['orderId'] not in [x['orderId'] for x in orders])

    def test_cancel_multiple_orders(self):
        order1 = self.client.place_limit_order('sell', 'btcusd', 0.001, 123000)
        order2 = self.client.place_limit_order('sell', 'btcusd', 0.001, 125000)

        status = self.client.cancel_multiple_orders([order1['orderId'], order2['orderId']])
        self.assertTrue(status)
        orders = self.client.open_orders()
        self.assertTrue(order1['orderId'] not in [x['orderId'] for x in orders])
        self.assertTrue(order2['orderId'] not in [x['orderId'] for x in orders])

    def test_cancel_all_orders(self):
        order1 = self.client.place_limit_order('sell', 'btcusd', 0.001, 123000)
        order2 = self.client.place_limit_order('sell', 'btcusd', 0.001, 125000)
        order3 = self.client.place_limit_order('sell', 'btcusd', 0.001, 127000)

        status = self.client.cancel_all_orders()
        self.assertTrue(status)
        orders = self.client.open_orders()
        self.assertTrue(order1['orderId'] not in [x['orderId'] for x in orders])
        self.assertTrue(order2['orderId'] not in [x['orderId'] for x in orders])
        self.assertTrue(order3['orderId'] not in [x['orderId'] for x in orders])


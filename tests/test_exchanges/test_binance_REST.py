import unittest
from os import path
from time import time
from exchanges.REST.binance import BinanceRESTClient
from exchanges.exception import ExchangeException


class BinanceRESTPublicClientTestCase(unittest.TestCase):
    client = BinanceRESTClient()

    def test_ping(self):
        self.assertTrue(self.client.ping())

    def test_quote_currencies(self):
        currencies = self.client.quote_currencies()
        self.assertIs(type(currencies), list)
        self.assertTrue('BTC' in currencies)
        self.assertTrue('USDT' in currencies)

    def test_symbols(self):
        try:
            symbols = self.client.symbols()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(symbols), list)
        self.assertTrue('BTCUSDT' in symbols)
        self.assertTrue('BNBBTC' in symbols)

    def test_symbols_details(self):
        try:
            symbols_details = self.client.symbols_details()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(symbols_details), dict)
        self.assertTrue('BTCUSDT' in symbols_details)
        self.assertEqual(symbols_details['BTCUSDT']['baseAsset'], 'BTC')
        self.assertEqual(symbols_details['BTCUSDT']['quoteAsset'], 'USDT')
        self.assertEqual(symbols_details['BTCUSDT']['minAmount'], '0.00000100')

    def test_candle_intervals(self):
        try:
            intervals = self.client.candle_intervals()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(intervals), list)
        self.assertTrue('1m' in intervals)

    def test_ticker(self):
        try:
            ticker = self.client.ticker('BTCUSDT')
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
        self.assertTrue('BTCUSDT' in tickers)
        self.assertIs(type(tickers['BTCUSDT']), list)
        self.assertEqual(len(tickers['BTCUSDT']), 8)

    def test_order_book(self):
        try:
            book = self.client.order_book('BTCUSDT')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(book), dict)
        self.assertTrue('bids' in book)
        self.assertTrue('asks' in book)

    def test_trades(self):
        try:
            trades = self.client.trades('BTCUSDT')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(trades), list)
        self.assertIs(type(trades[0]), list)
        self.assertEqual(len(trades[0]), 4)
        self.assertTrue('buy' in trades[0] or 'sell' in trades[0])

    def test_candles(self):
        # this also covers testing the historical_candles method
        try:
            candles = self.client.candles('BTCUSDT', '1m', startTime=1560696720000, endTime=1560696780000)
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(candles), list)
        self.assertListEqual(candles[0], [1560696720000, "9215.67000000", "9230.00000000",
                                          "9215.01000000", "9226.26000000", "38.22828700"])


class BinanceRESTAuthenticatedClientTestCase(unittest.TestCase):
    client = None
    placed_orders = []

    @classmethod
    def setUpClass(cls) -> None:
        key_file = 'exchanges/api_keys/binance.key'
        if not path.exists(key_file) or not path.isfile(key_file):
            print("Testing Binance authenticated channels requires an API key!")
            print("Please, provide the key file named 'binance.key' in the exchanges/api_keys folder.")
            raise unittest.SkipTest('Key file not found or invalid!')
        cls.client = BinanceRESTClient(key_file=key_file)
        if not cls.client.authenticated:
            raise unittest.SkipTest('Authentication failed using given key file!')

    @classmethod
    def tearDownClass(cls) -> None:
        for order in cls.placed_orders:
            cls.client.cancel_order(order['orderId'], order['symbol'])

    def test_server_time(self):
        server_time = self.client.server_time()
        self.assertIsNotNone(server_time)
        self.assertIs(type(server_time), int)
        current_time = time()
        self.assertTrue(current_time - 30 < server_time // 1000 <= current_time)

    def test_balances(self):
        balances = self.client.balance()
        self.assertIsNotNone(balances)
        self.assertIs(type(balances), dict)
        self.assertTrue('BTC' in balances.keys())
        self.assertTrue('USDT' in balances.keys())

    def test_user_trades(self):
        try:
            self.client.user_trades()
            self.fail('Exception not raised for invalid call to user_trades!')
        except ExchangeException:
            pass
        trades = self.client.user_trades('BNBBTC', limit=10)
        self.assertIsNotNone(trades)
        self.assertIs(type(trades), list)
        self.assertIs(type(trades[0]), dict)
        self.assertTrue('orderId' in trades[0].keys())
        self.assertTrue('price' in trades[0].keys())
        self.assertTrue('amount' in trades[0].keys())
        self.assertTrue('side' in trades[0].keys())
        self.assertTrue(trades[0]['side'] == 'buy' or trades[0]['side'] == 'sell')

    def test_limit_order(self):
        try:
            order = self.client.place_limit_order('buy', 'bnbbtc', 1, 0.0010655)
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
            self.client.place_limit_order('buy', 'bnbbtc', 10000000000000, 0.0010655)
            self.fail('Exception not raised for invalid limit order amount!')
        except ExchangeException:
            pass
        try:
            self.client.place_limit_order('buy', 'bnbbtc', 1, 0.00000001)
            self.fail('Exception not raised for invalid limit order price!')
        except ExchangeException:
            pass

    def test_single_order_status(self):
        order = self.client.place_limit_order('buy', 'bnbbtc', 1, 0.0010655)
        self.placed_orders.append(order)

        status = self.client.order(order['orderId'], 'BNBBTC')
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
        self.assertEqual(status['symbol'], 'BNBBTC')
        self.assertEqual(status['orderId'], order['orderId'])
        self.assertEqual(status['price'], '0.00106550')
        self.assertEqual(status['amount'], '1.00000000')
        self.assertEqual(status['type'], 'LIMIT')
        self.assertEqual(status['side'], 'BUY')
        self.assertEqual(status['status'], 'LIVE')

    def test_open_orders(self):
        order = self.client.place_limit_order('buy', 'bnbbtc', 1, 0.0010655)
        self.placed_orders.append(order)

        orders = self.client.open_orders()
        self.assertIsNotNone(orders)
        self.assertIs(type(orders), list)
        self.assertGreaterEqual(len(orders), 1)
        self.assertIs(type(orders[0]), dict)
        self.assertTrue(order['orderId'] in [x['orderId'] for x in orders])

    def test_open_orders_for_symbol(self):
        order = self.client.place_limit_order('buy', 'bnbbtc', 1, 0.0010655)
        self.placed_orders.append(order)

        orders = self.client.open_orders_for('BNBBTC')
        self.assertIsNotNone(orders)
        self.assertIs(type(orders), list)
        self.assertGreaterEqual(len(orders), 1)
        self.assertIs(type(orders[0]), dict)
        self.assertTrue(order['orderId'] in [x['orderId'] for x in orders])
        symbols = set([x['symbol'] for x in orders])
        self.assertEqual(len(symbols), 1)
        self.assertTrue('BNBBTC' in symbols)
        statuses = set([x['status'] for x in orders])
        self.assertEqual(len(statuses), 1)
        self.assertTrue('LIVE' in statuses, f'{statuses}\n{orders}')

    def test_all_orders(self):
        order = self.client.place_limit_order('buy', 'bnbbtc', 1, 0.0010655)
        self.placed_orders.append(order)

        orders = self.client.all_orders('BNBBTC', limit=10)
        self.assertIsNotNone(orders)
        self.assertIs(type(orders), list)
        self.assertGreaterEqual(len(orders), 1)
        self.assertIs(type(orders[0]), dict)
        self.assertTrue(order['orderId'] in [x['orderId'] for x in orders])
        symbols = set([x['symbol'] for x in orders])
        self.assertEqual(len(symbols), 1)
        self.assertTrue('BNBBTC' in symbols)

    def test_all_orders_since(self):
        order1 = self.client.place_limit_order('buy', 'bnbbtc', 1, 0.00106)
        order2 = self.client.place_limit_order('buy', 'bnbbtc', 1, 0.00103)
        self.placed_orders.append(order1)
        self.placed_orders.append(order2)

        orders = self.client.all_orders_since(order1['symbol'], order1['orderId'])
        self.assertIsNotNone(orders)
        self.assertIs(type(orders), list)
        self.assertGreaterEqual(len(orders), 1)
        self.assertIs(type(orders[0]), dict)
        self.assertTrue(order1['orderId'] in [x['orderId'] for x in orders])
        self.assertTrue(order2['orderId'] in [x['orderId'] for x in orders])
        symbols = set([x['symbol'] for x in orders])
        self.assertEqual(len(symbols), 1)
        self.assertTrue('BNBBTC' in symbols)

    def test_cancel_order(self):
        order = self.client.place_limit_order('buy', 'bnbbtc', 1, 0.0010655)

        status = self.client.cancel_order(order['orderId'], order['symbol'])
        self.assertTrue(status)
        orders = self.client.open_orders()
        self.assertTrue(order['orderId'] not in [x['orderId'] for x in orders])




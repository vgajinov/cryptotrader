import unittest
import time
from os import path
from collections import OrderedDict, deque
from exchanges.WS.bitfinex import *


class BitfinexWSDataTestCase(unittest.TestCase):

    def test_bitfinex_ticker(self):
        bfx_ticker = BitfinexTicker('dummy', [9074, 22.465169779999997, 9074.1, 30.91619495, -308.9,
                                              -0.0329, 9074.1, 12269.91735779, 9490, 8956.2])
        self.assertEqual(bfx_ticker.name, 'dummy')
        self.assertIs(type(bfx_ticker.data[0]), float)
        self.assertListEqual(bfx_ticker.data, [9074, 22.465169779999997, 9074.1, 30.91619495, -308.9,
                                               -0.0329, 9074.1, 12269.91735779, 9490, 8956.2])
        snapshot = bfx_ticker.snapshot()
        self.assertIs(type(snapshot), list)
        self.assertListEqual(snapshot, [9074, 22.465169779999997, 9074.1, 30.91619495, -308.9,
                                        -0.0329, 9074.1, 12269.91735779, 9490, 8956.2])


    def test_bitfinex_order_book_init(self):
        bfx_book = BitfinexOrderBook('dummy', [[9085.7, 1, 0.5], [9085.4, 2, 0.1567], [9084.7, 1, 0.15],
                                               [9097, 2, -0.14315086], [9100.6, 1, -1.25], [9101, 1, -0.62]])
        self.assertEqual(bfx_book.name, 'dummy')
        self.assertIs(type(bfx_book.bids), dict)
        self.assertIs(type(list(bfx_book.bids.keys())[0]), float)
        self.assertIs(type(list(bfx_book.bids.values())[-1]), float)
        self.assertIs(type(list(bfx_book.asks.keys())[0]), float)
        self.assertIs(type(list(bfx_book.asks.values())[-1]), float)
        self.assertEqual(len(bfx_book.bids), 3)
        self.assertEqual(len(bfx_book.asks), 3)
        self.assertEqual(bfx_book.bids[9085.7], 0.5)
        self.assertEqual(bfx_book.asks[9100.6], 1.25)


    def test_bitfinex_order_book_update(self):
        def check_key(dct, key):
            return dct[key]

        bfx_book = BitfinexOrderBook('dummy', [[9085.7, 1, 0.5], [9085.4, 2, 0.1567], [9084.7, 1, 0.15],
                                               [9097, 2, -0.14315086], [9100.6, 1, -1.25], [9101, 1, -0.62]])
        # remove a price from bids
        #    first test wrong combination of values for count and amount
        bfx_book.update([9085.7, 0, 0.5])
        self.assertEqual(len(bfx_book.bids), 3)
        #    now do it right
        bfx_book.update([9085.7, 0, 1])
        self.assertEqual(len(bfx_book.bids), 2)
        self.assertRaises(KeyError, check_key, bfx_book.bids, 9085.7)
        # remove a price form asks
        bfx_book.update([9100.6, 0, -1])
        self.assertEqual(len(bfx_book.asks), 2)
        self.assertRaises(KeyError, check_key, bfx_book.bids, 9100.6)
        # update a price from bids
        bfx_book.update([9084.7, 3, 0.675])
        self.assertEqual(len(bfx_book.bids), 2)
        self.assertEqual(bfx_book.bids[9084.7], 0.675)


    def test_bitfinex_order_book_sort(self):
        bfx_book = BitfinexOrderBook('dummy', [[9085.7, 1, 0.5], [9085.4, 2, 0.1567], [9084.7, 1, 0.15],
                                               [9097, 2, -0.14315086], [9100.6, 1, -1.25], [9101, 1, -0.62]])
        bids, asks = bfx_book._sort_book()
        self.assertIs(type(bids), OrderedDict)
        self.assertIs(type(asks), OrderedDict)
        self.assertListEqual(list(bids.keys()), [9084.7, 9085.4, 9085.7])
        self.assertListEqual(list(asks.keys()), [9097.0, 9100.6, 9101.0])
        bfx_book.update([9085.5, 3, 0.675])
        bids, asks = bfx_book._sort_book()
        self.assertListEqual(list(bids.keys()), [9084.7, 9085.4, 9085.5, 9085.7])


    def test_bitfinex_order_book_snapshot(self):
        bfx_book = BitfinexOrderBook('dummy', [[9085.7, 1, 0.5], [9085.4, 2, 0.1567], [9084.7, 1, 0.15],
                                               [9097, 2, -0.14315086], [9100.6, 1, -1.25], [9101, 1, -0.62]])
        snapshot = bfx_book.snapshot()
        self.assertIs(type(snapshot), dict)
        self.assertTrue('bids' in snapshot.keys())
        self.assertTrue('asks' in snapshot.keys())
        self.assertIs(type(snapshot['bids']), OrderedDict)
        self.assertIs(type(snapshot['asks']), OrderedDict)
        self.assertEqual(snapshot['bids'][9084.7], 0.15)
        self.assertEqual(snapshot['asks'][9097], 0.14315086)


    def test_bitfinex_trades_init(self):
        bfx_trades = BitfinexTrades('dummy', [[368737789, 1561056827798, -0.03, 9444.4],
                                              [368737774, 1561056823931, -0.5, 9444.6],
                                              [368737772, 1561056823759, 0.07130439, 9447.9],
                                              [368737773, 1561056823759, 0.03452574, 9448]])
        self.assertEqual(bfx_trades.name, 'dummy')
        self.assertIs(type(bfx_trades.trades), deque)
        self.assertIs(type(bfx_trades.trades[0]), list)
        self.assertEqual(len(bfx_trades.trades[0]), 3)
        self.assertIs(type(bfx_trades.trades[0][0]), int)
        self.assertIs(type(bfx_trades.trades[0][1]), float)
        self.assertIs(type(bfx_trades.trades[0][2]), float)
        self.assertEqual(bfx_trades.trades[0][0], 1561056827798)
        self.assertEqual(bfx_trades.trades[0][2], 9444.4)
        self.assertTrue(bfx_trades.trades[0][0] >= bfx_trades.trades[1][0])


    def test_bitfinex_trades_update(self):
        bfx_trades = BitfinexTrades('dummy', [[368737789, 1561056827798, -0.03, 9444.4],
                                              [368737774, 1561056823931, -0.5, 9444.6],
                                              [368737772, 1561056823759, 0.07130439, 9447.9],
                                              [368737773, 1561056823759, 0.03452574, 9448]])
        bfx_trades.update([368737791, 1561056829759, -0.12, 9444.4])
        self.assertEqual(len(bfx_trades.trades), 5)
        self.assertEqual(bfx_trades.trades[0][0], 1561056829759)
        for i in range(4):
            self.assertTrue(bfx_trades.trades[i][0] >= bfx_trades.trades[i+1][0], 'Order of trades violated for i = {}'.format(i))


    def test_bitfinex_trades_snapshot(self):
        bfx_trades = BitfinexTrades('dummy', [[368737789, 1561056827798, -0.03, 9444.4],
                                              [368737774, 1561056823931, -0.5, 9444.6],
                                              [368737772, 1561056823759, 0.07130439, 9447.9],
                                              [368737773, 1561056823759, 0.03452574, 9448]])
        bfx_trades.update([368737791, 1561056829759, -0.12, 9444.4])
        snapshot = bfx_trades.snapshot()
        self.assertIs(type(snapshot), tuple)
        self.assertEqual(snapshot[0], 'snapshot')
        self.assertIs(type(snapshot[1]), list)
        snapshot_data = snapshot[1]
        self.assertEqual(len(snapshot_data), 5)
        for i in range(len(snapshot_data)-1):
            self.assertTrue(snapshot_data[i][0] >= snapshot_data[i+1][0],
                            'Order of trades violated for i = {}'.format(i))


    def test_bitfinex_candles_init(self):
        bfx_candles = BitfinexCandles('dummy', [[1561128240000, 9808.2, 9808.90200952, 9811.9, 9807, 1.14],
                                                [1561128180000, 9802.1, 9808.5, 9811.5, 9797.1, 8.73577243],
                                                [1561128120000, 9801.3, 9802.5, 9803.1, 9801.3, 0.77115941],
                                                [1561128060000, 9805, 9802.6, 9807.05397991, 9800, 11.87870475]])
        self.assertEqual(bfx_candles.name, 'dummy')
        self.assertIs(type(bfx_candles.candles), deque)
        self.assertIs(type(bfx_candles.candles[0]), list)
        self.assertEqual(len(bfx_candles.candles[0]), 6)
        self.assertIs(type(bfx_candles.candles[0][0]), int)
        self.assertIs(type(bfx_candles.candles[0][1]), float)
        self.assertIs(type(bfx_candles.candles[0][2]), float)
        self.assertEqual(bfx_candles.candles[0][0], 1561128060000)
        self.assertEqual(bfx_candles.candles[0][2], 9807.05397991)
        self.assertTrue(bfx_candles.candles[0][0] < bfx_candles.candles[1][0])


    def test_bitfinex_candles_update(self):
        bfx_candles = BitfinexCandles('dummy', [[1561128240000, 9808.2, 9808.90200952, 9811.9, 9807, 1.14],
                                                [1561128180000, 9802.1, 9808.5, 9811.5, 9797.1, 8.73577243],
                                                [1561128120000, 9801.3, 9802.5, 9803.1, 9801.3, 0.77115941],
                                                [1561128060000, 9805, 9802.6, 9807.05397991, 9800, 11.87870475]])
        bfx_candles.update([1561128300000, 9816.5, 9807.3, 9820.3, 9807.3, 9.31694635])
        self.assertEqual(len(bfx_candles.candles), 5)
        self.assertEqual(bfx_candles.candles[-1][0], 1561128300000)
        for i in range(4):
            self.assertTrue(bfx_candles.candles[i][0] < bfx_candles.candles[i+1][0],
                            'Order of candles violated for i = {}'.format(i))


    def test_bitfinex_candles_snapshot(self):
        bfx_candles = BitfinexCandles('dummy', [[1561128240000, 9808.2, 9808.90200952, 9811.9, 9807, 1.14],
                                                [1561128180000, 9802.1, 9808.5, 9811.5, 9797.1, 8.73577243],
                                                [1561128120000, 9801.3, 9802.5, 9803.1, 9801.3, 0.77115941],
                                                [1561128060000, 9805, 9802.6, 9807.05397991, 9800, 11.87870475]])
        bfx_candles.update([1561128300000, 9816.5, 9807.3, 9820.3, 9807.3, 9.31694635])
        snapshot = bfx_candles.snapshot()
        self.assertIs(type(snapshot), tuple)
        self.assertEqual(snapshot[0], 'snapshot')
        self.assertIs(type(snapshot[1]), list)
        snapshot_data = snapshot[1]
        self.assertEqual(len(snapshot_data), 5)
        for i in range(len(snapshot_data)-1):
            self.assertTrue(snapshot_data[i][0] < snapshot_data[i+1][0],
                            'Order of trades violated for i = {}'.format(i))


class BitfinexWSPublicClientTestCase(unittest.TestCase):
    client = None

    @staticmethod
    def handle_info(sender, data):
        pass

    @classmethod
    def setUpClass(cls) -> None:
        # Bitfinex websocket is completely asynchronous, so we use 1s sleep after each request (subscribe ...)
        # This may fail because the wait was too short for the message to arrive!
        cls.client = BitfinexWSClient()
        cls.client.connect(BitfinexWSPublicClientTestCase.handle_info)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.disconnect()


    def test_ticker(self):
        def handle_update(sender, data):
            if sender != 'bitfinex':
                self.fail('Wrong sender for a Bitfinex update handler!')

        # test the subscription is successful and that the data for the stream is properly setup
        stream, snapshot  = self.client.subscribe_ticker('BTCUSD', update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(stream in self.client._subscriptions.values())
        self.assertEqual(len(self.client._data), 1)
        stream_id = [ key for (key, value) in self.client._subscriptions.items() if value == stream][0]
        ticker = self.client._data[stream_id]
        self.assertIsNotNone(ticker)
        self.assertIs(type(ticker.data), list)
        self.assertTrue(len(ticker.data) > 0)

        # test that the second subscriber will reuse the stream already used by the first subscriber
        stream2, snapshot2 = self.client.subscribe_ticker('BTCUSD', update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(stream2 in self.client._subscriptions.values())
        self.assertEqual(len(self.client._data), 1)

        # test that unsubscribe properly updates the client dictionaries
        self.client.unsubscribe(stream, update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 0)
        self.assertEqual(len(self.client._data), 0)


    def test_order_book(self):
        def handle_update(sender, data):
            if sender != 'bitfinex':
                self.fail('Wrong sender for a Bitfinex update handler!')

        # test the subscription is successful and that the data for the stream is properly setup
        stream, snapshot  = self.client.subscribe_order_book('BTCUSD', update_handler=handle_update)
        time.sleep(3)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(stream in self.client._subscriptions.values())
        self.assertEqual(len(self.client._data), 1)
        stream_id = [ key for (key, value) in self.client._subscriptions.items() if value == stream][0]
        book = self.client._data[stream_id]
        self.assertIsNotNone(book)
        self.assertIs(type(book.asks), dict)
        self.assertTrue(len(book.asks) > 0)

        # test that the second subscriber will reuse the stream already used by the first subscriber
        stream2, snapshot2 = self.client.subscribe_order_book('BTCUSD', update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(stream2 in self.client._subscriptions.values())
        self.assertEqual(len(self.client._data), 1)

        # test that unsubscribe properly updates the client dictionaries
        self.client.unsubscribe(stream, update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 0)
        self.assertEqual(len(self.client._data), 0)


    def test_trades(self):
        def handle_update(sender, data):
            if sender != 'bitfinex':
                self.fail('Wrong sender for a Bitfinex update handler!')

        # test the subscription is successful and that the data for the stream is properly setup
        stream, snapshot  = self.client.subscribe_trades('BTCUSD', update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(stream in self.client._subscriptions.values())
        self.assertEqual(len(self.client._data), 1)
        stream_id = [ key for (key, value) in self.client._subscriptions.items() if value == stream][0]
        trades = self.client._data[stream_id]
        self.assertIsNotNone(trades)
        self.assertIs(type(trades.trades), deque)
        self.assertTrue(len(trades.trades) > 0)

        # test that the second subscriber will reuse the stream already used by the first subscriber
        stream2, snapshot2 = self.client.subscribe_trades('BTCUSD', update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(stream2 in self.client._subscriptions.values())
        self.assertEqual(len(self.client._data), 1)

        # test that unsubscribe properly updates the client dictionaries
        self.client.unsubscribe(stream, update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 0)
        self.assertEqual(len(self.client._data), 0)


    def test_candles(self):
        def handle_update(sender, data):
            if sender != 'bitfinex':
                self.fail('Wrong sender for a Bitfinex update handler!')

        # test the subscription is successful and that the data for the stream is properly setup
        stream, snapshot  = self.client.subscribe_candles('BTCUSD', update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(stream in self.client._subscriptions.values())
        self.assertEqual(len(self.client._data), 1)
        stream_id = [ key for (key, value) in self.client._subscriptions.items() if value == stream][0]
        candles = self.client._data[stream_id]
        self.assertIsNotNone(candles)
        self.assertIs(type(candles.candles), deque)
        self.assertTrue(len(candles.candles) > 0)

        # test that the second subscriber will reuse the stream already used by the first subscriber
        stream2, snapshot2 = self.client.subscribe_candles('BTCUSD', update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(stream2 in self.client._subscriptions.values())
        self.assertEqual(len(self.client._data), 1)

        # test that unsubscribe properly updates the client dictionaries
        self.client.unsubscribe(stream, update_handler=handle_update)
        time.sleep(1)
        self.assertEqual(len(self.client._subscriptions), 0)
        self.assertEqual(len(self.client._data), 0)


class BitfinexWSAuthenticatedClientTestCase(unittest.TestCase):
    client = None

    @staticmethod
    def handle_info(sender, data):
        pass

    @classmethod
    def setUpClass(cls) -> None:
        key_file = 'exchanges/api_keys/bitfinex.key'
        if not path.exists(key_file) or not path.isfile(key_file):
            print("Testing Bitfinex authenticated channels requires an API key!")
            print("Please, provide the key file named 'bitfinex.key' in the exchanges/api_keys folder.")
            raise unittest.SkipTest('Key file not found or invalid!')

        cls.client = BitfinexWSClient()
        cls.client.connect(BitfinexWSPublicClientTestCase.handle_info)

        cls.client.authenticate(key_file=key_file)
        time.sleep(2)
        if not cls.client.authenticated:
            raise unittest.SkipTest('Authentication failed using given key file!')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.disconnect()

    def test_authenticate(self):
        self.assertIsNotNone(self.client._orders)
        self.assertTrue(len(self.client._balances) > 0)

    def test_balances(self):
        def handle_update(sender, data):
            if sender != 'bitfinex':
                self.fail('Wrong sender for a Bitfinex update handler!')

        # test the subscription is successful and that the data for the stream is properly setup
        stream = self.client.subscribe_balances(update_handler=handle_update)
        time.sleep(1)
        self.assertIsNotNone(self.client._balances)
        self.assertTrue(len(self.client._balances) > 0)


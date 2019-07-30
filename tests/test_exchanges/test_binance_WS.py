import unittest
from os import path
import time
from collections import OrderedDict, deque
from exchanges.WS.binance import *


class BinanceWSDataTestCase(unittest.TestCase):

    def test_binance_ticker(self):
        binance_ticker = BinanceTicker('dummy')
        self.assertEqual(binance_ticker.name, 'dummy')
        self.assertIs(type(binance_ticker.data), list)
        self.assertListEqual(binance_ticker.data, [])
        binance_ticker.update({
                                  "e": "24hrTicker",  # Event type
                                  "E": 123456789,     # Event time
                                  "s": "BNBBTC",      # Symbol
                                  "p": "0.0015",      # Price change
                                  "P": "250.00",      # Price change percent
                                  "w": "0.0018",      # Weighted average price
                                  "x": "0.0009",      # first trade before the 24hr rolling window
                                  "c": "0.0025",      # Last price
                                  "Q": "10",          # Last quantity
                                  "b": "0.0024",      # Best bid price
                                  "B": "10",          # Best bid quantity
                                  "a": "0.0026",      # Best ask price
                                  "A": "100",         # Best ask quantity
                                  "o": "0.0010",      # Open price
                                  "h": "0.0025",      # High price
                                  "l": "0.0010",      # Low price
                                  "v": "10000",       # Total traded base asset volume
                                  "q": "18",          # Total traded quote asset volume
                                  "O": 0,             # Statistics open time
                                  "C": 86400000,      # Statistics close time
                                  "F": 0,             # First trade ID
                                  "L": 18150,         # Last trade Id
                                  "n": 18151          # Total number of trades
                              })
        self.assertListEqual(binance_ticker.data, [0.0024, 10, 0.0026, 100, 0.0015, 250.0, 0.0025, 10000, 0.0025, 0.001])
        snapshot = binance_ticker.snapshot()
        self.assertIs(type(snapshot), list)
        self.assertListEqual(snapshot, [0.0024, 10, 0.0026, 100, 0.0015, 250.0, 0.0025, 10000, 0.0025, 0.001])


    def test_binance_order_book_init(self):
        binance_book = BinanceOrderBook('dummy', {"lastUpdateId": 731076714,
                                                  "bids": [["9888.29000000", "0.45293400"],
                                                           ["9888.25000000", "0.05848600"],
                                                           ["9888.24000000", "0.02594000"]],
                                                  "asks": [["9889.41000000", "0.09927600"],
                                                           ["9890.44000000", "0.02830100"],
                                                           ["9890.79000000", "0.15400000"]]
                                                  })
        self.assertEqual(binance_book.name, 'dummy')
        self.assertEqual(binance_book.lastUpdateId, 731076714)
        self.assertIs(type(binance_book.bids), dict)
        self.assertIs(type(list(binance_book.bids.keys())[0]), float)
        self.assertIs(type(list(binance_book.bids.values())[-1]), float)
        self.assertIs(type(list(binance_book.asks.keys())[0]), float)
        self.assertIs(type(list(binance_book.asks.values())[-1]), float)
        self.assertEqual(len(binance_book.bids), 3)
        self.assertEqual(len(binance_book.asks), 3)
        self.assertEqual(binance_book.bids[9888.29], 0.452934)
        self.assertEqual(binance_book.asks[9890.79], 0.154)


    def test_binance_order_book_update(self):
        def check_key(dct, key):
            return dct[key]

        binance_book = BinanceOrderBook('dummy', {"lastUpdateId": 731076714,
                                                  "bids": [["9888.29000000", "0.45293400"],
                                                           ["9888.25000000", "0.05848600"],
                                                           ["9888.24000000", "0.02594000"]],
                                                  "asks": [["9889.41000000", "0.09927600"],
                                                           ["9890.44000000", "0.02830100"],
                                                           ["9890.79000000", "0.15400000"]]
                                                  })
        test_update = {
            "e": "depthUpdate",        # Event type
            "E": 123456789,            # Event time
            "s": "BTCUSDT",            # Symbol
            "U": 731076704,            # First update ID in event
            "u": 731076710,            # Final update ID in event
            # Bids to be updated
            "b": [["9888.25000000", "1.34000000"], ["9888.31000000", "0.04320000"]],
            # Asks to be updated
            "a": [["9890.44000000", "0"]]
        }
        # test if the old update is ignored
        binance_book.update(test_update)
        self.assertEqual(len(binance_book.bids), 3)
        self.assertListEqual(list(binance_book.bids.values()), [0.452934, 0.058486, 0.02594])
        self.assertEqual(len(binance_book.asks), 3)
        self.assertListEqual(list(binance_book.asks.keys()), [9889.41, 9890.44, 9890.79])

        # now test an actual update
        test_update['u'] = 731076720
        binance_book.update(test_update)
        self.assertEqual(len(binance_book.bids), 4)
        self.assertListEqual(list(binance_book.bids.values()), [0.452934, 1.34, 0.02594, 0.0432])
        # one price level from the asks should be removed (amount == 0)
        self.assertEqual(len(binance_book.asks), 2)
        self.assertRaises(KeyError, check_key, binance_book.bids, 9890.44)
        self.assertListEqual(list(binance_book.asks.keys()), [9889.41, 9890.79])


    def test_binance_order_book_sort(self):
        binance_book = BinanceOrderBook('dummy', {"lastUpdateId": 731076714,
                                                  "bids": [["9888.29000000", "0.45293400"],
                                                           ["9888.25000000", "0.05848600"],
                                                           ["9888.24000000", "0.02594000"]],
                                                  "asks": [["9889.41000000", "0.09927600"],
                                                           ["9890.44000000", "0.02830100"],
                                                           ["9890.79000000", "0.15400000"]]
                                                  })
        bids, asks = binance_book._sort_book()
        self.assertIs(type(bids), OrderedDict)
        self.assertIs(type(asks), OrderedDict)
        self.assertListEqual(list(bids.keys()), [9888.24, 9888.25, 9888.29])
        self.assertListEqual(list(asks.keys()), [9889.41, 9890.44, 9890.79])
        test_update = {
            "e": "depthUpdate",        # Event type
            "E": 123456789,            # Event time
            "s": "BTCUSDT",            # Symbol
            "U": 731076714,            # First update ID in event
            "u": 731076720,            # Final update ID in event
            # Bids to be updated
            "b": [["9888.27000000", "0.04320000"]],
            # Asks to be updated
            "a": []
        }
        binance_book.update(test_update)
        bids, asks = binance_book._sort_book()
        self.assertListEqual(list(bids.keys()), [9888.24, 9888.25, 9888.27, 9888.29])


    def test_binance_order_book_snapshot(self):
        binance_book = BinanceOrderBook('dummy', {"lastUpdateId": 731076714,
                                                  "bids": [["9888.29000000", "0.45293400"],
                                                           ["9888.25000000", "0.05848600"],
                                                           ["9888.24000000", "0.02594000"]],
                                                  "asks": [["9889.41000000", "0.09927600"],
                                                           ["9890.44000000", "0.02830100"],
                                                           ["9890.79000000", "0.15400000"]]
                                                  })
        snapshot = binance_book.snapshot()
        self.assertIs(type(snapshot), dict)
        self.assertTrue('bids' in snapshot.keys())
        self.assertTrue('asks' in snapshot.keys())
        self.assertIs(type(snapshot['bids']), OrderedDict)
        self.assertIs(type(snapshot['asks']), OrderedDict)
        self.assertEqual(snapshot['bids'][9888.29], 0.452934)
        self.assertEqual(snapshot['asks'][9890.44], 0.028301)


    def test_binance_trades_init(self):
        binance_trades = BinanceTrades('dummy', [[1561150152842, "9869.99000000", "0.01023900", "buy"],
                                                 [1561150152854, "9868.52000000", "0.00202600", "sell"],
                                                 [1561150152913, "9869.99000000", "0.03398600", "buy"],
                                                 [1561150152913, "9870.00000000", "0.01147900", "buy"]])
        self.assertEqual(binance_trades.name, 'dummy')
        self.assertIs(type(binance_trades.trades), deque)
        self.assertIs(type(binance_trades.trades[0]), list)
        self.assertEqual(len(binance_trades.trades[0]), 3)
        self.assertIs(type(binance_trades.trades[0][0]), int)
        self.assertIs(type(binance_trades.trades[0][1]), float)
        self.assertIs(type(binance_trades.trades[0][2]), float)
        self.assertEqual(binance_trades.trades[0][0], 1561150152913)
        self.assertEqual(binance_trades.trades[2][1], -0.00202600)
        self.assertTrue(binance_trades.trades[0][0] >= binance_trades.trades[1][0])


    def test_binance_trades_update(self):
        binance_trades = BinanceTrades('dummy', [[1561150152842, "9869.99000000", "0.01023900", "buy"],
                                                 [1561150152854, "9868.52000000", "0.00202600", "sell"],
                                                 [1561150152913, "9869.99000000", "0.03398600", "buy"],
                                                 [1561150152913, "9870.00000000", "0.01147900", "buy"]])
        binance_trades.update({
            "e": "trade",          # Event type
            "E": 123456789,        # Event time
            "s": "BTCUSDT",        # Symbol
            "t": 12345,            # Trade ID
            "p": "9869.24000000",  # Price
            "q": "0.02363000",     # Quantity
            "b": 88,               # Buyer order ID
            "a": 50,               # Seller order ID
            "T": 1561150152956,    # Trade time
            "m": True,             # Is the buyer the market maker?
            "M": True              # Ignore
        })
        self.assertEqual(len(binance_trades.trades), 5)
        self.assertEqual(binance_trades.trades[0][0], 1561150152956)
        for i in range(4):
            self.assertTrue(binance_trades.trades[i][0] >= binance_trades.trades[i+1][0], 'Order of trades violated for i = {}'.format(i))


    def test_binance_trades_snapshot(self):
        binance_trades = BinanceTrades('dummy', [[1561150152842, "9869.99000000", "0.01023900", "buy"],
                                                 [1561150152854, "9868.52000000", "0.00202600", "sell"],
                                                 [1561150152913, "9869.99000000", "0.03398600", "buy"],
                                                 [1561150152913, "9870.00000000", "0.01147900", "buy"]])
        binance_trades.update({
            "e": "trade",          # Event type
            "E": 123456789,        # Event time
            "s": "BTCUSDT",        # Symbol
            "t": 12345,            # Trade ID
            "p": "9869.24000000",  # Price
            "q": "0.02363000",     # Quantity
            "b": 88,               # Buyer order ID
            "a": 50,               # Seller order ID
            "T": 1561150152956,    # Trade time
            "m": True,             # Is the buyer the market maker?
            "M": True              # Ignore
        })
        snapshot = binance_trades.snapshot()
        self.assertIs(type(snapshot), tuple)
        self.assertEqual(snapshot[0], 'snapshot')
        self.assertIs(type(snapshot[1]), list)
        snapshot_data = snapshot[1]
        self.assertEqual(len(snapshot_data), 5)
        for i in range(len(snapshot_data)-1):
            self.assertTrue(snapshot_data[i][0] >= snapshot_data[i+1][0],
                            'Order of trades violated for i = {}'.format(i))


    def test_binance_candles_init(self):
        binance_candles = BinanceCandles('dummy',
            [[1561239960000, "10623.26000000", "10625.00000000", "10620.10000000", "10623.05000000",
              "11.95821200", 1561240019999, "127042.21574730", 179, "5.70639000", "60626.14985316", "0"],
             [1561240020000, "10624.90000000", "10625.48000000", "10620.10000000", "10625.48000000",
              "10.43007700", 1561240079999, "110800.04655437", 167, "6.23521700", "66242.40878971", "0"],
             [1561240080000, "10625.00000000", "10633.25000000", "10622.73000000", "10625.31000000",
              "10.44544800", 1561240139999, "111003.83256628", 232, "6.08958800", "64717.90785306", "0"],
             [1561240140000, "10625.34000000", " 10632.10000000", "10617.36000000", "10626.14000000",
              "21.55120200", 1561240199999, "228973.71734709", 297, "10.58820700", "112507.52908365", "0"]])
        self.assertEqual(binance_candles.name, 'dummy')
        self.assertIs(type(binance_candles.candles), deque)
        self.assertIs(type(binance_candles.candles[0]), list)
        self.assertEqual(len(binance_candles.candles[0]), 6)
        self.assertIs(type(binance_candles.candles[0][0]), int)
        self.assertIs(type(binance_candles.candles[0][1]), float)
        self.assertIs(type(binance_candles.candles[0][2]), float)
        self.assertEqual(binance_candles.candles[0][0], 1561239960000)
        self.assertEqual(binance_candles.candles[0][2], 10625.0)
        self.assertTrue(binance_candles.candles[0][0] < binance_candles.candles[1][0])


    def test_binance_candles_update(self):
        binance_candles = BinanceCandles('dummy',
            [[1561239960000, "10623.26000000", "10625.00000000", "10620.10000000", "10623.05000000",
              "11.95821200", 1561240019999, "127042.21574730", 179, "5.70639000", "60626.14985316", "0"],
             [1561240020000, "10624.90000000", "10625.48000000", "10620.10000000", "10625.48000000",
              "10.43007700", 1561240079999, "110800.04655437", 167, "6.23521700", "66242.40878971", "0"],
             [1561240080000, "10625.00000000", "10633.25000000", "10622.73000000", "10625.31000000",
              "10.44544800", 1561240139999, "111003.83256628", 232, "6.08958800", "64717.90785306", "0"],
             [1561240140000, "10625.34000000", " 10632.10000000", "10617.36000000", "10626.14000000",
              "21.55120200", 1561240199999, "228973.71734709", 297, "10.58820700", "112507.52908365", "0"]])
        binance_candles.update(            {
              "e": "kline",                     # Event type
              "E": 123456789,                   # Event time
              "s": "BTCUSDT",                   # Symbol
              "k": {
                   "t": 1561240200000,          # Kline start time
                   "T": 1561240259999,          # Kline close time
                   "s": "BTCUSDT",              # Symbol
                   "i": "1m",                   # Interval
                   "f": 100,                    # First trade ID
                   "L": 200,                    # Last trade ID
                   "o": "10626.14000000",       # Open price
                   "c": "10629.23000000",       # Close price
                   "h": "10631.04000000",       # High price
                   "l": "10625.66000000",       # Low price
                   "v": "12.44544800",          # Base asset volume
                   "n": 192,                    # Number of trades
                   "x": False,                  # Is this kline closed?
                   "q": "1.0000",               # Quote asset volume
                   "V": "500",                  # Taker buy base asset volume
                   "Q": "0.500",                # Taker buy quote asset volume
                   "B": "123456"                # Ignore
              }
            })
        self.assertEqual(len(binance_candles.candles), 5)
        self.assertEqual(binance_candles.candles[-1][0], 1561240200000)
        for i in range(4):
            self.assertTrue(binance_candles.candles[i][0] < binance_candles.candles[i+1][0],
                            'Order of candles violated for i = {}'.format(i))


    def test_binance_candles_snapshot(self):
        binance_candles = BinanceCandles('dummy',
            [[1561239960000, "10623.26000000", "10625.00000000", "10620.10000000", "10623.05000000",
              "11.95821200", 1561240019999, "127042.21574730", 179, "5.70639000", "60626.14985316", "0"],
             [1561240020000, "10624.90000000", "10625.48000000", "10620.10000000", "10625.48000000",
              "10.43007700", 1561240079999, "110800.04655437", 167, "6.23521700", "66242.40878971", "0"],
             [1561240080000, "10625.00000000", "10633.25000000", "10622.73000000", "10625.31000000",
              "10.44544800", 1561240139999, "111003.83256628", 232, "6.08958800", "64717.90785306", "0"],
             [1561240140000, "10625.34000000", " 10632.10000000", "10617.36000000", "10626.14000000",
              "21.55120200", 1561240199999, "228973.71734709", 297, "10.58820700", "112507.52908365", "0"]])
        binance_candles.update(            {
              "e": "kline",                     # Event type
              "E": 123456789,                   # Event time
              "s": "BTCUSDT",                   # Symbol
              "k": {
                   "t": 1561240200000,          # Kline start time
                   "T": 1561240259999,          # Kline close time
                   "s": "BTCUSDT",              # Symbol
                   "i": "1m",                   # Interval
                   "f": 100,                    # First trade ID
                   "L": 200,                    # Last trade ID
                   "o": "10626.14000000",       # Open price
                   "c": "10629.23000000",       # Close price
                   "h": "10631.04000000",       # High price
                   "l": "10625.66000000",       # Low price
                   "v": "12.44544800",          # Base asset volume
                   "n": 192,                    # Number of trades
                   "x": False,                  # Is this kline closed?
                   "q": "1.0000",               # Quote asset volume
                   "V": "500",                  # Taker buy base asset volume
                   "Q": "0.500",                # Taker buy quote asset volume
                   "B": "123456"                # Ignore
              }
            })
        snapshot = binance_candles.snapshot()
        self.assertIs(type(snapshot), tuple)
        self.assertEqual(snapshot[0], 'snapshot')
        self.assertIs(type(snapshot[1]), list)
        snapshot_data = snapshot[1]
        self.assertEqual(len(snapshot_data), 5)
        for i in range(len(snapshot_data)-1):
            self.assertTrue(snapshot_data[i][0] < snapshot_data[i+1][0],
                            'Order of trades violated for i = {}'.format(i))


class BinanceWSPublicClientTestCase(unittest.TestCase):
    client = None

    @staticmethod
    def handle_info(sender, data):
        pass

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = BinanceWSClient()
        cls.client.connect(BinanceWSPublicClientTestCase.handle_info)

    @classmethod
    def tearDownClass(cls) -> None:
        time.sleep(2)
        cls.client.disconnect()


    def test_ticker(self):
        def handle_update(sender, data):
            if sender != 'binance':
                self.fail('Wrong sender for a Binance update handler!')

        # test the subscription is successful and that the data for the stream is properly setup
        stream, snapshot  = self.client.subscribe_ticker('BNBBTC', update_handler=handle_update)
        ticker = self.client._data[stream]
        self.assertIsNotNone(ticker)
        self.assertIs(type(ticker.data), list)
        self.assertEqual(len(self.client._subscriptions), 1)

        # test that the second subscriber will reuse the stream already used by the first subscriber
        stream2, snapshot2 = self.client.subscribe_ticker('BNBBTC', update_handler=handle_update)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertEqual(len(self.client._data), 1)
        time.sleep(2)

        # test that unsubscribe properly updates the client dictionaries
        self.client.unsubscribe(stream, update_handler=handle_update)
        self.assertEqual(len(self.client._subscriptions), 0)
        self.assertEqual(len(self.client._data), 0)


    def test_order_book(self):
        def handle_update(sender, data):
            if sender != 'binance':
                self.fail('Wrong sender for a Binance update handler!')

        # test the subscription is successful and that the data for the stream is properly setup
        stream, snapshot  = self.client.subscribe_order_book('BNBBTC', update_handler=handle_update)
        book = self.client._data[stream]
        self.assertIsNotNone(book)
        self.assertIs(type(book.asks), dict)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue('asks' in snapshot.keys())
        self.assertTrue('bids' in snapshot.keys())
        self.assertTrue(len(snapshot['asks']) > 0)
        self.assertTrue(len(snapshot['bids']) > 0)

        # test that the second subscriber will reuse the stream already used by the first subscriber
        stream2, snapshot2 = self.client.subscribe_order_book('BNBBTC', update_handler=handle_update)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertEqual(len(self.client._data), 1)
        time.sleep(2)

        # test that unsubscribe properly updates the client dictionaries
        self.client.unsubscribe(stream, update_handler=handle_update)
        self.assertEqual(len(self.client._subscriptions), 0)
        self.assertEqual(len(self.client._data), 0)


    def test_trades(self):
        def handle_update(sender, data):
            if sender != 'binance':
                self.fail('Wrong sender for a Binance update handler!')

        # test the subscription is successful and that the data for the stream is properly setup
        stream, snapshot  = self.client.subscribe_trades('BNBBTC', update_handler=handle_update)
        trades = self.client._data[stream]
        self.assertIsNotNone(trades)
        self.assertIs(type(trades.trades), deque)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(len(snapshot) > 0)

        # test that the second subscriber will reuse the stream already used by the first subscriber
        stream2, snapshot2 = self.client.subscribe_trades('BNBBTC', update_handler=handle_update)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertEqual(len(self.client._data), 1)
        time.sleep(2)

        # test that unsubscribe properly updates the client dictionaries
        self.client.unsubscribe(stream, update_handler=handle_update)
        self.assertEqual(len(self.client._subscriptions), 0)
        self.assertEqual(len(self.client._data), 0)


    def test_candles(self):
        def handle_update(sender, data):
            if sender != 'binance':
                self.fail('Wrong sender for a Binance update handler!')

        # test the subscription is successful and that the data for the stream is properly setup
        stream, snapshot  = self.client.subscribe_candles('BNBBTC', update_handler=handle_update)
        candles = self.client._data[stream]
        self.assertIsNotNone(candles)
        self.assertIs(type(candles.candles), deque)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertTrue(len(snapshot) > 0)

        # test that the second subscriber will reuse the stream already used by the first subscriber
        stream2, snapshot2 = self.client.subscribe_candles('BNBBTC', update_handler=handle_update)
        self.assertEqual(len(self.client._subscriptions), 1)
        self.assertEqual(len(self.client._data), 1)
        time.sleep(2)

        # test that unsubscribe properly updates the client dictionaries
        self.client.unsubscribe(stream, update_handler=handle_update)
        self.assertEqual(len(self.client._subscriptions), 0)
        self.assertEqual(len(self.client._data), 0)


class BinanceWSAuthenticatedClientTestCase(unittest.TestCase):
    client = None

    @staticmethod
    def handle_info(sender, data):
        pass

    @classmethod
    def setUpClass(cls) -> None:
        key_file = 'exchanges/api_keys/binance.key'
        if not path.exists(key_file) or not path.isfile(key_file):
            print("Testing Binance authenticated channels requires an API key!")
            print("Please, provide the key file named 'binance.key' in the exchanges/api_keys folder.")
            raise unittest.SkipTest('Key file not found or invalid!')

        cls.client = BinanceWSClient()
        cls.client.connect(BinanceWSPublicClientTestCase.handle_info)

        cls.client.authenticate(key_file=key_file)
        if not cls.client.authenticated:
            raise unittest.SkipTest('Authentication failed using given key file!')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.disconnect()

    def test_authenticate(self):
        self.assertIsNotNone(self.client._orders)
        self.assertTrue(len(self.client._balances) > 0)

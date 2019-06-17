import unittest
from exchanges.REST.binance import BinanceRESTClient

client = BinanceRESTClient()


class BinanceRESTClientTestCase(unittest.TestCase):
    cl = BinanceRESTClient()

    def test_ping(self):
        self.assertTrue(client.ping())

    def test_quote_currencies(self):
        currencies = client.quote_currencies()
        self.assertIs(type(currencies), list)
        self.assertTrue('BTC' in currencies)
        self.assertTrue('USDT' in currencies)

    def test_symbols(self):
        try:
            symbols = client.symbols()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(symbols), list)
        self.assertTrue('BTCUSDT' in symbols)
        self.assertTrue('BNBBTC' in symbols)

    def test_symbols_details(self):
        try:
            symbols_details = client.symbols_details()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(symbols_details), dict)
        self.assertTrue('BTCUSDT' in symbols_details)
        self.assertEqual(symbols_details['BTCUSDT']['baseAsset'], 'BTC')
        self.assertEqual(symbols_details['BTCUSDT']['quoteAsset'], 'USDT')
        self.assertEqual(symbols_details['BTCUSDT']['minAmount'], '0.00000100')

    def test_candle_intervals(self):
        try:
            intervals = client.candle_intervals()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(intervals), list)
        self.assertTrue('1m' in intervals)

    def test_ticker(self):
        try:
            ticker = client.ticker('BTCUSDT')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(ticker), list)
        self.assertEqual(len(ticker), 8)

    def test_all_tickers(self):
        try:
            tickers = client.all_tickers()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(tickers), dict)
        self.assertTrue('BTCUSDT' in tickers)
        self.assertIs(type(tickers['BTCUSDT']), list)
        self.assertEqual(len(tickers['BTCUSDT']), 8)

    def test_order_book(self):
        try:
            book = client.order_book('BTCUSDT')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(book), dict)
        self.assertTrue('bids' in book)
        self.assertTrue('asks' in book)

    def test_trades(self):
        try:
            trades = client.trades('BTCUSDT')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(trades), list)
        self.assertIs(type(trades[0]), list)
        self.assertEqual(len(trades[0]), 4)
        self.assertTrue('buy' in trades[0] or 'sell' in trades[0])

    def test_candles(self):
        # this also covers testing the historical_candles method
        try:
            candles = client.candles('BTCUSDT', '1m', startTime=1560696720000, endTime=1560696780000)
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(candles), list)
        self.assertListEqual(candles[0], [1560696720000, "9215.67000000", "9230.00000000",
                                          "9215.01000000", "9226.26000000", "38.22828700"])

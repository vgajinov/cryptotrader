import unittest
from exchanges.REST.bitfinex import BitfinexRESTClient

client = BitfinexRESTClient()


class BitfinexRESTClientTestCase(unittest.TestCase):

    def test_ping(self):
        self.assertTrue(client.ping())

    def test_quote_currencies(self):
        currencies = client.quote_currencies()
        self.assertIs(type(currencies), list)
        self.assertTrue('BTC' in currencies)
        self.assertTrue('USD' in currencies)

    def test_symbols(self):
        try:
            symbols = client.symbols()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(symbols), list)
        self.assertTrue('BTCUSD' in symbols)
        self.assertTrue('LTCBTC' in symbols)

    def test_symbols_details(self):
        try:
            symbols_details = client.symbols_details()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(symbols_details), dict)
        self.assertTrue('BTCUSD' in symbols_details)
        self.assertEqual(symbols_details['BTCUSD']['baseAsset'], 'BTC')
        self.assertEqual(symbols_details['BTCUSD']['quoteAsset'], 'USD')
        self.assertEqual(symbols_details['BTCUSD']['precision'], 5)

    def test_candle_intervals(self):
        try:
            intervals = client.candle_intervals()
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(intervals), list)
        self.assertTrue('1m' in intervals)

    def test_ticker(self):
        try:
            ticker = client.ticker('BTCUSD')
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
        self.assertTrue('BTCUSD' in tickers)
        self.assertIs(type(tickers['BTCUSD']), list)
        self.assertEqual(len(tickers['BTCUSD']), 8)

    def test_order_book(self):
        try:
            book = client.order_book('BTCUSD')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(book), dict)
        self.assertTrue('bids' in book)
        self.assertTrue('asks' in book)

    def test_trades(self):
        try:
            trades = client.trades('BTCUSD')
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(trades), list)
        self.assertIs(type(trades[0]), list)
        self.assertEqual(len(trades[0]), 4)
        self.assertTrue('buy' in trades[0] or 'sell' in trades[0])

    def test_candles(self):
        # this also covers testing the historical_candles method
        try:
            candles = client.candles('BTCUSD', '1m', start=1560696720000, end=1560696780000)
        except Exception as e:
            self.fail("Method threw an exception: {}".format(e))
        self.assertIs(type(candles), list)
        self.assertListEqual(candles[0], [1560696720000, 9261.33251778, 9269, 9260, 9269, 3.21300032])


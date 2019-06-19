import unittest
from collections import OrderedDict
from exchanges.WS.bitfinex import *


class BitfinexWSClientTestCase(unittest.TestCase):

    def test_bitfinex_ticker(self):
        bfx_ticker = BitfinexTicker('dummy', [9074, 22.465169779999997, 9074.1, 30.91619495, -308.9,
                                              -0.0329,9074.1, 12269.91735779, 9490, 8956.2])
        self.assertEqual(bfx_ticker.name, 'dummy')
        self.assertIs(type(bfx_ticker.data[0]), float)
        self.assertListEqual(bfx_ticker.data, [9074, 22.465169779999997, 9074.1, 30.91619495, -308.9,
                                               -0.0329,9074.1, 12269.91735779, 9490, 8956.2])


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
        self.assertEqual(bfx_book.asks[9100.6], -1.25)


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


    def test_order_book_sort(self):
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



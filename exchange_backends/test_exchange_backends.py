#!/usr/bin/env python
import sys
sys.path.insert(0, "./python-modules")

import unittest
import warnings
from exchange_backends.exchangeFactory import *

def ignore_warnings(test_func):
   def do_test(self, *args, **kwargs):
      with warnings.catch_warnings():
         warnings.simplefilter("ignore")
         test_func(self, *args, **kwargs)
   return do_test

class TestClassCreation(unittest.TestCase):

   @ignore_warnings
   def test_krakenClassExists(self):
      testObj = exchangeFactory().getExchange("kraken")

   @ignore_warnings
   def test_krakenTickerReturns(self):
      testObj = exchangeFactory().getExchange("kraken")
      self.assertIs(type(testObj.queryTicker("TMP")), dict)

if __name__ == '__main__':
    unittest.main()

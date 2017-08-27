#!/usr/bin/env python
import sys, os
sys.path.insert(0, "python-modules")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import unittest
import warnings
from exchangeFactory import *


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
   def test_krakenClassExistsWithKey(self):
      testObj = exchangeFactory().getExchange("kraken", keyfile="kraken.key")

class TestOrdersReturn(unittest.TestCase):
   @ignore_warnings
   def test_krakenTickerReturns(self):
      testObj = exchangeFactory().getExchange("kraken")
      self.assertIs(type(testObj.queryTicker("XXBTZ")), dict)

if __name__ == '__main__':
    unittest.main()

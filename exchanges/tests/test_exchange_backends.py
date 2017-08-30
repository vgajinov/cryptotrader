import unittest
import warnings
from exchanges import exchangeFactory
import os.path

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
   @unittest.skipUnless(os.path.isfile("kraken.key"), "Keyfile kraken.key does not exist")
   def test_krakenClassExistsWithKey(self):
      testObj = exchangeFactory().getExchange("kraken", keyfile="kraken.key")

class TestOrdersReturn(unittest.TestCase):
   @ignore_warnings
   def test_krakenTickerReturns(self):
      testObj = exchangeFactory().getExchange("kraken")
      self.assertIs(type(testObj.queryTicker("XXBTZEUR")), tuple)

if __name__ == '__main__':
    unittest.main()

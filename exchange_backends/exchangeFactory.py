from AutoTrader.exchange_backends.kraken.kraken import *


class exchangeFactory(object):

   def __init__(self):
      pass

   def getExchange(self, strExchange, params=[]):
      if strExchange == "kraken":
         return Kraken()
      else:
         raise Exception("Exchange not known")


from AutoTrader.exchange_backends.kraken.kraken import *


class exchangeFactory(object):

   def __init__(self):
      pass

<<<<<<< HEAD
   def getExchange(self, strExchange, params=[]):
      if strExchange == "kraken":
         return Kraken()
=======
   def getExchange(self, strExchange, **kwargs):
      if strExchange == "kraken":
         return wrapKraken(**kwargs)
>>>>>>> 69258120c3427f62e3704f9a4dba28f73749ae3c
      else:
         raise Exception("Exchange not known")


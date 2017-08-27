from .kraken.kraken import *
from .exchange import *

class exchangeFactory(object):

   def __init__(self):
      pass

   def getExchange(self, strExchange, **kwargs):
      if strExchange == "kraken":
         return Kraken(strExchange, **kwargs)
      else:
         raise Exception("Exchange not known")


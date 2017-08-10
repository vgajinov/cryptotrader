from .wrapKraken import *
from .exchange import *

class exchangeFactory(object):

   def __init__(self):
      pass

   def getExchange(self, strExchange):
      if strExchange == "kraken":
         return wrapKraken()
      else:
         raise Exception("Exchange not known")


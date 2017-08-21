import krakenex
from AutoTrader.exchange_backends.exchange import *


class Kraken(exchange):

   def __init__(self):
      self.k = krakenex.API()
      super().__init__()

   def queryTicker(self, curr):
      return self.k.query_public("Time")

   def addMarket(self, curr, vol):
      pass
   
   def sellMarket(self, curr, vol):
      pass

   def addMarketLmt(self, curr, vol, price):
      pass
   
   def sellMarketLmt(self, curr, vol, price):
      pass

   def queryOrder(self, orderID):
      pass

   def cancelOrder(self, orderID):
      pass


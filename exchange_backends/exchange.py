from abc import ABC, abstractmethod

class exchange(ABC):
   def __init__(self):
      super().__init__()

   @abstractmethod
   def queryTicker(self, curr):
      pass

   @abstractmethod
   def addMarket(self, curr, vol):
      pass
   
   @abstractmethod
   def sellMarket(self, curr, vol):
      pass

   @abstractmethod
   def addMarketLmt(self, curr, vol, price):
      pass
   
   @abstractmethod
   def sellMarketLmt(self, curr, vol, price):
      pass

   @abstractmethod
   def queryOrder(self, orderID):
      pass

   @abstractmethod
   def cancelOrder(self, orderID):
      pass


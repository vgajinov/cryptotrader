from abc import ABC, abstractmethod

class exchange(ABC):
   def __init__(self, exchangeName):
      self.exchangeName = exchangeName
      super().__init__()

   def __str__(self):
      return self.exchangeName

   @abstractmethod
   def queryBalance(self):
      pass

   @abstractmethod
   def queryTicker(self, curr):
      pass

   @abstractmethod
   def buyMkt(self, curr, vol):
      pass
   
   @abstractmethod
   def sellMkt(self, curr, vol):
      pass

   @abstractmethod
   def buyLmt(self, curr, vol, price):
      pass
   
   @abstractmethod
   def sellLmt(self, curr, vol, price):
      pass

   @abstractmethod
   def queryOrder(self, orderID):
      pass

   @abstractmethod
   def cancelOrder(self, orderID):
      pass


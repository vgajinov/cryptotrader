from abc import ABC, abstractmethod

'''
This is the base class for REST API clients
'''
class exchangeRESTClient(ABC):
   def __init__(self, exchangeName):
      self.exchangeName = exchangeName
      super().__init__()

   def __str__(self):
      return self.exchangeName

   #
   # Public API methods
   #

   @abstractmethod
   def ticker(self, symbol):
      pass




   #
   # Private (authenticated) API methods
   #

   @abstractmethod
   def getBalance(self):
      pass

   @abstractmethod
   def placeLimitOrder(self, symbol, volume, price):
      pass

   @abstractmethod
   def placeMarketOrder(self, symbol, volume):
      pass

   @abstractmethod
   def queryOrder(self, orderID):
      pass

   @abstractmethod
   def cancelOrder(self, orderID):
      pass
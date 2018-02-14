from abc import ABC, abstractmethod

class ExchangeWSClient(ABC):
   def __init__(self, exchange):
      self.exchange = exchange
      super().__init__()

   def __str__(self):
      return self.exchange

   @abstractmethod
   def connect(self):
      pass

   @abstractmethod
   def disconnect(self):
      pass

   @abstractmethod
   def subscribe(self):
      pass

   @abstractmethod
   def unsubscribe(self):
      pass
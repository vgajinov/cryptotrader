from exchanges.WS.api import WSClientAPI
from exchanges.WS.binance import BinanceWSClient
from exchanges.WS.bitfinex import BitfinexWSClient



class ExchangeWSFactory(object):
   exchanges = None

   @staticmethod
   def get_exchanges():
      if not ExchangeWSFactory.exchanges:
         ExchangeWSFactory.exchanges = {}
         for ex in WSClientAPI.__subclasses__():
            ExchangeWSFactory.exchanges[ex.name()] = ex
      return sorted(list(ExchangeWSFactory.exchanges.keys()))

   @staticmethod
   def create_client(name, key_file=None)-> WSClientAPI:
      if not ExchangeWSFactory.exchanges:
         ExchangeWSFactory.get_exchanges()
      try:
         return ExchangeWSFactory.exchanges[name](key_file=key_file)
      except KeyError:
         print('Exchange name not recognized')
         return None


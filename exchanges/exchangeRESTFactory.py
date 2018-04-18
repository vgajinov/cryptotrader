from exchanges.REST.api import RESTClientAPI
from exchanges.REST.binance import BinanceRESTClient
from exchanges.REST.bitfinex import BitfinexRESTClient


class ExchangeRESTFactory(object):
   exchanges = None

   @staticmethod
   def get_exchanges():
      if not ExchangeRESTFactory.exchanges:
         ExchangeRESTFactory.exchanges = {}
         for ex in RESTClientAPI.__subclasses__():
            ExchangeRESTFactory.exchanges[ex.name()] = ex
      return sorted(list(ExchangeRESTFactory.exchanges.keys()))

   @staticmethod
   def create_client(name, key_file=None) -> RESTClientAPI:
      if not ExchangeRESTFactory.exchanges:
         ExchangeRESTFactory.get_exchanges()
      if name in ExchangeRESTFactory.exchanges.keys():
         return ExchangeRESTFactory.exchanges[name]()
      else:
         print('Exchange name not recognized : ', name)
         return None




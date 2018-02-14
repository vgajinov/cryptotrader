from exchangeWSClient import ExchangeWSClient
from binance.binance_Websocket import BinanceWSClient
from bitfinex.bitfinex_v2_WebSockets import BitfinexWSClient


class ExchangeWSFactory(object):
   indicators = None

   @staticmethod
   def createClient(name):
      if not ExchangeWSFactory.indicators:
         ExchangeWSFactory.getIndicatorNames()
      if name in ExchangeWSFactory.indicators.keys():
         return ExchangeWSFactory.indicators[name]()
      else:
         print('Indicator not defined')

   @staticmethod
   def getIndicatorNames():
      if not ExchangeWSFactory.indicators:
         ExchangeWSFactory.indicators = {}
         for ex in ExchangeWSClient.__subclasses__():
            ExchangeWSFactory.indicators[ex.__name__] = ex
      return sorted(list(ExchangeWSFactory.indicators.keys()))



ExchangeWSFactory.getIndicatorNames()
ExchangeWSFactory.createClient('Binance')
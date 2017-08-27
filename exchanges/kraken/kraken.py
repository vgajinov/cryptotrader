import krakenex
from exchangeBase import *


class Kraken(exchangeBase):

   def __init__(self, exchangeName, keyfile=None):
      self.k = krakenex.API()

      if keyfile is not None:
         self.k.load_key(keyfile)

      super().__init__(exchangeName)


   def queryBalance(self):
      answer = self.k.query_private('Balance')
      if answer['error']:
         raise Exception(answer['error'])

      return float(answer['result'][''])


   def queryTicker(self, curr):
      buy_data = { 'pair' : ",".join(curr) if isinstance(curr,list) else curr }

      answer = self.k.query_public('Ticker', buy_data)
      if answer['error']:
         raise Exception(answer['error'])

      if isinstance(curr,list):
         result = []
         for c in curr:
            bid = float(answer['result'][c]['b'][0])
            ask = float(answer['result'][c]['a'][0])
            vol = float(answer['result'][c]['v'][0])
            result.append((bid, ask, vol))
      else:
         bid = float(answer['result'][curr]['b'][0])
         ask = float(answer['result'][curr]['a'][0])
         vol = float(answer['result'][curr]['v'][0])
         result = (bid, ask, vol)
      
      return result


   def buyMkt(self, curr, vol):
      buy_data = {
         'pair' : curr,
         'type' : 'buy',
         'ordertype' : 'market',
         'volume' : str(vol),
         'oflags' : 'fcib',
      }

      answer = self.k.query_private('AddOrder', buy_data)
      if answer['error']:
         raise Exception(answer['error'])

      return answer['result']['txid'][0]


   def sellMkt(self, curr, vol):
      buy_data = {
         'pair' : curr,
         'type' : 'sell',
         'ordertype' : 'market',
         'volume' : str(vol),
         'oflags' : 'fcib',
      }

      answer = self.k.query_private('AddOrder', buy_data)
      if answer['error']:
         raise Exception(answer['error'])

      return answer['result']['txid'][0]


   def buyLmt(self, curr, vol, price):
      buy_data = {
         'pair' : curr,
         'type' : 'buy',
         'ordertype' : 'limit',
         'price'  : str(price),
         'volume' : str(vol),
         'oflags' : 'fcib',
      }

      answer = self.k.query_private('AddOrder', buy_data)
      if answer['error']:
         raise Exception(answer['error'])

      return answer['result']['txid'][0]
 
   
   def sellLmt(self, curr, vol, price):
      buy_data = {
         'pair' : curr,
         'type' : 'sell',
         'ordertype' : 'limit',
         'price'  : str(price),
         'volume' : str(vol),
         'oflags' : 'fcib',
      }

      answer = self.k.query_private('AddOrder', buy_data)
      if answer['error']:
         raise Exception(answer['error'])

      return answer['result']['txid'][0]


   def queryOrder(self, orderID):
      answer = self.k.query_private('QueryOrders', {'txid' : orderID})
      if answer['error']:
         raise Exception(answer['error'])

      return answer['result'][txid]


   def cancelOrder(self, orderID):
      answer = self.k.query_private('CancelOrder', {'txid' : orderID})
      if answer['error']:
         raise Exception(answer['error'])
   

   def buyMktCondStop(self, curr, vol, stop):
      buy_data = {
         'pair' : curr,
         'type' : 'buy',
         'ordertype' : 'market',
         'volume' : str(vol),
         'oflags' : 'fcib',
         'close[ordertype]': 'stop-loss',
         'close[price]':  str(stop)
      }

      answer = self.k.query_private('AddOrder', buy_data)
      if answer['error']:
         raise Exception(answer['error'])

      return answer['result']['txid'][0]


   def buyMktCondTrailing(self, curr, vol, trail):
      buy_data = {
         'pair' : curr,
         'type' : 'buy',
         'ordertype' : 'market',
         'volume' : str(vol),
         'oflags' : 'fcib',
         'close[ordertype]': 'trailing-stop',
         'close[price]':  str(stop)
      }

      answer = self.k.query_private('AddOrder', buy_data)
      if answer['error']:
         raise Exception(answer['error'])

      return answer['result']['txid'][0]


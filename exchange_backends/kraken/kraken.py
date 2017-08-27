import krakenex
from AutoTrader.exchange_backends.exchange import *


class Kraken(exchange):

   def __init__(self, keyfile=None):
      self.k = krakenex.API()

      if keyfile is not None:
         self.k.load_key(keyfile)

      super().__init__()


   def queryBalance(self):
      answer = self.k.query_private('Balance')
      if answer['error']:
         raise Exception(answer['error'])

      return float(answer['result']['ZEUR'])


   def queryTicker(self, curr):
      pair = '{}EUR'.format(curr)
      buy_data = { 'pair' : pair }

      answer = self.k.query_public('Ticker', buy_data)
      if answer['error']:
         raise Exception(answer['error'])

      bid = float(answer['result'][pair]['b'][0])
      ask = float(answer['result'][pair]['a'][0])
      return (bid, ask)


   def buyMkt(self, curr, vol):
      buy_data = {
         'pair' : '{}EUR'.format(curr),
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
         'pair' : '{}EUR'.format(curr),
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
         'pair' : '{}EUR'.format(curr),
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
         'pair' : '{}EUR'.format(curr),
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
         'pair' : '{}EUR'.format(curr),
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
         'pair' : '{}EUR'.format(curr),
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


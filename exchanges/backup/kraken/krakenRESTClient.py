import json
import urllib3
import urllib.parse
import time
import hashlib
import hmac
import base64

from exchanges.exchangeRESTClient import exchangeRESTClient


urllib3.disable_warnings()

class _Connection(object):
   def __init__(self, uri='api.kraken.com', timeout=30):
      self.httpsPool = urllib3.HTTPSConnectionPool(uri, timeout=timeout, maxsize=10)
      return

   def _request(self, url, req={}, headers={}):
      headers['User-Agent'] =  'krakentest/1.0.2 (www.google.com)'

      response = self.httpsPool.request_encode_body('POST', url, req, headers, encode_multipart=False)
      if response.status not in (200, 201, 202):
         raise urllib3.connectionpool.HTTPException(response.status)
      return response.data.decode()


class _API(object):
   def __init__(self, path = None):
      self.uri = 'https://api.kraken.com'
      self.apiversion = '0'
      self.conn = _Connection()

      if path is not None:
         with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
      return

   def _query(self, urlpath, req, conn=None, headers={}):
      url = self.uri + urlpath
      ret = self.conn._request(url, req, headers)
      return json.loads(ret)

   def query_public(self, method, req={}, conn=None):
      urlpath = '/' + self.apiversion + '/public/' + method
      return self._query(urlpath, req, conn)

   def query_private(self, method, req={}, conn=None):
      urlpath = '/' + self.apiversion + '/private/' + method

      req['nonce'] = int(1000*time.time())
      postdata = urllib.parse.urlencode(req)

      encoded = (str(req['nonce']) + postdata).encode()
      message = urlpath.encode() + hashlib.sha256(encoded).digest()
      signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
      sigdigest = base64.b64encode(signature.digest())

      headers = {
         'API-Key': self.key,
         'API-Sign': sigdigest.decode()
      }

      return self._query(urlpath, req, conn, headers)


class krakenRESTClient(exchangeRESTClient):

   def __init__(self, exchangeName, keyfile=None):
      self.k = _API(keyfile)
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
         'oflags' : 'fcib'
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
      answer = self.k.query_private('QueryOrders', {'txid' : ",".join(orderID) if isinstance(orderID,list) else orderID})
      if answer['error']:
         raise Exception(answer['error'])

      if isinstance(orderID,list):
         result = [answer['result'][order] for order in orderID]
      else:
         result = answer['result'][orderID]

      return result


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


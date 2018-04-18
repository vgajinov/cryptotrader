
import requests


'''

The base endpoint is: https://api.binance.com
All endpoints return either a JSON object or array.
Data is returned in ascending order. Oldest first, newest last.
All time and timestamp related fields are in milliseconds.
HTTP 4XX return codes are used for for malformed requests; the issue is on the sender's side.
HTTP 429 return code is used when breaking a request rate limit.
HTTP 418 return code is used when an IP has been auto-banned for continuing to send requests after receiving 429 codes.
HTTP 5XX return codes are used for internal errors; the issue is on Binance's side.
HTTP 504 return code is used when the API successfully sent the message but not get a response within the timeout period. It is important to NOT treat this as a failure; the execution status is UNKNOWN and could have been a success.
Any endpoint can retun an ERROR; the error payload is as follows:
{
  "code": -1121,
  "msg": "Invalid symbol."
}
Specific error codes and messages defined in another document.
For GET endpoints, parameters must be sent as a query string.
For POST, PUT, and DELETE endpoints, the parameters may be sent as a query string or in the request body with content type application/x-www-form-urlencoded. You may mix parameters between both the query string and request body if you wish to do so.
Parameters may be sent in any order.
If a parameter sent in both the query string and request body, the query string parameter will be used.


Exchange information
=========================

GET /api/v1/exchangeInfo
Current exchange trading rules and symbol information

{
  "timezone": "UTC",
  "serverTime": 1508631584636,
  "rateLimits": [{
      "rateLimitType": "REQUESTS",
      "interval": "MINUTE",
      "limit": 1200
    },
    {
      "rateLimitType": "ORDERS",
      "interval": "SECOND",
      "limit": 10
    },
    {
      "rateLimitType": "ORDERS",
      "interval": "DAY",
      "limit": 100000
    }
  ],
  "exchangeFilters": [],
  "symbols": [{
    "symbol": "ETHBTC",
    "status": "TRADING",
    "baseAsset": "ETH",
    "baseAssetPrecision": 8,
    "quoteAsset": "BTC",
    "quotePrecision": 8,
    "orderTypes": ["LIMIT", "MARKET"],
    "icebergAllowed": false,
    "filters": [{
      "filterType": "PRICE_FILTER",
      "minPrice": "0.00000100",
      "maxPrice": "100000.00000000",
      "tickSize": "0.00000100"
    }, {
      "filterType": "LOT_SIZE",
      "minQty": "0.00100000",
      "maxQty": "100000.00000000",
      "stepSize": "0.00100000"
    }, {
      "filterType": "MIN_NOTIONAL",
      "minNotional": "0.00100000"
    }]
  }]
}





Order book
=========================

GET /api/v1/depth
Weight: Adjusted based on the limit:

Limit	Weight
5, 10, 20, 50, 100	1
500	25
1000	50
Parameters:

Name	Type	Mandatory	Description
symbol	STRING	YES
limit	INT	NO	Default 100; max 1000. Valid limits:[5, 10, 20, 50, 100, 500, 1000]
Caution: setting limit=0 can return a lot of data.

Response:

{
  "lastUpdateId": 1027024,
  "bids": [
    [
      "4.00000000",     // PRICE
      "431.00000000",   // QTY
      []                // Ignore.
    ]
  ],
  "asks": [
    [
      "4.00000200",
      "12.00000000",
      []
    ]
  ]
}





Kline/Candlestick data
=========================

GET /api/v1/klines
Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.

Weight: 1

Parameters:

Name	Type	Mandatory	Description
symbol	STRING	YES
interval	ENUM	YES
limit	INT	NO	Default 500; max 500.
startTime	LONG	NO
endTime	LONG	NO
If startTime and endTime are not sent, the most recent klines are returned.

[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore
  ]
]
'''

TIMEOUT = 5.0  # HTTP request timeout in seconds

# ==========================================================================================
#   restAPI
# ==========================================================================================

class BinanceRestAPI:
   """
   Client for the binance.com API.
   See https://github.com/binance-exchange/binance-official-api-docs for API documentation.
   """

   def server(self):
      return 'https://api.binance.com/api/v1'


   def url_for(self, path, path_arg=None, parameters=None):

      # build the basic url
      url = "%s/%s" % (self.server(), path)

      # If there is a path_arh, interpolate it into the URL.
      # In this case the path that was provided will need to have string
      # interpolation characters in it, such as PATH_TICKER
      if path_arg:
         url = url % (path_arg)
      # Append any parameters to the URL.
      if parameters:
         params = '&'.join(["%s=%s" % (k, parameters[k]) for k in parameters.keys()])
         url = "%s?%s" % (url, params)

      return url


   def _get(self, url):
      try:
         response = requests.get(url, timeout=TIMEOUT)
      except requests.exceptions.RequestException as e:
         print('Binance REST API exception: ' + e)
         return None
      return response.json()


   def _convert_to_floats(self, data):
      """
      Convert all values in a dict to floats
      """
      for key, value in data.items():
         data[key] = float(value)

      return data


   #  API calls
   # ----------------------------------------------------------------
   def exchangeInfo(self):
      return self._get(self.url_for('exchangeInfo'))

   def orderBook(self, symbol, limit=100):
      return self._get(self.url_for('depth', parameters={'symbol':symbol.upper(), 'limit':str(limit)}) )

   def candles(self, symbol, interval='1m', limit=500):
      return self._get(self.url_for('klines', parameters={'symbol':symbol.upper(), 'interval':interval, 'limit':str(limit)}))


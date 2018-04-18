import csv
from exchanges.binance.binanceRESTClient import binanceRESTClient


BEGIN_TIME = 1451606400000   # 00:00:00 01.01.2016
END_TIME   = 1519862400000   # 00:00:00 01.03.2018


client = binanceRESTClient(None, None)

info = client.get_exchange_info()
symbols = sorted([ s['symbol'] for s in info['symbols'] if 'BTC' in s['symbol'] ])


for symbol in symbols:
   print(symbol)
   with open(symbol+'.csv', 'w') as f:
      writer = csv.writer(f)
      candles = client.get_historical_klines(symbol, binanceRESTClient.KLINE_INTERVAL_1MINUTE, "1 Jan, 2018", "3 Jan, 2018")
      writer.writerows(candles)









import csv
from exchanges.exchangeRESTFactory import ExchangeRESTFactory


BEGIN_TIME  = 1519862400000   # 00:00:00 01.03.2018
END_TIME    = 1520035200000   # 00:00:00 03.03.2018
INTERVAL    = 60000           # 1 minute
MAX_CANDLES = 1000            # limit the size of data per each request

DELTA       = MAX_CANDLES * INTERVAL



client = ExchangeRESTFactory.create_client('Binance')

symbols = client.symbols()

for symbol in symbols[:2]:
   with open(symbol + '.csv', 'w') as f:
      csvwriter = csv.writer(f)
      for starttime in range(BEGIN_TIME, END_TIME, DELTA):
         endtime = starttime + DELTA
         candles = client.historical_candles(symbol, '1m', starttime, endtime)
         csvwriter.writerows(candles)


# Try increasing MAX_CANDLES
# Maybe add sleep(1) between each call to client.historical_candles
# to avoid being banned due to rate limitation of the API




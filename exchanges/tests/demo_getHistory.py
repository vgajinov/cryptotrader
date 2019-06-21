"""
<keywords>
history, symbol, exchange, fetch, binance
</keywords>
<description>
Fetch the historical data of several symbols and dump them into seperate csv
files.
</description>
<seealso>
</seealso>
"""
from time import mktime, strptime
import csv
import pandas as pd
from exchanges.exchangeRESTFactory import ExchangeRESTFactory


BEGIN_TIME   = '2018-03-01T00:00:00'
END_TIME     = '2018-03-03T00:00:00'
INTERVAL_SEC = 60              # 1 minute
MAX_CANDLES  = 1000            # limit the size of data per each request

INTERVAL_MILLI_SEC = INTERVAL_SEC * 1000
DELTA = MAX_CANDLES * INTERVAL_MILLI_SEC
T0_MILLI_SEC = int(mktime(strptime(BEGIN_TIME, '%Y-%m-%dT%H:%M:%S'))*1000.0)
TF_MILLI_SEC = int(mktime(strptime(END_TIME, '%Y-%m-%dT%H:%M:%S'))*1000.0)

client = ExchangeRESTFactory.create_client('Binance')

symbols = client.symbols()[:2]

print(f'fetch history for symbols: {symbols}')
for symbol in symbols:
    with open(symbol + '.csv', 'w') as fobj:
        print(f'\twrite data  to: {fobj.name}')
        csvwriter = csv.writer(fobj)
        for starttime in range(T0_MILLI_SEC, TF_MILLI_SEC, DELTA):
            endtime = starttime + DELTA
            candles = client.historical_candles(symbol, '1m', starttime, endtime)
            csvwriter.writerows(candles)

    # sanity check for the fetched data
    data_csv = pd.read_csv(fobj.name)
    assert len(data_csv) == 1499

# Try increasing MAX_CANDLES
# Maybe add sleep(1) between each call to client.historical_candles
# to avoid being banned due to rate limitation of the API

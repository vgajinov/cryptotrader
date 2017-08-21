import os, sys
import time
from datetime import datetime
import bitfinex_v2_WebSockets


# create the client
client = bitfinex_v2_WebSockets.BitfinexWSClient()
client.connect()

#client.subscribe('book', {'pair': "BTCUSD", 'prec': "P0"})
#client.subscribe('raw_book', {'pair':"BTCUSD"})
#client.subscribe('trades', {'pair':"BTCUSD"})
#client.subscribe('ticker', {'pair': "BTCUSD"})
client.subscribe('candles', {'pair': "BTCUSD", 'scale': "1m"})

time.sleep(30)
client.disconnect()

book = {}
rawBook = {}
trades = {}
tickers = {}

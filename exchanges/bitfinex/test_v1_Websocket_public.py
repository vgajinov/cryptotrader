import os, sys
import time
from datetime import datetime
import bitfinex_v1_WebSockets

# create the client
client = bitfinex_v1_WebSockets.Client()
client.connect()

#client.subscribe('book', {'pair': "BTCUSD", 'prec': "P0"})
#client.subscribe('raw_book', {'pair':"BTCUSD"})
#client.subscribe('trades', {'pair':"BTCUSD"})
client.subscribe('ticker', {'pair': "BTCUSD"})

time.sleep(30)
client.disconnect()

book = {}
rawBook = {}
trades = {}
tickers = {}
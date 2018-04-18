#!/usr/bin/env python

# TODO: this was taken from the github. Needs more work!

from exchanges.binance.binanceRESTClient import binanceRESTClient
import pytest
import requests_mock


#client = binanceRESTClient('api_key', 'api_secret')

client = binanceRESTClient('MX02juMe57w7jQZorBEvva2OBjyx8MftdXdTC3n4oUnYduPZyjpyfCC3MgXH8zvK',
                           'tVHHC0KzKWVQQCRhxm7RGtkfEEgdNfbd44GRpXxpgH1UCTYIWaoUcqNpFnYfxgTI')


# Test historic candles
def test_exact_amount():
    """Test Exact amount returned"""

    first_res = []
    row = [1519892340000,"0.00099400","0.00099810","0.00099400","0.00099810","4806.04000000",1519892399999,"4.78553253",154,"1785.14000000","1.77837524","0"]

    for i in range(0, 500):
        first_res.append(row)

    second_res = []

    with requests_mock.mock() as m:
        m.get('https://api.binance.com/api/v1/klines?interval=1m&limit=500&startTime=1519862400000&symbol=BNBBTC', json=first_res)
        m.get('https://api.binance.com/api/v1/klines?interval=1m&limit=500&startTime=1519892400000&symbol=BNBBTC', json=second_res)
        client.get_historical_klines(
            symbol="BNBBTC",
            interval=binanceRESTClient.KLINE_INTERVAL_1MINUTE,
            start_str="1st March 2018"
        )



#test_exact_amount()


import time
print(int(time.time() * 1000))
print(client.get_server_time())

# res = client.get_my_trades(symbol='BNBBTC', limit=10)
# print(res)

res = client.order_limit_buy(symbol='BNBBTC', quantity=1, price=0.0010655)
print(res)


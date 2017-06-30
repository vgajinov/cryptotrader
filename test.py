#!/usr/bin/env python2

import cryptowatch.Client as cl
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import date2num, DateFormatter, HourLocator, DayLocator
from finance_metrics import *

def display_plot(quotes, technical_indicators=None, processing_results=None):
   # plot the candle chart
   # set the formatters for the horizontal axis
   days = DayLocator()
   allhours = HourLocator()
   weekFormatter = DateFormatter('%m-%d')
   
   # format the plot
   fig, ax = plt.subplots()
   fig.subplots_adjust(bottom=0.2)
   ax.xaxis.set_major_locator(days)
   ax.xaxis.set_minor_locator(allhours)
   ax.xaxis.set_major_formatter(weekFormatter)
   
   # generate the candlesticks
   candlestick_ohlc(ax, list(map(tuple, quotes)), width=.001, colorup='g', colordown='r', )
   
   # create the plot itself and display it
   ax.xaxis_date()
   ax.autoscale_view()
   plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
   if technical_indicators is not None:
      dates = [x[0] for x in quotes]
      for indicator, data in technical_indicators.iteritems():
         if "KELCH" in indicator:
            linestyle = ":" if indicator == "KELCH_average" else "-"
            linecolor = "blue"
         if "psar" in indicator:
            linestyle = ":"
            linecolor = "violet"
         plt.plot(dates, data, linestyle=linestyle, linewidth=1, color=linecolor)
   
   if processing_results is not None:
      for indicator, result in processing_results.iteritems():
         dates = [x[0] for x in result]
         data = [x[1] for x in result]
         linecolor = "black"
         plt.plot(dates, data, linestyle=linestyle, label=indicator, linewidth=1, color=linecolor)

   plt.legend()
   plt.show()


def get_trade_proposals(quotes, technical_indicators):

   #for i in quotes:
   #   print i
   #raise Exception()
   # we want to BUY when technical_indicators['psar_bear'] switches from value to None,
   # if there are AT LEAST N consecutives Nones
   consec_nones = 4
   numsamples = len(technical_indicators['psar_bear'])

   # get the indices of the None elements in array, whose preceding element is not None
   local_mins = [ i for i, j in enumerate(technical_indicators['psar_bear']) if j is None and technical_indicators['psar_bear'][i-1] is not None]
   #print local_mins

   # restrict the eligible elements only to those that have AT LEAST N consecutives Nones
   buy_time_idx = []
   for i in local_mins:
      window = min(4, numsamples - i)
   
      if all([sample is None for sample in technical_indicators['psar_bear'][i:i+window]]):
         buy_time_idx.append(min(i+window,numsamples-1))
   #print buy_time_idx
   
   # get the indices of the None elements in array, whose next element is None
   local_maxs = [ i for i, j in enumerate(technical_indicators['psar_bull']) if j is None and technical_indicators['psar_bull'][i-1] is not None]
   #print local_maxs

   # restrict the eligible elements only to those that have AT LEAST N consecutives Nones
   #print technical_indicators['psar_bull']
   sell_time_idx = []
   for i in local_maxs:
      window = min(4, numsamples - i)
   
      if all([sample is None for sample in technical_indicators['psar_bull'][i:i+window]]):
         sell_time_idx.append(min(i+window,numsamples-1))
   #print sell_time_idx

   # generate an order book
   OrderBook = [ (quotes[i,0], 'B', quotes[i,1]) for i in buy_time_idx ] + [ (quotes[i,0], 'S', quotes[i,1]) for i in sell_time_idx ]
   
   return sorted(OrderBook, key=lambda x: x[0])


def simulate_trading(OrderBook):
   capital=1000
   coins=0
   last_buy = 0
   last_sell = 1000

   #print OrderBook[0]
   #for i,value in enumerate(OrderBook[1:]):
   #   print value, (value[2]*100/OrderBook[i][2]) - 100

   for order in OrderBook:
      order_sent = False
      if order[1] == 'S' and coins>0 and order[2]>last_buy:
         coins_sold=min(.2*coins, .5)
         capital += order[2] * coins_sold
         coins -= coins_sold
         last_sell = order[2]
         order_sent = True
         
      if order[1] == 'B' and capital>0:
         invest = min(capital, 500)
         coins += invest / order[2]
         capital -= invest
         last_buy = order[2]
         order_sent = True
     
      if order_sent: 
         print order, capital, coins, "<-------"
      #else:
      #   print order

   total_assets_value = capital + coins * OrderBook[-1][2]
   print "Total assets value: ", total_assets_value 
   



period='1800'
s = "26/06/2017 00:00:00"
today=int(time.mktime(datetime.strptime(s, "%d/%m/%Y %H:%M:%S").timetuple()))

client = cl.MarketClient("kraken", "etheur")
OHLC = client.GetOHLC(after=str(today), periods=[period])

quotes = np.array( [ (date2num(datetime.fromtimestamp(x.open_time)), x.open, x.high, x.low, x.close, x.volume) for x in OHLC[period] ], dtype=float )
technical_indicators = KELCH(quotes, 14)

psar_results = parabolic_sar(quotes)
technical_indicators['psar_bull'] = psar_results['psarbull']
technical_indicators['psar_bear'] = psar_results['psarbear']

OrderBook = get_trade_proposals(quotes, technical_indicators)
simulate_trading(OrderBook)
#processing_results = {}
#processing_results['order_book'] = np.array([(x[0],x[2]) for x in OrderBook], dtype=float)
#display_plot(quotes, technical_indicators, processing_results)

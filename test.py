#!/usr/bin/env python2

import matplotlib.pyplot as plt
import cryptowatch.Client as cl
import time
from datetime import datetime
import numpy as np

def ATR(candlestick_list, n):
   PC = np.array([ candlestick_list[0].close ] + [x.close for x in candlestick_list[:-1]])
   h = np.array([x.high for x in candlestick_list])
   l = np.array([x.low for x in candlestick_list])
   TR = np.maximum(h - l, h - PC, PC - l)
   #initialize ATR array
   ATR = np.zeros(len(candlestick_list))
   ATR[0] = np.mean(TR[:n])

   for i in range(1, len(candlestick_list)):
      ATR[i] = (n - 1) * ATR[i - 1] + TR[i]
      ATR[i] /= n
   return ATR

def moving_average(a, n=3, type='simple') :
   from scipy.ndimage.filters import convolve1d
   from scipy.signal import exponential
   if type=='simple':
      weights = np.ones(n)
   else:
      tau2 = -(n-1) / np.log(0.01)
      weights = exponential(n, 0, tau2, False)
   weights /= weights.sum()

   return convolve1d(a, weights)

#Keltner Channel  
def KELCH(candlestick_list, n):
   #KelChM = moving_average( [(x.high + x.low + x.close)/3 for x in candlestick_list], n=n, type='exp')
   #KelChU = moving_average( [(4 * x.high - 2 * x.low + x.close)/3 for x in candlestick_list], n=n, type='exp')
   #KelChL = moving_average( [(-2 * x.high + 4 * x.low + x.close)/3 for x in candlestick_list], n=n, type='exp')

   KelChM = moving_average( [(x.high + x.low + x.close)/3 for x in candlestick_list], n=n, type='exp')
   KelChU = KelChM + 2 * ATR(candlestick_list, n)
   KelChL = KelChM - 2 * ATR(candlestick_list, n)

   return KelChM, KelChU, KelChL

def display_plot(candlestick_list, Keltner_channels=None):
   # plot the candle chart
   from matplotlib.finance import candlestick_ohlc
   from matplotlib.dates import date2num, DateFormatter, HourLocator, DayLocator
   
   #Prepare the data for plotting
   quotes = [ (date2num(datetime.fromtimestamp(x.open_time)), x.open, x.high, x.low, x.close) for x in candlestick_list]
   
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
   candlestick_ohlc(ax, quotes, width=.001, colorup='g', colordown='r', )
   
   # create the plot itself and display it
   ax.xaxis_date()
   ax.autoscale_view()
   plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
   if Keltner_channels is not None:
      dates = [x[0] for x in quotes]
      for channel in Keltner_channels:
         plt.plot(dates, channel, linewidth=1, color='black')
   plt.show()
   
def get_average_moves(candlestick_list):
   # get the list of dynamic ranges
   DR = [ x.close for x in candlestick_list]
   average = np.mean(DR)
   stdevOverAvg = np.std(DR)/average

   return average, stdevOverAvg
   
period='180'
s = "29/06/2017 08:00:00"
today=int(time.mktime(datetime.strptime(s, "%d/%m/%Y %H:%M:%S").timetuple()))

client = cl.MarketClient("kraken", "etheur")
OHLC, allowance = client.GetOHLC(after=str(today), periods=[period], get_allowance=True)

average, stdevOverAvg = get_average_moves(OHLC[period])
print average, stdevOverAvg
KelChM, KelChU, KelChL = KELCH(OHLC[period], 14)

display_plot(OHLC[period], [KelChM, KelChU, KelChL])

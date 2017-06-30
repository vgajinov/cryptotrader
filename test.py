#!/usr/bin/env python2

import cryptowatch.Client as cl
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import date2num, DateFormatter, HourLocator, DayLocator
from finance_metrics import *

def display_plot(quotes, technical_indicators=None):
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
   plt.show()


period='180'
s = "29/06/2017 18:00:00"
today=int(time.mktime(datetime.strptime(s, "%d/%m/%Y %H:%M:%S").timetuple()))

client = cl.MarketClient("kraken", "etheur")
OHLC = client.GetOHLC(after=str(today), periods=[period])

quotes = np.array( [ (date2num(datetime.fromtimestamp(x.open_time)), x.open, x.high, x.low, x.close) for x in OHLC[period] ], dtype=float )
technical_indicators = KELCH(quotes, 14)

psar_results = parabolic_sar(quotes)
technical_indicators['psar_bull'] = psar_results['psarbull']
technical_indicators['psar_bear'] = psar_results['psarbear']
display_plot(quotes, technical_indicators)

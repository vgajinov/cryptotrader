#!/usr/bin/env python2

import finance_metrics as fm
import numpy as np
import sys
import strategies
from datetime import datetime
from collections import namedtuple

# init strategies list with the list of strategies
strategies_list = [method for method in dir(strategies) if callable(getattr(strategies, method)) and not method.startswith("_") ]

class dbconnector(object):
   def __init__(self, fname):
      self.con, self._db_is_initialized = self.connect_to_db(fname)

   @property
   def db_is_initialized(self):
      return self._db_is_initialized

   def __enter__(self):
      return self

   def __exit__(self, exc_type, exc_value, traceback):
         self.close_db()

   def connect_to_db(self, fname):
      import sqlite3 as lite
   
      con = None
   
      # connect to the database, will be created if not existent
      try:
         con = lite.connect(fname)
         c = con.cursor()
      except lite.Error, e:
         print "Error %s:" % e.args[0]
         sys.exit(1)
   
      sql_create_data_table = """ CREATE TABLE IF NOT EXISTS samples (
                                          ts real PRIMARY KEY,
                                          open real,
                                          high real,
                                          low real,
                                          close real,
                                          volume real
                                      ); """
   
      # create the table for the data, if it does not exist
      try:
         c.execute(sql_create_data_table)
      except Error as e:
         print(e)
         sys.exit(1)
   
      # get the number of rows (to find if db is initialized or not)
      try:
         c.execute('SELECT Count(*) FROM samples')
         data = c.fetchone()[0]
      except Error as e:
         print(e)
         sys.exit(1)
   
      # return the conection, and a boolean indicating if there is data in the database
      return con, data > 0

   def close_db(self):
      if self.con:
         self.con.close()

   def save_data(self, quotes):
      cur = self.con.cursor()
      cur.executemany("INSERT INTO samples VALUES(?, ?, ?, ?, ?, ?)", map(tuple, quotes.tolist()))
      self.con.commit()
   
   def load_data(self):
      cur = self.con.cursor()
   
      # get the number of rows
      try:
         cur.execute('SELECT Count(*) FROM samples')
         nrows = cur.fetchone()[0]
      except Error as e:
         print(e)
         sys.exit(1)
   
      quotes = np.ndarray(shape=(nrows,6), dtype=float)
   
      try:
         cur.execute('SELECT * FROM samples')
         records = cur.fetchall()
      except Error as e:
         print(e)
         sys.exit(1)
   
      for idx,record in enumerate(records):
         quotes[idx][:] = record
   
      return quotes


def display_plot(quotes, technical_indicators=None, processing_results=None):
   import matplotlib.pyplot as plt
   from matplotlib.finance import candlestick_ohlc
   from matplotlib.dates import date2num, DateFormatter, HourLocator, DayLocator

   # plot the candle chart
   # set the formatters for the horizontal axis
   days = DayLocator()
   allhours = HourLocator()
   weekFormatter = DateFormatter('%m-%d')
   dayFormatter = DateFormatter('%H')
   
   # format the plot
   if technical_indicators is not None:
      for indicator in technical_indicators:
         if "macd" in indicator.label:
            fig, ax = plt.subplots(2, sharex=True)
            break
      else:
         fig, ax = plt.subplots()
         ax = [ax]
   else:
      fig, ax = plt.subplots()
      ax = [ax]

   fig.subplots_adjust(bottom=0.2)
   ax[0].xaxis.set_major_locator(days)
   ax[0].xaxis.set_minor_locator(allhours)
   ax[0].xaxis.set_major_formatter(weekFormatter)

   if ax[0].get_xlim()[0] - ax[0].get_xlim()[0]<1:
      ax[0].xaxis.set_minor_formatter(dayFormatter)

   
   # generate the candlesticks
   candlestick_ohlc(ax[0], list(map(tuple, quotes)), width=.001, colorup='g', colordown='r', )
   
   # create the plot itself and display it
   ax[0].xaxis_date()
   ax[0].autoscale_view()
   plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

   if technical_indicators is not None:
      dates = [x[0] for x in quotes]
      for indicator in technical_indicators:
         if not indicator.display:
            continue

         linestyle = "-"
         linecolor = "k"

         if "kelner" in indicator.label:
            linestyle = ":" if indicator.label == "kelner_average" else "-"
            linecolor = "blue"
         if "psar" in indicator.label:
            linestyle = ":"
            linecolor = "violet"
         if "macd" in indicator.label:
            linecolor = "violet" if "_s" in indicator.label else "blue"
            ax[1].plot(dates, indicator.data, label=indicator.legend, linestyle=linestyle, linewidth=1, color=linecolor)
            ax[1].axhline(linewidth=0.5, color = 'k')
            continue

         ax[0].plot(dates, indicator.data, label=indicator.legend, linestyle=linestyle, linewidth=1, color=linecolor)
   
   if processing_results is not None:

      yoffset = ax[0].get_ylim()[0]
      for event in processing_results['order_book_events']:
         ax[0].annotate(event[1], xy=(event[0], event[2]),  xycoords='data',
                  xytext=(event[0], yoffset+1), textcoords='data',
                  bbox=dict(boxstyle="round", fc="0.8"),
                  arrowprops=dict(arrowstyle="->",
                  connectionstyle="angle,angleA=0,angleB=90,rad=10"),
                  )

   plt.legend()
   plt.show()


def simulate_trading(quotes, technical_indicators, capital, broker_fee=.002, strategy=0):
   indicators_dict = {indic.label: indic.data for indic in technical_indicators}
   total_assets_value, OrderBookOut = getattr(strategies, strategies_list[strategy])(quotes, indicators_dict, capital, broker_fee)

   print "Total assets value: ", total_assets_value 
   return total_assets_value, OrderBookOut

if __name__ == "__main__":

   technical_indicator = namedtuple('technical_indicator', 'label data display legend')
   technical_indicator.__new__.__defaults__ = ("", [], False, None)

   period='300'
   start_date = "18/07/2017 00:00:00"
   start_date_obj = datetime.strptime(start_date, "%d/%m/%Y %H:%M:%S")
    
   with dbconnector( "samples_%s_%s.db"%(period, start_date_obj.strftime('%d%m%Y_%H%M%S')) ) as dbObj:
      if not dbObj.db_is_initialized:
         from matplotlib.dates import date2num
         import cryptowatch.Client as cl
         import time
      
         after=int(time.mktime(start_date_obj.timetuple()))

         print "Grabbing data from cryptowatch. Be patient, can take a minute..."
         client = cl.MarketClient("kraken", "etheur")
         OHLC = client.GetOHLC( after=str(after), periods=[period])
      
         quotes = np.array( [ (date2num(datetime.fromtimestamp(x.open_time)), x.open, x.high, x.low, x.close, x.volume) for x in OHLC[period] ], dtype=float )
         dbObj.save_data(quotes)
      else:
         quotes = dbObj.load_data()
   
   total_time_years = len(quotes)*int(period) / (3600.0*24*365)
   print "Simulating %d samples separated %s seconds: %f years."%(len(quotes), period, total_time_years)
   
   technical_indicators = []
   kelchM, kelchU, kelchL = fm.KELCH(quotes, 14)
   technical_indicators.append( technical_indicator('kelner_average', kelchM, True, 'kelner') )
   technical_indicators.append( technical_indicator('kelner_upper', kelchU, True) )
   technical_indicators.append( technical_indicator('kelner_lower', kelchL, True) )
   
   psar_results = fm.parabolic_sar(quotes)
   technical_indicators.append( technical_indicator('psar_bull', psar_results['psarbull'], True, 'psar') )
   technical_indicators.append( technical_indicator('psar_bear', psar_results['psarbear'], True) )

   macd = fm.macd(quotes, short_term = 10)
   technical_indicators.append( technical_indicator('macd', macd[0], True, 'macd') )
   technical_indicators.append( technical_indicator('macd_s', macd[1], True, 'macd_s') )

   initial_capital = 1000
   end_capital, OrderBook = simulate_trading(quotes, technical_indicators, initial_capital)
   
   # compute annual percentage rate
   periods_year = 1.0/total_time_years
   rate_period = end_capital/initial_capital
   APY = pow( rate_period, periods_year) - 1
   print "Initial capital: %f\nProfit: %f\nTime: %f\nInterest rate: %.2f%%\nAPY: %.2f%%\n"%(initial_capital, end_capital - initial_capital, total_time_years, (rate_period-1)*100, APY*100)
   
   processing_results = {'order_book_events': OrderBook }
   display_plot(quotes, technical_indicators, processing_results)
    

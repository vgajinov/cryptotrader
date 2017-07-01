#!/usr/bin/env python2

from finance_metrics import *
import sys

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
      #indicator = 'order_book'
      #result = processing_results[ indicator ]
      #dates = [x[0] for x in result]
      #data = [x[1] for x in result]
      #linecolor = "black"
      #plt.plot(dates, data, linestyle=linestyle, label=indicator, linewidth=1, color=linecolor)

      yoffset = ax.get_ylim()[0]
      for event in processing_results['order_book_events']:
         ax.annotate(event[1], xy=(event[0], event[2]),  xycoords='data',
                  xytext=(event[0], yoffset+1), textcoords='data',
                  bbox=dict(boxstyle="round", fc="0.8"),
                  arrowprops=dict(arrowstyle="->",
                  connectionstyle="angle,angleA=0,angleB=90,rad=10"),
                  )

   plt.legend()
   plt.show()


def get_trade_proposals(quotes, technical_indicators):

   #for i in quotes:
   #   print i
   #raise Exception()
   # we want to BUY when technical_indicators['psar_bear'] switches from value to None,
   # if there are AT LEAST N consecutives Nones
   consec_nones = 2
   numsamples = len(technical_indicators['psar_bear'])

   # get the indices of the None elements in array, whose preceding element is not None
   #for elem in technical_indicators['psar_bear']:
   #   print elem

   local_mins = [ min(i+consec_nones, numsamples) for i, j in enumerate(technical_indicators['psar_bear']) if j is None and technical_indicators['psar_bear'][i-1] is not None]

   # restrict the eligible elements only to those that have AT LEAST N consecutives Nones
   buy_time_idx = []
   for i in local_mins:
      window = max(i - consec_nones, 0 )
   
      if all([sample is None for sample in technical_indicators['psar_bear'][window:i]]):
         buy_time_idx.append(i)
   
   # get the indices of the None elements in array, whose next element is None
   local_maxs = [ i for i, j in enumerate(technical_indicators['psar_bull']) if j is None and technical_indicators['psar_bull'][i-1] is not None]

   # restrict the eligible elements only to those that have AT LEAST N consecutives Nones
   sell_time_idx = []
   for i in local_maxs:
      window = max(i-consec_nones, 0)
   
      if all([sample is None for sample in technical_indicators['psar_bull'][window:i]]):
         sell_time_idx.append(i)

   # generate an order book
   OrderBook = [ (quotes[i,0], 'B', quotes[i,1]) for i in buy_time_idx ] + [ (quotes[i,0], 'S', quotes[i,1]) for i in sell_time_idx ]
  
   print OrderBook
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

with dbconnector( "samples_%s_26062017_000000.db"%period ) as dbObj:
   if not dbObj.db_is_initialized:
      from matplotlib.dates import date2num
      import cryptowatch.Client as cl
      import time
      from datetime import datetime
   
      s = "26/06/2017 00:00:00"
      after=int(time.mktime(datetime.strptime(s, "%d/%m/%Y %H:%M:%S").timetuple()))
      #s = "27/06/2017 00:00:00"
      #before=int(time.mktime(datetime.strptime(s, "%d/%m/%Y %H:%M:%S").timetuple()))
   
      client = cl.MarketClient("kraken", "etheur")
      #OHLC = client.GetOHLC(before=str(before), after=str(after), periods=[period])
      OHLC = client.GetOHLC( after=str(after), periods=[period])
   
      quotes = np.array( [ (date2num(datetime.fromtimestamp(x.open_time)), x.open, x.high, x.low, x.close, x.volume) for x in OHLC[period] ], dtype=float )
      dbObj.save_data(quotes)
   else:
      quotes = dbObj.load_data()

#technical_indicators = KELCH(quotes, 14)
technical_indicators = {}

psar_results = parabolic_sar(quotes)
technical_indicators['psar_bull'] = psar_results['psarbull']
technical_indicators['psar_bear'] = psar_results['psarbear']

OrderBook = get_trade_proposals(quotes, technical_indicators)
#simulate_trading(OrderBook)
processing_results = {}
processing_results['order_book_events'] = OrderBook
display_plot(quotes, technical_indicators, processing_results)

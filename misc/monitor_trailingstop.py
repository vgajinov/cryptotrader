#!/usr/bin/env python3
import sys, socket, threading
import signal
from time import sleep
from datetime import datetime, timedelta

# Add the local folder "python-modules" to the python path
sys.path.insert(0, "./python-modules")

from notification import *
from exchanges import exchangeFactory

logger = None

#import code, traceback, signal
#def debug(sig, frame):
#    """Interrupt running process, and provide a python prompt for
#    interactive debugging."""
#    d={'_frame':frame}         # Allow access to frame object.
#    d.update(frame.f_globals)  # Unless shadowed by global
#    d.update(frame.f_locals)
#
#    i = code.InteractiveConsole(d)
#    message  = "Signal received : entering python shell.\nTraceback:\n"
#    message += ''.join(traceback.format_stack(frame))
#    i.interact(message)
#
#signal.signal(signal.SIGUSR1, debug)  # Register handler

# set up a clean exit when calling ctrl+c
signal.signal(signal.SIGINT, lambda s,f: sys.exit(0))

# Class to start a helper thread that checks the exchange at a given frequency and
# updates the dictionary with the ticker data
class exchange_checker(object):
   def __init__(self, cryptocurr=None, period_seconds=5):
      self.spreads = {}
      for curr, mkt in cryptocurr:
         try:
            self.spreads[mkt][curr] = (None, None, None)
         except:
            self.spreads[mkt] = {curr: (None, None, None)}

      self._lastupdate = [None]
      self.period_seconds = period_seconds
      self.helper = threading.Thread(target=self.queryExchange, args=(self.spreads,self._lastupdate))
      self.helper.setDaemon(True)
      self.helper.start()

   @property
   def lastupdate(self):
      return self._lastupdate[0]

   def add_curr(self, curr):
      # setdefault is guaranteed to be atomic from 2.7 on.
      self.spreads.setdefault(curr)

   def queryExchange(self, spreadDict, lastupdate):
      while True:
         lastupdate[0] = datetime.now()

         # the reason we do it this weird way is (instead of a simple loop
         # over the currencies) is: the exchange might have optimized
         # queries for list, so we perform just one call to get all
         # the spreads at once
         for mkt in spreadDict:
            spreads = mkt.queryTicker(list(spreadDict[mkt]))
            for idx,key in enumerate(spreadDict[mkt]):
               spreadDict[mkt][key] = spreads[idx]
         
         sleep(self.period_seconds)


def check_sell_trailing_stops(monitor, orders):
   # buffer for the items to be removed
   items_to_remove = []

   # cryptocurrs_markets not ready
   cryptocurrs_markets=set()

   # check all the orders
   for idx, order in enumerate(orders):
      logger.debug("Checking order {}".format(order))
      cryptocurr, order_buy, order_vol, mkt, stop_loss_distance, stop_loss = order

      # if the mkt and cryptocurr are known for not being ready, just
      # continue
      if (mkt, cryptocurr) in cryptocurrs_markets:
         logger.info("Ignoring ticker request for cryptocurr {} and market {}".format(cryptocurr,mkt))
         continue

      # request last available information to the exchange monitor
      # for this currency
      bid, ask, vol = t = monitor.spreads[mkt][cryptocurr]
      if not all(t):
         logger.info("No ticker info received for cryptocurr {} and market {}".format(cryptocurr,mkt))
         cryptocurrs_markets.add((mkt, cryptocurr))
         continue
      curr_time = monitor.lastupdate

      #calculate the bid price with respect to the buying price,
      # because this is the price at which we will sell
      midprice = bid
      logger.debug("crypto {} in market {} at price {:.3f}".format(cryptocurr, mkt, midprice ))

      # check the status of the trailing stop
      if midprice < stop_loss:
         try:
            mkt.sellMkt(cryptocurr, order_vol)
         except Exception as e:
            logger.notify("Exception triggered while managing TSs triggered for crypto {} in market {} at price {:.3f} SL {:.3f}: {}".format(cryptocurr, mkt, midprice, stop_loss, e))
         else:
            logger.notify("TSs triggered for crypto {} in market {} at price {:.3f} SL {:.3f}".format(cryptocurr, mkt, midprice, stop_loss ))
         items_to_remove.append(idx)
      else:
         t = max(midprice - stop_loss_distance, stop_loss)
         if t > stop_loss:
            order[5] = stop_loss = t
            logger.info("TSs reset for crypto {} in market {} at price {:.3f} SL {:.3f}".format(cryptocurr, mkt, midprice, stop_loss ))

   orders[:] = [ x for i,x in enumerate(orders) if i not in items_to_remove ]


def check_buy_trailing_stops(monitor, orders, buy_trailing_stop, open_orders_buy):
   # buffer for the items to be removed
   items_to_remove = []

   # cryptocurrs_markets not ready
   cryptocurrs_markets=set()

   # check the status for the orders in open_orders_buy
   try:
      infoOrders = mkt.queryOrder(open_orders_buy)
   except Exception as e:
      logger.notify("Exception triggered while querying buy open orders")
   else:
      for info in infoOrders:
         if info['status'] == "canceled":
            logger.notify("TSb {} triggered for crypto {} in market {} at market price was canceled.".format(mktOrderId, cryptocurr, mkt ))
         elif info['status'] == "closed":
            logger.notify("TSb triggered for crypto {} in market {} at price {:.3f} SL {:.3f}".format(cryptocurr, mkt, midprice, stop_loss ))
            orders.append([cryptocurr, float(info['price']), float(info['vol']), mkt, stop_loss, float(info['price'])-stop_loss])

   # check all the orders
   for idx, order in enumerate(buy_trailing_stop):
      logger.debug("Checking order {}".format(order))
      cryptocurr, mkt, stop_loss_distance, stop_loss = order

      # if the mkt and cryptocurr are known for not being ready, just
      # continue
      if (mkt, cryptocurr) in cryptocurrs_markets:
         logger.info("Ignoring ticker request for cryptocurr {} and market {}".format(cryptocurr,mkt))
         continue

      # request last available information to the exchange monitor
      # for this currency
      bid, ask, vol = t = monitor.spreads[mkt][cryptocurr]
      if not all(t):
         logger.info("No ticker info received for cryptocurr {} and market {}".format(cryptocurr,mkt))
         cryptocurrs_markets.add((mkt, cryptocurr))
         continue
      curr_time = monitor.lastupdate

      #calculate the bid price with respect to the buying price,
      # because this is the price at which we will sell
      midprice = bid
      logger.debug("crypto {} in market {} at price {:.3f}".format(cryptocurr, mkt, midprice ))

      # if check the status of the trailing stop
      if midprice > stop_loss:
         # TODO: calculate how much we want to invest in this transaction
         order_vol = 0.02

         try:
            mktOrderId = mkt.buyMkt(cryptocurr, order_vol)
         except Exception as e:
            logger.notify("Exception triggered while managing TSb triggered for crypto {} in market {} at price {:.3f} SL {:.3f}: {}".format(cryptocurr, mkt, midprice, stop_loss, e))
         else:
            try:
               info = mkt.queryOrder(mktOrderId)
            except Exception as e:
               logger.notify("Exception triggered while querying TSb {} triggered for crypto {} in market {} at price {:.3f} SL {:.3f}: {}".format(mktOrderId, cryptocurr, mkt, midprice, stop_loss, e))
            else:
               if info['status'] == "canceled":
                  logger.notify("TSb {} triggered for crypto {} in market {} at market price was canceled.".format(mktOrderId, cryptocurr, mkt ))
               elif info['status'] != "closed":
                  logger.debug("TSb {} triggered for crypto {} in market {} at market price. status: {}".format(mktOrderId, cryptocurr, mkt, info['status'] ))
                  open_orders_buy.append(mktOrderId)
                  items_to_remove.append(idx)
               else:
                  logger.notify("TSb triggered for crypto {} in market {} at price {:.3f} SL {:.3f}".format(cryptocurr, mkt, midprice, stop_loss ))
                  orders.append([cryptocurr, float(info['price']), float(info['vol']), mkt, stop_loss, float(info['price'])-stop_loss])
      else:
         order[3] = stop_loss = min(midprice + stop_loss_distance, stop_loss)
         logger.debug("TSb reset for crypto {} in market {} at price {:.3f} SL {:.3f}".format(cryptocurr, mkt, midprice, stop_loss ))

   buy_trailing_stop[:] = [ x for i,x in enumerate(buy_trailing_stop) if i not in items_to_remove ]


if __name__ == "__main__":
   # get the reference to the exchange
   exchangeKraken = exchangeFactory().getExchange("kraken", keyfile="kraken_trade.key")

   # set up notification
   setup_basic_logging()
   setup_remote_notification("pushbullet.key")

   logger = logging.getLogger("monitor_trailingstop")

   # set up a trailing stop for the order at the
   # distance for that crypto (related to market volatility)
   # the legend is "CRYPTO" : distance
   stop_loss_distance = {}
   stop_loss_distance[exchangeKraken] = { "XETHZEUR": 1 , "XXBTZEUR": 30 }

   # array of orders we are monitoring
   # and buffer to track the buying trailing stop for each order
   orders = [["XETHZEUR", 330, 0.020, exchangeKraken, 4, 329], ["XXBTZEUR", 3600.0, 3.0, exchangeKraken, 30, 3570]]
   orders = [["XXBTZEUR", 4085.82, 0.196, exchangeKraken, 40, 4049.53]]
   buy_trailing_stop = [["XETHZEUR", exchangeKraken, 4, 320]]
   open_orders_buy = []

   # start a helper thread to monitor the currencies for markets
   monitor = exchange_checker(cryptocurr=set((x[0],x[3]) for x in orders))

   # wait for the monitor to contain any data
   logger.info("Waiting for initialization")
   while not any( x.count(None) != len(x) for mkt,currs in monitor.spreads.items() for x in currs.values() ):
      sleep(1)
   logger.info("Price monitor initialized")

   last_minute_notification = datetime.now().minute
   # endless loop
   while True:
      if len(orders) > 0:
         check_sell_trailing_stops(monitor, orders)

      if len(buy_trailing_stop) > 0:
         check_buy_trailing_stops(monitor, orders, buy_trailing_stop, open_orders_buy)

      t = datetime.now().minute
      if t%5 == 0 and t != last_minute_notification:
         last_minute_notification = t
         logger.info("Autotrader still alive!")
      sleep(10)
   

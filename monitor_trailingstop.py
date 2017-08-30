#!/usr/bin/env python3
import sys, socket, threading
import signal
from time import sleep
from datetime import datetime, timedelta
import daemon

# Add the local folder "python-modules" to the python path
sys.path.insert(0, "./python-modules")

from notification import *
from exchanges import exchangeFactory

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


if __name__ == "__main__":
   #daemonContext = daemon.DaemonContext( files_preserve = [ handler.stream ] )

   #logging.setLevel(logging.DEBUG)
   # get the reference to the exchange
   exchangeKraken = exchangeFactory().getExchange("kraken", keyfile="kraken_trade.key")

   # set up notification
   setup_remote_notification("pushbullet.key")

   logger = logging.getLogger("monitor_trailingstop")

   # set up a trailing stop for the order at the
   # distance for that crypto (related to market volatility)
   # the legend is "CRYPTO" : (noise value, distance)
   stop_loss_distance = {}
   stop_loss_distance[exchangeKraken] = { "XETHZEUR": 1 , "XXBTZEUR": 30 }

   # array of orders we are monitoring
   orders = [("XETHZEUR", 326, 0.020, exchangeKraken)]#, ("XXBTZEUR", 3600.0, 3.0, exchangeKraken)]

   # buffer to track the trailing stop-loss, if set, for each order
   stop_loss = [ x[1] - stop_loss_distance[x[3]][x[0]] for x in orders ]

   # once an alarm has been triggered, we do not want to bother for the
   # same currency in the next snooze_time minutes
   snooze_time = timedelta(minutes=3)
   curr_time = datetime.now()

   # start a helper thread to monitor the currencies for markets
   monitor = exchange_checker(cryptocurr=set((x[0],x[3]) for x in orders))

   # wait for the monitor to contain any data
   logger.info("Waiting for initialization")
   while not any( x != (None, None, None) for mkt,currs in monitor.spreads.items() for x in currs.values() ):
      sleep(1)
   logger.info("Price monitor initialized")

   # endless loop
   while True:
      # check all the orders
      for idx, order in enumerate(orders):
         cryptocurr, order_buy, order_vol, mkt = order

         # request last available information to the exchange monitor
         # for this currency
         bid, ask, vol = t = monitor.spreads[mkt][cryptocurr]
         if not all(t):
            logger.info("No ticker info received for cryptocurr {}".format(cryptocurr))
            sleep(10)
            continue

         curr_time = monitor.lastupdate

         #calculate the bid price with respect to the buying price,
         # because this is the price at which we will sell
         midprice = bid 
         logger.debug("crypto {} in market {} at relative price {:.3f}".format(cryptocurr, mkt, midprice ))

         # if check the status of the trailing stop
         if midprice >= (order_buy + stop_loss_distance[mkt][cryptocurr]):
            stop_loss[idx] = midprice - stop_loss_distance[mkt][cryptocurr]
            logger.debug("TS reset for crypto {} in market {} at relative price {:.3f}: {:.3f}".format(cryptocurr, mkt, midprice, stop_loss[idx] ))
         elif midprice < stop_loss[idx]:
            mkt.sellMkt(cryptocurr, order_vol)
            logger.notify("TS triggered for crypto {} in market {} at relative price {:.3f}: {:.3f}".format(cryptocurr, mkt, midprice, stop_loss[idx] ))

      logger.debug("Price check performed")

      sleep(10)
   

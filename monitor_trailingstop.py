#!/usr/bin/env python3
import sys, socket, threading
from time import sleep
from datetime import datetime, timedelta

# Add the local folder "python-modules" to the python path
sys.path.insert(0, "./python-modules")

from notification import *
from exchange_backends.exchangeFactory import *

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

# set up the logging system
logger = setup_custom_logger('myapp')
# get the reference to the exchange
exchange = exchangeFactory().getExchange("kraken", keyfile="kraken.key")
# set up notification
notification = Notification("pushbullet.key")


# Class to start a helper thread that checks the exchange at a given frequency and
# updates the dictionary with the ticker data
class exchange_checker(object):
   def __init__(self, cryptocurr=None, period_seconds=5):
      self.spreads = { x : (None, None, None) for x in cryptocurr }
      self._lastupdate = [None]
      self.period_seconds = period_seconds
      self.helper = threading.Thread(target=self.queryExchange, args=(self.spreads,self._lastupdate))
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
         spreads = exchange.queryTicker(list(spreadDict.keys()))
         for idx,key in enumerate(spreadDict.keys()):
            spreadDict[key] = spreads[idx]
         
         sleep(self.period_seconds)


# function that, given a list of volumes and thresholds,
# returns the aggregated volumes for accumulated up to
# each threshold
def aggregated_volumes(vol_buffer, thList):
   result = [0.0] * len(thList)
   last_idx = 0
   for i,s in enumerate(vol_buffer[:0:-1]):
      t,v = s
   
      # get the index of the first threshold that is above
      cond = map(lambda x: t<=x, thList)
   
      # if there are not True values, just break
      if not any(cond):
         last_idx = i
         break
   
      # accumulate v for the thresholds that are True
      result = [ r + c*v for r,c in zip(result,cond)]

   # remove the elements, from the beginning of the list,
   # that exceed all thresholds taken into account
   del vol_buffer[:last_idx+1]
   return result


if __name__ == "__main__":
   # these are profit thresholds we want to monitor, toghether with the states/messages 
   # to be notified when the midprice falls on them.
   profit_thresholds = (0.980, 0.985, 1.005, 1.015, 1.025)
   profit_messages = ("CONSIDER SELLING", "WARNING", "no change", "Fees covered", "Some profit", "Sensible profit")

   # time thresholds for aggregated volumes, and the alarm levels for each one of them
   # and each currency
   volume_thresholds = [ timedelta(minutes=1), timedelta(minutes=3) ]
   volume_alarms = { "XETHZEUR": [ 200, 300 ], "XXBTZEUR": [ 200, 300 ]}

   # in case midprice is above "Fees covered"+<noise value>, set up a trailing stop for the order at the
   # distance for that crypto (related to market volatility)
   # the legend is "CRYPTO" : (noise value, distance)
   stop_loss_distance = { "XETHZEUR": (4, 4) , "XXBTZEUR": (30, 30) }

   # array of orders we are monitoring
   orders = [("XETHZEUR", 275.5, 3.0), ("XXBTZEUR", 3600.0, 3.0)] 

   # to track state changes we want to compare the previous and current states
   prev_state = [ None ]*len(orders)
   curr_state = [ None ]*len(orders)

   # buffer to track the trailing stop-loss, if set, for each order
   stop_loss = [ None ]*len(orders)

   # the current delta volumes and previous full volume for each currency
   vol_buffer = { x[0]:[] for x in orders}
   prev_vol = { x[0]:[] for x in orders}
   
   # once an alarm has been triggered, we do not want to bother for the
   # same currency in the next snooze_time minutes
   snooze_time = timedelta(minutes=3)
   curr_time = datetime.now()
   last_alert_volume_time = {x[0]: curr_time - snooze_time for x in orders}

   # start a helper thread to monitor the currencies
   monitor = exchange_checker(cryptocurr=set(x[0] for x in orders))

   # wait for the monitor to contain any data
   while not any(x != (None, None, None) for x in monitor.spreads.values()):
      print ("Waiting for initialization...")
      sleep(1)
  
   # endless loop
   while True:
      # flags to find if we have already cheked a currency in this iteration
      currency_wide = {x[0]: False for x in orders}

      # flags to find if any volume alert has been triggered for any currency in this iteration
      alert_volume = {x[0]: False for x in orders }

      # flag to alert of a trailing stop being triggered
      alert_trailing_stop = [False] * len(orders)

      # check all the orders
      for idx, order in enumerate(orders):
         cryptocurr, order_buy, order_vol = order

         # request last available information to the exchange monitor
         # for this currency
         bid, ask, vol = monitor.spreads[cryptocurr]
         curr_time = monitor.lastupdate

         #calculate the midprice with respect to the buying price, and get the profit threshold
         midprice = (ask + bid) / 2.0
         midprice_rel = midprice / order_buy
         curr_state[idx] = sum( map(lambda x: midprice_rel <= x, profit_thresholds) )
 
         # if check if we can set up the trailing stop
         if stop_loss[idx] is None and curr_state[idx] > 3 and midprice >= (buy_price + stop_loss_distance[idx][0]):
            stop_loss[idx] = midprice - stop_loss_distance[idx][1]
         elif stop_loss[idx] is not None:
            # if the stop_loss has been set, check for update or if it has been triggered
            if midprice - stop_loss_distance[idx][1] >= stoploss:
               stop_loss[idx] = midprice - stop_loss_distance[idx][1]
            elif midprice < stoploss[idx]:
               alert_trailing_stop[idx] = True

         # check the volume-related data for this cryptocurrency (if it has not been alread
         # evaluated in the current iteration)
         if not currency_wide[cryptocurr]:
            delta_vol = 0.0 if not vol_buffer[cryptocurr] else vol - prev_vol[cryptocurr]
            vol_buffer[cryptocurr].append((curr_time, delta_vol))
            prev_vol[cryptocurr] = vol
   
            # get the aggregated volumes for the previous thresholds
            agg_vol = aggregated_volumes(vol_buffer[cryptocurr], [curr_time - x for x in volume_thresholds])
  
            # check if any of the aggregated volumes triggers an alarm
            alert_volume[cryptocurr] = any( x>y for x,y in zip(agg_vol,volume_alarms[cryptocurr]) )

            # Mark this currency as updated in this iteration
            currency_wide[cryptocurr] = True
            
      # check if sending a message is required
      msg = ""

      # check if the monitoring state has changed for any order
      for x,y,o in zip(curr_state, prev_state, orders):
         if x != y:
            msg += "{} for {}, {}, {}. ".format(profit_messages[x], *o)

      #remove the last space from msg
      if msg:
         del msg[-1]
      
      # check if any volume alarm has been triggered
      for key,val in alert_volume.items():
         # if there is an alarm and snooze_time has already passed,
         # update the messge and reset last_alert_volume_time
         if val and curr_time > last_alert_volume_time[key] + snooze_time:
            last_alert_volume_time[key] = curr_time
            msg += " Alert VOLUME for crypto {}.".format(k)
  
      # check if any trailing stop has been triggered
      for idx in [i for i, x in enumerate(alert_trailing_stop) if x]:
         msg += " Alert TS for order {}, {}, {}.".format(orders[idx])

      # if there is anything to be send, send it
      if msg:
         logger.info(msg)
         notification.notify("Monitor alert", msg)
         prev_state= list(curr_state)

      logger.info("Price check performed")
      logger.debug(vol_buffer)
      logger.debug(curr_state)

      sleep(10)
      

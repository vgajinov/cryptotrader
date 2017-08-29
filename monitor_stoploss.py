#!/usr/bin/env python3
import sys, socket, threading
import signal
from time import sleep
from datetime import datetime, timedelta

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


#logging.setLevel(logging.DEBUG)
# get the reference to the exchange
exchangeKraken = exchangeFactory().getExchange("kraken", keyfile="kraken.key")
# set up notification
notification = setup_remote_notification("pushbullet.key")


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
   logger = logging.getLogger("monitor_stoploss")

   # these are profit thresholds we want to monitor, toghether with the states/messages 
   # to be notified when the midprice falls on them.
   profit_thresholds = (0.980, 0.985, 1.005, 1.015, 1.025)
   profit_messages = ("CONSIDER SELLING", "WARNING", "no change", "Fees covered", "Some profit", "Sensible profit")

   # time thresholds for aggregated volumes, and the alarm levels for each one of them
   # and each currency
   volume_thresholds = [ timedelta(minutes=1), timedelta(minutes=3) ]
   volume_alarms = { }
   volume_alarms[exchangeKraken] = { "XETHZEUR": [ 200, 300 ], "XXBTZEUR": [ 200, 300 ]}

   # array of orders we are monitoring
   orders = [("XETHZEUR", 281, 3.51, exchangeKraken)]#, ("XXBTZEUR", 3600.0, 3.0, exchangeKraken)]

   # to track state changes we want to compare the previous and current states
   prev_state = [ None ]*len(orders)
   curr_state = [ None ]*len(orders)

   # the current delta volumes and previous full volume for each currency
   vol_buffer = {}
   prev_vol = {}
   for x in orders:
      try:
         vol_buffer[x[3]][x[0]] = []
      except:
         vol_buffer[x[3]] = {x[0]: []}
         prev_vol[x[3]] = {}
   
   # once an alarm has been triggered, we do not want to bother for the
   # same currency in the next snooze_time minutes
   snooze_time = timedelta(minutes=3)
   curr_time = datetime.now()
   last_alert_volume_time = {}
   for x in orders:
      try:
         last_alert_volume_time[x[3]][x[0]] = curr_time - snooze_time
      except:
         last_alert_volume_time[x[3]] = {x[0] : curr_time - snooze_time}


   # start a helper thread to monitor the currencies for markets
   monitor = exchange_checker(cryptocurr=set((x[0],x[3]) for x in orders))

   # wait for the monitor to contain any data
   print ("Waiting for initialization.", end="")
   while not any( x != (None, None, None) for mkt,currs in monitor.spreads.items() for x in currs.values() ):
      sleep(1)
      print(".", end="")
   print ("\nPrice monitor initialized")

   # endless loop
   while True:
      # flags to find if we have already checked a currency in this iteration
      currency_wide = {}
      for x in orders:
         try:
            currency_wide[x[3]][x[0]] = False
         except:
            currency_wide[x[3]] = {x[0]: False}

      # flags to find if any volume alert has been triggered for any currency in this iteration
      alert_volume = {}
      for x in orders:
         try:
            alert_volume[x[3]][x[0]] = False
         except:
            alert_volume[x[3]] = {x[0]: False}

      # check all the orders
      for idx, order in enumerate(orders):
         cryptocurr, order_buy, order_vol, mkt = order

         # request last available information to the exchange monitor
         # for this currency
         t = monitor.spreads[mkt][cryptocurr]
         if not all(t):
            logger.info("No ticker info received for cryptocurr {}".format(cryptocurr))
            sleep(10)
            continue

         bid, ask, vol = t
         curr_time = monitor.lastupdate

         #calculate the midprice with respect to the buying price
         midprice = (ask + bid) / ( 2.0 * order_buy )
         t = sum(map(lambda x: midprice >= x, profit_thresholds))
         logger.debug("State vec for crypto {} in market {} at relative price {:.3f}: {} ({})".format(cryptocurr, mkt, midprice, t, profit_messages[t]))
         curr_state[idx] = t
  
         # check the volume-related data for this cryptocurrency (if it has not been alread
         # evaluated in the current iteration)
         if not currency_wide[mkt][cryptocurr]:
            try:
               delta_vol = vol - prev_vol[mkt][cryptocurr]
            except:
               delta_vol = 0.0
            vol_buffer[mkt][cryptocurr].append((curr_time, delta_vol))
            prev_vol[mkt][cryptocurr] = vol
   
            # get the aggregated volumes for the previous thresholds
            agg_vol = aggregated_volumes(vol_buffer[mkt][cryptocurr], [curr_time - x for x in volume_thresholds])
  
            # check if any of the aggregated volumes triggers an alarm
            alert_volume[mkt][cryptocurr] = any( x>y for x,y in zip(agg_vol,volume_alarms[mkt][cryptocurr]) )
            
            # Mark this currency as updated in this iteration
            currency_wide[cryptocurr] = True
            
      # check if sending a message is required
      msg = ""

      # check if the monitoring state has changed for any order
      for x,y,o in zip(curr_state, prev_state, orders):
         if x != y:
            msg += "{} for {}, {}, {}.".format(profit_messages[x], *o[:3])
      
      # check if any volume alarm has been triggered
      for mkt,val in alert_volume.items():
         for curr,flag in val.items():
            # if there is an alarm and snooze_time has already passed,
            # update the messge and reset last_alert_volume_time
            if flag and curr_time > last_alert_volume_time[mkt][curr] + snooze_time:
               last_alert_volume_time[mkt][key] = curr_time
               msg += "Alert VOLUME for crypto {} in market {}.".format(curr, mkt)
  
      # if there is anything to be send, send it
      if msg:
         logger.notify(msg)
         prev_state= list(curr_state)
      logger.debug("Price check performed")

      sleep(10)
      


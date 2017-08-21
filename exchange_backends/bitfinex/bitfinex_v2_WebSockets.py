import os, sys
import websocket
import json
import time
from datetime import datetime
from threading import Thread
from pydispatch import dispatcher


# NOTES:
#
# 1. Do not parse text descriptions, use only codes.
#    Text descriptions are subject to changes and adjustments without any warning
# 2. Messages may contain null placeholders in the payload for future additional fields
# 3. All times are UTC timestamps expressed as milliseconds.
# 4. The precision level of all trading prices is calculated based on significant figures.
#    For all pairs on Bitfinex we use 5 significant digits.
#    Examples of five significant digits would be 12.123, 1.1234, 123.43, and 1234.5.
#    API will truncate price with precision > 5
# 5. Trading pairs symbols are formed prepending a "t" before the pair (i.e tBTCUSD, tETHUSD).
#    Margin currencies symbols are formed prepending a "f" before the currency (i.e fUSD, fBTC, ...)
# 6. Each message sent and received via the Bitfinex's websocket channel is encoded in JSON format
#
#
# ERRORS:
#
# In case of error, you receive a message containing the proper error code (code JSON field).
# Generic Error Codes:
#   10000 : Unknown event
#   10001 : Unknown pair
#
#
# INFO MESSAGES:
#
# Info messages are sent from the websocket server to notify the state of your connection.
# Right after connecting you receive an info message that contains the actual version of the websocket stream.
#   {
#     "event"  :"info",
#     "version": 1
#   }
#
# Websocket server sends other info messages to inform regarding relevant events.
#   {
#     "event": "info",
#     "code" : "<CODE>",
#     "msg"  : "<MSG>"
#   }
#
# Info Codes
# 20051 : Stop/Restart Websocket Server (please try to reconnect)
# 20060 : Refreshing data from the Trading Engine. Please pause any activity and resume
#         after receiving the info message 20061 (it should take 10 seconds at most).
# 20061 : Done Refreshing data from the Trading Engine. You can resume normal activity.
#         It is advised to unsubscribe/subscribe again all channels.
#
#
# CONFIGURATION:
#
# In order to change the configuration, there is a new event able to be requested conf,
# and this will have a parameter flags which is the bitwise XOR of the different options listed below
#   {
#     event: "conf",
#     flags: FLAGS
#   }
#
# Example:
# To enable all decimals as strings and all times as date strings, you would set the value of flags to 40
#
# Available Options
#    Name     Value        Description
#    DEC_S        8     Enable all decimal as strings.
#    TIME_S      32     Enable all times as date strings.
#    SEQ_ALL  65536     Enable sequencing BETA FEATURE
#
#
# SUBSCRIBING TO CHANNEL:
#
# 1. To receive data from a channel you have to send a "subscribe" message first.
# 2. Upon subscribing to a channel an initial snapshot is sent.
#    Typically, the snapshot will have as its first item, the CHANNEL_ID, its second item will be the CHANNEL_NAME
#    and the third item will be an array of UPDATE_MESSAGEs (each of which is itself an array).
# 3. After receiving the snapshot, you will receive updates upon any change.
#    CHANNEL_ID's allow you to keep track of the messages, they are static per session,
#    you will receive both the CHANNEL_NAME and the CHANNEL_ID in the response to a subscription message.
# 4. To stop receiving data from a channel you have to send a "unsubscribe" message.
#
# Error Codes:
#   10300 : Subscription failed (generic)
#   10301 : Already subscribed
#   10302 : Unknown channel
#
#
# API MESSAGE LIST:
#
#  This is the list of all the message types that the API will send
#    Term       Definition
#  ------------------------------
#    bu       balance update
#    ps       position snapshot
#    pn       new position
#    pu       position update
#    pc       position close
#    ws       wallet snapshot
#    wu       wallet update
#    os       order snapshot
#    on       new order
#    ou       order update
#    oc       order cancel
#    oc-req   order cancel
#    te       trade executed
#    tu       trade execution update
#    fte      funding trade execution
#    ftu      funding trade update
#    hos      historical order snapshot
#    mis      margin information snapshot
#    miu      margin information update
#    n        notification
#    fos      funding offer snapshot
#    fon      funding offer new
#    fou      funding offer update
#    foc      funding offer cancel
#    hfos     historical funding offer snapshot
#    fcs      funding credits snapshot
#    fcn      funding credits new
#    fcu      funding credits update
#    fcc      funding credits close
#    hfcs     historical funding credits snapshot
#    fls      funding loan snapshot
#    fln      funding loan new
#    flu      funding loan update
#    flc      funding loan close
#    hfls     historical funding loan snapshot
#    hfts     historical funding trade snapshot
#    fte      funding trade execution
#    ftu      funding trade update
#    uac      user custom price alert
#
#
# ERROR / INFO CODES:
#
#   Event              Code	 Description
#  -------------------------------------------------------------------------------
#   ERR_UNK           10000    Unknown error
#   ERR_GENERIC       10001    Generic error
#   ERR_CONCURRENCY   10008    Concurrency error
#   ERR_PARAMS        10020    Request parameters error
#   ERR_CONF_FAIL     10050    Configuration setup failed
#   ERR_AUTH_FAIL     10100    Failed authentication
#   ERR_AUTH_PAYLOAD  10111    Error in authentication request payload
#   ERR_AUTH_SIG      10112    Error in authentication request signature
#   ERR_AUTH_HMAC     10113    Error in authentication request encryption
#   ERR_AUTH_NONCE    10114    Error in authentication request nonce
#   ERR_UNAUTH_FAIL   10200    Error in un-authentication request
#   ERR_SUB_FAIL      10300    Failed channel subscription
#   ERR_SUB_MULTI     10301    Failed channel subscription: already subscribed
#   ERR_UNSUB_FAIL    10400    Failed channel un-subscription: channel not found
#   ERR_READY         11000    Not ready, try again later
#   EVT_STOP          20051    Websocket server stopping... please reconnect later
#   EVT_RESYNC_START  20060    Websocket server resyncing... please reconnect later
#   EVT_RESYNC_STOP   20061    Websocket server resync complete. please reconnect
#   EVT_INFO           5000    Info message
#
#
# SYMBOLS:
# ["btcusd","ltcusd","ltcbtc","ethusd","ethbtc","etcbtc","etcusd","rrtusd","rrtbtc",
#  "zecusd","zecbtc","xmrusd","xmrbtc","dshusd","dshbtc","bccbtc","bcubtc","bccusd",
#  "bcuusd","xrpusd","xrpbtc","iotusd","iotbtc","ioteth","eosusd","eosbtc","eoseth",
#  "sanusd","sanbtc","saneth","omgusd","omgbtc","omgeth","bchusd","bchbtc","bcheth"]


# SSL connection
WEBSOCKET_URI = "wss://api.bitfinex.com/ws/2"

SYMBOLS = ["btcusd","ltcusd","ltcbtc","ethusd","ethbtc","bchbtc","bcheth"]

# ==========================================================================================
#   Client
# ==========================================================================================

class BitfinexWSClient:
   def __init__(self):
      self.ws = None
      self.channels = {
         'book'     : self.subscribeToBook,
         'raw_book' : self.subscribeToRawBook,
         'trades'   : self.subscribeToTrades,
         'ticker'   : self.subscribeToTicker,
         'candles'  : self.subscribeToCandles
      }
      # channelId -> updateHandler
      self.updateHandlers = {}
      self.subscriptions = {}
      self.channel_info = {}

      self.thread = None
      self.msgCount = 0
      # channels
      self.book    = {}
      self.rawBook = {}
      self.trades  = {}
      self.tickers = {}
      self.candles = {}

   def _connect(self):
      print ('Connecting to bitfinex websocket API ...')
      # websocket.enableTrace(True)
      self.ws = websocket.WebSocketApp(WEBSOCKET_URI,
                                       on_message=self.on_message,
                                       on_error=self.on_error,
                                       on_close=self.on_close)
      self.ws.on_open = self.on_open
      self.ws.run_forever()

   def connect(self):
      def run():
         self._connect()

      self.thread = Thread(target=run)
      self.thread.start()
      time.sleep(1)  # halt the calling thread until the connection is up

   def disconnect(self):
      if self.ws is not None:
         self.ws.close()
      self.thread.join()

   def on_open(self, ws):
      print ('Websocket connection open.')

   def on_close(self, ws):
      print ('Connection to bitfinex closed.')

   def on_error(self, ws, error):
      print (error)

   # Main message handler
   # ---------------------------------------------------------------------------------

   def on_message(self, ws, message):
      # Websocket client returns message as string. Convert it to json
      msg = json.loads(message)

      # Dictionary of callbacks based on the received event type
      event_callback = {
         'info'        : (self.info, [msg]),
         'pong'        : (self.printMsg, ['Pong received.']),
         'subscribed'  : (self.channelSubcribed, [msg]),
         'unsubscribed': (self.printMsg, ['Unsubscribed from channel.']),
         'error'       : (self.errorMsg, [msg]),
         'hb'          : (self.heartbeatMsg, [msg])
      }
      # get the message handler and call it
      if isinstance(msg, dict):
         msgHadler, args = event_callback.get(msg['event'], (None, None))
         msgHadler(*args)
      else:
         # if the message is a channel update get the handler from subscriptions dictionary
         msgHadler = self.updateHandlers.get(msg[0])
         msgHadler(msg)

   def printMsg(self, msg):
      print (msg)

   def errorMsg(self, msg):
      print ('Error ' + msg['code'] + ' : ' + msg['msg'])

   def heartbeatMsg(self, msg):
      pass

   def info(self, msg):
      if msg['version']:
         print ('version ' + str(msg['version']))
      elif msg['code']:
         print ('Received code' + str(msg['code']) + ' : ' + msg['msg'])
      return

   # Subscriptions
   # ---------------------------------------------------------------------------------

   def subscribe(self, channel, parameters={}):
      subscribeHandler = self.channels[channel]
      subscribeHandler(parameters)

   def unsubscribe(self):
      pass

   def channelSubcribed(self, msg):
      if msg['channel'] == 'book':
         if msg['prec'] == 'R0':
            self.RawBookSubscribed(msg)
         else:
            self.BookSubscribed(msg)
      elif msg['channel'] == 'trades':
         self.TradesSubscribed(msg)
      elif msg['channel'] == 'ticker':
         self.TickerSubscribed(msg)
      elif msg['channel'] == 'candles':
         self.CandlesSubscribed(msg)
      else:
         print ('No channel handler for channel - ' + msg['channel'])
         # channel_handlers = {
         #    'trades': (self.TradesSubscribed),
         #    'book'  : (self.RawBookSubscribed) if msg['prec'] == 'R0' else (self.BookSubscribed)
         # }
         # get the channel callback and call it
         # channelHandler = channel_handlers[msg['channel']]
         # channelHandler(msg)

   # ===============================================================================
   # Channels
   # ===============================================================================

   # Order Book
   # ---------------------------------------------------------------------------------

      """
      // request
      { 
        event   : 'subscribe',
        channel : 'book',
        symbol  : SYMBOL,
        prec    : PRECISION,
        freq    : FREQUENCY,
        len     : LENGTH 
      }
      
      // response
      { 
        event   : 'subscribed',
        channel : 'book',
        chanId  : CHANNEL_ID,
        symbol  : SYMBOL,
        prec    : PRECISION,
        freq    : FREQUENCY,
        len     : LENGTH 
      }
      
      Fields       Type    Description
      PRECISION    string  Level of price aggregation (P0, P1, P2, P3). The default is P0
      FREQUENCY    string  Frequency of updates (F0, F1, F2, F3).
                           F0=realtime / F1=2sec / F2=5sec / F3=10sec
      LENGTH       string  Number of price points ("25", "100") [default="25"]
      
      PRICE        float   Price level
      RATE         float   Rate level
      PERIOD       float   Period level
      COUNT        int     Number of orders at that price level
      AMOUNT       float   Total amount available at that price level.
                           Trading: if AMOUNT > 0 then bid else ask; Funding: if AMOUNT < 0 then bid else ask;
      
      // Snapshot on trading pairs (ex. tBTCUSD)
      [
        CHANNEL_ID,
        [ [ PRICE, COUNT, AMOUNT ], ... ]
      ]
      
      // Update on trading pairs (ex. tBTCUSD)
      [
        CHANNEL_ID,
        [ PRICE, COUNT, AMOUNT ]
      ]
      
      Algorithm to create and keep a book instance updated
      
      1. subscribe to channel
      2. receive the book snapshot and create your in-memory book structure
      3. when count > 0 then you have to add or update the price level
           3.1 if amount > 0 then add/update bids
           3.2 if amount < 0 then add/update asks
      4. when count = 0 then you have to delete the price level.
           4.1 if amount = 1 then remove from bids
           4.2 if amount = -1 then remove from asks
      """


   def subscribeToBook(self, params={}):
      print ('Subscribing to order book ...')
      pair = params.get('pair', "BTCUSD")
      prec = params.get('prec', "P0")
      freq = params.get('freq', "F0")
      len  = params.get('len', "25")
      self.ws.send(json.dumps({"event": "subscribe", "channel": "book", "symbol": 't'+pair, "prec": prec, "freq": freq, "len": len}))

   def BookSubscribed(self, msg):
      # register snapshot handler for the channel based on bitfinex channel ID
      self.updateHandlers[msg['chanId']] = self.BookUpdate

      print ( 'Subcribed to Book channel' )
      print ( '-' * 40 )
      print ( 'ID        : ' + str(msg['chanId']) )
      print ( 'Pair      : ' + str(msg['symbol']) )
      print ( 'Precision : ' + str(msg['prec']) )
      print ( 'Frequency : ' + str(msg['freq']) )
      print ( 'Lenght    : ' + str(msg['len']) )
      print

   def BookUpdate(self, msg):
      if not self.subscriptions.get(msg[0], None):
         # snapshot message
         orders = msg[1]
         self.subscriptions[msg[0]] = orders
         for order in orders:
            print ( "{:>12} {:>12}".format(order[0], order[2]) )
         print
      elif 'hb' in msg:
         return
      else:
         print ( "BookUpdate     {:>12} {:>12}".format(msg[1][0], msg[1][2]) )


   # Raw Order Book
   # ---------------------------------------------------------------------------------

      """
      // request
      {
        event   : "subscribe",
        channel : "book",
        prec    : "R0",
        symbol  : SYMBOL,
        len     : LENGTH
      }
      
      // response
      {
        event   : "subscribed",
        channel : "book",
        chanId  : CHANNEL_ID,
        symbol  : SYMBOL,
        prec    : PRECISION,
        len     : LENGTH
      }
      
      Fields    Type   Description
      ORDER_ID  int    Order id
      PRICE     float  Order price; if 0 you have to rr from your book
      AMOUNT    float  Total amount available at that price level.
                       Trading: if AMOUNT > 0 then bid else ask; Funding: if AMOUNT < 0 then bid else ask;
      
      // Snapshot on trading pairs (ex. tBTCUSD)
      [
        CHANNEL_ID,
        [ [ ORDER_ID, PRICE, AMOUNT ], ... ]
      ]
      
      // on trading pairs (ex. tBTCUSD)
      [ 
        CHANNEL_ID,
        [ ORDER_ID, PRICE, AMOUNT ] 
      ]
      
      
      Algorithm to create and keep a book instance updated
      
      1. subscribe to channel with R0 precision
      2. receive the raw book snapshot and create your in-memory book structure
      3. when AMOUNT > 0 then you have to add or update the order
      4. when AMOUNT = 0 then you have to delete the order
      """

   def subscribeToRawBook(self, params={}):
      print ('Subscribing to raw order book ...')
      pair = params.get('pair', "BTCUSD")
      len  = params.get('len', "25")
      self.ws.send(json.dumps({"event": "subscribe", "channel": "book", "pair": 't'+pair, "prec": "R0", "len": len}))

   def RawBookSubscribed(self, msg):
      # register update handler for the channel based on bitfinex channel ID
      self.updateHandlers[msg['chanId']] = self.RawBookUpdate

      print ( 'Subcribed to Raw Order Book channel' )
      print ( '-' * 40 )
      print ( 'ID        : ' + str(msg['chanId']) )
      print ( 'Pair      : ' + str(msg['symbol']) )
      print ( 'Precision : ' + str(msg['prec']) )
      print ( 'Lenght    : ' + str(msg['len']) )
      print

   def RawBookUpdate(self, msg):
      if not self.subscriptions.get(msg[0], None):
         # snapshot message
         orders = msg[1]
         self.subscriptions[msg[0]] = orders
         for order in orders:
            print ( "{:>12} {:>12}".format(order[1], order[2]) )
         print
      elif 'hb' in msg:
         return
      else:
         # update
         print ( "RawBookUpdate  {:>12} {:>12}".format(msg[1][1], msg[1][2]) )


   # Trades
   # ---------------------------------------------------------------------------------

      """
      // request
      { 
        event   : "subscribe", 
        channel : "trades", 
        symbol  : SYMBOL 
      }
      
      // response Trading
      {
        event   : "subscribed",
        channel : "trades",
        chanId  : CHANNEL_ID,
        symbol  : "tBTCUSD"
        pair    : "BTCUSD"
      }
      
      // response Funding
      {
        event   : "subscribed",
        channel : "trades",
        chanId  : CHANNEL_ID,
        symbol  : "fUSD"
      }
      
      Fields	Type	  Description
      MTS      int     millisecond time stamp
      AMOUNT   float   How much was bought (positive) or sold (negative).
      PRICE    float   Price at which the trade was executed
      RATE     float   Rate at which funding transaction occurred
      PERIOD   int     Amount of time the funding transaction was for
      
      // Snapshot on trading pairs (ex. tBTCUSD)
      [
        CHANNEL_ID,
        [ [ ID, MTS, AMOUNT, PRICE ], ... ]
      ]
      
      // Snapshot on funding currencies (ex. fUSD)
      [
        CHANNEL_ID,
        [ [ ID, MTS, AMOUNT, RATE, PERIOD ], ... ]
      ]
         
      // Update on trading pairs (ex. tBTCUSD)
      [
        CHANNEL_ID,
        <"te", "tu">,
        [ ID, MTS, AMOUNT, PRICE ]
      ]
      
      // Update on funding currencies (ex. fUSD)
      [
        CHANNEL_ID,
        <"fte", "ftu">,
        [ ID, MTS, AMOUNT, RATE, PERIOD ]
      ]
      
      NOTE: funding ticker not implemented as I do not see the need for it at the moment.
      """

   def subscribeToTrades(self, params={}):
      print ( 'Subscribing to trades ...' )
      pair = params.get('pair', "BTCUSD")
      self.ws.send(json.dumps({"event": "subscribe", "channel": "trades", "symbol": 't'+pair}))


   def TradesSubscribed(self, msg):
      # register update handler for the channel based on bitfinex channel ID
      self.updateHandlers[msg['chanId']] = self.TradesUpdate

      print ( 'Subcribed to Trades channel' )
      print ( '-' * 40 )
      print ( 'ID        : ' + str(msg['chanId']) )
      print ( 'Pair      : ' + str(msg['pair']) )
      print


   def TradesUpdate(self, msg):
      if not self.subscriptions.get(msg[0], None):
         # snapshot message
         trades = msg[1]
         self.subscriptions[msg[0]] = trades
         for trade in trades:
            print ( "{:>12} {:>12} {:>12}".format(trade[1], trade[2], trade[3]) )
         print
      elif 'hb' in msg:
         pass
      else:
         # update
         print ( "TradesUpdate  {:>12} {:>12} {:>12}".format(*msg[2][1:] ) )



   # Ticker
   # ---------------------------------------------------------------------------------
            
      """
      // request
      {
         event   : "subscribe",
         channel : "ticker",
         symbol  : SYMBOL
      }
      
      // response - trading
      {
         event   : "subscribed",
         channel : "ticker",
         chanId  : CHANNEL_ID,
         pair    : "BTCUSD"
      }
      
      // response - funding
      {
         event   : "subscribed",
         channel : "fticker",
         chanId  : CHANNEL_ID,
         symbol  : "USD"
      }
      
      // Trading pairs
      [
        CHANNEL_ID,
        [ BID, BID_SIZE, ASK, ASK_SIZE, DAILY_CHANGE, DAILY_CHANGE_PERC, LAST_PRICE, VOLUME, HIGH, LOW   ]
      ]
      
      // Funding pairs
      [
        CHANNEL_ID,
        [ FRR, BID, BID_PERIOD, BID_SIZE, ASK, ASK_PERIOD, ASK_SIZE, DAILY_CHANGE, DAILY_CHANGE_PERC, LAST_PRICE, VOLUME, HIGH, LOW ]
      ]
      
      // Trading pairs
      [
        CHANNEL_ID,
        [ BID, BID_SIZE, ASK, ASK_SIZE, DAILY_CHANGE, DAILY_CHANGE_PERC, LAST_PRICE, VOLUME, HIGH, LOW ]
      ]
      
      // Funding pairs
      [
        CHANNEL_ID,
        [ FRR, BID, BID_PERIOD, BID_SIZE, ASK, ASK_PERIOD, ASK_SIZE, DAILY_CHANGE, DAILY_CHANGE_PERC, LAST_PRICE, VOLUME, HIGH, LOW ]
      ]
      
      NOTE: funding ticker not implemented as I do not see the need for it at the moment.
   """

   def subscribeToTicker(self, params={}):
      print ( 'Subscribing to ticker ...' )
      pair = params.get('pair', "BTCUSD")
      self.ws.send(json.dumps({"event": "subscribe", "channel": "ticker", "symbol": 't'+pair}))


   def TickerSubscribed(self, msg):
      # register update handler for the channel based on bitfinex channel ID
      self.updateHandlers[msg['chanId']] = self.TickerUpdate
      self.tickers[msg['pair']] = []

      print ( 'Subcribed to Ticker channel' )
      print ( '-' * 40 )
      print ( 'ID        : ' + str(msg['chanId']) )
      print ( 'Pair      : ' + str(msg['pair']) )
      print


   def TickerUpdate(self, msg):
      chanId = msg[0]
      fmt = "{:^14}" * (len(msg[1]) - 1)
      if not self.subscriptions.get(msg[0], None):
         # snapshot message
         self.subscriptions[chanId] = msg
         self.tickers[chanId] = []
         print( fmt.format('BID', 'BID_SIZE', 'ASK', 'ASK_SIZE', 'DAY_CHANGE', 'DAY_CH_PERC', 'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW') )
      elif 'hb' in msg:
         return
      self.tickers[chanId].append([float(x) for x in msg[1]])
      print (fmt.format(*msg[1]))


   def GetTickerHistory(self, chanId):
      return self.tickers[chanId]


   def GetTicker(self, chanId):
      return self.tickers[chanId][-1]


   # Candles
   # ---------------------------------------------------------------------------------

      """
      // request
      {
         event   : "subscribe",
         channel : "candles",
         key     : "trade:1m:tBTCUSD"
      }
      
      // response
      {
        event   : "subscribed",
        channel : "candles",
        chanId" : CHANNEL_ID,
        key     : "trade:1m:tBTCUSD"
      }
      
      Fields   Type     Description
      MTS      int      millisecond time stamp
      OPEN     float    First execution during the time frame
      CLOSE    float    Last execution during the time frame
      HIGH     integer  Highest execution during the time frame
      LOW      float    Lowest execution during the timeframe
      VOLUME   float    Quantity of symbol traded within the timeframe
      
      Time frames
      1m  : one minute
      5m  : five minutes
      15m : 15 minutes
      30m : 30 minutes
      1h  : one hour
      3h  : 3 hours
      6h  : 6 hours
      12h : 12 hours
      1D  : one day
      7D  : one week
      14D : two weeks
      1M  : one month
      
      // Snapshot
      [
        CHANNEL_ID,
        [ [ MTS, OPEN, CLOSE, HIGH, LOW, VOLUME ], ... ]
      ]
      
      [
        CHANNEL_ID,
        [ MTS, OPEN, CLOSE, HIGH, LOW, VOLUME ] ]
      """


   def subscribeToCandles(self, params={}):
      print ( 'Subscribing to candels channel ...' )
      pair  = params.get('pair', "BTCUSD")
      scale = params.get('scale', "15m")
      self.ws.send(json.dumps({"event": "subscribe", "channel": "candles", "key": 'trade:' + scale + ':t'+pair}))


   def CandlesSubscribed(self, msg):
      # register update handler for the channel based on bitfinex channel ID
      self.updateHandlers[msg['chanId']] = self.CandlesUpdate

      print ( 'Subcribed to Candles channel' )
      print ( '-' * 40 )
      print ( 'ID        : ' + str(msg['chanId']) )
      print ( 'Key       : ' + str(msg['key']) )
      print


   def CandlesUpdate(self, msg):
      header = ['MTS', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']
      chanId = msg[0]
      fmt = "{:^14}" * len(header)
      if not self.subscriptions.get(msg[0], None):
         # snapshot message
         self.subscriptions[chanId] = msg[1]
         print( fmt.format(*header) )
         candles = msg[1]
         for candle in candles:
            print( fmt.format(*candle) )
      elif 'hb' in msg:
         return
      else:
         # update
         print (fmt.format(*msg[1]))
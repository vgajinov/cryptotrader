import os, sys
import time
from datetime import datetime
import websocket
import json
from threading import Thread


# Each message sent and received via the Bitfinex's websocket channel is encoded in JSON format
#
# In case of error, you receive a message containing the proper error code (code JSON field).
# Generic Error Codes:
#   10000 : Unknown event
#   10001 : Unknown pair
#
# Info Messages:
#
# Info messages are sent from the websocket server to notify the state of your connection.
# Right after connecting you receive an info message that contains the actual version of the websocket stream.
#   {
#     "event":"info",
#     "version": 1
#   }
#
# Websocket server sends other info messages to inform regarding relevant events.
#   {
#     "event":"info",
#     "code": "<CODE>",
#     "msg": "<MSG>"
#   }
#
# Info Codes
# 20051 : Stop/Restart Websocket Server (please try to reconnect)
# 20060 : Refreshing data from the Trading Engine. Please pause any activity and resume
#         after receiving the info message 20061 (it should take 10 seconds at most).
# 20061 : Done Refreshing data from the Trading Engine. You can resume normal activity.
#         It is advised to unsubscribe/subscribe again all channels.




PROTOCOL = "https"
HOST = "api.bitfinex.com"
VERSION = "v1"

# SSL connection
WEBSOCKET_URI = "wss://api.bitfinex.com/ws"


# ==========================================================================================
#   Client
# ==========================================================================================

class Client:

    def __init__(self):
        self.ws = None
        self.channels = {
           'book'     : self.subscribeToBook,
           'raw_book' : self.subscribeToRawBook,
           'trades'   : self.subscribeToTrades,
           'ticker'   : self.subscribeToTicker
        }
        # channelId -> updateHandler
        self.updateHandlers = {}
        self.subscriptions = {}
        self.channel_info = {}

        self.thread = None
        self.msgCount = 0
        # channels
        self.book = {}
        self.rawBook = {}
        self.trades = {}
        self.tickers = {}


    def _connect(self):
        print 'Connecting to bitfinex websocket API ...'
        #websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp( WEBSOCKET_URI,
                                          on_message = self.on_message,
                                          on_error   = self.on_error,
                                          on_close   = self.on_close )
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def connect(self):
       def run():
          #pass
          self._connect()
       self.thread = Thread(target=run)
       self.thread.start()
       time.sleep(1) # halt the calling thread until the connection is up

    def disconnect(self):
        if self.ws is not None:
           self.ws.close()
        self.thread.join()

    def on_open(self, ws):
        print 'Websocket connection open.'

    def on_close(self, ws):
        print('Connection to bitfinex closed.')

    def on_error(self, ws, error):
        print(error)


    # Main message handler
    # ---------------------------------------------------------------------------------

    def on_message(self, ws, message):
        # Websocket client returns message as string. Convert it to json
        msg = json.loads(message)

        # Dictionary of callbacks based on the received event type
        event_callback = {
            'info'         : (self.info, [msg]),
            'pong'         : (self.printMsg, ['Pong received.']),
            'subscribed'   : (self.channelSubcribed, [msg]),
            'unsubscribed' : (self.printMsg, ['Unsubscribed from channel.']),
            'error'        : (self.errorMsg, [msg]),
            'hb'           : (self.heartbeatMsg, [msg])
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
        print msg

    def errorMsg(self, msg):
        print 'Error ' + msg['code'] + ' : ' + msg['msg']

    def heartbeatMsg(self, msg):
        pass

    def info(self, msg):
        if msg['version']:
            print 'version ' + str(msg['version'])
        elif msg['code']:
            print 'Received code' + str(msg['code']) + ' : ' + msg['msg']
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
        else:
           print 'No channel handler for channel - ' + msg['channel']
        #channel_handlers = {
        #    'trades': (self.TradesSubscribed),
        #    'book'  : (self.RawBookSubscribed) if msg['prec'] == 'R0' else (self.BookSubscribed)
        #}
        # get the channel callback and call it
        #channelHandler = channel_handlers[msg['channel']]
        #channelHandler(msg)


    # ===============================================================================
    # Channels
    # ===============================================================================

    # Order Book
    # ---------------------------------------------------------------------------------

    def subscribeToBook(self, params={}):
        """
        request :
        {
           "event":"subscribe",
           "channel":"book",
           "pair":"<PAIR>",
           "prec":"<PRECISION>",
           "freq":"<FREQUENCY>"
        }
        """
        print 'Subscribing to order book ...'
        pair = params.get('pair', "BTCUSD")
        prec = params.get('prec', "P0")
        freq = params.get('freq', "F0")
        self.ws.send(json.dumps({"event":"subscribe","channel":"book","pair":pair, "prec":prec, "freq":freq}))


    def BookSubscribed(self, msg):
        """ response
        {
            "event"  : "subscribed",
            "channel": "book",
            "chanId" : "<CHANNEL_ID>",
            "pair"   : "<PAIR>",
            "prec"   : "<PRECISION>",
            "freq"   : "<FREQUENCY>",
            "len"    : "<LENGTH>"
        }
        
        Fields	    Type	    Description
        PRECISION	 string	 Level of price aggregation (P0, P1, P2, P3).
                            The default is P0.
        FREQUENCY	 string	 Frequency of updates (F0, F1, F2, F3).
                            F0=realtime / F1=2sec / F2=5sec / F3=10sec.
        PRICE	    float	 Price level.
        COUNT   	 int      Number of orders at that price level.
        AMOUNT 	 float	 Total amount available at that price level.
                            Positive values mean bid, negative values mean ask.
        LENGTH	    string	 Number of price points ("25", "100") [default="25"]
        """
        # register snapshot handler for the channel based on bitfinex channel ID
        self.updateHandlers[msg['chanId']] = self.BookUpdate

        self.channel_info

        print 'Subcribed to Book channel'
        print '-'*40
        print 'ID        : ' + str(msg['chanId'])
        print 'Pair      : ' + str(msg['pair'])
        print 'Precision : ' + str(msg['prec'])
        print 'Frequency : ' + str(msg['freq'])
        print 'Lenght    : ' + str(msg['len'])
        print


    def BookUpdate(self, msg):
        """
        The first message is a snapshot and following messages are single updates
        snapshot:
        [ "<CHANNEL_ID>", [  [ "<PRICE>", "<COUNT>", "<AMOUNT>" ],
                             [ "<PRICE>", "<COUNT>", "<AMOUNT>" ], ... ]
        ]
        updates:
        [
           "<CHANNEL_ID>",
           "<PRICE>",
           "<COUNT>",
           "<AMOUNT>"
        ]
        """
        if not self.subscriptions.get(msg[0], None):
            # snapshot message
            orders = msg[1]
            self.subscriptions[msg[0]] = orders
            for order in orders:
               print "{:>12} {:>12}".format(order[0], order[2])
            print
        elif 'hb' in msg:
            pass
        else:
            print "BookUpdate     {:>12} {:>12}".format(msg[1], msg[3])


    # Raw Order Book
    # ---------------------------------------------------------------------------------

    def subscribeToRawBook(self, params={}):
        """
        request :
        {
           "event"   : "subscribe",
           "channel" : "book",
           "pair"    : "<PAIR>",
           "prec"    : "R0",
        }
        """
        print 'Subscribing to raw order book ...'
        pair = params.get('pair', "BTCUSD")
        self.ws.send(json.dumps({"event":"subscribe","channel":"book","pair":pair, "prec":"R0"}))


    def RawBookSubscribed(self, msg):
        """ response
        {
           "event"   : "subscribed",
           "channel" : "book",
           "chanId"  : "<CHANNEL_ID>",
           "pair"    : "<PAIR>",
           "prec"    : "R0",
           "len"     : "<LENGTH>"
        }

        Fields	    Type	    Description
        PRECISION	 string	 Aggregation level (R0).
        ORD_ID     int    	 Order id.
        PRICE	    float	 Price level.
        COUNT   	 int      Number of orders at that price level.
        AMOUNT 	 float	 Total amount available at that price level.
                            Positive values mean bid, negative values mean ask.
        LENGTH	    string	 Number of price points ("25", "100") [default="25"]
        """
        # register update handler for the channel based on bitfinex channel ID
        self.updateHandlers[msg['chanId']] = self.RawBookUpdate

        print 'Subcribed to Raw Order Book channel'
        print '-' * 40
        print 'ID        : ' + str(msg['chanId'])
        print 'Pair      : ' + str(msg['pair'])
        print 'Precision : ' + str(msg['prec'])
        print 'Lenght    : ' + str(msg['len'])
        print


    def RawBookUpdate(self, msg):
        """
        The first message is a snapshot and following messages are single updates
        snapshot:
        [ "<CHANNEL_ID>", [  [ "<ORDER_ID>", "<PRICE>", "<AMOUNT>" ],
                             [ "<ORDER_ID>", "<PRICE>", "<AMOUNT>" ], ... ]
        ]
        updates:
        [
           "<CHANNEL_ID>",
           "<ORD_ID>",
           "<ORD_PRICE>",
           "<AMOUNT>"
        ]
        """
        if not self.subscriptions.get(msg[0], None):
            # snapshot message
            orders = msg[1]
            self.subscriptions[msg[0]] = orders
            for order in orders:
                print "{:>12} {:>12}".format(order[1], order[2])
            print
        elif 'hb' in msg:
            pass
        else:
            # update
            print "RawBookUpdate  {:>12} {:>12}".format(msg[2], msg[3])


    # Trades
    # ---------------------------------------------------------------------------------

    def subscribeToTrades(self, params={}):
        """
        request :
        {
           "event": "subscribe",
           "channel": "trades",
           "pair": "BTCUSD"
        }
        """
        print 'Subscribing to trades ...'
        pair = params.get('pair', "BTCUSD")
        self.ws.send(json.dumps({"event":"subscribe","channel":"trades","pair":pair}))


    def TradesSubscribed(self, msg):
        """
        response
        {
            "event": "subscribed",
            "channel": "trades",
            "chanId": "<CHANNEL_ID>",
            "pair":"<PAIR>"
        }

        Fields	    Type	     Description
        SEQ	       string	Trade sequence id
        ID	       int	   Trade database id
        TIMESTAMP	 int	   Unix timestamp of the trade.
        PRICE	    float	Price at which the trade was executed
        AMOUNT	    float	How much was bought (positive) or sold (negative).
        """
        # register update handler for the channel based on bitfinex channel ID
        self.updateHandlers[msg['chanId']] = self.TradesUpdate

        print 'Subcribed to Trades channel'
        print '-' * 40
        print 'ID        : ' + str(msg['chanId'])
        print 'Pair      : ' + str(msg['pair'])
        print


    def TradesUpdate(self, msg):
        """
        The first message is a snapshot and following messages are single updates
        snapshot:
        [ "<CHANNEL_ID>", [  [ "<SEQ> OR <ID>", "<TIMESTAMP>", "<PRICE>", "<AMOUNT>" ],
                             [ "<SEQ> OR <ID>", "<TIMESTAMP>", "<PRICE>", "<AMOUNT>" ], ... ]
        ]
        updates:
        SEQ is different from canonical ID.
        Websocket server uses SEQ strings to push trades with low latency.
        After a 'te' message you receive shortly a 'tu' message that contains the real trade 'ID'.
        [
           "<CHANNEL_ID>",
           "te",
           "<SEQ>",
           "<TIMESTAMP>",
           "<PRICE>",
           "<AMOUNT>"
        ]

        [
           "<CHANNEL_ID>",
           "tu",
           "<SEQ>",
           "<ID>",
           "<TIMESTAMP>",
           "<PRICE>",
           "<AMOUNT>"
        ]
        """
        if not self.subscriptions.get(msg[0], None):
            # snapshot message
            trades = msg[1]
            self.subscriptions[msg[0]] = trades
            for trade in trades:
                print "{:>12} {:>12} {:>12}".format(trade[1], trade[2], trade[3])
            print
        elif 'hb' in msg:
            pass
        else:
            # update
            if len(msg) == 6:
               # 'te' message
               print "TradesUpdate  {:>12} {:>12} {:>12}".format(msg[3], msg[4], msg[5])
            else:
               # 'tu' message
               print "TradesUpdate  {:>12} {:>12} {:>12}".format(msg[4], msg[5], msg[6])


    # Ticker
    # ---------------------------------------------------------------------------------

    def subscribeToTicker(self, params={}):
        """
        request :
        {
            "event":"subscribe",
            "channel":"ticker",
            "pair":"BTCUSD"
        }
        """
        print 'Subscribing to ticker ...'
        pair = params.get('pair', "BTCUSD")
        self.ws.send(json.dumps({"event":"subscribe","channel":"ticker","pair":pair}))


    def TickerSubscribed(self, msg):
        """
        response
        {
            "event":"subscribed",
            "channel":"ticker",
            "chanId":"<CHANNEL_ID>",
            "pair":"BTCUSD"
        }

        Fields	            Type	       Description
        BID	               float	   Price of last highest bid
        BID_SIZE	         float	   Size of the last highest bid
        ASK	               float	   Price of last lowest ask
        ASK_SIZE	         float	   Size of the last lowest ask
        DAILY_CHANGE       float	   Amount that the last price has changed since yesterday
        DAILY_CHANGE_PERC	float	   Amount that the price has changed expressed in percentage terms
        LAST_PRICE	      float	   Price of the last trade.
        VOLUME	            float	   Daily volume
        HIGH	            float	   Daily high
        LOW	               float	   Daily low
        """
        # register update handler for the channel based on bitfinex channel ID
        self.updateHandlers[msg['chanId']] = self.TickerUpdate
        self.tickers[msg['pair']] = []

        print 'Subcribed to Ticker channel'
        print '-' * 40
        print 'ID        : ' + str(msg['chanId'])
        print 'Pair      : ' + str(msg['pair'])
        print


    def TickerUpdate(self, msg):
        """
        snapshot & updates
        [
           "<CHANNEL_ID>",
           "<BID>",
           "<BID_SIZE>",
           "<ASK>",
           "<ASK_SIZE>",
           "<DAILY_CHANGE>",
           "<DAILY_CHANGE_PERC>",
           "<LAST_PRICE>",
           "<VOLUME>",
           "<HIGH>",
           "<LOW>"
        ]
        """
        chanId = msg[0]
        if not self.subscriptions.get(msg[0], None):
            self.subscriptions[chanId] = msg
            self.tickers[chanId].apend([float(x) for x in msg[1:]])
            print '{:>12} {:>12} {:>12} {:>12} {:>14} {:>12} {:>12} {:>12}'.format(
               'BID','BID_SIZE', 'ASK', 'ASK_SIZE', 'LAST_PRICE', 'VOLUME', 'HIGH', 'LOW')

        elif 'hb' in msg:
            pass
        else:
            self.tickers[chanId].apend([float(x) for x in msg[1:]])
            print '{:>12} {:>12} {:>12} {:>12} {:>14} {:>12} {:>12} {:>12}'.format(
               msg[1], msg[2], msg[3], msg[4], msg[7], msg[8], msg[9], msg[10])
            #fmt = "{:>12} "*(len(msg)-1)
            #print fmt.format(msg[1:])

    def GetTickerHistory(self, chanId):
       return self.tickers[chanId]

    def GetTicker(self, chanId):
       return self.tickers[chanId][-1]
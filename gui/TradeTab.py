from PyQt5 import QtCore, QtWidgets, QtGui
from .ControlBarWidget import ControlBarWidget
from .ChartWidget import ChartWidget
from .PlaceOrderWidget import PlaceOrderWidget
from .OrderBookWidget import OrderBookWidget
from .TradesWidget import TradesWidget
from .Separators import *
from .CustomEvents import *

from exchanges.exchangeWSFactory import ExchangeWSFactory
from exchanges.exchangeRESTFactory import ExchangeRESTFactory




class TradeTab(QtWidgets.QWidget):
   wsClient   = None
   restClient = None
   exchange   = None
   pair       = None
   interval   = None

   # channels
   tickerChannel  = None
   bookChannel    = None
   tradeChannel   = None
   candlesChannel = None


   def __init__(self):
      super(TradeTab, self).__init__()
      self.createLayout()


   def createLayout(self):
      # left layout
      self.ControlBarWidget = ControlBarWidget(self)
      self.ChartWidget = ChartWidget()
      self.TradesWidget = TradesWidget()
      self.leftLayout = QtWidgets.QVBoxLayout()
      self.leftLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
      self.leftLayout.addWidget(self.ControlBarWidget, stretch=1)
      self.leftLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                                    spacecolor='rgb(0,0,0)', stroke=1, width=3))
      self.leftLayout.addWidget(self.ChartWidget, stretch=20)
      self.leftLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
      self.leftLayout.addWidget(self.TradesWidget, stretch=8)
      self.leftLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))

      # right layout
      self.OrderBookWidget = OrderBookWidget()
      self.PlaceOrderWidget = PlaceOrderWidget()
      self.rightLayout = QtWidgets.QVBoxLayout()
      self.rightLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
      self.rightLayout.addWidget(self.OrderBookWidget, stretch=7)
      self.rightLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
      self.rightLayout.addWidget(self.PlaceOrderWidget, stretch=2)
      self.rightLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))

      # main layout
      self.mainLayout = QtWidgets.QHBoxLayout(self)
      self.mainLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
      self.mainLayout.addLayout(self.leftLayout, stretch=2)
      self.mainLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
      self.mainLayout.addLayout(self.rightLayout, stretch=1)
      self.mainLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
      self.mainLayout.setSpacing(0)
      self.mainLayout.setContentsMargins(0, 2, 0, 0)

      self.ControlBarWidget.setExchangeList(ExchangeWSFactory.get_exchanges())


   # ------------------------------------------------------------------------------------
   # ControlBar interaction
   # ------------------------------------------------------------------------------------

   def clearChannels(self):
      self.tickerChannel  = None
      self.bookChannel    = None
      self.tradeChannel   = None
      self.candlesChannel = None

   def exchangeChanged(self, exchangeName):
      if exchangeName == self.exchange:
         return
      self.exchange = exchangeName

      if self.wsClient is not None:
         self.wsClient.disconnect()
         self.wsClient = None

      self.wsClient = ExchangeWSFactory.create_client(exchangeName)
      self.restClient = ExchangeRESTFactory.create_client(exchangeName)
      self.wsClient.connect(self.infoUpdate)

      self.pair = None
      self.interval = None
      self.clearChannels()

      self.ControlBarWidget.setPairList(self.restClient.symbols())
      self.ControlBarWidget.setIntervalList(self.restClient.candle_intervals())


   def pairChanged(self, pair):
      if pair == self.pair:
         return

      if self.pair is not None:
         self.wsClient.unsubscribe(self.tickerChannel, self.updateTicker)
         self.wsClient.unsubscribe(self.bookChannel, self.updateOrderBook)
         self.wsClient.unsubscribe(self.tradesChannel, self.updateTrades)
         if self.candlesChannel is not None:
            self.wsClient.unsubscribe(self.candlesChannel, self.updateCandles)
         self.clearChannels()

      self.pair = pair
      self.tickerChannel = self.wsClient.subscribe_ticker(pair, self.updateTicker)
      self.bookChannel = self.wsClient.subscribe_order_book(pair, self.updateOrderBook)
      self.tradesChannel = self.wsClient.subscribe_trades(pair, self.updateTrades)
      if self.interval is not None:
         self.candlesChannel = self.wsClient.subscribe_candles(pair, self.interval, self.updateCandles)


   def intervalChanged(self, interval):
      if interval == self.interval:
         return
      self.interval = interval
      if self.candlesChannel is not None:
         self.wsClient.unsubscribe(self.candlesChannel, self.updateCandles)
      self.candlesChannel = self.wsClient.subscribe_candles(self.pair, interval, self.updateCandles)


   # ------------------------------------------------------------------------------------
   # Update methods
   # ------------------------------------------------------------------------------------

   def customEvent(self, event):
      #print('received event' + str(event.type()))
      if event.type() == OrderBookUpdateEvent.EVENT_TYPE:
         self.OrderBookWidget.setOrderBookGraphData(event.bids, event.asks)
         self.OrderBookWidget.setOrderBookNumericData(event.bids, event.asks)
      if event.type() == TradesUpdateEvent.EVENT_TYPE:
         # self.OrderBookWidget.setLastPrice(event.trades[0][2])
         self.OrderBookWidget.setOrderBookTradesData(event.trades)
      if event.type() == TickerUpdateEvent.EVENT_TYPE:
         lastPrice = event.ticker[6]
         self.OrderBookWidget.setLastPrice(lastPrice)
      if event.type() == CandlesUpdateEvent.EVENT_TYPE:
         self.ChartWidget.setData(event.candles)
         self.ChartWidget.updateChart()

   # update OrderBook
   def updateOrderBook(self, data):
      QtWidgets.QApplication.postEvent(self, OrderBookUpdateEvent(data['bids'], data['asks']))

   # update Trades
   def updateTrades(self, data):
      QtWidgets.QApplication.postEvent(self, TradesUpdateEvent(data))

   # update Ticker
   def updateTicker(self, data):
      QtWidgets.QApplication.postEvent(self, TickerUpdateEvent(data))

   # update Candles
   def updateCandles(self, data):
      QtWidgets.QApplication.postEvent(self, CandlesUpdateEvent(data))

   # handle info messages
   def infoUpdate(self, data):
      pass

from .ControlBarWidget import ControlBarWidget
from .CandleChartWidget import CandleChartWidget
from .PlaceOrderWidget import PlaceOrderWidget
from .TradesWidget import TradesWidget
from .OrderBookGraphWidget import OrderBookGraphWidget
from .OrderBookNumericWidget import OrderBookNumericWidget
from .UserTradingWidget import UserTradingWidget
from .Separators import *
from .CustomEvents import *

from exchanges.exchangeWSFactory import ExchangeWSFactory
from exchanges.exchangeRESTFactory import ExchangeRESTFactory




class TradingTab(QtWidgets.QWidget):
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
      super(TradingTab, self).__init__()
      self.createLayout()


   def createLayout(self):
      # left layout
      self.controlBarWidget = ControlBarWidget(self)
      self.chartWidget = CandleChartWidget()
      self.userTradingWidget = UserTradingWidget()
      self.leftLayout = QtWidgets.QVBoxLayout()
      self.leftLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
      self.leftLayout.addWidget(self.controlBarWidget, stretch=1)
      self.leftLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                                    spacecolor='rgb(0,0,0)', stroke=1, width=3))
      self.leftLayout.addWidget(self.chartWidget, stretch=20)
      self.leftLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
      self.leftLayout.addWidget(self.userTradingWidget, stretch=8)
      self.leftLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))

      # right layout
      self.orderBookAndTradesLayout = QtWidgets.QHBoxLayout()
      self.placeOrderWidget = PlaceOrderWidget()
      self.rightLayout = QtWidgets.QVBoxLayout()
      self.rightLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
      self.rightLayout.addLayout(self.orderBookAndTradesLayout, stretch=7)
      self.rightLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
      self.rightLayout.addWidget(self.placeOrderWidget, stretch=2)
      self.rightLayout.addWidget(LineSeparator(orientation='horizontal', stroke=5))
      self.initOrderBookAndTradesLayout()

      # main layout
      self.mainLayout = QtWidgets.QHBoxLayout(self)
      self.mainLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
      self.mainLayout.addLayout(self.leftLayout, stretch=2)
      self.mainLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
      self.mainLayout.addLayout(self.rightLayout, stretch=1)
      self.mainLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
      self.mainLayout.setSpacing(0)
      self.mainLayout.setContentsMargins(0, 2, 0, 0)

      self.controlBarWidget.setExchangeList(ExchangeWSFactory.get_exchanges())


   def initOrderBookAndTradesLayout(self):
      self.orderBookAndTradesLayout.setContentsMargins(0, 0, 0, 0)
      self.orderBookAndTradesLayout.setSpacing(0)

      self.orderBookGraphLayout = QtWidgets.QVBoxLayout()
      self.orderBookNumericLayout = QtWidgets.QVBoxLayout()
      self.orderBookTradesLayout = QtWidgets.QHBoxLayout()

      self.orderBookAndTradesLayout.addLayout(self.orderBookGraphLayout, stretch=4)
      self.orderBookAndTradesLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
      self.orderBookAndTradesLayout.addLayout(self.orderBookNumericLayout, stretch=5)
      self.orderBookAndTradesLayout.addWidget(LineSeparator(orientation='vertical', stroke=5))
      self.orderBookAndTradesLayout.addLayout(self.orderBookTradesLayout, stretch=5)

      # add OrderBookGraph
      self.orderBookGraph = OrderBookGraphWidget()
      self.orderBookGraphLayout.addWidget(self.orderBookGraph)
      self.orderBookGraphLayout.setContentsMargins(5, 5, 3, 0)

      # add numeric display of order book data
      self.numericOrderBookWidget = OrderBookNumericWidget()
      self.orderBookNumericLayout.addWidget(self.numericOrderBookWidget)
      self.orderBookNumericLayout.setContentsMargins(5, 5, 5, 2)

      # add trades display widget
      self.tradesTable = TradesWidget()
      self.orderBookTradesLayout.addWidget(self.tradesTable)
      self.orderBookTradesLayout.setContentsMargins(5, 5, 5, 2)


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

      self.controlBarWidget.setPairList(self.restClient.symbols())
      self.controlBarWidget.setIntervalList(self.restClient.candle_intervals())


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
         self.orderBookGraph.setData(event.bids, event.asks)
         self.numericOrderBookWidget.setData(event.bids, event.asks)
      if event.type() == TradesUpdateEvent.EVENT_TYPE:
         self.tradesTable.setData(event.trades)
      if event.type() == TickerUpdateEvent.EVENT_TYPE:
         lastPrice = event.ticker[6]
         self.numericOrderBookWidget.setLastPrice(lastPrice)
      if event.type() == CandlesUpdateEvent.EVENT_TYPE:
         self.chartWidget.setData(event.candles)
         self.chartWidget.updateChart()

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

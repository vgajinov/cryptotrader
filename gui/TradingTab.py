import os.path
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

from PyQt5 import QtGui




class TradingTab(QtWidgets.QWidget):
   keysDir    = None
   wsClient   = None
   restClient = None

   exchange   = None
   pair       = None
   interval   = None
   symbols    = None
   symbols_details  = None
   all_tickers      = None
   quote_currencies = None

   # public WS channels
   tickerChannel  = None
   bookChannel    = None
   tradeChannel   = None
   candlesChannel = None

   # user WS channels
   ordersChannel     = None
   userTradesChannel = None
   balancesChannel   = None



   def __init__(self):
      super(TradingTab, self).__init__()
      self._createLayout()


   def _createLayout(self):
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
      self._initOrderBookAndTradesLayout()

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


   def _initOrderBookAndTradesLayout(self):
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
      self.orderBookGraphLayout.setContentsMargins(0, 5, 3, 0)

      # add numeric display of order book data
      self.numericOrderBookWidget = OrderBookNumericWidget()
      self.orderBookNumericLayout.addWidget(self.numericOrderBookWidget)
      self.orderBookNumericLayout.setContentsMargins(5, 5, 5, 2)

      # add trades display widget
      self.tradesTable = TradesWidget()
      self.orderBookTradesLayout.addWidget(self.tradesTable)
      self.orderBookTradesLayout.setContentsMargins(5, 5, 5, 2)

   def reset(self):
      self.tradesTable.clear()
      self.orderBookGraph.reset()
      self.numericOrderBookWidget.clear()
      self.chartWidget.reset()


   # ------------------------------------------------------------------------------------
   # WS client interaction
   # ------------------------------------------------------------------------------------

   def _subscribe_ws_public_channels(self):
      self.tickerChannel = self.wsClient.subscribe_ticker(self.pair, self.updateTicker)
      self.bookChannel = self.wsClient.subscribe_order_book(self.pair, self.updateOrderBook)
      self.tradesChannel = self.wsClient.subscribe_trades(self.pair, self.updateTrades)
      if self.interval is not None:
         self.candlesChannel = self.wsClient.subscribe_candles(self.pair, self.interval, self.updateCandles)

   def _subscribe_ws_user_channels(self):
      self.ordersChannel = self.wsClient.subscribe_user_orders(self.updateOrders)
      self.userTradesChannel = self.wsClient.subscribe_user_trades(self.updateUserTrades)
      self.balancesChannel = self.wsClient.subscribe_balances(self.updateBalances)

   def _unsubscribe_ws_public_chanels(self):
      self.wsClient.unsubscribe(self.tickerChannel, self.updateTicker)
      self.wsClient.unsubscribe(self.bookChannel, self.updateOrderBook)
      self.wsClient.unsubscribe(self.tradesChannel, self.updateTrades)
      if self.candlesChannel is not None:
         self.wsClient.unsubscribe(self.candlesChannel, self.updateCandles)


   # ------------------------------------------------------------------------------------
   # ControlBar interaction
   # ------------------------------------------------------------------------------------

   def _clearChannels(self):
      self.tickerChannel  = None
      self.bookChannel    = None
      self.tradeChannel   = None
      self.candlesChannel = None

   def exchangeChanged(self, exchangeName):
      if exchangeName == self.exchange:
         return
      self.exchange = exchangeName

      self.reset()
      self.userTradingWidget.clear()

      self.setCursor(QtCore.Qt.WaitCursor)

      if self.wsClient is not None:
         self.wsClient.disconnect()
         self.wsClient = None
         self.restClient = None

      keyfile = None
      if self.keysDir is not None:
         keyFileName = os.path.join(self.keysDir, '{}.key'.format(self.exchange.lower()))
         keyfile = keyFileName if os.path.isfile(keyFileName) else None

      self.wsClient = ExchangeWSFactory.create_client(exchangeName)
      self.wsClient.connect(self.infoUpdate)
      if keyfile is not None:
         self.wsClient.authenticate(keyFile=keyfile)
         self._subscribe_ws_user_channels()

      self.pair = None
      self.interval = None
      self._clearChannels()

      self.restClient = ExchangeRESTFactory.create_client(exchangeName, key_file=keyfile)
      self.placeOrderWidget.setClient(self.restClient)
      self.userTradingWidget.setClient(self.restClient)

      self.quote_currencies = self.restClient.quote_currencies()
      self.symbols = self.restClient.symbols()
      self.symbols_details = self.restClient.symbols_details()
      self.all_tickers = self.restClient.all_tickers()

      self.controlBarWidget.setPairList(self.all_tickers, self.restClient.quote_currencies())
      self.controlBarWidget.setIntervalList(self.restClient.candle_intervals())
      self.userTradingWidget.setSymbolDetails(self.symbols_details)

      self.setCursor(QtCore.Qt.ArrowCursor)


   def pairChanged(self, pair):
      if pair == self.pair:
         return

      self.setCursor(QtCore.Qt.WaitCursor)

      if self.pair is not None:
         self.reset()
         self._unsubscribe_ws_public_chanels()
         self._clearChannels()

      self.pair = pair
      self._subscribe_ws_public_channels()

      for cur in self.quote_currencies:
         if pair.endswith(cur):
            base_currency = pair[:-len(cur)]
            quote_currency = cur
            break

      symbol_details = self.symbols_details[pair.upper()]
      self.tradesTable.setSymbolDetails(symbol_details)
      self.numericOrderBookWidget.setSymbolDetails(symbol_details)
      if self.restClient.authenticated:
         self.placeOrderWidget.setSymbolDetails(base_currency, quote_currency, symbol_details, self.all_tickers[pair])

      self.setCursor(QtCore.Qt.ArrowCursor)


   def intervalChanged(self, interval):
      if interval == self.interval:
         return
      self.interval = interval
      if self.candlesChannel is not None:
         self.wsClient.unsubscribe(self.candlesChannel, self.updateCandles)
      self.candlesChannel = self.wsClient.subscribe_candles(self.pair, interval, self.updateCandles)


   # ------------------------------------------------------------------------------------
   # MainWindow interactions
   # ------------------------------------------------------------------------------------

   def setKeysDirectory(self, dir):
      self.keysDir = dir
      if self.restClient is not None:
         keyFileName = os.path.join(self.keysDir, '{}.key'.format(self.exchange.lower()))
         keyfile = keyFileName if os.path.isfile(keyFileName) else None
         self.restClient = ExchangeRESTFactory.create_client(self.exchange, key_file=keyfile)
         self.wsClient.authenticate(keyFile=keyfile)
         self._subscribe_ws_user_channels()


   # This should be called on quitting the application
   def closeConnections(self):
      if self.wsClient is not None:
         self.wsClient.disconnect()


   # ------------------------------------------------------------------------------------
   # Update methods
   # ------------------------------------------------------------------------------------

   def customEvent(self, event):
      if event.type() == OrderBookUpdateEvent.EVENT_TYPE:
         self.orderBookGraph.setData(event.bids, event.asks)
         self.numericOrderBookWidget.setData(event.bids, event.asks)
      elif event.type() == TradesUpdateEvent.EVENT_TYPE:
         self.tradesTable.setData(event.trades)
      elif event.type() == TickerUpdateEvent.EVENT_TYPE:
         lastPrice = event.ticker[6]
         self.numericOrderBookWidget.setLastPrice(lastPrice)
         self.placeOrderWidget.setTicker(event.ticker)
      elif event.type() == CandlesUpdateEvent.EVENT_TYPE:
         self.chartWidget.setData(event.candles)
         self.chartWidget.updateChart()
      elif event.type() == OrdersUpdateEvent.EVENT_TYPE:
         self.userTradingWidget.updateOrders(event.orders)
      elif event.type() == UserTradesUpdateEvent.EVENT_TYPE:
         self.userTradingWidget.updateUserTrades(event.trades)
      elif event.type() == BalancesUpdateEvent.EVENT_TYPE:
         self.placeOrderWidget.setBalances(event.balances)

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

   # update Orders
   def updateOrders(self, data):
      QtWidgets.QApplication.postEvent(self, OrdersUpdateEvent(data))

   # update Orders
   def updateUserTrades(self, data):
      QtWidgets.QApplication.postEvent(self, UserTradesUpdateEvent(data))

   # update Orders
   def updateBalances(self, data):
      QtWidgets.QApplication.postEvent(self, BalancesUpdateEvent(data))

   # handle info messages
   def infoUpdate(self, data):
      pass





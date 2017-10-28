import os
import numpy as np
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot
import pyqtgraph as pg
from .ControlBarWidget import ControlBarWidget
from .ChartWidget import ChartWidget
from .PlaceOrderWidget import PlaceOrderWidget
from .OrderBookWidget import OrderBookWidget
from .TradesWidget import TradesWidget
from .Separators import *


# Exchange events
class OrderBookUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, bids, asks):
      super(OrderBookUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.bids = bids
      self.asks = asks

class TradesUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, trades):
      super(TradesUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.trades = trades

class TickerUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, ticker):
      super(TickerUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.ticker = ticker

class CandlesUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, candles):
      super(CandlesUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.candles = candles



class ATMainWindow(QtGui.QMainWindow):
   def __init__(self, width, height):
      super(ATMainWindow, self).__init__()

      # window properties
      self.setWindowTitle('AutoTrader')
      self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),'logo.png')))
      self.resize(width, height)

      # menu
      self.createMenu()

      # set central widget
      self.centralwidget = QtGui.QWidget(self)
      self.setCentralWidget(self.centralwidget)
      self.horizontalLayout = QtGui.QVBoxLayout(self.centralwidget)

      # add Tab widget
      self.tabWidget = QtGui.QTabWidget(self.centralwidget)
      self.tabCharts = QtGui.QWidget()
      self.tabPredictors = QtGui.QWidget()
      self.tabWidget.addTab(self.tabCharts, "Charts")
      self.tabWidget.addTab(self.tabPredictors, "Predictors")
      self.horizontalLayout.addWidget(self.tabWidget)

      # create tabs
      self.createChartTab()
      self.createPredictorTab()

      #import stylesheet file
      qss = open(os.path.join(os.path.dirname(__file__),'style.qss'), 'r')
      self.setStyleSheet(qss.read())
      qss.close()




   # createMenu
   # ---------------------------------------------------------
   def createMenu(self):
      quitAction = QtGui.QAction('Quit', self)
      quitAction.setShortcut('Ctrl+q')
      quitAction.setStatusTip('Quit AutoTrader')
      #quitAction.triggered.connect(self.close)

      self.menubar = QtGui.QMenuBar(self)
      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setTitle("File")
      self.setMenuBar(self.menubar)
      self.menubar.addAction(self.menuFile.menuAction())
      self.menuFile.addAction(quitAction)


   # ------------------------------------------------------------------------------------
   # Chart Tab
   # ------------------------------------------------------------------------------------

   def createChartTab(self):
      # main layout
      self.ctMainLayout = QtGui.QHBoxLayout(self.tabCharts)
      self.ctLeftLayout = QtGui.QVBoxLayout()
      self.ctRightLayout = QtGui.QVBoxLayout()
      self.ctMainLayout.addWidget(LineSeparator(orientation='vertical', color=COLOR_SEPARATOR, stroke=5))
      self.ctMainLayout.addLayout(self.ctLeftLayout, stretch=2)
      self.ctMainLayout.addWidget(LineSeparator(orientation='vertical', color=COLOR_SEPARATOR, stroke=5))
      self.ctMainLayout.addLayout(self.ctRightLayout, stretch=1)
      self.ctMainLayout.addWidget(LineSeparator(orientation='vertical', color=COLOR_SEPARATOR, stroke=5))
      self.ctMainLayout.setSpacing(0)
      #self.ctMainLayout.setMargin(1)
      self.ctMainLayout.setContentsMargins(0,2,0,0)

      # left layout
      self.ControlBarWidget = ControlBarWidget(self)
      self.ChartWidget = ChartWidget()
      self.TradesWidget = TradesWidget()
      self.ctLeftLayout.addWidget(LineSeparator(orientation='horizontal', color=COLOR_SEPARATOR, stroke=5))
      self.ctLeftLayout.addWidget(self.ControlBarWidget, stretch=1)
      self.ctLeftLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                                      spacecolor='rgb(0,0,0)', stroke=1, width=3))
      self.ctLeftLayout.addWidget(self.ChartWidget, stretch=20)
      self.ctLeftLayout.addWidget(LineSeparator(orientation='horizontal', color=COLOR_SEPARATOR, stroke=5))
      self.ctLeftLayout.addWidget(self.TradesWidget, stretch=8)
      self.ctLeftLayout.addWidget(LineSeparator(orientation='horizontal', color=COLOR_SEPARATOR, stroke=5))


      # right layout
      self.OrderBookWidget = OrderBookWidget()
      self.PlaceOrderWidget = PlaceOrderWidget()
      self.ctRightLayout.addWidget(LineSeparator(orientation='horizontal', color=COLOR_SEPARATOR, stroke=5))
      self.ctRightLayout.addWidget(self.OrderBookWidget, stretch=7)
      self.ctRightLayout.addWidget(LineSeparator(orientation='horizontal', color=COLOR_SEPARATOR, stroke=5))
      self.ctRightLayout.addWidget(self.PlaceOrderWidget, stretch=2)
      self.ctRightLayout.addWidget(LineSeparator(orientation='horizontal', color=COLOR_SEPARATOR, stroke=5))



   # ------------------------------------------------------------------------------------
   # Predictor Tab
   # ------------------------------------------------------------------------------------

   # createPredictorTab
   def createPredictorTab(self):
      pass




   # ------------------------------------------------------------------------------------
   # Update methods
   # ------------------------------------------------------------------------------------

   def customEvent(self, event):
      #print('received event' + str(event.type()))
      if event.type() == OrderBookUpdateEvent.EVENT_TYPE:
         self.OrderBookWidget.setOrderBookGraphData(event.bids, event.asks)
         self.OrderBookWidget.setOrderBookNumericData(event.bids, event.asks)
      if event.type() == TradesUpdateEvent.EVENT_TYPE:
         self.OrderBookWidget.setLastPrice(event.trades[0][2])
         self.OrderBookWidget.setOrderBookTradesData(event.trades)
      if event.type() == TickerUpdateEvent.EVENT_TYPE:
         lastPrice = event.ticker[6]
         self.OrderBookWidget.setLastPrice(lastPrice)
      if event.type() == CandlesUpdateEvent.EVENT_TYPE:
         pass

   # update OrderBook
   def updateOrderBook(self, bids, asks):
      QtGui.QApplication.postEvent(self, OrderBookUpdateEvent(bids,asks))

   # update Trades
   def updateTrades(self, trades):
      QtGui.QApplication.postEvent(self, TradesUpdateEvent(trades))

   # update Ticker
   def updateTicker(self, ticker):
      QtGui.QApplication.postEvent(self, TickerUpdateEvent(ticker))

   # update Candles
   def updateCandles(self, candles):
      QtGui.QApplication.postEvent(self, CandlesUpdateEvent(candles))
import sys
import numpy as np
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot
import pyqtgraph as pg
#from pyqtgraph import PlotWidget


# colors
COLOR_RED    = 'color: rgb(255, 0, 0)'
COLOR_GREEN  = 'color: rgb(0, 255, 0)'
COLOR_SEPARATOR = 'rgb(167, 174, 186, 50)'


class ATMainWindow(QtGui.QMainWindow):
   def __init__(self, width, height):
      super(ATMainWindow, self).__init__()

      # window properties
      self.setWindowTitle('AutoTrader')
      self.setWindowIcon(QtGui.QIcon('logo.png'))
      self.resize(width, height)

      self.createMenu()

      # set central widget
      self.centralwidget = QtGui.QWidget(self)
      self.setCentralWidget(self.centralwidget)
      self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)

      # add Tab widget
      self.tabWidget = QtGui.QTabWidget(self.centralwidget)
      self.tabCharts = QtGui.QWidget()
      self.tabPredictors = QtGui.QWidget()
      self.tabWidget.addTab(self.tabCharts, "Charts")
      self.tabWidget.addTab(self.tabPredictors, "Predictors")
      self.verticalLayout.addWidget(self.tabWidget)

      # create tabs
      self.createChartTab()
      self.createPredictorTab()



      qss = open('style.qss', 'r')
      self.setStyleSheet(qss.read())
      qss.close()

      #self.statusbar = QtGui.QStatusBar(MainWindow)
      #MainWindow.setStatusBar(self.statusbar)


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
      self.ctMainLayout.addWidget(self.createSeparator(orientation=1, color=COLOR_SEPARATOR, stroke=5))
      self.ctMainLayout.addLayout(self.ctLeftLayout, stretch=2)
      self.ctMainLayout.addWidget(self.createSeparator(orientation=1, color=COLOR_SEPARATOR, stroke=5))
      self.ctMainLayout.addLayout(self.ctRightLayout, stretch=1)
      self.ctMainLayout.setSpacing(0)

      # left layout
      self.ctControlsLayout = QtGui.QHBoxLayout()
      self.ctChartLayout = QtGui.QVBoxLayout()
      self.ctTradesLayout = QtGui.QHBoxLayout()
      self.ctLeftLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=5))
      self.ctLeftLayout.addLayout(self.ctControlsLayout, stretch=1)
      self.ctLeftLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=1))
      self.ctLeftLayout.addWidget(self.createSeparator(orientation=0, color='rgb(0,0,0)', stroke=3))
      self.ctLeftLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=1))
      self.ctLeftLayout.addLayout(self.ctChartLayout, stretch=10)
      self.ctLeftLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=5))
      self.ctLeftLayout.addLayout(self.ctTradesLayout, stretch=4)
      self.ctLeftLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=5))

      self.setControlsLayout(self.ctControlsLayout)
      self.addCandleChart(self.ctChartLayout)
      self.setTradesLayout(self.ctTradesLayout)


      # right layout
      #self.ctControlsLayout = QtGui.QHBoxLayout()
      self.ctOrderBookLayout = QtGui.QHBoxLayout()
      self.ctPlaceOrderLayout = QtGui.QHBoxLayout()
      #self.ctRightLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=5))
      #self.ctRightLayout.addLayout(self.ctControlsLayout, stretch=1)
      self.ctRightLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=5))
      self.ctRightLayout.addLayout(self.ctOrderBookLayout, stretch=5)
      self.ctRightLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=5))
      self.ctRightLayout.addLayout(self.ctPlaceOrderLayout, stretch=2)
      self.ctRightLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=5))

      self.setOrderBookLayout(self.ctOrderBookLayout)
      self.setPlaceOrderLayout(self.ctPlaceOrderLayout)



   # ------------------------------------------------------------------------------------
   # Controls
   # ------------------------------------------------------------------------------------
   def setControlsLayout(self, parentLayout):
      ctrlLeftLayout = QtGui.QHBoxLayout()
      ctrlRightLayout = QtGui.QHBoxLayout()

      self.ctrlExchange = QtGui.QComboBox()
      self.ctrlExchange.setObjectName('exchangeCombo')
      self.ctrlExchange.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
      self.ctrlExchangeView = QtGui.QListView()
      self.ctrlExchangeView.setObjectName('exchangeComboView')
      self.ctrlExchangeView.setSpacing(2)
      self.ctrlExchange.setView(self.ctrlExchangeView)


      self.ctrlPair = QtGui.QComboBox()
      self.ctrlPair.setObjectName('pairCombo')
      self.ctrlPair.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
      self.ctrlPairView = QtGui.QListView()
      self.ctrlPairView.setObjectName('pairComboView')
      self.ctrlPairView.setSpacing(2)
      self.ctrlPair.setView(self.ctrlPairView)

      self.ctrlTime = QtGui.QComboBox()
      self.ctrlTime.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
      self.ctrlTime.view().setSpacing(2)
      self.ctrlTime.setObjectName('timeCombo')

      # This centers the text but adds a scrollbar and the drop-down has to be enabled
      #self.ctrlTime.setEditable(True)
      #self.ctrlTime.lineEdit().setReadOnly(True)
      #self.ctrlTime.lineEdit().setAlignment(QtCore.Qt.AlignCenter)

      ctrlLeftLayout.addWidget(self.ctrlExchange)
      ctrlLeftLayout.addWidget(self.ctrlPair)
      ctrlLeftLayout.addWidget(self.ctrlTime)
      ctrlLeftLayout.setSpacing(10)
      ctrlLeftLayout.setContentsMargins(5,5,5,5)
      ctrlLeftLayout.setAlignment(QtCore.Qt.AlignLeft)

      self.ctrlOverlay = QtGui.QComboBox()
      self.ctrlOverlay.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
      self.ctrlOverlay.view().setSpacing(2)
      self.ctrlOverlay.setObjectName('overlayCombo')

      self.ctrlIndicator = QtGui.QComboBox()
      self.ctrlIndicator.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
      self.ctrlIndicator.view().setSpacing(2)
      self.ctrlIndicator.setObjectName('indicatorCombo')

      ctrlRightLayout.addWidget(self.ctrlOverlay)
      ctrlRightLayout.addWidget(self.ctrlIndicator)
      ctrlRightLayout.setSpacing(10)
      ctrlRightLayout.setContentsMargins(5,5,5,5)
      ctrlRightLayout.setAlignment(QtCore.Qt.AlignRight)

      parentLayout.addLayout(ctrlLeftLayout)
      parentLayout.addLayout(ctrlRightLayout)

      self.setControlsData()


   def setControlsData(self):
      # Set exchange list
      self.ctrlExchange.addItems(['Bitfinex', 'Kraken', 'Binance'])

      # Set pair list
      pairList = ['BTCUSD', 'ETHBTC', 'DASHBTC', 'BCHBTC', 'ETCBTC', 'RPMBTC', 'ETHUSD', 'IOTABTC']
      self.ctrlPair.addItems(pairList)
      self.ctrlPairView.setMinimumHeight((len(pairList) + 1) * (self.ctrlPairView.sizeHintForRow(0) + 6))
      self.ctrlPairView.updateGeometry()

      # Set time spans
      timeList = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w']
      self.ctrlTime.addItems(timeList)
      self.ctrlTime.setMaxVisibleItems(len(timeList)+1)
      for i in range(self.ctrlTime.count()):
         self.ctrlTime.setItemData(i, QtCore.Qt.AlignCenter, QtCore.Qt.TextAlignmentRole)

      # Set overlays
      overlayList = ['Grid', 'EMA', 'SMA', 'Parabolic SAR', 'SomeLongOverlayExample']
      overlayModel = QtGui.QStandardItemModel(len(overlayList), 1)
      item = QtGui.QStandardItem('Overlays')
      item.setSelectable(False)
      overlayModel.setItem(0, item)
      for i in range(len(overlayList)):
         item = QtGui.QStandardItem(overlayList[i])
         item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
         item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
         overlayModel.setItem(i+1, item)
      self.ctrlOverlay.setModel(overlayModel)
      self.ctrlOverlay.view().setMinimumWidth(1.5 * self.ctrlOverlay.view().sizeHintForColumn(0))
      self.ctrlOverlay.view().setMinimumHeight(overlayModel.rowCount() * (self.ctrlOverlay.view().sizeHintForRow(1) + 3))
      self.ctrlOverlay.model().item(0,0).setSizeHint(QtCore.QSize(0,0))

      # Set indicators
      indicatorList = ['MACD', 'RSA', 'StockRSA']
      indicatorModel = QtGui.QStandardItemModel(len(indicatorList), 1)
      item = QtGui.QStandardItem('Indicators')
      item.setSelectable(False)
      indicatorModel.setItem(0, item)
      for i in range(len(indicatorList)):
         item = QtGui.QStandardItem(indicatorList[i])
         item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
         item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
         indicatorModel.setItem(i+1, item)
      self.ctrlIndicator.setModel(indicatorModel)
      self.ctrlIndicator.view().setMinimumWidth( 1.5 * self.ctrlIndicator.view().sizeHintForColumn(0))
      self.ctrlIndicator.view().setMinimumHeight((indicatorModel.rowCount()) * (self.ctrlIndicator.view().sizeHintForRow(1) + 3))
      self.ctrlIndicator.model().item(0,0).setSizeHint(QtCore.QSize(0,0))

      self.ctrlIndicator.model().itemChanged.connect(self.indicatorChanged)



   @pyqtSlot(QtGui.QStandardItem)
   def indicatorChanged(self, itemChanged):
      if (itemChanged.checkState() == QtCore.Qt.Checked):
         if itemChanged.text() == 'MACD':
            try:
               self.macdFrame.show()
            except AttributeError:
               self.addMACD()
         if itemChanged.text() == 'RSA':
            try:
               self.rsaFrame.show()
            except AttributeError:
               self.addRSA()

      else:
         if itemChanged.text() == 'MACD':
                  self.macdFrame.hide()
         if itemChanged.text() == 'RSA':
                  self.rsaFrame.hide()


   # ------------------------------------------------------------------------------------
   # Candle chart
   # ------------------------------------------------------------------------------------
   def addCandleChart(self, parentLayout):

      candleChart = pg.PlotWidget()
      x = np.cos(np.linspace(0, 2 * np.pi, 1000))
      y = np.sin(np.linspace(0, 4 * np.pi, 1000))
      candleChart.plot(x, y)
      candleChart.showGrid(x=True, y=True)

      parentLayout.addWidget(candleChart, stretch=4)

   def addMACD(self):
      self.macdChart = pg.PlotWidget()
      x = np.sin(np.linspace(0, 2 * np.pi, 1000))
      self.macdChart.plot(x)

      self.macdFrame = QtGui.QFrame()
      self.macdLayout = QtGui.QVBoxLayout()
      self.macdLayout.setSpacing(0)
      self.macdLayout.setMargin(0)
      self.macdFrame.setLayout(self.macdLayout)
      self.macdLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=1))
      self.macdLayout.addWidget(self.createSeparator(orientation=0, color='rgb(0,0,0)', stroke=3))
      self.macdLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=1))
      self.macdLayout.addWidget(self.macdChart)

      self.ctChartLayout.addWidget(self.macdFrame, stretch=1)

   def addRSA(self):
      self.rsaChart = pg.PlotWidget()
      x = np.cos(np.linspace(0, 2 * np.pi, 1000))
      self.rsaChart.plot(x)

      self.rsaFrame = QtGui.QFrame()
      self.rsaLayout = QtGui.QVBoxLayout()
      self.rsaLayout.setSpacing(0)
      self.rsaLayout.setMargin(0)
      self.rsaFrame.setLayout(self.rsaLayout)
      self.rsaLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=1))
      self.rsaLayout.addWidget(self.createSeparator(orientation=0, color='rgb(0,0,0)', stroke=3))
      self.rsaLayout.addWidget(self.createSeparator(orientation=0, color=COLOR_SEPARATOR, stroke=1))
      self.rsaLayout.addWidget(self.rsaChart)

      self.ctChartLayout.addWidget(self.rsaFrame, stretch=1)



   # ------------------------------------------------------------------------------------
   # Trades
   # ------------------------------------------------------------------------------------



   def setTradesLayout(self, parentLayout):
      self.cttabTradesLayout = QtGui.QHBoxLayout()
      self.tabTradesWidget = QtGui.QTabWidget()
      self.tabTradesWidget.setObjectName('tradesTabWidget')
      self.tabOpenOrders = QtGui.QTableWidget()
      self.tabHistory = QtGui.QTableWidget()
      self.tabTradesWidget.addTab(self.tabOpenOrders, "Open Orders")
      self.tabTradesWidget.addTab(self.tabHistory, "History")
      self.cttabTradesLayout.addWidget(self.tabTradesWidget)
      self.cttabTradesLayout.setContentsMargins(0,5,0,0)
      self.tabTradesWidget.tabBar().setObjectName('tradesTabBar')

      # OpenOrders tab
      tableOpenOrdersHeader = ['Pair', 'Type', 'Amount', 'Price', 'Date', 'Filled%', '']
      self.tabOpenOrders.setColumnCount(len(tableOpenOrdersHeader))
      self.tabOpenOrders.setHorizontalHeaderLabels(tableOpenOrdersHeader)
      self.tabOpenOrders.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
      self.tabOpenOrders.horizontalHeader().setResizeMode(self.tabOpenOrders.columnCount()-1, QtGui.QHeaderView.ResizeToContents)
      self.tabOpenOrders.verticalHeader().setVisible(False)
      self.tabOpenOrders.setShowGrid(False)
      self.tabOpenOrders.setAlternatingRowColors(True)
      self.tabOpenOrders.horizontalHeader().setStyleSheet( 'QHeaderView::s‌​ection { background-color: rgb(0,0,0); }')
      self.tabOpenOrders.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

      # History tab
      tabHistoryLayout = QtGui.QHBoxLayout(self.tabHistory)
      tabHistoryControlsLayout = QtGui.QVBoxLayout()
      self.tabHistoryTable = QtGui.QTableWidget()
      self.tabHistoryTable.setObjectName('historyTable')
      tabHistoryLayout.addLayout(tabHistoryControlsLayout, stretch=1)
      tabHistoryLayout.addWidget(self.tabHistoryTable, stretch=40)
      tabHistoryLayout.setMargin(0)
      tabHistoryLayout.setSpacing(0)

      periodList = ['1d', '3d', '1w', '1m']
      self.historyPeriodCombo = QtGui.QComboBox()
      self.historyPeriodCombo.setObjectName('historyPeriodCombo')
      self.historyPeriodCombo.addItems(periodList)
      self.historyPeriodCombo.setMaxVisibleItems(len(periodList) + 1)
      self.historyPeriodCombo.adjustSize()
      for i in range(self.historyPeriodCombo.count()):
         self.historyPeriodCombo.setItemData(i, QtCore.Qt.AlignCenter, QtCore.Qt.TextAlignmentRole)
      tabHistoryControlsLayout.addWidget(self.historyPeriodCombo)
      tabHistoryControlsLayout.addWidget(self.createSeparator(orientation=0, color='white', stroke=1))
      tabHistoryControlsLayout.setAlignment(QtCore.Qt.AlignTop)
      tabHistoryControlsLayout.setSpacing(3)
      tabHistoryControlsLayout.setContentsMargins(4,4,0,0)

      tableHistoryHeader = ['Time', 'Pair', 'Type', 'Price', 'Amount', 'Total', 'Fee']
      self.tabHistoryTable.setColumnCount(len(tableHistoryHeader))
      self.tabHistoryTable.setHorizontalHeaderLabels(tableHistoryHeader)
      self.tabHistoryTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
      self.tabHistoryTable.verticalHeader().setVisible(False)
      self.tabHistoryTable.setShowGrid(False)
      self.tabHistoryTable.setAlternatingRowColors(True)
      self.tabHistoryTable.horizontalHeader().setStyleSheet( 'QHeaderView::s‌​ection { background-color: rgb(0,0,0); }')
      self.tabHistoryTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)


      parentLayout.addLayout(self.cttabTradesLayout)

      self.setOpenOrdersData(['WTC/BTC', 'Sell', '20', '0.00107880', '2017-10-15 16:06:12', '0.00'])
      self.setOpenOrdersData(['WTC/BTC', 'Buy', '40', '0.00107880', '2017-10-15 16:06:12', '0.00'])
      self.setHistoryData(['2017-10-16 06:43:53', 'WTC/BTC', 'Sell', '0.00115990', '20', '0.02319800', '0.04239456 BNB'])
      self.setHistoryData(['2017-10-16 06:36:53', 'WTC/BTC', 'Buy', '0.00113655', '20', '0.02273100', '0.04160735 BNB'])
      self.setHistoryData(['2017-10-16 06:35:53', 'WTC/BTC', 'Buy', '0.00113655', '20', '0.02273100', '0.04160735 BNB'])


   def setOpenOrdersData(self, rowData):
      self.tabOpenOrders.insertRow(0)
      self.tabOpenOrders.setRowHeight(0, 25)
      for i, data in enumerate(rowData):
         item = QtGui.QTableWidgetItem(data)
         item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
         item.setTextAlignment(QtCore.Qt.AlignCenter)
         if i == 1:
            if rowData[i] == 'Sell':
               item.setTextColor(QtCore.Qt.red)
            else:
               item.setTextColor(QtCore.Qt.green)
         self.tabOpenOrders.setItem(0, i, item)
      cancelButton = QtGui.QPushButton('Cancel')
      cancelButton.setObjectName('cancelButton')
      cancelButton.clicked.connect(self.cancelButtonClicked)
      cancelButton.adjustSize()
      self.tabOpenOrders.setCellWidget(0, len(rowData), cancelButton)


   def setHistoryData(self, rowData):
      self.tabHistoryTable.insertRow(0)
      self.tabHistoryTable.setRowHeight(0, 25)
      for i, data in enumerate(rowData):
         item = QtGui.QTableWidgetItem(data)
         item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
         item.setTextAlignment(QtCore.Qt.AlignCenter)
         if i == 2:
            if rowData[i] == 'Sell':
               item.setTextColor(QtCore.Qt.red)
            else:
               item.setTextColor(QtCore.Qt.green)
         self.tabHistoryTable.setItem(0, i, item)


   def cancelButtonClicked(self):
      button = QtGui.qApp.focusWidget()
      # or button = self.sender()
      index = self.tabOpenOrders.indexAt(button.pos())
      if index.isValid():
         self.tabOpenOrders.removeRow(index.row())

   # ------------------------------------------------------------------------------------
   # OrderBook
   # ------------------------------------------------------------------------------------

   # set OrderBook layout
   def setOrderBookLayout(self, OrderBookLayout):
      self.ctOrderBookGraphLayout = QtGui.QVBoxLayout()
      self.ctOrderBookNumericLayout = QtGui.QVBoxLayout()
      self.ctOrderBookTradesLayout = QtGui.QHBoxLayout()
      OrderBookLayout.addLayout(self.ctOrderBookGraphLayout, stretch=6)
      OrderBookLayout.addWidget(self.createSeparator(orientation=1, color=COLOR_SEPARATOR, stroke=5))
      OrderBookLayout.addLayout(self.ctOrderBookNumericLayout, stretch=5)
      OrderBookLayout.addWidget(self.createSeparator(orientation=1, color=COLOR_SEPARATOR, stroke=5))
      OrderBookLayout.addLayout(self.ctOrderBookTradesLayout, stretch=5)
      OrderBookLayout.addWidget(self.createSeparator(orientation=1, color=COLOR_SEPARATOR, stroke=5))
      self.setOrderBookGraphLayout(self.ctOrderBookGraphLayout)
      self.setOrderBookNumericLayout(self.ctOrderBookNumericLayout)
      self.setOrderBookTradesLayout(self.ctOrderBookTradesLayout)

   # OrderBook Graph layout
   def setOrderBookGraphLayout(self, ctOrderBookGraphLayout):
      p1 = pg.PlotWidget()
      p1.plot(np.random.normal(size=100), pen=(255, 0, 0), name="Red curve")
      ctOrderBookGraphLayout.addWidget(p1)
      ctOrderBookGraphLayout.setContentsMargins(5, 5, 5, 5)


   # OrderBook Numeric layout
   def setOrderBookNumericLayout(self,ctOrderBookNumericLayout):
      # asks
      self.askLabelPrice = QtGui.QLabel()
      self.askLabelPrice.setAlignment(QtCore.Qt.AlignLeft)
      self.askLabelPrice.setStyleSheet(COLOR_RED)
      self.askLabelAmount = QtGui.QLabel()
      self.askLabelAmount.setAlignment(QtCore.Qt.AlignRight)
      self.askLabelSum = QtGui.QLabel()
      self.askLabelSum.setAlignment(QtCore.Qt.AlignRight)
      self.askLabelLayout = QtGui.QHBoxLayout()
      self.askLabelLayout.addWidget(self.askLabelPrice, stretch=3)
      self.askLabelLayout.addWidget(self.askLabelAmount, stretch=3)
      self.askLabelLayout.addWidget(self.askLabelSum, stretch=4)

      # last price
      self.priceLabel = QtGui.QLabel()
      self.priceLabel.setAlignment(QtCore.Qt.AlignCenter)
      self.priceLabel.setStyleSheet('font-size: 30px;')

      # bids
      self.bidLabelPrice = QtGui.QLabel()
      self.bidLabelPrice.setAlignment(QtCore.Qt.AlignLeft)
      self.bidLabelPrice.setStyleSheet(COLOR_GREEN)
      self.bidLabelAmount = QtGui.QLabel()
      self.bidLabelAmount.setAlignment(QtCore.Qt.AlignRight)
      self.bidLabelSum = QtGui.QLabel()
      self.bidLabelSum.setAlignment(QtCore.Qt.AlignRight)
      self.bidLabelLayout = QtGui.QHBoxLayout()
      self.bidLabelLayout.addWidget(self.bidLabelPrice, stretch=3)
      self.bidLabelLayout.addWidget(self.bidLabelAmount, stretch=3)
      self.bidLabelLayout.addWidget(self.bidLabelSum, stretch=4)

      # add widgets to layout
      ctOrderBookNumericLayout.addLayout(self.askLabelLayout, stretch=12)
      ctOrderBookNumericLayout.addWidget(self.priceLabel, stretch=2)
      ctOrderBookNumericLayout.addLayout(self.bidLabelLayout, stretch=12)
      ctOrderBookNumericLayout.setContentsMargins(5,5,5,5)

      # set data
      self.setOrderBookNumericData(None)


   # OrderBook Trades layout
   def setOrderBookTradesLayout(self, ctOrderBookTradesLayout):
      self.tradesPriceLabel = QtGui.QLabel()
      self.tradesPriceLabel.setAlignment(QtCore.Qt.AlignLeft)
      self.tradesAmountLabel = QtGui.QLabel()
      self.tradesAmountLabel.setAlignment(QtCore.Qt.AlignRight)
      self.tradesSumLabel = QtGui.QLabel()
      self.tradesSumLabel.setAlignment(QtCore.Qt.AlignRight)

      ctOrderBookTradesLayout.addWidget(self.tradesPriceLabel, stretch=3)
      ctOrderBookTradesLayout.addWidget(self.tradesAmountLabel, stretch=3)
      ctOrderBookTradesLayout.addWidget(self.tradesSumLabel, stretch=4)
      ctOrderBookTradesLayout.setContentsMargins(5, 5, 5, 5)

      self.setOrderBookTradesData(None)



   def setOrderBookGraphData(self, data):
      pass

   def setOrderBookNumericData(self, data):
      self.askLabelPrice.setText('4001\n4002\n4003')
      self.askLabelAmount.setText('1.23\n2.2334\n3.23')
      self.askLabelSum.setText('1.23\n3.46\n5.45')
      self.priceLabel.setText('4987.23')
      self.bidLabelPrice.setText('4001\n4002\n4003')
      self.bidLabelAmount.setText('1.23\n2.23\n3.23')
      self.bidLabelSum.setText('1.23\n3.46\n5.45')


   def setOrderBookTradesData(self, data):
      priceText = ''
      tradesData = [[4000, 1.1, 10], [-4001, 2.22, 12], [4002, 3.333, 13]]
      for i in range(len(tradesData)):
         if (tradesData[i][0] < 0):
            priceText += '<font color=\"red\">' + str(-tradesData[i][0]) + '</font><br /> '
         else:
            priceText += '<font color=\"#00ff00\">' + str(tradesData[i][0]) + '</font><br /> '

      self.tradesPriceLabel.setText(priceText)
      self.tradesAmountLabel.setText('1.23\n2.2334\n3.23')
      self.tradesSumLabel.setText('1.23\n3.46\n5.45')



   # ------------------------------------------------------------------------------------
   # PlaceOrder Layout
   # ------------------------------------------------------------------------------------

   def setPlaceOrderLayout(self, PlaceOrderLayout):
      self.cttabOrderLayout = QtGui.QHBoxLayout()
      self.tabOrderWidget = QtGui.QTabWidget()
      self.tabLimitOrder = QtGui.QWidget()
      self.tabMarketOrder = QtGui.QWidget()
      self.tabOrderWidget.addTab(self.tabLimitOrder, "Limit")
      self.tabOrderWidget.addTab(self.tabMarketOrder, "Market")
      self.cttabOrderLayout.addWidget(self.tabOrderWidget)
      self.cttabOrderLayout.setContentsMargins(0,5,0,0)
      PlaceOrderLayout.addLayout(self.cttabOrderLayout)
      PlaceOrderLayout.addWidget(self.createSeparator(orientation=1, color=COLOR_SEPARATOR, stroke=5))


      self.ctLimitOrderLayout = QtGui.QHBoxLayout(self.tabLimitOrder)
      self.ctMarketOrderLayout = QtGui.QHBoxLayout(self.tabMarketOrder)

      self.addLimitOrderLayout(self.ctLimitOrderLayout)
      self.setLimitData()

      self.addMarketOrderLayout(self.ctMarketOrderLayout)
      self.setMarketData()


   # Limit Order Layout
   # ---------------------------------------------------
   def addLimitOrderLayout(self, parentLayout):
      self.ctLimitOrderBuyLayout = QtGui.QGridLayout()
      self.ctLimitOrderSellLayout = QtGui.QGridLayout()

      self.addLimitBuyLayout(self.ctLimitOrderBuyLayout)
      self.addLimitSellLayout(self.ctLimitOrderSellLayout)

      parentLayout.addLayout(self.ctLimitOrderBuyLayout, stretch=1)
      parentLayout.addLayout(self.ctLimitOrderSellLayout, stretch=1)
      parentLayout.setSpacing(10)


   # Limit BUY Layout
   # ---------------------------------------------------
   def addLimitBuyLayout(self, parentLayout):
      self.limitBuyInfoLabel = QtGui.QLabel()
      self.limitBuyInfoLabel.setStyleSheet('font: bold 16px;')

      self.limitBuyBalanceLabel = QtGui.QLabel()
      self.limitBuyBalanceAmountLabel = QtGui.QLabel()
      self.limitBuyBalanceLabel.setObjectName('grayedLabel')
      self.limitBuyBalanceAmountLabel.setObjectName('grayedLabel')

      limitBuyPriceLabel = QtGui.QLabel('Price:')
      self.limitBuyPriceInput = QtGui.QLineEdit()
      self.limitBuyPriceInput.setValidator(QtGui.QDoubleValidator(0, 100000.0, 2))

      limitBuyAmountLabel = QtGui.QLabel('Amount:')
      self.limitBuyAmountInput = QtGui.QLineEdit()

      limitBuyTotalLabel = QtGui.QLabel('Total:')
      self.limitBuyTotalValueLabel = QtGui.QLabel()
      limitBuyTotalLabel.setObjectName('totalLabel')

      self.limitBuyButton = QtGui.QPushButton()
      self.limitBuyButton.setMinimumHeight(40)
      self.limitBuyButton.setText('BUY')
      self.limitBuyButton.setObjectName('limitBuyButton')

      parentLayout.addWidget(self.limitBuyInfoLabel, 0, 0)
      parentLayout.addWidget(self.limitBuyBalanceLabel, 1, 0)
      parentLayout.addWidget(self.limitBuyBalanceAmountLabel, 1, 1)
      parentLayout.addWidget(limitBuyPriceLabel, 2, 0)
      parentLayout.addWidget(self.limitBuyPriceInput, 2, 1)
      parentLayout.addWidget(limitBuyAmountLabel, 3, 0)
      parentLayout.addWidget(self.limitBuyAmountInput, 3, 1)
      parentLayout.addWidget(limitBuyTotalLabel, 4, 0)
      parentLayout.addWidget(self.limitBuyTotalValueLabel, 4, 1)
      parentLayout.addWidget(self.limitBuyButton, 5, 0, 1, 2)
      parentLayout.setMargin(15)
      parentLayout.setSpacing(10)
      parentLayout.setColumnStretch(0,1)
      parentLayout.setColumnStretch(1,3)
      parentLayout.setRowStretch(0, 2)
      parentLayout.setRowStretch(5, 2)


   # Limit SELL Layout
   # ---------------------------------------------------
   def addLimitSellLayout(self, parentLayout):
      self.limitSellInfoLabel = QtGui.QLabel()
      self.limitSellInfoLabel.setStyleSheet('font: bold 16px;')

      self.limitSellBalanceLabel = QtGui.QLabel()
      self.limitSellBalanceAmountLabel = QtGui.QLabel()
      self.limitSellBalanceLabel.setObjectName('grayedLabel')
      self.limitSellBalanceAmountLabel.setObjectName('grayedLabel')

      limitSellPriceLabel = QtGui.QLabel('Price:')
      self.limitSellPriceInput = QtGui.QLineEdit()
      self.limitSellPriceInput.setValidator(QtGui.QDoubleValidator(0, 100000.0, 2))

      limitSellAmountLabel = QtGui.QLabel('Amount:')
      self.limitSellAmountInput = QtGui.QLineEdit()

      limitSellTotalLabel = QtGui.QLabel('Total:')
      self.limitSellTotalValueLabel = QtGui.QLabel()
      limitSellTotalLabel.setObjectName('totalLabel')

      self.limitSellButton = QtGui.QPushButton()
      self.limitSellButton.setMinimumHeight(40)
      self.limitSellButton.setText('SELL')
      self.limitSellButton.setObjectName('limitSellButton')

      parentLayout.addWidget(self.limitSellInfoLabel, 0, 0)
      parentLayout.addWidget(self.limitSellBalanceLabel, 1, 0)
      parentLayout.addWidget(self.limitSellBalanceAmountLabel, 1, 1)
      parentLayout.addWidget(limitSellPriceLabel, 2, 0)
      parentLayout.addWidget(self.limitSellPriceInput, 2, 1)
      parentLayout.addWidget(limitSellAmountLabel, 3, 0)
      parentLayout.addWidget(self.limitSellAmountInput, 3, 1)
      parentLayout.addWidget(limitSellTotalLabel, 4, 0)
      parentLayout.addWidget(self.limitSellTotalValueLabel, 4, 1)
      parentLayout.addWidget(self.limitSellButton, 5, 0, 1, 2)
      parentLayout.setMargin(15)
      parentLayout.setSpacing(10)
      parentLayout.setColumnStretch(0,1)
      parentLayout.setColumnStretch(1,3)
      parentLayout.setRowStretch(0, 2)
      parentLayout.setRowStretch(5, 3)


   def setLimitData(self):
      self.limitBuyInfoLabel.setText('Buy BTC')
      self.limitBuyBalanceLabel.setText(('USD Balance:'))
      self.limitBuyBalanceAmountLabel.setText('1450.65')

      self.limitSellInfoLabel.setText('Sell BTC')
      self.limitSellBalanceLabel.setText(('BTC Balance:'))
      self.limitSellBalanceAmountLabel.setText('2.356')



   # Market Order Layout
   # ---------------------------------------------------
   def addMarketOrderLayout(self, parentLayout):
      self.ctMarketOrderBuyLayout = QtGui.QGridLayout()
      self.ctMarketOrderSellLayout = QtGui.QGridLayout()

      self.addMarketBuyLayout(self.ctMarketOrderBuyLayout)
      self.addMarketSellLayout(self.ctMarketOrderSellLayout)

      parentLayout.addLayout(self.ctMarketOrderBuyLayout, stretch=1)
      parentLayout.addLayout(self.ctMarketOrderSellLayout, stretch=1)
      parentLayout.setSpacing(10)

   # Market BUY Layout
   # ---------------------------------------------------
   def addMarketBuyLayout(self, parentLayout):
      self.marketBuyInfoLabel = QtGui.QLabel()
      self.marketBuyInfoLabel.setStyleSheet('font: bold 16px;')

      self.marketBuyBalanceLabel = QtGui.QLabel()
      self.marketBuyBalanceAmountLabel = QtGui.QLabel()
      self.marketBuyBalanceLabel.setObjectName('grayedLabel')
      self.marketBuyBalanceAmountLabel.setObjectName('grayedLabel')

      #marketBuyPriceLabel = QtGui.QLabel
      marketBuyPriceLabel = QtGui.QLabel('Price:')
      marketBuyPriceLabel.setObjectName('grayedLabel')
      self.marketBuyPriceInput = QtGui.QLineEdit()
      self.marketBuyPriceInput.setText('Market price')
      self.marketBuyPriceInput.setDisabled(True)
      self.marketBuyPriceInput.setObjectName('disabledInput')

      marketBuyAmountLabel = QtGui.QLabel('Amount:')
      self.marketBuyAmountInput = QtGui.QLineEdit()

      marketBuyTotalLabel = QtGui.QLabel('Total:')
      self.marketBuyTotalValueLabel = QtGui.QLabel()
      marketBuyTotalLabel.setObjectName('totalLabel')

      self.marketBuyButton = QtGui.QPushButton()
      self.marketBuyButton.setMinimumHeight(40)
      self.marketBuyButton.setText('BUY')
      self.marketBuyButton.setObjectName('marketBuyButton')

      parentLayout.addWidget(self.marketBuyInfoLabel, 0, 0)
      parentLayout.addWidget(self.marketBuyBalanceLabel, 1, 0)
      parentLayout.addWidget(self.marketBuyBalanceAmountLabel, 1, 1)
      parentLayout.addWidget(marketBuyPriceLabel, 2, 0)
      parentLayout.addWidget(self.marketBuyPriceInput, 2, 1)
      parentLayout.addWidget(marketBuyAmountLabel, 3, 0)
      parentLayout.addWidget(self.marketBuyAmountInput, 3, 1)
      parentLayout.addWidget(marketBuyTotalLabel, 4, 0)
      parentLayout.addWidget(self.marketBuyTotalValueLabel, 4, 1)
      parentLayout.addWidget(self.marketBuyButton, 5, 0, 1, 2)
      parentLayout.setMargin(15)
      parentLayout.setSpacing(10)
      parentLayout.setColumnStretch(0,1)
      parentLayout.setColumnStretch(1,3)
      parentLayout.setRowStretch(0, 2)
      parentLayout.setRowStretch(5, 2)


   # Market SELL Layout
   # ---------------------------------------------------
   def addMarketSellLayout(self, parentLayout):
      self.marketSellInfoLabel = QtGui.QLabel()
      self.marketSellInfoLabel.setStyleSheet('font: bold 16px;')

      self.marketSellBalanceLabel = QtGui.QLabel()
      self.marketSellBalanceAmountLabel = QtGui.QLabel()
      self.marketSellBalanceLabel.setObjectName('grayedLabel')
      self.marketSellBalanceAmountLabel.setObjectName('grayedLabel')

      marketSellPriceLabel = QtGui.QLabel('Price:')
      marketSellPriceLabel.setObjectName('grayedLabel')
      self.marketSellPriceInput = QtGui.QLineEdit()
      self.marketSellPriceInput.setText('Market price')
      self.marketSellPriceInput.setDisabled(True)
      self.marketSellPriceInput.setObjectName('disabledInput')

      marketSellAmountLabel = QtGui.QLabel('Amount:')
      self.marketSellAmountInput = QtGui.QLineEdit()

      marketSellTotalLabel = QtGui.QLabel('Total:')
      self.marketSellTotalValueLabel = QtGui.QLabel()
      marketSellTotalLabel.setObjectName('totalLabel')

      self.marketSellButton = QtGui.QPushButton()
      self.marketSellButton.setMinimumHeight(40)
      self.marketSellButton.setText('SELL')
      self.marketSellButton.setObjectName('marketSellButton')

      parentLayout.addWidget(self.marketSellInfoLabel, 0, 0)
      parentLayout.addWidget(self.marketSellBalanceLabel, 1, 0)
      parentLayout.addWidget(self.marketSellBalanceAmountLabel, 1, 1)
      parentLayout.addWidget(marketSellPriceLabel, 2, 0)
      parentLayout.addWidget(self.marketSellPriceInput, 2, 1)
      parentLayout.addWidget(marketSellAmountLabel, 3, 0)
      parentLayout.addWidget(self.marketSellAmountInput, 3, 1)
      parentLayout.addWidget(marketSellTotalLabel, 4, 0)
      parentLayout.addWidget(self.marketSellTotalValueLabel, 4, 1)
      parentLayout.addWidget(self.marketSellButton, 5, 0, 1, 2)
      parentLayout.setMargin(15)
      parentLayout.setSpacing(10)
      parentLayout.setColumnStretch(0,1)
      parentLayout.setColumnStretch(1,3)
      parentLayout.setRowStretch(0, 2)
      parentLayout.setRowStretch(5, 3)


   def setMarketData(self):
      self.marketBuyInfoLabel.setText('Buy BTC')
      self.marketBuyBalanceLabel.setText(('USD Balance:'))
      self.marketBuyBalanceAmountLabel.setText('1450.65')

      self.marketSellInfoLabel.setText('Sell BTC')
      self.marketSellBalanceLabel.setText(('BTC Balance:'))
      self.marketSellBalanceAmountLabel.setText('2.356')



   # ------------------------------------------------------------------------------------
   # Predictor Tab
   # ------------------------------------------------------------------------------------

   # createPredictorTab
   def createPredictorTab(self):
      pass

   # ------------------------------------------------------------------------------------
   # Mics
   # ------------------------------------------------------------------------------------
   def createSeparator(self,orientation=0, color='white', stroke=1):
      separator = QtGui.QLabel()
      if orientation:
         separator.setFixedWidth(stroke)
      else:
         separator.setFixedHeight(stroke)
      separator.setStyleSheet('background-color:' + color + ';')
      return separator

# =================================================================================
#   Run qt app
# =================================================================================
def run():
   app = QtGui.QApplication(sys.argv)
   screenSize = app.desktop().screenGeometry()
   GUI = ATMainWindow(screenSize.width(), screenSize.height())
   GUI.show()
   sys.exit(app.exec_())


run()

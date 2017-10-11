import sys
import numpy as np
from PyQt4 import QtCore, QtGui
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
      self.ctMainLayout.addLayout(self.ctLeftLayout, stretch=2)
      self.ctMainLayout.addWidget(self.createSeparator(orientation=1, color=COLOR_SEPARATOR, stroke=5))
      self.ctMainLayout.addLayout(self.ctRightLayout, stretch=1)
      self.ctMainLayout.setSpacing(0)

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


      # TEST
      p4 = pg.PlotWidget()
      x = np.cos(np.linspace(0, 2 * np.pi, 1000))
      y = np.sin(np.linspace(0, 4 * np.pi, 1000))
      p4.plot(x, y)
      p4.showGrid(x=True, y=True)

      self.ctLeftLayout.addWidget(p4)


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
      self.addLimitOrderLayout(PlaceOrderLayout)


   def addLimitOrderLayout(self, parentLayout):
      self.ctPlaceOrderBuyLayout = QtGui.QGridLayout()
      self.ctPlaceOrderSellLayout = QtGui.QGridLayout()

      self.addLimitBuyLayout(self.ctPlaceOrderBuyLayout)
      self.addLimitSellLayout(self.ctPlaceOrderSellLayout)

      parentLayout.addLayout(self.ctPlaceOrderBuyLayout, stretch=1)
      parentLayout.addLayout(self.ctPlaceOrderSellLayout, stretch=1)
      parentLayout.addWidget(self.createSeparator(orientation=1, color=COLOR_SEPARATOR, stroke=5))
      parentLayout.setSpacing(10)


   def addLimitBuyLayout(self, parentLayout):

      # BUY Layout
      # ---------------------------------------------------
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

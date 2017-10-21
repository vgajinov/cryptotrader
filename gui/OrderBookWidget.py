import numpy as np
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot
import pyqtgraph as pg
from .Separators import *

# colors
COLOR_RED    = 'color: rgb(255, 0, 0)'
COLOR_GREEN  = 'color: rgb(0, 255, 0)'


class OrderBookWidget(QtGui.QWidget):
   def __init__(self):
      super(OrderBookWidget, self).__init__()

      OrderBookLayout = QtGui.QHBoxLayout(self)
      OrderBookLayout.setMargin(0)
      OrderBookLayout.setSpacing(0)

      self.orderBookGraphLayout = QtGui.QVBoxLayout()
      self.orderBookNumericLayout = QtGui.QVBoxLayout()
      self.orderBookTradesLayout = QtGui.QHBoxLayout()

      OrderBookLayout.addLayout(self.orderBookGraphLayout, stretch=6)
      OrderBookLayout.addWidget(LineSeparator(orientation='vertical', color=COLOR_SEPARATOR, stroke=5))
      OrderBookLayout.addLayout(self.orderBookNumericLayout, stretch=5)
      OrderBookLayout.addWidget(LineSeparator(orientation='vertical', color=COLOR_SEPARATOR, stroke=5))
      OrderBookLayout.addLayout(self.orderBookTradesLayout, stretch=5)

      self.setOrderBookGraphLayout(self.orderBookGraphLayout)
      self.setOrderBookNumericLayout(self.orderBookNumericLayout)
      self.setOrderBookTradesLayout(self.orderBookTradesLayout)

   # OrderBook Graph layout
   def setOrderBookGraphLayout(self, ctOrderBookGraphLayout):
      p1 = pg.PlotWidget()
      p1.plot(np.random.normal(size=100), pen=(255, 0, 0), name="Red curve")
      ctOrderBookGraphLayout.addWidget(p1)
      ctOrderBookGraphLayout.setContentsMargins(5, 5, 5, 5)


   # OrderBook Numeric layout
   def setOrderBookNumericLayout(self ,ctOrderBookNumericLayout):
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
      ctOrderBookNumericLayout.setContentsMargins(5 ,5 ,5 ,5)

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



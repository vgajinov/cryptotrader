import datetime
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

      self.createOrderBookGraphLayout(self.orderBookGraphLayout)
      self.createOrderBookNumericLayout(self.orderBookNumericLayout)
      self.createOrderBookTradesLayout(self.orderBookTradesLayout)

   # OrderBook Graph layout
   def createOrderBookGraphLayout(self, orderBookGraphLayout):
      self.orderBookGraph = pg.PlotWidget()
      self.orderBookGraph.invertX()
      self.orderBookGraph.showGrid(y=True, alpha=0.3)

      # brush is defined here using the tuple (r,g,b,a)
      self.curveBids = pg.PlotCurveItem(fillLevel=0, brush=(127, 255, 0, 250), antialias=True)
      self.curveAsks = pg.PlotCurveItem(fillLevel=0, brush=(255, 0, 0, 250), antialias=True)
      self.curveBids.rotate(90)
      self.curveAsks.rotate(90)
      self.curveBids.scale(1, -1)
      self.curveAsks.scale(1, -1)
      self.orderBookGraph.addItem(self.curveBids)
      self.orderBookGraph.addItem(self.curveAsks)

      tickFont = QtGui.QFont()
      tickFont.setPointSize(8)
      tickFont.setStretch(QtGui.QFont.Condensed)
      fm = QtGui.QFontMetrics(tickFont)
      self.orderBookGraph.getAxis('left').tickFont = tickFont
      self.orderBookGraph.getAxis('left').setWidth(1.1*fm.width('5555555'))
      self.orderBookGraph.getAxis('bottom').tickFont = tickFont

      orderBookGraphLayout.addWidget(self.orderBookGraph)
      orderBookGraphLayout.setContentsMargins(5,5,3,0)






   # OrderBook Numeric layout
   def createOrderBookNumericLayout(self, orderBookNumericLayout):
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
      self.priceLabel.setStyleSheet('font-size: 24px;')

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

      # set names for stylesheet
      self.askLabelPrice.setObjectName('orderBookLabel')
      self.askLabelAmount.setObjectName('orderBookLabel')
      self.askLabelSum.setObjectName('orderBookLabel')
      self.bidLabelPrice.setObjectName('orderBookLabel')
      self.bidLabelAmount.setObjectName('orderBookLabel')
      self.bidLabelSum.setObjectName('orderBookLabel')

      # add widgets to layout
      orderBookNumericLayout.addLayout(self.askLabelLayout, stretch=5)
      orderBookNumericLayout.addWidget(self.priceLabel, stretch=1)
      orderBookNumericLayout.addLayout(self.bidLabelLayout, stretch=5)
      orderBookNumericLayout.setContentsMargins(5, 5, 5, 2)


   # OrderBook Trades layout
   def createOrderBookTradesLayout(self, orderBookTradesLayout):
      self.tradesTable = QtGui.QTableWidget()
      self.tradesTable.setObjectName('tradeTable')
      font = self.tradesTable.font()
      font.setPixelSize(11)
      self.tradesTable.setFont(font)
      self.tradesTable.setColumnCount(3)
      self.tradesTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
      self.tradesTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
      self.tradesTable.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
      self.tradesTable.horizontalHeader().setVisible(False)
      self.tradesTable.verticalHeader().setVisible(False)
      self.tradesTable.setShowGrid(False)
      self.tradesTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
      self.tradesTable.setTextElideMode(QtCore.Qt.ElideNone)
      self.tradesTable.verticalScrollBar().setDisabled(True)
      self.tradesTable.horizontalScrollBar().setDisabled(True)
      orderBookTradesLayout.addWidget(self.tradesTable)
      orderBookTradesLayout.setContentsMargins(5, 5, 5, 2)



   # ------------------------------------------------------------------------------------
   # Update methods
   # ------------------------------------------------------------------------------------

   # set/update OrderBook graph
   def setOrderBookGraphData(self, bids, asks):
      limit     = 0.01    # minumum percent of midPrice for lower and upper bound to show on a graph
      minPoints = 20      # minimum points to show for bids and asks
      tickRatio = 0.2     # amount delta to show price tick

      # get bids and ask prices and amounts in increasing order
      askItems   = list(asks.items())
      askPrices  = [item[0] for item in askItems]
      askAmounts = [-item[1] for item in askItems]
      bidItems   = list(bids.items())
      bidPrices  = [item[0] for item in bidItems]
      bidAmounts = [item[1] for item in bidItems]

      # find the medium price and lower and upper bounds
      midPrice = bidPrices[-1] + (askPrices[0] - bidPrices[-1]) / 2
      bound = min(limit * midPrice, max(midPrice - bidPrices[-minPoints], askPrices[minPoints] - midPrice))
      lowerBound = midPrice - bound
      upperBound = midPrice + bound

      # purge bids and asks list of excessive items
      for i in range(len(bidPrices)):
         if (bidPrices[-i - 1] < lowerBound):
            bidPrices = bidPrices[-i:]
            bidAmounts = bidAmounts[-i:]
            break

      for i in range(len(askPrices)):
         if (askPrices[i] > upperBound):
            askPrices = askPrices[:i]
            askAmounts = askAmounts[:i]
            break

      # calculate histograms
      bidSums = bidAmounts[:]
      for i in range(len(bidAmounts) - 2, -1, -1):
         bidSums[i] = bidSums[i] + bidSums[i + 1]

      askSums = askAmounts[:]
      for i in range(len(askAmounts) - 1):
         askSums[i + 1] = askSums[i] + askSums[i + 1]

      lowerBound = lowerBound - 0.01*bound
      upperBound = upperBound + 0.01*bound

      # add extra points to produce zig-zag curves
      bidPrices = [lowerBound] + [item for item in bidPrices for cnt in range(2)]
      bidSums = [item for item in bidSums for cnt in range(2)] + [0]
      askPrices = [item for item in askPrices for cnt in range(2)] + [upperBound]
      askSums = [0] + [item for item in askSums for cnt in range(2)]

      # find price ticks
      ticks = [lowerBound]
      bidMax = max(bidSums)
      for i in range(len(bidPrices) - 1):
         if (bidSums[i] - bidSums[i + 1]) / bidMax > tickRatio:
            if not bidPrices[i] - ticks[-1] < 0.05 * bound:
               ticks.append(bidPrices[i])
      if midPrice - ticks[-1] < 0.05 * bound:
         ticks = ticks[:-1]
      ticks.append(midPrice)
      askMax = max(askSums)
      for i in range(len(askPrices) - 1):
         if (askSums[i + 1] - askSums[i]) / askMax > tickRatio:
            if not askPrices[i] - ticks[-1] < 0.05 * bound:
               ticks.append(askPrices[i + 1])
      if askPrices[-1] - ticks[-1] < 0.05 * bound:
         ticks[-1] = upperBound
      else:
         ticks.append(upperBound)

      # update graph data
      self.curveBids.setData(bidPrices, bidSums)
      self.curveAsks.setData(askPrices, askSums)
      self.orderBookGraph.setYRange(lowerBound, upperBound, padding=0.01)
      self.orderBookGraph.setXRange(0, 1.1*max(bidMax, askMax), padding=0.01)

      # update Y axis (prices)
      ax = self.orderBookGraph.getAxis('left')
      ax.setTicks([[(t, '{0:.2f}'.format(t)) for t in ticks]])
      ax.setStyle(stopAxisAtTick=(True, True))



   # set OrderBook numeric data
   def setOrderBookNumericData(self, bids, asks):

      numItems = int(self.askLabelPrice.height() / (self.askLabelPrice.fontInfo().pixelSize() + 2))

      askItems   = list(asks.items())[:numItems]
      askItems   = list(reversed(askItems))
      askPrices  = [item[0] for item in askItems]
      askAmounts = [-item[1] for item in askItems]

      bidItems   = list(bids.items())[-numItems:]
      bidItems   = list(reversed(bidItems))
      bidPrices  = [item[0] for item in bidItems]
      bidAmounts = [item[1] for item in bidItems]

      # calculate sums
      bidSums = bidAmounts[:]
      for i in range(len(bidAmounts) - 1):
         bidSums[i+1] = bidSums[i] + bidSums[i+1]

      askSums = askAmounts[:]
      for i in range(len(bidAmounts) - 2, -1, -1):
         askSums[i] = askSums[i] + askSums[i+1]

      # set labels
      self.askLabelPrice.setText ('\n'.join(['{:.2f}'.format(x) for x in askPrices]))
      self.askLabelAmount.setText('\n'.join(['{:.2f}'.format(x) for x in askAmounts]))
      self.askLabelSum.setText   ('\n'.join(['{:.2f}'.format(x) for x in askSums]))

      self.bidLabelPrice.setText ('\n'.join(['{:.2f}'.format(x) for x in bidPrices]))
      self.bidLabelAmount.setText('\n'.join(['{:.2f}'.format(x) for x in bidAmounts]))
      self.bidLabelSum.setText   ('\n'.join(['{:.2f}'.format(x) for x in bidSums]))


   # set price on the OrderBook numeric layout
   def setLastPrice(self, price):
      self.priceLabel.setText('{:.2f}'.format(price))


   # set OrderBook trades data
   def setOrderBookTradesData(self, tradesData):
      rowHeight = self.tradesTable.font().pixelSize() + 3
      numItems   = int(self.tradesTable.height() / rowHeight)
      tradesData = list(reversed(tradesData[-numItems:]))
      self.tradesTable.setRowCount(len(tradesData))

      # set items
      pItemMaxText = ''
      dItemMaxText = datetime.datetime.utcfromtimestamp(tradesData[0][0]/1000).strftime('%H:%M:%S')
      amountThreshold = 0.1 * sum([abs(x[1]) for x in tradesData])
      for i in range(len(tradesData)):
         self.tradesTable.setRowHeight(i, rowHeight)

         # prices
         priceString = '{:.4f}'.format(tradesData[i][2])
         priceItem = QtGui.QTableWidgetItem(priceString)
         if tradesData[i][1] < 0:
            priceItem.setForeground(QtCore.Qt.red)
         else:
            priceItem.setForeground(QtCore.Qt.green)
         self.tradesTable.setItem(i, 0, priceItem)
         if len(priceString) > len(pItemMaxText):
            pItemMaxText = priceString

         # amouns
         amountItem = QtGui.QTableWidgetItem('{:.4f}'.format(abs(tradesData[i][1])))
         amountItem.setTextAlignment(QtCore.Qt.AlignRight)
         if abs(tradesData[i][1]) > amountThreshold:
            amountItem.setForeground(QtCore.Qt.yellow)
         self.tradesTable.setItem(i, 1, amountItem)

         # date/time
         dateItem = QtGui.QTableWidgetItem(datetime.datetime.utcfromtimestamp(tradesData[i][0]/1000).strftime('%H:%M:%S'))
         dateItem.setTextAlignment(QtCore.Qt.AlignRight)
         self.tradesTable.setItem(i, 2, dateItem)

      # adjust font to fit text into columns
      fm = QtGui.QFontMetrics(self.tradesTable.font())
      pFactor = float(self.tradesTable.columnWidth(0)) / fm.width(pItemMaxText)
      dFactor = float(self.tradesTable.columnWidth(2)) / fm.width(dItemMaxText)
      fontFactor = (pFactor + dFactor) / 2
      if fontFactor < 1.1 or fontFactor > 1.25:
         newSize = int(0.9*fontFactor * self.tradesTable.font().pixelSize())-1
         newSize = min(13, max(7, newSize))
         if newSize != self.tradesTable.font().pixelSize():
            newFont = QtGui.QFont(self.tradesTable.font())
            newFont.setPixelSize(newSize)
            self.tradesTable.setFont(newFont)
            self.tradesTable.setTextElideMode(QtCore.Qt.ElideNone)
            self.tradesTable.verticalScrollBar().setDisabled(True)
            self.tradesTable.horizontalScrollBar().setDisabled(True)





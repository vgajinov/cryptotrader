import sys
from pydispatch import dispatcher
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import exchanges.bitfinex.bitfinex_v2_WebSockets as bitfinexWS
import time


class OrderBookUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, bids, asks):
      super(OrderBookUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.bids = bids
      self.asks = asks

class TradesUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, bids, asks):
      super(TradesUpdateEvent, self).__init__(self.EVENT_TYPE)


class MainWindow(QtGui.QMainWindow):
   def __init__(self, width, height):
      super(MainWindow, self).__init__()

      self.resize(width, height)
      self.setWindowTitle('OrderBook')

      self.orderBookGraph = pg.PlotWidget()
      self.orderBookGraph.invertX()
      self.orderBookGraph.showGrid(y=True, alpha=0.3)

      self.curveBids = pg.PlotCurveItem(fillLevel=0, brush=(127, 255, 0, 250), antialias=True)
      self.curveAsks = pg.PlotCurveItem(fillLevel=0, brush=(255, 0, 0, 250), antialias=True)
      self.curveBids.rotate(90)
      self.curveAsks.rotate(90)
      self.curveBids.scale(1, -1)
      self.curveAsks.scale(1, -1)
      self.orderBookGraph.addItem(self.curveBids)
      self.orderBookGraph.addItem(self.curveAsks)
      self.orderBookGraph.getViewBox().setLimits(xMin=0)

      tickFont = QtGui.QFont()
      tickFont.setPointSize(8)
      self.orderBookGraph.getAxis('left').tickFont = tickFont
      self.orderBookGraph.getAxis('bottom').tickFont = tickFont
      #self.orderBookGraph.hideAxis('bottom')

      self.setCentralWidget(self.orderBookGraph)
      self. threadID = QtCore.QThread.currentThreadId()


   def plotBook(self, bids, asks):
      global curve, hist
      limit = 0.01  # minumum percent of midPrice for lower and upper bound to show on a graph
      minPoints = 20  # minimum points to show for bids and asks
      tickRatio = 0.2  # amount delta to show price tick

      # get bids and ask prices and amounts in increasing order
      askItems = list(asks.items())
      askPrices = [item[0] for item in askItems]
      askAmounts = [-item[1] for item in askItems]
      bidItems = list(bids.items())
      bidPrices = [item[0] for item in bidItems]
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
      if not askPrices[-1] - ticks[-1] < 0.05 * bound:
         ticks.append(upperBound)

      # update graph data
      self.curveBids.setData(bidPrices, bidSums)
      self.curveAsks.setData(askPrices, askSums)
      ax = self.orderBookGraph.getAxis('left')
      ax.setTicks([[(t, "{0:.2f}".format(t)) for t in ticks]])
      ax.setStyle(stopAxisAtTick=(True, False))


   def customEvent(self, event):
      #print('received event' + str(event.type()))
      if event.type() == OrderBookUpdateEvent.EVENT_TYPE:
         self.plotBook(event.bids, event.asks)



   def bookUpdate(self, bids, asks):
      QtGui.QApplication.postEvent(self, OrderBookUpdateEvent(bids,asks))



if __name__ == '__main__':
   app = QtGui.QApplication(sys.argv)
   GUI = MainWindow(350, 800)
   GUI.show()

   # subsribe to the bitfinex OrderBook
   client = bitfinexWS.BitfinexWSClient()
   client.connect()
   dispatcher.connect(GUI.bookUpdate, signal='book_BTCUSD', sender='bitfinex')

   app.exec_()
   client.disconnect()
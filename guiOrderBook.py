import sys
from pydispatch import dispatcher
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import exchanges.bitfinex.bitfinex_v2_WebSockets as bitfinexWS
import time


class BarPlot(pg.BarGraphItem):
   def __init__(self, **opts):
      super(BarPlot, self).__init__(**opts)

   def setData(self, **opts):
      self.opts.update(opts)
      #self.picture = None    # there is a race condition here - leads to crash
      self.drawPicture()
      self._shape = None
      self.update()
      self.informViewBoundsChanged()
      time.sleep(1)


win = pg.GraphicsWindow()
#win.resize(350, 800)
win.resize(200, 500)

win.setWindowTitle('pyqtgraph example: Histogram')
plt1 = win.addPlot()
plt1.invertX()
plt1.showGrid(y=True, alpha=0.3)

# brush is defined here using the tuple (r,g,b,a)
curveBids = pg.PlotCurveItem(fillLevel=0, brush=(127,255,0,250), antialias=True)
curveAsks = pg.PlotCurveItem(fillLevel=0, brush=(255,0,0,250), antialias=True)
curveBids.rotate(90)
curveAsks.rotate(90)
curveBids.scale(1,-1)
curveAsks.scale(1,-1)
plt1.addItem(curveBids)
plt1.addItem(curveAsks)
plt1.getViewBox().setLimits(xMin=0)

tickFont = QtGui.QFont()
tickFont.setPointSize(8)
plt1.getAxis('left').tickFont=tickFont
plt1.getAxis('bottom').tickFont=tickFont

#bars = BarPlot(x=[0,1], y1=[0,0], width=0.1, brush=(0,0,255,150))
#bars.rotate(90)
#plt1.addItem(bars)



def plotBook(bids,asks):
   global curve, hist
   limit = 0.01     # minumum percent of midPrice for lower and upper bound to show on a graph
   minPoints = 20   # minimum points to show for bids and asks
   tickRatio = 0.2  # amount delta to show price tick

   # get bids and ask prices and amounts in increasing order
   askItems = list(reversed(list(asks.items())))
   askPrices = [item[0] for item in askItems]
   askAmounts = [-item[1] for item in askItems]
   bidItems = list(reversed(list(bids.items())))
   bidPrices = [item[0] for item in bidItems]
   bidAmounts = [item[1] for item in bidItems]

   # find the medium price and lower and upper bounds
   midPrice = bidPrices[-1] + (askPrices[0] - bidPrices[-1]) / 2
   bound = min( limit * midPrice, max( midPrice - bidPrices[-minPoints], askPrices[minPoints] - midPrice))
   lowerBound = midPrice - bound
   upperBound = midPrice + bound

   # purge bids and asks list of excessive items
   for i in range(len(bidPrices)):
      if (bidPrices[-i-1] < lowerBound):
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
   for i in range(len(bidAmounts)-2,-1,-1):
      bidSums[i] = bidSums[i] + bidSums[i+1]

   askSums = askAmounts[:]
   for i in range(len(askAmounts)-1):
      askSums[i+1] = askSums[i] + askSums[i+1]


   # add extra points to produce zig-zag curves
   bidPrices = [lowerBound] + [item for item in bidPrices for cnt in range(2)]
   bidSums   = [item for item in bidSums for cnt in range(2)]  + [0]

   askPrices = [item for item in askPrices for cnt in range(2)] + [ upperBound ]
   askSums   = [0] + [item for item in askSums for cnt in range(2)]

   # find price ticks
   ticks = [bidPrices[0]]
   bidMax = max(bidSums)
   for i in range(len(bidPrices)-1):
      if (bidSums[i] - bidSums[i+1]) / bidMax > tickRatio:
         if not bidPrices[i] - ticks[-1] < 0.05*bound:
            ticks.append(bidPrices[i])
   if midPrice - ticks[-1] < 0.05*bound:
      ticks = ticks[:-1]
   ticks.append(midPrice)
   askMax = max(askSums)
   for i in range(len(askPrices)-1):
      if (askSums[i+1] - askSums[i]) / askMax > tickRatio:
         if not askPrices[i] - ticks[-1] < 0.05 * bound:
            ticks.append(askPrices[i+1])
   if not askPrices[-1] - ticks[-1] < 0.05*bound:
      ticks.append(askPrices[-1])

   # update graph data
   curveBids.setData(bidPrices, bidSums)
   curveAsks.setData(askPrices, askSums)
   ax = plt1.getAxis('left')
   ax.setTicks([[(t, "{0:.2f}".format(t)) for t in ticks]])
   ax.setStyle(stopAxisAtTick=(True, False))


   # example of using bars
   # prices = bidPrices + askPrices
   # amounts = bidAmounts + askAmounts  # have to update amount or use non-duplicated prices
   # bars.setData(x=prices, y1=amounts)




# listener for book updates
def handleBook(sender, bids, asks):
   plotBook(bids, asks)


# subsribe to the bitfinex OrderBook
client = bitfinexWS.BitfinexWSClient()
client.connect()
dispatcher.connect(handleBook, signal='book_BTCUSD', sender='bitfinex')




## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
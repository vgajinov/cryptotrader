import math
from PyQt5 import QtGui
import pyqtgraph as pg



# ======================================================================
# OrderBookGraphWidget class provides
# the OrderBook graph display
# ======================================================================

class OrderBookGraphWidget(pg.PlotWidget):
    def __init__(self):
        super(OrderBookGraphWidget, self).__init__()

        self.invertX()
        self.showGrid(y=True, alpha=0.3)

        # brush is defined here using the tuple (r,g,b,a)
        self.curveBids = pg.PlotCurveItem(fillLevel=0, brush=(127, 255, 0, 250), antialias=True)
        self.curveAsks = pg.PlotCurveItem(fillLevel=0, brush=(255, 0, 0, 250), antialias=True)
        self.curveBids.rotate(90)
        self.curveAsks.rotate(90)
        self.curveBids.scale(1, -1)
        self.curveAsks.scale(1, -1)
        self.addItem(self.curveBids)
        self.addItem(self.curveAsks)

        # set font for axes
        tickFont = QtGui.QFont()
        tickFont.setPointSize(8)
        tickFont.setStretch(QtGui.QFont.Condensed)
        self.fm = QtGui.QFontMetrics(tickFont)
        self.getAxis('left').tickFont = tickFont
        self.getAxis('bottom').tickFont = tickFont


    # set/update OrderBook graph
    def setData(self, bids, asks):
        limit     = 0.01    # minumum percent of midPrice for lower and upper bound to show on a graph
        tickRatio = 0.2     # amount delta to show price tick

        # get bids and ask prices and amounts in increasing order
        askPrices  = list(asks.keys())
        askAmounts = [-x for x in asks.values()]
        bidPrices  = list(bids.keys())
        bidAmounts = list(bids.values())

        # find the medium price and lower and upper bounds
        try:
            midPrice = bidPrices[-1] + (askPrices[0] - bidPrices[-1]) / 2
            bound = limit * midPrice
            lowerBound = midPrice - bound
            upperBound = midPrice + bound
        except IndexError as e:
            print(e)
            print('len(bids) = ', len(bids))
            print('len(asks) = ', len(asks))
            return

        # purge bids and asks list of excessive items
        bidPrices = [ x for x in bidPrices if x > lowerBound]
        bidAmounts = bidAmounts[-len(bidPrices):]
        askPrices = [ x for x in askPrices if x < upperBound]
        askAmounts = askAmounts[:len(askPrices)]

        # calculate histograms
        bidSums = bidAmounts[:]
        for i in range(len(bidAmounts) - 2, -1, -1):
            bidSums[i] = bidSums[i] + bidSums[i + 1]

        askSums = askAmounts[:]
        for i in range(len(askAmounts) - 1):
            askSums[i + 1] = askSums[i] + askSums[i + 1]

        # adjust bounds for plotting
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
        self.setYRange(lowerBound, upperBound, padding=0.01)
        self.setXRange(0, 1.1*max(bidMax, askMax), padding=0.01)

        # determine the float precision for left axis
        # precision is usually in 5 siginificant digits
        # but we don't need last two, so we subtract with 3
        exp = math.ceil(math.log10(midPrice)) - 3
        pricePrec = abs(exp) if exp < 0  else 0

        # update Y axis (prices)
        ay = self.getAxis('left')
        ay.setTicks([[(t, '{0:.{prec}f}'.format(t, prec=pricePrec)) for t in ticks]])
        ay.setStyle(stopAxisAtTick=(True, True))
        self.getAxis('left').setWidth(self.fm.width('{0:.{prec}f}'.format(ticks[0], prec=pricePrec+1)))

        # set tick for X axis (amount)
        maxAmount = max(bidMax, askMax)
        exp = math.floor(math.log10(maxAmount))
        maxAmount = math.ceil(maxAmount/pow(10,exp-1)) * pow(10,exp-1)
        ax = self.getAxis('bottom')
        ax.setTicks([[(t, str(t)) for t in [maxAmount, maxAmount/2, 0]]])


    def reset(self):
        # clear graph data
        self.curveBids.setData([], [])
        self.curveAsks.setData([], [])
import math
from PyQt5 import QtGui
import pyqtgraph as pg


# ======================================================================
# OrderBookGraphWidget class provides
# the OrderBook graph display
# ======================================================================

class OrderBookGraphWidget(pg.PlotWidget):
    """The widget for the order book graph display"""

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
        tick_font = QtGui.QFont()
        tick_font.setPointSize(8)
        tick_font.setStretch(QtGui.QFont.Condensed)
        self.fm = QtGui.QFontMetrics(tick_font)
        self.getAxis('left').tickFont = tick_font
        self.getAxis('bottom').tickFont = tick_font


    def setData(self, data):
        """Sets/updates the order book graph
        :param data    order book snapshot or and update
        """
        if not data:
            return

        limit      = 0.01    # minimum percent of mid_price for lower and upper bound to show on a graph
        tick_ratio = 0.2     # amount delta to show price tick

        asks = data['asks']
        bids = data['bids']

        # get bids and ask prices and amounts in increasing order
        ask_prices  = list(asks.keys())
        ask_amounts = list(asks.values())   # [-x for x in asks.values()]
        bid_prices  = list(bids.keys())
        bid_amounts = list(bids.values())

        # find the medium price and lower and upper bounds
        try:
            mid_price = bid_prices[-1] + (ask_prices[0] - bid_prices[-1]) / 2
            bound = limit * mid_price
            lower_bound = mid_price - bound
            upper_bound = mid_price + bound
        except IndexError as e:
            print(e)
            print('len(bids) = ', len(bids))
            print('len(asks) = ', len(asks))
            return

        # purge bids and asks list of excessive items
        bid_prices = [ x for x in bid_prices if x > lower_bound]
        bid_amounts = bid_amounts[-len(bid_prices):]
        ask_prices = [ x for x in ask_prices if x < upper_bound]
        ask_amounts = ask_amounts[:len(ask_prices)]

        # calculate histograms
        bid_sums = bid_amounts[:]
        for i in range(len(bid_amounts) - 2, -1, -1):
            bid_sums[i] = bid_sums[i] + bid_sums[i + 1]

        ask_sums = ask_amounts[:]
        for i in range(len(ask_amounts) - 1):
            ask_sums[i + 1] = ask_sums[i] + ask_sums[i + 1]

        # adjust bounds for plotting
        lower_bound = lower_bound - 0.01*bound
        upper_bound = upper_bound + 0.01*bound

        # add extra points to produce zig-zag curves
        bid_prices = [lower_bound] + [item for item in bid_prices for cnt in range(2)]
        bid_sums = [item for item in bid_sums for cnt in range(2)] + [0]
        ask_prices = [item for item in ask_prices for cnt in range(2)] + [upper_bound]
        ask_sums = [0] + [item for item in ask_sums for cnt in range(2)]

        # find price ticks
        ticks = [lower_bound]
        bid_max = max(bid_sums)
        for i in range(len(bid_prices) - 1):
            if (bid_sums[i] - bid_sums[i + 1]) / bid_max > tick_ratio:
                if not bid_prices[i] - ticks[-1] < 0.05 * bound:
                    ticks.append(bid_prices[i])
        if mid_price - ticks[-1] < 0.05 * bound:
            ticks = ticks[:-1]
        ticks.append(mid_price)

        ask_max = max(ask_sums)
        for i in range(len(ask_prices) - 1):
            if (ask_sums[i + 1] - ask_sums[i]) / ask_max > tick_ratio:
                if not ask_prices[i] - ticks[-1] < 0.05 * bound:
                    ticks.append(ask_prices[i + 1])
        if ask_prices[-1] - ticks[-1] < 0.05 * bound:
            ticks[-1] = upper_bound
        else:
            ticks.append(upper_bound)

        # update graph data
        self.curveBids.setData(bid_prices, bid_sums)
        self.curveAsks.setData(ask_prices, ask_sums)
        self.setYRange(lower_bound, upper_bound, padding=0.01)
        self.setXRange(0, 1.1*max(bid_max, ask_max), padding=0.01)

        # determine the float precision for left axis
        # precision is usually in 5 significant digits
        # but we don't need last two, so we subtract with 3
        exp = math.ceil(math.log10(mid_price)) - 3
        price_precision = abs(exp) if exp < 0 else 0

        # update Y axis (prices)
        ay = self.getAxis('left')
        ay.setTicks([[(tick, f'{tick:.{price_precision}f}') for tick in ticks]])
        ay.setStyle(stopAxisAtTick=(True, True))
        self.getAxis('left').setWidth(self.fm.width(f'{ticks[0]:.{price_precision+1}f}'))

        # set tick for X axis (amount)
        max_amount = max(bid_max, ask_max)
        exp = math.floor(math.log10(max_amount))
        max_amount = math.ceil(max_amount/pow(10, exp-1)) * pow(10, exp-1)
        ax = self.getAxis('bottom')
        ax.setTicks([[(t, str(t)) for t in [max_amount, max_amount/2, 0]]])


    def reset(self):
        # clear graph data
        self.curveBids.setData([], [])
        self.curveAsks.setData([], [])

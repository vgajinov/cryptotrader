import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class TrueRange(Indicator):
    """True Range volatility index"""
    chart = None

    def __init__(self):
        super().__init__()
        self.true_range_line = QtChart.QLineSeries()
        self.true_range_line.setColor(QtCore.Qt.yellow)
        self.addSeries(self.true_range_line)
        self.true_range_avg = QtChart.QLineSeries()
        self.true_range_avg.setColor(QtCore.Qt.blue)
        self.addSeries(self.true_range_avg)


    def updateIndicator(self, data, candles_visible):
        true_range = talib.TRANGE(data[2], data[3], data[4])
        firstNotNan = np.where(np.isnan(true_range))[0][-1] + 1
        true_range[:firstNotNan] = true_range[firstNotNan]

        true_range_avg = talib.ATR(data[2], data[3], data[4], timeperiod=14)
        firstNotNan = np.where(np.isnan(true_range_avg))[0][-1] + 1
        true_range_avg[:firstNotNan] = true_range_avg[firstNotNan]

        true_range = true_range[-candles_visible:]
        true_range_avg = true_range_avg[-candles_visible:]

        self.true_range_line.clear()
        self.true_range_avg.clear()
        for i in range(candles_visible):
            self.true_range_line.append(i + 0.5, true_range[i])
            self.true_range_avg.append(i + 0.5, true_range_avg[i])

        # detach and remove old axes
        for ax in self.true_range_line.attachedAxes():
            self.true_range_line.detachAxis(ax)
        for ax in self.true_range_avg.attachedAxes():
            self.true_range_avg.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # candle_set hidden x axis
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # candle_set y price delta axis
        ay = QtChart.QValueAxis()
        ay.setRange(0.0, abs(max(true_range)))
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.true_range_line.attachAxis(ax)
        self.true_range_line.attachAxis(ay)
        self.true_range_avg.attachAxis(ax)
        self.true_range_avg.attachAxis(ay)

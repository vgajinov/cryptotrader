import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class StochasticFast(Indicator):
    """Fast Stochastic oscillator"""

    def __init__(self):
        super().__init__()
        # add color area
        self.top_line = QtChart.QLineSeries()
        self.bottom_line = QtChart.QLineSeries()
        self.top_line.setColor(QtGui.QColor(0, 127, 255, 150))
        self.bottom_line.setColor(QtGui.QColor(0, 127, 255, 150))
        self.area = QtChart.QAreaSeries(self.top_line, self.bottom_line)
        self.area.setColor(QtGui.QColor(0, 127, 255, 35))
        self.area.setBorderColor(QtGui.QColor(0, 127, 255, 35))
        self.addSeries(self.area)

        self.fastK = QtChart.QLineSeries()
        self.fastD = QtChart.QLineSeries()
        self.fastK.setColor(QtCore.Qt.magenta)
        self.fastD.setColor(QtCore.Qt.blue)
        self.addSeries(self.fastK)
        self.addSeries(self.fastD)


    def updateIndicator(self, data, candles_visible):
        # fastk, fastd = STOCHF(high, low, close, fastk_period=5, fastd_period=3, fastd_matype=0)
        fastK, fastD = talib.STOCHF(data[2], data[3], data[4], fastk_period=5, fastd_period=3, fastd_matype=0)
        firstNotNan = np.where(np.isnan(fastK))[0][-1] + 1
        fastK[:firstNotNan] = fastK[firstNotNan]
        firstNotNan = np.where(np.isnan(fastD))[0][-1] + 1
        fastD[:firstNotNan] = fastD[firstNotNan]

        fastK = fastK[-candles_visible:]
        fastD = fastD[-candles_visible:]

        self.fastK.clear()
        self.fastD.clear()
        for i in range(candles_visible):
            self.fastK.append(i + 0.5, fastK[i])
            self.fastD.append(i + 0.5, fastD[i])

        self.top_line.clear()
        self.bottom_line.clear()
        self.top_line.append(0, 80)
        self.top_line.append(candles_visible, 80)
        self.bottom_line.append(0, 20)
        self.bottom_line.append(candles_visible, 20)

        # detach and remove old axes
        for ax in self.fastK.attachedAxes():
            self.fastK.detachAxis(ax)
        for ax in self.fastD.attachedAxes():
            self.fastD.detachAxis(ax)
        for ax in self.area.attachedAxes():
            self.area.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # set x axes
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # set y axes
        ay = QtChart.QValueAxis()
        ay.setRange(0, 100)
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.fastK.attachAxis(ax)
        self.fastK.attachAxis(ay)
        self.fastD.attachAxis(ax)
        self.fastD.attachAxis(ay)

        self.area.attachAxis(ax)
        self.area.attachAxis(ay)


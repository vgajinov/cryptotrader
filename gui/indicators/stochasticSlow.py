import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class StochasticSlow(Indicator):
    """Slow Stochastic oscillator"""

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

        self.slowK = QtChart.QLineSeries()
        self.slowD = QtChart.QLineSeries()
        self.slowK.setColor(QtCore.Qt.magenta)
        self.slowD.setColor(QtCore.Qt.blue)
        self.addSeries(self.slowK)
        self.addSeries(self.slowD)


    def updateIndicator(self, data, candles_visible):
        # STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        slowK, slowD = talib.STOCH(data[2], data[3], data[4],
                                   fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        firstNotNan = np.where(np.isnan(slowK))[0][-1] + 1
        slowK[:firstNotNan] = slowK[firstNotNan]
        firstNotNan = np.where(np.isnan(slowD))[0][-1] + 1
        slowD[:firstNotNan] = slowD[firstNotNan]

        slowK = slowK[-candles_visible:]
        slowD = slowD[-candles_visible:]

        self.slowK.clear()
        self.slowD.clear()
        for i in range(candles_visible):
            self.slowK.append(i + 0.5, slowK[i])
            self.slowD.append(i + 0.5, slowD[i])

        self.top_line.clear()
        self.bottom_line.clear()
        self.top_line.append(0, 80)
        self.top_line.append(candles_visible, 80)
        self.bottom_line.append(0, 20)
        self.bottom_line.append(candles_visible, 20)

        # detach and remove old axes
        for ax in self.slowK.attachedAxes():
            self.slowK.detachAxis(ax)
        for ax in self.slowD.attachedAxes():
            self.slowD.detachAxis(ax)
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
        self.slowK.attachAxis(ax)
        self.slowK.attachAxis(ay)
        self.slowD.attachAxis(ax)
        self.slowD.attachAxis(ay)

        self.area.attachAxis(ax)
        self.area.attachAxis(ay)


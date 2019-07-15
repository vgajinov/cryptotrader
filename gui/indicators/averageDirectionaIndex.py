import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class ADX_AverageDirectionalIndex(Indicator):
    """ADX - Average Directional Movement Index with Rating"""

    def __init__(self):
        super().__init__()
        self.adx = QtChart.QLineSeries()
        self.adxr = QtChart.QLineSeries()
        self.adx.setColor(QtCore.Qt.magenta)
        self.adxr.setColor(QtCore.Qt.blue)
        self.addSeries(self.adx)
        self.addSeries(self.adxr)


    def updateIndicator(self, data, candles_visible):
        # ADX(high, low, close, timeperiod=14)
        adx = talib.ADX(data[2], data[3], data[4], timeperiod=14)
        adxr = talib.ADXR(data[2], data[3], data[4], timeperiod=14)
        firstNotNan = np.where(np.isnan(adx))[0][-1] + 1
        adx[:firstNotNan] = adx[firstNotNan]
        firstNotNan = np.where(np.isnan(adxr))[0][-1] + 1
        adxr[:firstNotNan] = adxr[firstNotNan]

        adx = adx[-candles_visible:]
        adxr = adxr[-candles_visible:]

        self.adx.clear()
        self.adxr.clear()
        for i in range(candles_visible):
            self.adx.append(i + 0.5, adx[i])
            self.adxr.append(i + 0.5, adxr[i])

        # detach and remove old axes
        for ax in self.adx.attachedAxes():
            self.adx.detachAxis(ax)
        for ax in self.adxr.attachedAxes():
            self.adxr.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # set x axes
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # set y axes
        ay = QtChart.QValueAxis()
        ay.setRange(min(adx), max(adx))
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.adx.attachAxis(ax)
        self.adx.attachAxis(ay)
        self.adxr.attachAxis(ax)
        self.adxr.attachAxis(ay)



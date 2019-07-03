import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class AROON_Oscillator(Indicator):
    """Absolute Price Oscillator"""
    chart = None

    def __init__(self):
        super().__init__()
        self.aroon = QtChart.QLineSeries()
        self.aroon.setColor(QtCore.Qt.magenta)
        self.addSeries(self.aroon)


    def updateIndicator(self, data, candles_visible):
        # AROONOSC(high, low, timeperiod=14)
        aroon = talib.AROONOSC(data[2], data[3], timeperiod=14)
        try:
            firstNotNan = np.where(np.isnan(aroon))[0][-1] + 1
        except:
            firstNotNan = 0
        aroon[:firstNotNan] = aroon[firstNotNan]
        aroon = aroon[-candles_visible:]

        self.aroon.clear()
        for i in range(candles_visible):
            self.aroon.append(i + 0.5, aroon[i])

        # detach and remove old axes
        for ax in self.aroon.attachedAxes():
            self.aroon.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # set x axes
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # set y axes
        ay = QtChart.QValueAxis()
        ay.setRange(min(aroon), max(aroon))
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.aroon.attachAxis(ax)
        self.aroon.attachAxis(ay)



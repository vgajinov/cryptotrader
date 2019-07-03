import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class OBV_OnBalanceVolume(Indicator):
    """On Balance Volume indicator"""

    def __init__(self):
        super().__init__()
        self.obv = QtChart.QLineSeries()
        self.obv.setColor(QtCore.Qt.yellow)
        self.addSeries(self.obv)


    def updateIndicator(self, data, candles_visible):
        # OBV(close, volume)
        obv = talib.OBV(data[4], data[5])
        obv = obv[-candles_visible:]

        self.obv.clear()
        for i in range(candles_visible):
            self.obv.append(i + 0.5, obv[i])

        # detach and remove old axes
        for ax in self.obv.attachedAxes():
            self.obv.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # set x axes
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # set y axes
        ay = QtChart.QValueAxis()
        ay.setRange(min(obv), max(obv))
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.obv.attachAxis(ax)
        self.obv.attachAxis(ay)



import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class Absolute_Price_Oscillator(Indicator):
    """Absolute Price Oscillator"""
    chart = None

    def __init__(self):
        super().__init__()
        self.apo = QtChart.QLineSeries()
        self.apo.setColor(QtCore.Qt.yellow)
        self.addSeries(self.apo)


    def updateIndicator(self, data, candles_visible):
        # APO(close, fastperiod=12, slowperiod=26, matype=0)
        apo = talib.APO(data[4], fastperiod=12, slowperiod=26, matype=0)
        try:
            firstNotNan = np.where(np.isnan(apo))[0][-1] + 1
        except:
            firstNotNan = 0
        apo[:firstNotNan] = apo[firstNotNan]
        apo = apo[-candles_visible:]

        self.apo.clear()
        for i in range(candles_visible):
            self.apo.append(i + 0.5, apo[i])

        # detach and remove old axes
        for ax in self.apo.attachedAxes():
            self.apo.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # set x axes
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # set y axes
        ay = QtChart.QValueAxis()
        ay.setRange(min(apo), max(apo))
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.apo.attachAxis(ax)
        self.apo.attachAxis(ay)



import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class Chande_Momentum_Oscillator(Indicator):
    """Chande Momentum Oscillator"""

    def __init__(self):
        super().__init__()
        self.chande = QtChart.QLineSeries()
        self.chande.setColor(QtCore.Qt.magenta)
        self.addSeries(self.chande)


    def updateIndicator(self, data, candles_visible):
        # CMO(close, timeperiod=14)
        chande = talib.CMO(data[4], timeperiod=14)
        try:
            firstNotNan = np.where(np.isnan(chande))[0][-1] + 1
        except:
            firstNotNan = 0
        chande[:firstNotNan] = chande[firstNotNan]
        chande = chande[-candles_visible:]

        self.chande.clear()
        for i in range(candles_visible):
            self.chande.append(i + 0.5, chande[i])

        # detach and remove old axes
        for ax in self.chande.attachedAxes():
            self.chande.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # set x axes
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # set y axes
        ay = QtChart.QValueAxis()
        ay.setRange(min(chande), max(chande))
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.chande.attachAxis(ax)
        self.chande.attachAxis(ay)



import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class Momentum(Indicator):
    """Momentum"""

    def __init__(self):
        super().__init__()
        self.line = QtChart.QLineSeries()
        self.line.setColor(QtCore.Qt.green)
        self.addSeries(self.line)


    def updateIndicator(self, data, candles_visible):
        # MOM(close, timeperiod=10)
        momentum = talib.MOM(data[4], timeperiod=10)
        try:
            firstNotNan = np.where(np.isnan(momentum))[0][-1] + 1
        except:
            firstNotNan = 0
        momentum[:firstNotNan] = momentum[firstNotNan]
        momentum = momentum[-candles_visible:]

        self.line.clear()
        for i in range(candles_visible):
            self.line.append(i + 0.5, momentum[i])

        # detach and remove old axes
        for ax in self.line.attachedAxes():
            self.line.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # set x axes
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # set y axes
        ay = QtChart.QValueAxis()
        bound = max(abs(min(momentum)), max(momentum))
        ay.setRange(-bound, bound)
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.line.attachAxis(ax)
        self.line.attachAxis(ay)



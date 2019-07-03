import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class TRIX_1dayRateOfChange(Indicator):
    """TRIX - 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA"""

    def __init__(self):
        super().__init__()
        self.line = QtChart.QLineSeries()
        self.line.setColor(QtCore.Qt.green)
        self.addSeries(self.line)


    def updateIndicator(self, data, candles_visible):
        # real = TRIX(close, timeperiod=30)
        trix = talib.TRIX(data[4], timeperiod=30)
        try:
            firstNotNan = np.where(np.isnan(trix))[0][-1] + 1
        except:
            firstNotNan = 0
        trix[:firstNotNan] = trix[firstNotNan]
        trix = 100 * trix
        trix = trix[-candles_visible:]

        self.line.clear()
        for i in range(candles_visible):
            self.line.append(i + 0.5, trix[i])

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
        ay.setRange(min(trix), max(trix))
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.line.attachAxis(ax)
        self.line.attachAxis(ay)






import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class RSI_RelativeStrengthIndex(Indicator):
    """RSI - Relative Strength Index"""

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

        self.index_line = QtChart.QLineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidthF(0.75)
        pen.setColor(QtCore.Qt.white)
        self.index_line.setPen(pen)
        self.addSeries(self.index_line)


    def updateIndicator(self, data, candles_visible):
        # RSI(close, timeperiod=14)
        rsi = talib.RSI(data[4], timeperiod=14)
        try:
            firstNotNan = np.where(np.isnan(rsi))[0][-1] + 1
        except:
            firstNotNan = 0
        rsi[:firstNotNan] = rsi[firstNotNan]
        rsi = rsi[-candles_visible:]

        self.index_line.clear()
        for i in range(candles_visible):
            self.index_line.append(i + 0.5, rsi[i])

        self.top_line.clear()
        self.bottom_line.clear()
        self.top_line.append(0, 70)
        self.top_line.append(candles_visible, 70)
        self.bottom_line.append(0, 30)
        self.bottom_line.append(candles_visible, 30)

        # detach and remove old axes
        for ax in self.index_line.attachedAxes():
            self.index_line.detachAxis(ax)
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
        self.index_line.attachAxis(ax)
        self.index_line.attachAxis(ay)

        self.area.attachAxis(ax)
        self.area.attachAxis(ay)


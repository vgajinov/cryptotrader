import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class Williams_pR(Indicator):
    """Williams' %R"""

    def __init__(self):
        super().__init__()
        # add color area
        self.top_line = QtChart.QLineSeries()
        self.bottom_line = QtChart.QLineSeries()
        self.top_line.setColor(QtGui.QColor(0, 127, 255, 100))
        self.bottom_line.setColor(QtGui.QColor(0, 127, 255, 100))
        self.area = QtChart.QAreaSeries(self.top_line, self.bottom_line)
        self.area.setColor(QtGui.QColor(0, 127, 255, 30))
        self.area.setBorderColor(QtGui.QColor(0, 127, 255, 30))
        self.addSeries(self.area)

        self.cci = QtChart.QLineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidthF(0.75)
        pen.setColor(QtCore.Qt.blue)
        self.cci.setPen(pen)
        self.addSeries(self.cci)


    def updateIndicator(self, data, candles_visible):
        # WILLR(high, low, close, timeperiod=14)
        willr = talib.WILLR(data[2], data[3], data[4], timeperiod=14)
        try:
            firstNotNan = np.where(np.isnan(willr))[0][-1] + 1
        except:
            firstNotNan = 0
        willr[:firstNotNan] = willr[firstNotNan]
        willr = willr[-candles_visible:]

        self.cci.clear()
        for i in range(candles_visible):
            self.cci.append(i + 0.5, willr[i])

        self.top_line.clear()
        self.bottom_line.clear()
        self.top_line.append(0, -20)
        self.top_line.append(candles_visible, -20)
        self.bottom_line.append(0, -80)
        self.bottom_line.append(candles_visible, -80)

        # detach and remove old axes
        for ax in self.cci.attachedAxes():
            self.cci.detachAxis(ax)
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
        ay.setRange(-100, 0)
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.cci.attachAxis(ax)
        self.cci.attachAxis(ay)

        self.area.attachAxis(ax)
        self.area.attachAxis(ay)


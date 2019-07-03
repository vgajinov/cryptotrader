import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from .base import Overlay


class LinearRegression(Overlay):
    """Linear regression"""
    chart = None

    def __init__(self):
        self.series_fast = QtChart.QSplineSeries()
        self.series_slow = QtChart.QSplineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidthF(0.8)
        pen.setColor(QtGui.QColor(255, 255, 0))
        self.series_fast.setPen(pen)
        pen.setColor(QtGui.QColor(0, 127, 255))
        self.series_slow.setPen(pen)

    def addToChart(self, chart: QtChart.QChart):
        self.chart = chart
        self.chart.addSeries(self.series_fast)
        self.chart.addSeries(self.series_slow)

    def removeFromChart(self):
        self.chart.removeSeries(self.series_fast)
        self.chart.removeSeries(self.series_slow)
        self.chart = None

    def update(self, data, N):
        close = data[4]
        self.clear()
        self.series_fast.attachAxis(self.chart.ax)
        self.series_fast.attachAxis(self.chart.ay)
        self.series_slow.attachAxis(self.chart.ax)
        self.series_slow.attachAxis(self.chart.ay)

        regression_fast = talib.LINEARREG(close, timeperiod=11)
        firstNotNan = np.where(np.isnan(regression_fast))[0][-1] + 1
        regression_fast[:firstNotNan] = regression_fast[firstNotNan]
        for i, val in enumerate(regression_fast[-N:]):
            self.series_fast.append(i + 0.5, val)

        regression_slow = talib.LINEARREG(close, timeperiod=23)
        firstNotNan = np.where(np.isnan(regression_slow))[0][-1] + 1
        regression_slow[:firstNotNan] = regression_slow[firstNotNan]
        for i, val in enumerate(regression_slow[-N:]):
            self.series_slow.append(i + 0.5, val)


    def clear(self):
        self.series_fast.clear()
        self.series_slow.clear()

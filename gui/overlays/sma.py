import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from .base import Overlay


class SMA(Overlay):
    """SMA - Simple Moving Average"""
    chart = None

    def __init__(self):
        self.series15 = QtChart.QSplineSeries()
        self.series50 = QtChart.QSplineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidthF(0.5)
        pen.setColor(QtGui.QColor(255, 255, 0))
        self.series15.setPen(pen)
        pen.setColor(QtGui.QColor(255, 0, 255))
        self.series50.setPen(pen)


    def addToChart(self, chart: QtChart.QChart):
        self.chart = chart
        self.chart.addSeries(self.series15)
        self.chart.addSeries(self.series50)

    def removeFromChart(self):
        self.chart.removeSeries(self.series15)
        self.chart.removeSeries(self.series50)

    def update(self, data, N):
        close = data[4]
        self.clear()
        self.series15.attachAxis(self.chart.ax)
        self.series15.attachAxis(self.chart.ay)
        self.series50.attachAxis(self.chart.ax)
        self.series50.attachAxis(self.chart.ay)

        sma15 = talib.SMA(close, timeperiod=15)
        firstNotNan = np.where(np.isnan(sma15))[0][-1] + 1
        sma15[:firstNotNan] = sma15[firstNotNan]
        for i, val in enumerate(sma15[-N:]):
            self.series15.append(i + 0.5, val)

        sma50 = talib.SMA(close, timeperiod=50)
        firstNotNan = np.where(np.isnan(sma50))[0][-1] + 1
        sma50[:firstNotNan] = sma50[firstNotNan]
        for i, val in enumerate(sma50[-N:]):
            self.series50.append(i + 0.5, val)

    def clear(self):
        self.series15.clear()
        self.series50.clear()

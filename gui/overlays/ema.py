import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from .base import Overlay


class EMA(Overlay):
    """EMA - Exponential Moving Average"""
    chart = None

    def __init__(self):
        super().__init__()
        self.series9 = QtChart.QSplineSeries()
        self.series26 = QtChart.QSplineSeries()
        self.series100 = QtChart.QSplineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidthF(0.5)
        pen.setColor(QtGui.QColor(255, 255, 0))
        self.series9.setPen(pen)
        pen.setColor(QtGui.QColor(255, 0, 255))
        self.series26.setPen(pen)
        pen.setColor(QtGui.QColor(0, 127, 255))
        self.series100.setPen(pen)

    def addToChart(self, chart: QtChart.QChart):
        self.chart = chart
        self.chart.addSeries(self.series9)
        self.chart.addSeries(self.series26)
        self.chart.addSeries(self.series100)

    def removeFromChart(self):
        self.chart.removeSeries(self.series9)
        self.chart.removeSeries(self.series26)
        self.chart.removeSeries(self.series100)
        self.chart = None

    def update(self, data, N):
        close = data[4]
        self.clear()
        self.series9.attachAxis(self.chart.ax)
        self.series9.attachAxis(self.chart.ay)
        self.series26.attachAxis(self.chart.ax)
        self.series26.attachAxis(self.chart.ay)
        self.series100.attachAxis(self.chart.ax)
        self.series100.attachAxis(self.chart.ay)

        ema9 = talib.EMA(close, timeperiod=9)
        firstNotNan = np.where(np.isnan(ema9))[0][-1] + 1
        ema9[:firstNotNan] = ema9[firstNotNan]
        for i, val in enumerate(ema9[-N:]):
            self.series9.append(i + 0.5, val)

        ema21 = talib.EMA(close, timeperiod=26)
        firstNotNan = np.where(np.isnan(ema21))[0][-1] + 1
        ema21[:firstNotNan] = ema21[firstNotNan]
        for i, val in enumerate(ema21[-N:]):
            self.series26.append(i + 0.5, val)

        ema100 = talib.EMA(close, timeperiod=100)
        firstNotNan = np.where(np.isnan(ema100))[0][-1] + 1
        ema100[:firstNotNan] = ema100[firstNotNan]
        for i, val in enumerate(ema100[-N:]):
            self.series100.append(i + 0.5, val)

    def clear(self):
        self.series9.clear()
        self.series26.clear()
        self.series100.clear()

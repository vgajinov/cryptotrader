import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from .base import Overlay
from ..CandleChart import CandleChart


# ------------------------------------------------------------------------------------
# SMA - Simple Moving Average
# ------------------------------------------------------------------------------------

class SMA(Overlay):
    def __init__(self):
        self.series15 = QtChart.QSplineSeries()
        self.series50 = QtChart.QSplineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidth(0.5)
        pen.setColor(QtGui.QColor(255,255,0))
        self.series15.setPen(pen)
        pen.setColor(QtGui.QColor(255, 0, 255))
        self.series50.setPen(pen)


    def addToChart(self, chart : QtChart.QChart):
        chart.addSeries(self.series15)
        chart.addSeries(self.series50)

    def removeFromChart(self, chart : QtChart.QChart):
        chart.removeSeries(self.series15)
        chart.removeSeries(self.series50)

    def update(self, data, N, chart : CandleChart):
        close = data[4]
        self.clear()
        self.series15.attachAxis(chart.ax)
        self.series15.attachAxis(chart.ay)
        self.series50.attachAxis(chart.ax)
        self.series50.attachAxis(chart.ay)

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
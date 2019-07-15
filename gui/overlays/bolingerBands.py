import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from .base import Overlay


class BolingerBands(Overlay):
    """Parabolic SAR"""
    chart = None

    def __init__(self):
        self.upperband  = QtChart.QSplineSeries()
        self.middleband = QtChart.QSplineSeries()
        self.lowerband  = QtChart.QSplineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidthF(0.5)
        pen.setColor(QtGui.QColor(255, 255, 0))
        self.upperband.setPen(pen)
        self.middleband.setPen(pen)
        self.lowerband.setPen(pen)

    def addToChart(self, chart: QtChart.QChart):
        self.chart = chart
        self.chart.addSeries(self.upperband)
        self.chart.addSeries(self.middleband)
        self.chart.addSeries(self.lowerband)

    def removeFromChart(self):
        self.chart.removeSeries(self.upperband)
        self.chart.removeSeries(self.middleband)
        self.chart.removeSeries(self.lowerband)
        self.chart = None

    def update(self, data, N):
        close = data[4]

        self.clear()
        self.upperband.attachAxis(self.chart.ax)
        self.upperband.attachAxis(self.chart.ay)
        self.middleband.attachAxis(self.chart.ax)
        self.middleband.attachAxis(self.chart.ay)
        self.lowerband.attachAxis(self.chart.ax)
        self.lowerband.attachAxis(self.chart.ay)
        upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20, nbdevup=2,
                                                        nbdevdn=2, matype=talib.MA_Type.EMA)
        print(upperband - middleband)
        print(middleband - lowerband)
        firstNotNan = np.where(np.isnan(upperband))[0][-1] + 1
        upperband[:firstNotNan] = upperband[firstNotNan]
        middleband[:firstNotNan] = middleband[firstNotNan]
        lowerband[:firstNotNan] = lowerband[firstNotNan]
        for i in range(N):
            self.upperband.append(i + 0.5, upperband[-N + i])
            self.middleband.append(i + 0.5, middleband[-N + i])
            self.lowerband.append(i + 0.5, lowerband[-N + i])

    def clear(self):
        self.upperband.clear()
        self.middleband.clear()
        self.lowerband.clear()



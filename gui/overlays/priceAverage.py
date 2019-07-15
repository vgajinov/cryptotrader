import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from .base import Overlay


class PriceAverage(Overlay):
    """Average Price"""
    chart = None

    def __init__(self):
        self.series = QtChart.QSplineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidthF(0.5)
        pen.setColor(QtGui.QColor(255, 255, 0))
        self.series.setPen(pen)

    def addToChart(self, chart: QtChart.QChart):
        self.chart = chart
        self.chart.addSeries(self.series)

    def removeFromChart(self):
        self.chart.removeSeries(self.series)
        self.chart = None

    def update(self, data, N):
        self.clear()
        self.series.attachAxis(self.chart.ax)
        self.series.attachAxis(self.chart.ay)

        price_average = talib.AVGPRICE(data[1], data[2], data[3], data[4])
        for i, val in enumerate(price_average[-N:]):
            self.series.append(i + 0.5, val)


    def clear(self):
        self.series.clear()

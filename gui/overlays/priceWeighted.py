import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from .base import Overlay


class PriceWeighted(Overlay):
    """Weighted Price"""
    chart = None

    def __init__(self):
        self.series = QtChart.QSplineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidthF(0.5)
        pen.setColor(QtGui.QColor(255, 0, 255))
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

        price_weighted = talib.WCLPRICE(data[2], data[3], data[4])
        for i, val in enumerate(price_weighted[-N:]):
            self.series.append(i + 0.5, val)


    def clear(self):
        self.series.clear()

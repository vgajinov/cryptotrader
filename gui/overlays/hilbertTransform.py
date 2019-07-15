import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from .base import Overlay


class HTTrendline(Overlay):
    """Hilbert Transform - Trendline"""
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
        close = data[4]
        self.clear()
        self.series.attachAxis(self.chart.ax)
        self.series.attachAxis(self.chart.ay)

        htt = talib.HT_TRENDLINE(close)
        firstNotNan = np.where(np.isnan(htt))[0][-1] + 1
        htt[:firstNotNan] = htt[firstNotNan]
        for i, val in enumerate(htt[-N:]):
            self.series.append(i + 0.5, val)


    def clear(self):
        self.series.clear()

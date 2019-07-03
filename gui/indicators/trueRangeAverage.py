import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.overlays.base import Overlay


class TrueRange_AVG(Overlay):
    """Average True Range volatility index"""
    chart = None

    def __init__(self):
        self.series = QtChart.QSplineSeries()
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidthF(0.5)
        pen.setColor(QtGui.QColor(0, 127, 255))
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

        true_range = talib.ATR(data[2], data[3], data[4], timeperiod=14)
        firstNotNan = np.where(np.isnan(true_range))[0][-1] + 1
        true_range[:firstNotNan] = true_range[firstNotNan]
        for i, val in enumerate(true_range[-N:]):
            self.series.append(i + 0.5, val)


    def clear(self):
        self.series.clear()

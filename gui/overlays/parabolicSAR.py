import talib
import numpy as np
from PyQt5 import QtChart
from .base import Overlay


class ParabolicSAR(Overlay):
    """Parabolic SAR"""
    chart = None

    def __init__(self):
        self.series = QtChart.QScatterSeries()
        self.series.setMarkerSize(1)

    def addToChart(self, chart: QtChart.QChart):
        self.chart = chart
        self.chart.addSeries(self.series)

    def removeFromChart(self):
        self.chart.removeSeries(self.series)
        self.chart = None

    def update(self, data, N):
        high = data[2]
        low = data[3]

        self.clear()
        self.series.attachAxis(self.chart.ax)
        self.series.attachAxis(self.chart.ay)
        psarValues = talib.SAR(high, low)   # , acceleration=0, maximum=0
        psarValues = psarValues[-N:]
        for i, val in enumerate(psarValues):
            self.series.append(i + 0.5, val)

    def clear(self):
        self.series.clear()

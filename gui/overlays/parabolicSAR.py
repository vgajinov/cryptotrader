import talib
import numpy as np
from PyQt5 import QtChart
from .base import Overlay
from ..CandleChart import CandleChart


# ------------------------------------------------------------------------------------
# Parabolic SAR
# ------------------------------------------------------------------------------------

class ParabolicSAR(Overlay):
    def __init__(self):
        self.series = QtChart.QScatterSeries()
        self.series.setMarkerSize(1)

    def addToChart(self, chart : QtChart.QChart):
        chart.addSeries(self.series)

    def removeFromChart(self, chart : QtChart.QChart):
        chart.removeSeries(self.series)

    def update(self, data, N, chart : CandleChart):
        high      = data[2,-N:].tolist()
        low       = data[3,-N:].tolist()
        close     = data[4,-N:].tolist()

        self.clear()
        self.series.attachAxis(chart.ax)
        self.series.attachAxis(chart.ay)
        psarValues = self.parabolicSAR(high, low, close)
        #psarValues = talib.SAR(np.array(high), np.array(low), acceleration=0, maximum=0)
        for i, val in enumerate(psarValues):
            self.series.append(i + 0.5, val)

    def clear(self):
        self.series.clear()

    def parabolicSAR(self, high, low, close, iaf=0.02, maxaf=0.2):
        psar = close[:]
        bull = True
        af = iaf
        ep = low[0]
        hp = high[0]
        lp = low[0]
        for i in range(2, len(close)):
            if bull:
                psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
            else:
                psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
            reverse = False
            if bull:
                if low[i] < psar[i]:
                    bull = False
                    reverse = True
                    psar[i] = hp
                    lp = low[i]
                    af = iaf
            else:
                if high[i] > psar[i]:
                    bull = True
                    reverse = True
                    psar[i] = lp
                    hp = high[i]
                    af = iaf
            if not reverse:
                if bull:
                    if high[i] > hp:
                        hp = high[i]
                        af = min(af + iaf, maxaf)
                    if low[i - 1] < psar[i]:
                        psar[i] = low[i - 1]
                    if low[i - 2] < psar[i]:
                        psar[i] = low[i - 2]
                else:
                    if low[i] < lp:
                        lp = low[i]
                        af = min(af + iaf, maxaf)
                    if high[i - 1] > psar[i]:
                        psar[i] = high[i - 1]
                    if high[i - 2] > psar[i]:
                        psar[i] = high[i - 2]
        return psar
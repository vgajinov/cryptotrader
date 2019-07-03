import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class ChaikinOscillator(Indicator):
    """On Balance Volume indicator"""
    chart = None

    def __init__(self):
        super().__init__()
        self.oscillator = QtChart.QLineSeries()
        self.oscillator.setColor(QtCore.Qt.red)
        self.addSeries(self.oscillator)


    def updateIndicator(self, data, candles_visible):
        # ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
        chaikin_oscillator = talib.ADOSC(data[2], data[3], data[4], data[5], fastperiod=3, slowperiod=10)
        chaikin_oscillator = chaikin_oscillator[-candles_visible:]

        self.oscillator.clear()
        for i in range(candles_visible):
            self.oscillator.append(i + 0.5, chaikin_oscillator[i])

        # detach and remove old axes
        for ax in self.oscillator.attachedAxes():
            self.oscillator.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # candle_set hidden x axis
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # candle_set y price delta axis
        ay = QtChart.QValueAxis()
        bound = max(abs(min(chaikin_oscillator)), max(chaikin_oscillator))
        ay.setRange(-bound, bound)
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.oscillator.attachAxis(ax)
        self.oscillator.attachAxis(ay)



import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class ChaikinMoneyFlow(Indicator):
    """On Balance Volume indicator"""
    chart = None

    def __init__(self):
        super().__init__()
        self.moneyFlow = QtChart.QLineSeries()
        self.moneyFlow.setColor(QtCore.Qt.red)
        self.addSeries(self.moneyFlow)


    def updateIndicator(self, data, candles_visible):
        """
        The calculation for Chaikin Money Flow (CMF) has three distinct steps
        (for this example we will use a 21 Period CMF):
        1. Find the Money Flow Multiplier
           [(Close  -  Low) - (High - Close)] /(High - Low) = Money Flow Multiplier
        2. Calculate Money Flow Volume
           Money Flow Multiplier x Volume for the Period = Money Flow Volume
        3. Calculate The CMF
           21 Period Sum of Money Flow Volume / 21 Period Sum of Volume = 21 Period CMF

        """
        volume = data[5]
        # 1. Find the Money Flow Multiplier
        mf = ((data[4] - data[3]) - (data[2] - data[4])) / (data[2] - data[3])
        # 2. Calculate Money Flow Volume
        mf_volume = mf * data[5]
        # use auxiliary numpy arrays for period window accumulation (21 in this case)
        mf_period = np.zeros(np.shape(mf_volume))
        volume_period = np.zeros(np.shape(mf_volume))
        # set all elements at the beginning of the arrays to the first period accumulation
        mf_period[0:21] = np.sum(mf_volume[0:21])
        volume_period[0:21] = np.sum(volume[0:21])
        # find all other accumulation using the rolling window approach to reduce the number of operations
        for i in range(21, len(mf_volume)):
            mf_period[i] = mf_period[i-1] - mf_volume[i-21] + mf_volume[i]
            volume_period[i] = volume_period[i - 1] - volume[i - 21] + volume[i]
        # 3. Calculate The CMF
        cmf = mf_period / volume_period
        cmf = cmf[-candles_visible:]

        self.moneyFlow.clear()
        for i in range(candles_visible):
            self.moneyFlow.append(i + 0.5, cmf[i])

        # detach and remove old axes
        for ax in self.moneyFlow.attachedAxes():
            self.moneyFlow.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # candle_set hidden x axis
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # candle_set y price delta axis
        ay = QtChart.QValueAxis()
        bound = max(abs(min(cmf)), max(cmf))
        ay.setRange(-bound, bound)
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.moneyFlow.attachAxis(ax)
        self.moneyFlow.attachAxis(ay)



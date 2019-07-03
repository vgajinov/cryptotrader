import talib
import numpy as np
from PyQt5 import QtCore, QtGui, QtChart
from gui.indicators.base import Indicator


class PPO_PercentagePriceOscillator(Indicator):
    """PPO - Percentage Price Oscillator"""

    def __init__(self):
        super().__init__()
        self.line = QtChart.QLineSeries()
        self.line.setColor(QtCore.Qt.green)
        self.addSeries(self.line)


    def updateIndicator(self, data, candles_visible):
        # PPO(close, fastperiod=12, slowperiod=26, matype=0)
        ppo = talib.PPO(data[4], fastperiod=12, slowperiod=26, matype=0)
        try:
            firstNotNan = np.where(np.isnan(ppo))[0][-1] + 1
        except:
            firstNotNan = 0
        ppo[:firstNotNan] = ppo[firstNotNan]
        ppo = np.round(100 * ppo, 2)
        ppo = ppo[-candles_visible:]

        self.line.clear()
        for i in range(candles_visible):
            self.line.append(i + 0.5, ppo[i])

        # detach and remove old axes
        for ax in self.line.attachedAxes():
            self.line.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # set x axes
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # set y axes
        ay = QtChart.QValueAxis()
        bound = max(abs(min(ppo)), max(ppo))
        ay.setRange(-bound, bound)
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.line.attachAxis(ax)
        self.line.attachAxis(ay)






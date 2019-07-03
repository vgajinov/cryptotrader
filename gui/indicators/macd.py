import talib
from .base import *


# ------------------------------------------------------------------------------------
# MACD
# ------------------------------------------------------------------------------------

class MACD(Indicator):
    def __init__(self):
        super().__init__()
        self.macdBars = QtChart.QCandlestickSeries()
        self.macdBars.setIncreasingColor(QtCore.Qt.black)
        self.macdBars.setDecreasingColor(QtCore.Qt.red)
        self.macdBars.setBodyWidth(0.7)
        self.macdLine   = QtChart.QLineSeries()
        self.macdLine.setColor(QtCore.Qt.yellow)
        self.macdSignal = QtChart.QLineSeries()
        self.macdSignal.setColor(QtCore.Qt.blue)
        self.addSeries(self.macdBars)
        self.addSeries(self.macdLine)
        self.addSeries(self.macdSignal)
        self.IndicatorName.setText('MACD')


    def updateIndicator(self, data, candles_visible):
        close  = data[4]
        macd_line, macd_signal, macd_bars = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        macd_line = macd_line[-candles_visible:]
        macd_signal = macd_signal[-candles_visible:]
        macd_bars = macd_bars[-candles_visible:]

        # clear old data
        self.macdLine.clear()
        self.macdSignal.clear()
        if self.macdBars.count() > 0:
            self.macdBars.remove(self.macdBars.sets())

        # add new macd bar data
        for i, bar in enumerate(macd_bars):
            if bar > 0:
                candle_set = QtChart.QCandlestickSet(0, bar, 0, bar, timestamp=i)
                candle_set.setPen(QtGui.QPen(QtCore.Qt.green, 1))
                candle_set.setBrush(QtGui.QBrush(QtCore.Qt.black))
            else:
                candle_set = QtChart.QCandlestickSet(0, 0, bar, bar, timestamp=i)
                candle_set.setPen(QtGui.QPen(QtCore.Qt.red, 1))
                candle_set.setBrush(QtGui.QBrush(QtCore.Qt.red))
            self.macdBars.append(candle_set)

        # add new macd line and signal data
        for i in range(candles_visible):
            self.macdLine.append(i + 0.5, macd_line[i])
            self.macdSignal.append(i + 0.5, macd_signal[i])

        # detach and remove old axes
        for ax in self.macdLine.attachedAxes():
            self.macdLine.detachAxis(ax)
        for ax in self.macdSignal.attachedAxes():
            self.macdSignal.detachAxis(ax)
        for ax in self.macdBars.attachedAxes():
            self.macdBars.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # candle_set hidden x axis
        ax = QtChart.QValueAxis()
        ax.setRange(0, candles_visible)
        ax.hide()

        # candle_set y price delta axis
        ay = QtChart.QValueAxis()
        bound = max(abs(min(macd_line)), abs(max(macd_line)))
        ay.setRange(-bound, bound)
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.setLabelFormat("%-6.2f")
        ay.applyNiceNumbers()
        ay.setTickCount(3)

        # candle_set hidden x axis for macd bars
        ac = QtChart.QBarCategoryAxis()
        ac.append([str(x) for x in range(candles_visible)])
        ac.hide()

        # add and attach new axes
        self.addAxis(ax, QtCore.Qt.AlignBottom)
        self.addAxis(ac, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.macdLine.attachAxis(ax)
        self.macdLine.attachAxis(ay)
        self.macdSignal.attachAxis(ax)
        self.macdSignal.attachAxis(ay)
        self.macdBars.attachAxis(ac)
        self.macdBars.attachAxis(ay)





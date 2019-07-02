from abc import ABC, abstractmethod
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import talib
from .Separators import *


# ------------------------------------------------------------------------------------
# Indicator Factory
# ------------------------------------------------------------------------------------

class IndicatorFactory(object):
    indicators = None

    @staticmethod
    def createIndicator(name):
        if not IndicatorFactory.indicators:
            IndicatorFactory.indicators = {}
            for ind in Indicator.__subclasses__():
                IndicatorFactory.indicators[ind.__name__] = ind
        if name in IndicatorFactory.indicators.keys():
            return IndicatorFactory.indicators[name]()
        else:
            print('Indicator not defined')

    @staticmethod
    def getIndicatorNames():
        if not IndicatorFactory.indicators:
            IndicatorFactory.indicators = {}
            for ind in Indicator.__subclasses__():
                IndicatorFactory.indicators[ind.__name__] = ind
        return sorted(list(IndicatorFactory.indicators.keys()))


# ------------------------------------------------------------------------------------
# Indicator base class
# ------------------------------------------------------------------------------------

class Indicator(QtChart.QChart):
    frame = None

    def __init__(self):
        super(Indicator, self).__init__()
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        self.setBackgroundRoundness(0)
        self.setMargins(QtCore.QMargins(0, 0, 0, 0))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.legend().hide()
        chartFont = QtGui.QFont(self.font())
        chartFont.setPixelSize(9)
        self.setFont(chartFont)

        self.IndicatorName = QtWidgets.QGraphicsSimpleTextItem(self)
        self.IndicatorName.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.IndicatorName.setOpacity(1.0)
        self.IndicatorName.setPos(0, 0)

        indView = QtChart.QChartView(self)
        indView.setRenderHint(QtGui.QPainter.Antialiasing)

        indLayout = QtWidgets.QVBoxLayout()
        indLayout.setSpacing(0)
        indLayout.setContentsMargins(0, 0, 0, 0)
        indLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                                spacecolor='rgb(0,0,0)', stroke=1, width=3))
        indLayout.addWidget(indView)

        self.frame = QtWidgets.QFrame()
        self.frame.setLayout(indLayout)


    @abstractmethod
    def updateIndicator(self, data, N):
        pass

    def clear(self):
        for ser in self.series():
            ser.clear()


# ------------------------------------------------------------------------------------
# Volume
# ------------------------------------------------------------------------------------

class Volume(Indicator):
    def __init__(self):
        super(Volume, self).__init__()
        self.volumeBars = QtChart.QCandlestickSeries()
        self.volumeBars.setIncreasingColor(QtCore.Qt.black)
        self.volumeBars.setDecreasingColor(QtCore.Qt.red)
        self.volumeBars.setBodyWidth(0.7)
        self.addSeries(self.volumeBars)
        self.IndicatorName.setText('Volume')

    def updateIndicator(self, data, N):
        open   = data[1,-N:].tolist()
        close  = data[4,-N:].tolist()
        volume = data[5,-N:].tolist()

        # remove old set
        if self.volumeBars.count() > 0:
            self.volumeBars.remove(self.volumeBars.sets())

        # add new volume bar data
        for i, val in enumerate(volume):
            set = None
            if close[i] > open[i]:
                set = QtChart.QCandlestickSet(0, val, 0, val, timestamp=i)
                set.setPen(QtGui.QPen(QtCore.Qt.green, 1))
                set.setBrush(QtGui.QBrush(QtCore.Qt.black))
            else:
                set = QtChart.QCandlestickSet(val, val, 0, 0, timestamp=i)
                set.setPen(QtGui.QPen(QtCore.Qt.red, 1))
                set.setBrush(QtGui.QBrush(QtCore.Qt.red))
            self.volumeBars.append(set)

        # detach and remove old axes
        for ax in self.volumeBars.attachedAxes():
            self.volumeBars.detachAxis(ax)
        for ax in self.axes():
            self.removeAxis(ax)

        # set hidden x axis for volume bars
        ac = QtChart.QBarCategoryAxis()
        ac.append( [str(x) for x in range(len(volume))] )
        ac.hide()

        # set y volume axis
        ay = QtChart.QValueAxis()
        ay.setRange(0, max(volume))
        ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
        ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
        ay.setLabelFormat("%-6.2f")
        ay.applyNiceNumbers()
        ay.setTickCount(2)

        # add and attach new axes
        self.addAxis(ac, QtCore.Qt.AlignBottom)
        self.addAxis(ay, QtCore.Qt.AlignRight)
        self.volumeBars.attachAxis(ac)
        self.volumeBars.attachAxis(ay)


# ------------------------------------------------------------------------------------
# MACD
# ------------------------------------------------------------------------------------

class MACD(Indicator):
    def __init__(self):
        super(MACD, self).__init__()
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


    def updateIndicator(self, data, N):
        close  = data[4]
        macd_line, macd_signal, macd_bars = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        macd_line = macd_line[-N:]
        macd_signal = macd_signal[-N:]
        macd_bars = macd_bars[-N:]

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
        for i in range(N):
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
        ax.setRange(0,N)
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
        ac.append( [str(x) for x in range(N)] )
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





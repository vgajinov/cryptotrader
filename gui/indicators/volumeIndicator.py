from .base import *


class Volume(Indicator):
    """Volume"""

    def __init__(self):
        super(Volume, self).__init__()
        self.volumeBars = QtChart.QCandlestickSeries()
        self.volumeBars.setIncreasingColor(QtCore.Qt.black)
        self.volumeBars.setDecreasingColor(QtCore.Qt.red)
        self.volumeBars.setBodyWidth(0.7)
        self.addSeries(self.volumeBars)
        self.IndicatorName.setText('Volume')

    def updateIndicator(self, data, candles_visible):
        open   = data[1, -candles_visible:].tolist()
        close  = data[4, -candles_visible:].tolist()
        volume = data[5, -candles_visible:].tolist()

        # remove old set
        if self.volumeBars.count() > 0:
            self.volumeBars.remove(self.volumeBars.sets())

        # add new volume bar data
        for i, val in enumerate(volume):
            if close[i] > open[i]:
                candle_set = QtChart.QCandlestickSet(0, val, 0, val, timestamp=i)
                candle_set.setPen(QtGui.QPen(QtCore.Qt.green, 1))
                candle_set.setBrush(QtGui.QBrush(QtCore.Qt.black))
            else:
                candle_set = QtChart.QCandlestickSet(val, val, 0, 0, timestamp=i)
                candle_set.setPen(QtGui.QPen(QtCore.Qt.red, 1))
                candle_set.setBrush(QtGui.QBrush(QtCore.Qt.red))
            self.volumeBars.append(candle_set)

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
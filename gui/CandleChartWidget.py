import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
from .CandleChart import CandleChart
from .overlays.factory import OverlayFactory
from .indicators.factory import IndicatorFactory
from .Separators import *


class CandleChartWidget(QtWidgets.QWidget):
    """The widget for displaying candle chart."""
    data = None
    numCandlesVisible = 50
    minCandlesVisible = 20
    maxCandlesVisible = 200
    overlays = {}
    indicators = {}

    def __init__(self):
        super(CandleChartWidget, self).__init__()

        self.setContentsMargins(0, 0, 0, 0)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.candleGraph = CandleChart()
        chartView = QtChart.QChartView(self.candleGraph)
        chartView.setRenderHint(QtGui.QPainter.Antialiasing)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(chartView, stretch=4)


    # ------------------------------------------------------------------------------------
    # Overlays
    # ------------------------------------------------------------------------------------

    def addOverlay(self, name):
        """Adds an overlay to the candle chart
        :param name:  the name of an overlay to add
        """
        new_overlay = OverlayFactory.create_overlay(name)
        new_overlay.addToChart(self.candleGraph)
        self.overlays[name] = new_overlay
        self.updateChart()

    def removeOverlay(self, name):
        """Removes an overlay to the candle chart
        :param name:  the name of an overlay to remove
        """
        self.overlays[name].removeFromChart()
        self.overlays.pop(name)


    # ------------------------------------------------------------------------------------
    # Indicators
    # ------------------------------------------------------------------------------------

    def addIndicator(self, name):
        """Adds an indicator bellow the candle chart
        :param name:  the name of an indicator to add
        """
        new_indicator = IndicatorFactory.create_indicator(name)
        self.mainLayout.addWidget(new_indicator.frame, stretch=1)
        self.indicators[name] = (new_indicator.frame, new_indicator)


    def showIndicator(self, name):
        """Displays an indicator bellow the candle chart
        :param name:  the name of an indicator
        """
        try:
            self.indicators[name][0].show()
        except KeyError:
            self.addIndicator(name)
        self.updateChart()


    def hideIndicator(self, name):
        """Hides an indicator.
        :param name:  the name of an indicator
        """
        try:
            self.indicators[name][0].hide()
        except KeyError:
            pass


    # ------------------------------------------------------------------------------------
    # Update methods
    # ------------------------------------------------------------------------------------

    def setData(self, data):
        """Sets/updates the candle values.
        :param data    candles snapshot or and update
        Data is one of the (type, data) tuples:
            ('snapshot', list(candles))    data is a a complete snapshot
            ('add', candle)                data is a new candle
            ('update', candle)             data is an update of the last candle
        """
        if not data:
            return
        elif data[0] == 'snapshot':
            self.data = np.transpose(np.array(data[1]))
        elif data[0] == 'add':
            self.data = np.c_[self.data, data[1]]
        elif data[0] == 'update':
            self.data[:, -1] = data[1]
        else:
            pass


    def updateChart(self):
        """Updates the candle chart display"""
        if self.data is None:
            return
        self.candleGraph.updateCandleChart(self.data, self.numCandlesVisible)
        for overlay in self.overlays.values():
            overlay.update(self.data, self.numCandlesVisible)
        for indicator in self.indicators.values():
            if indicator[0].isVisible:
                indicator[1].updateIndicator(self.data, self.numCandlesVisible)


    def reset(self):
        """Clears the candle chart and displayed overlays and indicators"""
        for overlay in self.overlays.values():
            overlay.clear()
        for indicator in self.indicators.values():
            indicator[1].clear()
        self.candleGraph.clear()


    # ------------------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------------------

    def wheelEvent(self, QWheelEvent):
        """handle mouse wheel event for zooming in and out.
        :param QWheelEvent:  mouse wheel event
        """
        if QWheelEvent.angleDelta().y() < 0:
            # wheel down - zoom out
            self.numCandlesVisible = min(self.numCandlesVisible + 10, self.maxCandlesVisible)
        else:
            # wheel up - zoom in
            self.numCandlesVisible = max(self.numCandlesVisible - 10, self.minCandlesVisible)
        self.updateChart()














from abc import ABC, abstractmethod
from PyQt5 import QtCore, QtGui, QtChart
from ..Separators import *


# ------------------------------------------------------------------------------------
# Indicator base class
# ------------------------------------------------------------------------------------

class Indicator(QtChart.QChart):
    """A base class for indicators.
    Indicators are displayed bellow the main candle chart.
    This base class provides the display framework for all indicators.
    """
    frame = None

    def __init__(self):
        super().__init__()
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

        indicatorView = QtChart.QChartView(self)
        indicatorView.setRenderHint(QtGui.QPainter.Antialiasing)

        indicatorLayout = QtWidgets.QVBoxLayout()
        indicatorLayout.setSpacing(0)
        indicatorLayout.setContentsMargins(0, 0, 0, 0)
        indicatorLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                                      spacecolor='rgb(0,0,0)', stroke=1, width=3))
        indicatorLayout.addWidget(indicatorView)

        self.frame = QtWidgets.QFrame()
        self.frame.setLayout(indicatorLayout)

#    @abstractmethod
#    def name(self):
#        """Then name of the indicator."""
#        pass

    @abstractmethod
    def updateIndicator(self, data, candles_visible):
        """Updates the indicator with latest candle data.
        :param data:             candles values
        :param candles_visible:  the number of displayed candles on the main candle chart
        """
        pass

    def clear(self):
        """Clears the indicator values."""
        for series in self.series():
            series.clear()

from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import numpy as np
from .CandleChart import CandleChart
from .Indicators import Indicator
from .Separators import *


class ChartWidget(QtWidgets.QWidget):
   data = None
   numCandlesVisible = 50
   minCandlesVisible = 20
   maxCandlesVisible = 200
   indicators = {}

   def __init__(self):
      super(ChartWidget, self).__init__()

      self.setContentsMargins(0,0,0,0)
      palette = QtGui.QPalette()
      palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
      self.setAutoFillBackground(True)
      self.setPalette(palette)

      self.candleGraph = CandleChart()
      chartView = QtChart.QChartView(self.candleGraph)
      chartView.setRenderHint(QtGui.QPainter.Antialiasing)

      self.mainLayout = QtWidgets.QVBoxLayout(self)
      self.mainLayout.setSpacing(0)
      self.mainLayout.setContentsMargins(0,0,0,0)
      self.mainLayout.addWidget(chartView, stretch=4)



   def addIndicator(self, name):
      newIndicator = Indicator()
      newIndicator.setIndicator(name)
      indView = QtChart.QChartView(newIndicator)
      indView.setRenderHint(QtGui.QPainter.Antialiasing)

      indFrame = QtWidgets.QFrame()
      indLayout = QtWidgets.QVBoxLayout()
      indLayout.setSpacing(0)
      indLayout.setContentsMargins(0,0,0,0)
      indFrame.setLayout(indLayout)
      indLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                              spacecolor='rgb(0,0,0)', stroke=1, width=3))
      indLayout.addWidget(indView)
      self.mainLayout.addWidget(indFrame, stretch=1)
      self.indicators[name] = (indFrame, newIndicator)


   def showIndicator(self, name):
      try:
         self.indicators[name.lower()][0].show()
      except:
         self.addIndicator(name.lower())


   def hideIndicator(self, name):
      try:
         self.indicators[name.lower()][0].hide()
      except:
         pass


   def setData(self, data):
      self.data = data


   def updateChart(self):
      data = self.data[-self.numCandlesVisible:]
      timestamp = [x[0] for x in data]
      open      = [x[1] for x in data]
      high      = [x[2] for x in data]
      low       = [x[3] for x in data]
      close     = [x[4] for x in data]
      volume    = [x[5] for x in data]
      self.candleGraph.updateCandleChart(timestamp, open, high, low, close)
      self.candleGraph.updateOverlays(open, high, low, close)

      # update indicators
      for name, indicator in self.indicators.items():
         if name == 'volume':
            indicator[1].updateIndicator(open, close, volume)
         if name == 'macd':
            indicator[1].updateIndicator(None, [x[4] for x in self.data], None, self.numCandlesVisible)


   # handle mouse wheel event for zooming
   def wheelEvent(self, QWheelEvent):
      if QWheelEvent.angleDelta().y() < 0:
         # wheel down - zoom out
         self.numCandlesVisible = min(self.numCandlesVisible + 10, self.maxCandlesVisible)
      else:
         # wheel up - zoom in
         self.numCandlesVisible = max(self.numCandlesVisible - 10, self.minCandlesVisible)
      self.updateChart()














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

      self.mainLayout = QtWidgets.QVBoxLayout(self)
      self.mainLayout.setSpacing(0)
      self.mainLayout.setContentsMargins(0,0,0,0)

      self.candleGraph = CandleChart()
      chartView = QtChart.QChartView(self.candleGraph)
      chartView.setRenderHint(QtGui.QPainter.Antialiasing)

      # self.volume = Indicator()
      # self.volume.setIndicator('volume')
      # volumeView = QtChart.QChartView(self.volume)
      # volumeView.setRenderHint(QtGui.QPainter.Antialiasing)
      #
      # self.macd = Indicator()
      # self.macd.setIndicator('macd')
      # macdView = QtChart.QChartView(self.macd)
      # macdView.setRenderHint(QtGui.QPainter.Antialiasing)

      self.mainLayout.addWidget(chartView, stretch=4)
      # self.mainLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
      #                                               spacecolor='rgb(0,0,0)', stroke=1, width=3))
      # self.mainLayout.addWidget(volumeView, stretch=1)
      # self.mainLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
      #                                               spacecolor='rgb(0,0,0)', stroke=1, width=3))
      # self.mainLayout.addWidget(macdView, stretch=1)


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
      indLayout.addWidget(newIndicator)
      self.mainLayout.addWidget(self.macdFrame, stretch=1)
      self.indicators[name] = (indFrame, newIndicator)


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
      # self.volume.updateIndicator(open, close, volume)
      # # we need entire list of close prices for MACD
      # self.macd.updateIndicator(None, [x[4] for x in self.data], None, self.numCandlesVisible)

      for name, indicator in self.indicators:
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




   def showIndicator(self, name):
      try:
         self.indicators[name.lower()][0].show()
      except:
         self.addIndicator(name.lower())

      # if name == 'MACD':
      #    try:
      #       self.macd.show()
      #    except AttributeError:
      #       self.addIndicator('macd')
      # if name == 'Volume':
      #    try:
      #       self.volume.show()
      #    except AttributeError:
      #       self.addIndicator('volume')


   def hideIndicator(self, name):
      try:
         self.indicators[name.lower()][0].hide()
      except:
         pass
      # if name == 'MACD':
      #    self.indicators[name][0].hide()
      # if name == 'RSA':
      #    self.volume.hide()



























#
#
# class ChartWidget(QtWidgets.QWidget):
#
#    def addMACD(self):
#       self.macdChart = pg.PlotWidget()
#       x = np.sin(np.linspace(0, 2 * np.pi, 1000))
#       self.macdChart.plot(x)
#
#       self.macdFrame = QtWidgets.QFrame()
#       self.macdLayout = QtWidgets.QVBoxLayout()
#       self.macdLayout.setSpacing(0)
#       self.macdLayout.setContentsMargins(0,0,0,0)
#       self.macdFrame.setLayout(self.macdLayout)
#       self.macdLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
#                                                     spacecolor='rgb(0,0,0)', stroke=1, width=3))
#       self.macdLayout.addWidget(self.macdChart)
#
#       self.mainLayout.addWidget(self.macdFrame, stretch=1)
#
#    def addRSA(self):
#       self.rsaChart = pg.PlotWidget()
#       x = np.cos(np.linspace(0, 2 * np.pi, 1000))
#       self.rsaChart.plot(x)
#
#       self.rsaFrame = QtWidgets.QFrame()
#       self.rsaLayout = QtWidgets.QVBoxLayout()
#       self.rsaLayout.setSpacing(0)
#       self.rsaLayout.setContentsMargins(0,0,0,0)
#       self.rsaFrame.setLayout(self.rsaLayout)
#       self.rsaLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
#                                                    spacecolor='rgb(0,0,0)', stroke=1, width=3))
#       self.rsaLayout.addWidget(self.rsaChart)
#
#       self.mainLayout.addWidget(self.rsaFrame, stretch=1)
#
#
#    def showIndicator(self, name):
#       if name == 'MACD':
#          try:
#             self.macdFrame.show()
#          except AttributeError:
#             self.addMACD()
#       if name == 'RSA':
#          try:
#             self.rsaFrame.show()
#          except AttributeError:
#             self.addRSA()
#
#
#    def hideIndicator(self, name):
#       if name == 'MACD':
#          self.macdFrame.hide()
#       if name == 'RSA':
#          self.rsaFrame.hide()
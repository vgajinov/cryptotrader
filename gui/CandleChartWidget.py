from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import numpy as np
from .CandleChart import CandleChart
from .Overlays   import *
from .Indicators import *
from .Separators import *


class CandleChartWidget(QtWidgets.QWidget):
   data = None
   numCandlesVisible = 50
   minCandlesVisible = 20
   maxCandlesVisible = 200
   overlays = {}
   indicators = {}

   def __init__(self):
      super(CandleChartWidget, self).__init__()

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


   def addOverlay(self, name):
      newOverlay = OverlayFactory.createOverlay(name)
      newOverlay.addToChart(self.candleGraph)
      self.overlays[name] = newOverlay
      self.updateChart()

   def removeOverlay(self, name):
      self.overlays[name].removeFromChart(self.candleGraph)
      self.overlays.pop(name)


   def addIndicator(self, name):
      newIndicator = IndicatorFactory.createIndicator(name)
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
         self.indicators[name][0].show()
      except:
         self.addIndicator(name)
      self.updateChart()


   def hideIndicator(self, name):
      try:
         self.indicators[name][0].hide()
      except:
         pass


   def setData(self, data):
      self.data = np.transpose(np.array(data))


   def updateChart(self):
      if self.data is None:
         return
      self.candleGraph.updateCandleChart(self.data, self.numCandlesVisible)
      for overlay in self.overlays.values():
         overlay.update(self.data, self.numCandlesVisible, self.candleGraph)
      for indicator in self.indicators.values():
         if indicator[0].isVisible:
            indicator[1].updateIndicator(self.data, self.numCandlesVisible)


   def reset(self):
      for overlay in self.overlays.values():
         overlay.clear()
      for indicator in self.indicators.values():
         indicator[1].clear()
      self.candleGraph.clear()

   # ------------------------------------------------------------------------------------
   # Event handlers
   # ------------------------------------------------------------------------------------

   # handle mouse wheel event for zooming
   def wheelEvent(self, QWheelEvent):
      if QWheelEvent.angleDelta().y() < 0:
         # wheel down - zoom out
         self.numCandlesVisible = min(self.numCandlesVisible + 10, self.maxCandlesVisible)
      else:
         # wheel up - zoom in
         self.numCandlesVisible = max(self.numCandlesVisible - 10, self.minCandlesVisible)
      self.updateChart()














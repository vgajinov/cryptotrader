import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
import pyqtgraph as pg
from .Separators import *



class ChartWidget(QtWidgets.QWidget):
   def __init__(self):
      super(ChartWidget, self).__init__()

      self.mainLayout = QtWidgets.QVBoxLayout(self)
      #self.mainLayout.setMargin(0)
      self.mainLayout.setContentsMargins(0,0,0,0)
      self.mainLayout.setSpacing(0)

      candleChart = pg.PlotWidget()
      x = np.cos(np.linspace(0, 2 * np.pi, 1000))
      y = np.sin(np.linspace(0, 4 * np.pi, 1000))
      candleChart.plot(x, y)
      candleChart.showGrid(x=True, y=True)

      self.mainLayout.addWidget(candleChart, stretch=4)

   def addMACD(self):
      self.macdChart = pg.PlotWidget()
      x = np.sin(np.linspace(0, 2 * np.pi, 1000))
      self.macdChart.plot(x)

      self.macdFrame = QtWidgets.QFrame()
      self.macdLayout = QtWidgets.QVBoxLayout()
      self.macdLayout.setSpacing(0)
      self.macdLayout.setContentsMargins(0,0,0,0)
      self.macdFrame.setLayout(self.macdLayout)
      self.macdLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                                    spacecolor='rgb(0,0,0)', stroke=1, width=3))
      self.macdLayout.addWidget(self.macdChart)

      self.mainLayout.addWidget(self.macdFrame, stretch=1)

   def addRSA(self):
      self.rsaChart = pg.PlotWidget()
      x = np.cos(np.linspace(0, 2 * np.pi, 1000))
      self.rsaChart.plot(x)

      self.rsaFrame = QtWidgets.QFrame()
      self.rsaLayout = QtWidgets.QVBoxLayout()
      self.rsaLayout.setSpacing(0)
      self.rsaLayout.setContentsMargins(0,0,0,0)
      self.rsaFrame.setLayout(self.rsaLayout)
      self.rsaLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                                   spacecolor='rgb(0,0,0)', stroke=1, width=3))
      self.rsaLayout.addWidget(self.rsaChart)

      self.mainLayout.addWidget(self.rsaFrame, stretch=1)


   def showIndicator(self, name):
      if name == 'MACD':
         try:
            self.macdFrame.show()
         except AttributeError:
            self.addMACD()
      if name == 'RSA':
         try:
            self.rsaFrame.show()
         except AttributeError:
            self.addRSA()


   def hideIndicator(self, name):
      if name == 'MACD':
         self.macdFrame.hide()
      if name == 'RSA':
         self.rsaFrame.hide()
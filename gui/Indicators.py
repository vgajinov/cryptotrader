from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import numpy as np



# INDICATORS
#=======================================================================================

class Indicator(QtChart.QChart):
   type = None
   types = ['volume', 'macd']

   def __init__(self):
      super(Indicator, self).__init__()
      self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
      self.setBackgroundRoundness(0)
      self.setMargins(QtCore.QMargins(0, 0, 0, 0))
      self.layout().setContentsMargins(0, 0, 0, 0);
      self.setContentsMargins(0, 0, 0, 0);
      self.legend().hide()
      chartFont = QtGui.QFont(self.font())
      chartFont.setPixelSize(9)
      self.setFont(chartFont)

      self.IndicatorName = QtWidgets.QGraphicsSimpleTextItem(self)
      self.IndicatorName.setBrush(QtGui.QBrush(QtGui.QColor(255,255,255)))
      self.IndicatorName.setOpacity(1.0)
      self.IndicatorName.setPos(0,0)



   def setIndicator(self, type):
      if type not in self.types:
         return
      if type == 'volume':
         self.setVolume()
      if type == 'macd':
         self.setMACD()
      self.type = type


   def updateIndicator(self, open, close, volume, N=-1):
      if self.type == 'volume':
         self.updateVolume(open, close, volume)
      if self.type == 'macd':
         self.updateMACD(close, N)

   def setVolume(self):
      self.volumeBars = QtChart.QCandlestickSeries()
      self.volumeBars.setIncreasingColor(QtCore.Qt.black)
      self.volumeBars.setDecreasingColor(QtCore.Qt.red)
      self.volumeBars.setBodyWidth(0.7)
      self.addSeries(self.volumeBars)
      self.IndicatorName.setText('Volume')

   def updateVolume(self, open, close, volume):
      ''' data is a tuple of lists (open, close, volume)'''

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


   def setMACD(self):
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


   def updateMACD(self, data, N):
      ''' data is a list of close prices'''
      macdLine, macdSignal, macdBars = self.macd(data)[-N-26:]  # assuming p2=26
      macdLine = macdLine[-N:]
      macdSignal = macdSignal[-N:]
      macdBars = macdBars[-N:]

      # clear old data
      self.macdLine.clear()
      self.macdSignal.clear()
      if self.macdBars.count() > 0:
         self.macdBars.remove(self.macdBars.sets())

      # add new macd bar data
      for i, bar in enumerate(macdBars):
         set = None
         if bar > 0:
            set = QtChart.QCandlestickSet(0, bar, 0, bar, timestamp=i)
            set.setPen(QtGui.QPen(QtCore.Qt.green, 1))
            set.setBrush(QtGui.QBrush(QtCore.Qt.black))
         else:
            set = QtChart.QCandlestickSet(0, 0, bar, bar, timestamp=i)
            set.setPen(QtGui.QPen(QtCore.Qt.red, 1))
            set.setBrush(QtGui.QBrush(QtCore.Qt.red))
         self.macdBars.append(set)

      # add new macd line and signal data
      for i in range(N):
         self.macdLine.append(i + 0.5, macdLine[i])
         self.macdSignal.append(i + 0.5, macdSignal[i])

      # detach and remove old axes
      for ax in self.macdLine.attachedAxes():
         self.macdLine.detachAxis(ax)
      for ax in self.macdSignal.attachedAxes():
         self.macdSignal.detachAxis(ax)
      for ax in self.macdBars.attachedAxes():
         self.macdBars.detachAxis(ax)
      for ax in self.axes():
         self.removeAxis(ax)

      # set hidden x axis
      ax = QtChart.QValueAxis()
      ax.setRange(0,N)
      ax.hide()

      # set y price delta axis
      ay = QtChart.QValueAxis()
      bound = max(abs(min(macdLine)), abs(max(macdLine)))
      ay.setRange(-bound, bound)
      ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
      ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      ay.setLabelFormat("%-6.2f")
      ay.applyNiceNumbers()
      ay.setTickCount(3)

      # set hidden x axis for macd bars
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


   def sma(self, data, N):
      cumsum, sma = [0], []
      for i, x in enumerate(data, 1):
         cumsum.append(cumsum[i - 1] + x)
         if i >= N:
            sma.append((cumsum[i] - cumsum[i - N]) / N)
      return sma

   def ema(self, data, N):
      c = 2.0 / (N + 1)
      ema = [sum(data[:N])/N]  # self.sma(data, N)
      for val in data[N:]:
         ema.append( (c * val) + ((1-c) * ema[-1]) )
      return ema

   def macd(self, data, p1=12, p2=26, ps=9):
      me1 = self.ema(data, p1)
      me2 = self.ema(data, p2)
      me1 = me1[-len(me2):]
      macdLine   = [me1[i] - me2[i] for i in range(len(me2))]
      macdSignal = self.ema(macdLine, ps)
      macdLine = macdLine[-len(macdSignal):]
      macdBars   = [macdLine[i] - macdSignal[i] for i in range(len(macdSignal))]
      return macdLine, macdSignal, macdBars



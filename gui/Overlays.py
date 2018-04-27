from abc import ABC, abstractmethod
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
from .CandleChart import CandleChart
import talib
import numpy as np



# ------------------------------------------------------------------------------------
# Overlay Factory
# ------------------------------------------------------------------------------------

class OverlayFactory(object):
   overlays = None

   @staticmethod
   def createOverlay(name):
      if not OverlayFactory.overlays:
         OverlayFactory.overlays = {}
         for ind in Overlay.__subclasses__():
            OverlayFactory.overlays[ind.__name__] = ind
      if name in OverlayFactory.overlays.keys():
         return OverlayFactory.overlays[name]()
      else:
         print('Indicator not defined')

   @staticmethod
   def getOverlayNames():
      if not OverlayFactory.overlays:
         OverlayFactory.overlays = {}
         for ind in Overlay.__subclasses__():
            OverlayFactory.overlays[ind.__name__] = ind
      return sorted(list(OverlayFactory.overlays.keys()))


# ------------------------------------------------------------------------------------
# Overlay base class
# ------------------------------------------------------------------------------------

class Overlay():
   @abstractmethod
   def addToChart(self, chart : QtChart.QChart):
      pass

   @abstractmethod
   def removeFromChart(self, chart : QtChart.QChart):
      pass

   @abstractmethod
   def update(self, data, N):
      pass

   @abstractmethod
   def clear(self):
      pass




# ------------------------------------------------------------------------------------
# SMA - Simple Moving Average
# ------------------------------------------------------------------------------------

class SMA(Overlay):
   def __init__(self):
      self.series15 = QtChart.QSplineSeries()
      self.series50 = QtChart.QSplineSeries()
      pen = QtGui.QPen(QtCore.Qt.SolidLine)
      pen.setWidth(0.5)
      pen.setColor(QtGui.QColor(255,255,0))
      self.series15.setPen(pen)
      pen.setColor(QtGui.QColor(255, 0, 255))
      self.series50.setPen(pen)


   def addToChart(self, chart : QtChart.QChart):
      chart.addSeries(self.series15)
      chart.addSeries(self.series50)

   def removeFromChart(self, chart : QtChart.QChart):
      chart.removeSeries(self.series15)
      chart.removeSeries(self.series50)

   def update(self, data, N, chart : CandleChart):
      close = data[4]
      self.clear()
      self.series15.attachAxis(chart.ax)
      self.series15.attachAxis(chart.ay)
      self.series50.attachAxis(chart.ax)
      self.series50.attachAxis(chart.ay)

      sma15 = talib.SMA(close, timeperiod=15)
      firstNotNan = np.where(np.isnan(sma15))[0][-1] + 1
      sma15[:firstNotNan] = sma15[firstNotNan]
      for i, val in enumerate(sma15[-N:]):
         self.series15.append(i + 0.5, val)

      sma50 = talib.SMA(close, timeperiod=50)
      firstNotNan = np.where(np.isnan(sma50))[0][-1] + 1
      sma50[:firstNotNan] = sma50[firstNotNan]
      for i, val in enumerate(sma50[-N:]):
         self.series50.append(i + 0.5, val)

   def clear(self):
      self.series15.clear()
      self.series50.clear()



# ------------------------------------------------------------------------------------
# EMA - Exponential Moving Average
# ------------------------------------------------------------------------------------

class EMA(Overlay):
   def __init__(self):
      self.series9 = QtChart.QSplineSeries()
      self.series26 = QtChart.QSplineSeries()
      self.series100 = QtChart.QSplineSeries()
      pen = QtGui.QPen(QtCore.Qt.SolidLine)
      pen.setWidth(0.5)
      pen.setColor(QtGui.QColor(255,255,0))
      self.series9.setPen(pen)
      pen.setColor(QtGui.QColor(255, 0, 255))
      self.series26.setPen(pen)
      pen.setColor(QtGui.QColor(0, 127, 255))
      self.series100.setPen(pen)

   def addToChart(self, chart : QtChart.QChart):
      chart.addSeries(self.series9)
      chart.addSeries(self.series26)
      chart.addSeries(self.series100)

   def removeFromChart(self, chart : QtChart.QChart):
      chart.removeSeries(self.series9)
      chart.removeSeries(self.series26)
      chart.removeSeries(self.series100)

   def update(self, data, N, chart : CandleChart):
      close = data[4]
      self.clear()
      self.series9.attachAxis(chart.ax)
      self.series9.attachAxis(chart.ay)
      self.series26.attachAxis(chart.ax)
      self.series26.attachAxis(chart.ay)
      self.series100.attachAxis(chart.ax)
      self.series100.attachAxis(chart.ay)

      ema9 = talib.EMA(close, timeperiod=9)
      firstNotNan = np.where(np.isnan(ema9))[0][-1] + 1
      ema9[:firstNotNan] = ema9[firstNotNan]
      for i, val in enumerate(ema9[-N:]):
         self.series9.append(i + 0.5, val)

      ema21 = talib.EMA(close, timeperiod=26)
      firstNotNan = np.where(np.isnan(ema21))[0][-1] + 1
      ema21[:firstNotNan] = ema21[firstNotNan]
      for i, val in enumerate(ema21[-N:]):
         self.series26.append(i + 0.5, val)

      ema100 = talib.EMA(close, timeperiod=100)
      firstNotNan = np.where(np.isnan(ema100))[0][-1] + 1
      ema100[:firstNotNan] = ema100[firstNotNan]
      for i, val in enumerate(ema100[-N:]):
         self.series100.append(i + 0.5, val)

   def clear(self):
      self.series9.clear()
      self.series26.clear()
      self.series100.clear()


# ------------------------------------------------------------------------------------
# Parabolic SAR
# ------------------------------------------------------------------------------------

class ParabolicSAR(Overlay):
   def __init__(self):
      self.series = QtChart.QScatterSeries()
      self.series.setMarkerSize(1)

   def addToChart(self, chart : QtChart.QChart):
      chart.addSeries(self.series)

   def removeFromChart(self, chart : QtChart.QChart):
      chart.removeSeries(self.series)

   def update(self, data, N, chart : CandleChart):
      high      = data[2,-N:].tolist()
      low       = data[3,-N:].tolist()
      close     = data[4,-N:].tolist()

      self.clear()
      self.series.attachAxis(chart.ax)
      self.series.attachAxis(chart.ay)
      psarValues = parabolicSAR(high, low, close)
      #psarValues = talib.SAR(np.array(high), np.array(low), acceleration=0, maximum=0)
      for i, val in enumerate(psarValues):
         self.series.append(i + 0.5, val)

   def clear(self):
      self.series.clear()

# ------------------------------------------------------------------------------------
# Bollinger Bands (BBANDS)
# ------------------------------------------------------------------------------------






# ------------------------------------------------------------------------------------
# TRIMA - Triangular Moving Average
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
# WMA - Weighted Moving Average
# ------------------------------------------------------------------------------------




def parabolicSAR(high, low, close, iaf=0.02, maxaf=0.2):
   psar = close[:]
   bull = True
   af = iaf
   ep = low[0]
   hp = high[0]
   lp = low[0]
   for i in range(2, len(close)):
      if bull:
         psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
      else:
         psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
      reverse = False
      if bull:
         if low[i] < psar[i]:
            bull = False
            reverse = True
            psar[i] = hp
            lp = low[i]
            af = iaf
      else:
         if high[i] > psar[i]:
            bull = True
            reverse = True
            psar[i] = lp
            hp = high[i]
            af = iaf
      if not reverse:
         if bull:
            if high[i] > hp:
               hp = high[i]
               af = min(af + iaf, maxaf)
            if low[i - 1] < psar[i]:
               psar[i] = low[i - 1]
            if low[i - 2] < psar[i]:
               psar[i] = low[i - 2]
         else:
            if low[i] < lp:
               lp = low[i]
               af = min(af + iaf, maxaf)
            if high[i - 1] > psar[i]:
               psar[i] = high[i - 1]
            if high[i - 2] > psar[i]:
               psar[i] = high[i - 2]
   return psar

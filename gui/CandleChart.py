from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import numpy as np
import talib



class CandleChart(QtChart.QChart):
   minTicks = 5
   maxTicks = 10
   timeframes = [1, 3, 5, 10, 15, 30, 60, 120, 180, 360, 720, 1440, 4320, 10080]
   currTimeframeIndex = 0

   def __init__(self):
      super(CandleChart, self).__init__()

      # set margins, colors and font
      self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
      self.setBackgroundRoundness(0)
      self.layout().setContentsMargins(0, 0, 0, 0)
      self.setMargins(QtCore.QMargins(0,0,0,0))
      self.setContentsMargins(0, 0, 0, 0)
      self.legend().hide()
      chartFont = QtGui.QFont(self.font())
      chartFont.setPixelSize(9)
      self.setFont(chartFont)
      self.setAcceptHoverEvents(True)

      self.candlestickSeries = QtChart.QCandlestickSeries()
      self.candlestickSeries.setIncreasingColor(QtCore.Qt.black)
      self.candlestickSeries.setDecreasingColor(QtCore.Qt.red)
      self.addSeries(self.candlestickSeries)

      # add hover line and price tag
      self.hoverLinePriceTag = QtWidgets.QGraphicsSimpleTextItem(self)
      self.hoverLinePriceTag.setBrush(QtGui.QBrush(QtGui.QColor(255,255,255)))
      self.hoverLinePriceTag.setOpacity(1.0)
      self.hoverLine = QtChart.QLineSeries()
      hoverPen = QtGui.QPen(QtCore.Qt.DashLine)
      hoverPen.setColor(QtCore.Qt.white)
      hoverPen.setWidth(0.5)
      hoverPen.setDashPattern([5,10])
      self.hoverLine.setPen(hoverPen)
      self.hoverLineAxisX = QtChart.QValueAxis()
      self.hoverLineAxisX.hide()
      self.hoverLineAxisX.setRange(0,1)
      self.addSeries(self.hoverLine)
      self.addAxis(self.hoverLineAxisX, QtCore.Qt.AlignBottom)
      self.hoverLine.attachAxis(self.hoverLineAxisX)

      # add overlays
      self.addOverlays()


   # update candle chart
   def updateCandleChart(self, timestamp, open, high, low, close):
      # remove candlestick data
      if self.candlestickSeries.count() > 0:
         self.candlestickSeries.remove(self.candlestickSeries.sets())

      # add new candlestick data
      for i, ts in enumerate(timestamp):
         set = QtChart.QCandlestickSet(open[i], high[i], low[i], close[i], timestamp=ts)
         self.setCandleColors(set)
         self.candlestickSeries.append(set)

      # set candlestick time axes (hidden)
      axisXtime = QtChart.QBarCategoryAxis()
      timestamps = [QtCore.QDateTime.fromMSecsSinceEpoch(x).toString('HH:mm') for x in timestamp]
      axisXtime.setCategories(timestamps)
      axisXtime.setGridLineVisible(False)
      axisXtime.hide()

      self.axisXvalue = QtChart.QValueAxis()
      self.axisXvalue.setRange(0, len(axisXtime))
      self.axisXvalue.setGridLineVisible(False)
      self.axisXvalue.hide()

      # set visible time axes with selexted time ticks
      axisXticks = QtChart.QCategoryAxis()
      axisXticks.setLabelsPosition(QtChart.QCategoryAxis.AxisLabelsPositionOnValue)
      linuxTimestamps = [x/1000 for x in timestamp]
      categories = self.extractNiceCategories(linuxTimestamps)
      for tst in categories:
         axisXticks.append(tst, timestamps.index(tst))
      axisXticks.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      axisXticks.setGridLineVisible(False)
      axisXticks.setStartValue(-1)

      # set y axes (prices)
      maxVal = max(high)
      minVal = min(low)
      self.ay = QtChart.QValueAxis()
      self.ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
      self.ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      self.ay.setMax(maxVal)
      self.ay.setMin(minVal)
      self.ay.applyNiceNumbers()

      # remove old axes
      for axis in self.candlestickSeries.attachedAxes():
         self.candlestickSeries.detachAxis(axis)
         self.removeAxis(axis)

      # add updated axes
      self.addAxis(axisXtime, QtCore.Qt.AlignTop)
      self.addAxis(self.axisXvalue, QtCore.Qt.AlignBottom)
      self.addAxis(axisXticks, QtCore.Qt.AlignBottom)
      self.addAxis(self.ay, QtCore.Qt.AlignRight)

      # attach updated axes to data series
      self.candlestickSeries.attachAxis(axisXtime)
      self.candlestickSeries.attachAxis(axisXticks)
      self.candlestickSeries.attachAxis(self.ay)

      # update hover line x axes
      for axis in self.hoverLine.attachedAxes():
         self.hoverLine.detachAxis(axis)
      self.hoverLine.attachAxis(self.ay)


   # choose ticks for visible time axes
   def extractNiceCategories(self, timestamps):
      # we want to show approximately 5 ticks on the time axes
      for delta in self.timeframes:  #[self.currTimeframeIndex : ]:
         minuteDelta = 60 * delta
         timestamps = [ t for t in timestamps if t%(minuteDelta) == 0 ]
         if len(timestamps) < self.maxTicks:
            break
      categories = [QtCore.QDateTime.fromSecsSinceEpoch(t).toString('HH:mm') for t in timestamps]
      return categories

   # set candle colors
   def setCandleColors(self, candleSet : QtChart.QCandlestickSet):
      if candleSet.close() < candleSet.open():
         candleSet.setPen(QtGui.QPen(QtCore.Qt.red, 1))
         candleSet.setBrush(QtGui.QBrush(QtCore.Qt.red))
      else:
         candleSet.setPen(QtGui.QPen(QtCore.Qt.green, 1))
         candleSet.setBrush(QtGui.QBrush(QtCore.Qt.black))


   # handle hover event by showing hover price line
   def hoverMoveEvent(self, event : QtWidgets.QGraphicsSceneHoverEvent):
      event.setAccepted(True)
      pos = self.mapToParent(event.pos())
      val = self.mapToValue(pos)
      self.hoverLine.clear()
      self.hoverLine.append(0, val.y())
      self.hoverLine.append(1, val.y())
      self.hoverLinePriceTag.setPos(self.plotArea().getCoords()[2] + 5, pos.y() - 7)  # TODO calculate offsets instead of hardcoding
      self.hoverLinePriceTag.setText('{:.2f}'.format(val.y()))
      yAxes = self.hoverLine.attachedAxes()[0]
      if val.y() > yAxes.min() and val.y() < yAxes.max():
         self.hoverLinePriceTag.show()
      else:
         self.hoverLinePriceTag.hide()

   def hoverLeaveEvent(self, event : QtWidgets.QGraphicsSceneHoverEvent):
      self.hoverLine.hide()
      self.hoverLinePriceTag.hide()

   def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):
      self.hoverLine.show()


# OVERLAYS
#=======================================================================================


   def addOverlays(self):
      self.psarOverlay = QtChart.QScatterSeries()
      self.psarOverlay.setMarkerSize(1)
      self.addSeries(self.psarOverlay)


   def updateOverlays(self, open, high, low, close):
      self.psarOverlay.clear()
      self.psarOverlay.attachAxis(self.axisXvalue)
      self.psarOverlay.attachAxis(self.ay)
      #psarValues = self.parabolicSAR(high, low, close)
      psarValues = talib.SAR(np.array(high), np.array(low), acceleration=0, maximum=0)
      for i, val in enumerate(psarValues):
         self.psarOverlay.append(i+0.5, val)



   def parabolicSAR(self, high, low, close, iaf=0.02, maxaf=0.2):
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

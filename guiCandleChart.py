import sys
from pydispatch import dispatcher
from abc import ABC, abstractmethod
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import talib
import numpy as np
import exchanges.bitfinex.bitfinex_v2_WebSockets as bitfinexWS



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
      psarValues = self.parabolicSAR(high, low, close)
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


# INDICATORS
#=======================================================================================

class IndicatorFactory(object):
   indicators = None

   @staticmethod
   def createIndicator(name):
      if not IndicatorFactory.indicators:
         IndicatorFactory.indicators = {}
         for ind in Indicator.__subclasses__():
            IndicatorFactory.indicators[ind.__name__] = ind
      if name in IndicatorFactory.indicators.keys():
         return IndicatorFactory.indicators[name]()
      else:
         print('Indicator not defined')

   @staticmethod
   def getIndicatorNames():
      if not IndicatorFactory.indicators:
         IndicatorFactory.indicators = {}
         for ind in Indicator.__subclasses__():
            IndicatorFactory.indicators[ind.__name__] = ind
      return sorted(list(IndicatorFactory.indicators.keys()))


class Indicator(QtChart.QChart):
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

   # @abstractmethod
   # def setIndicator(self, type):
   #    pass

   @abstractmethod
   def updateIndicator(self):
      pass



class Volume(Indicator):
   def __init__(self):
      super(Volume, self).__init__()
      self.IndicatorName.setText(self.__class__.__name__)
      self.volumeBars = QtChart.QCandlestickSeries()
      self.volumeBars.setIncreasingColor(QtCore.Qt.black)
      self.volumeBars.setDecreasingColor(QtCore.Qt.red)
      self.volumeBars.setBodyWidth(0.7)
      self.addSeries(self.volumeBars)



   def updateIndicator(self, open, close, volume):
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



class MACD(Indicator):
   def __init__(self):
      super(MACD, self).__init__()
      self.IndicatorName.setText(self.__class__.__name__)
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


   def updateIndicator(self, close, N):
      ''' data is a list of close prices'''
      macdLine, macdSignal, macdBars = talib.MACD(np.array(close), fastperiod=12, slowperiod=26, signalperiod=9)
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





#=======================================================================================



class ChartWidget(QtWidgets.QWidget):
   data = None
   numCandlesVisible = 50
   minCandlesVisible = 20
   maxCandlesVisible = 200

   def __init__(self):
      super(ChartWidget, self).__init__()

      self.setContentsMargins(0,0,0,0)
      palette = QtGui.QPalette()
      palette.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
      self.setAutoFillBackground(True)
      self.setPalette(palette)

      self.mainLayout = QtWidgets.QVBoxLayout(self)
      self.mainLayout.setSpacing(10)
      self.mainLayout.setContentsMargins(0,0,0,0)

      self.candleGraph = CandleChart()
      chartView = QtChart.QChartView(self.candleGraph)
      chartView.setRenderHint(QtGui.QPainter.Antialiasing)

      self.volume = IndicatorFactory.createIndicator('Volume')
      volumeView = QtChart.QChartView(self.volume)
      volumeView.setRenderHint(QtGui.QPainter.Antialiasing)

      self.macd = IndicatorFactory.createIndicator('MACD')
      macdView = QtChart.QChartView(self.macd)
      macdView.setRenderHint(QtGui.QPainter.Antialiasing)

      self.mainLayout.addWidget(chartView, stretch=4)
      self.mainLayout.addWidget(volumeView, stretch=1)
      self.mainLayout.addWidget(macdView, stretch=1)


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
      self.volume.updateIndicator(open, close, volume)
      # we need entire list of close prices for MACD
      self.macd.updateIndicator([x[4] for x in self.data], self.numCandlesVisible)


   # handle mouse wheel event for zooming
   def wheelEvent(self, QWheelEvent):
      if QWheelEvent.angleDelta().y() < 0:
         # wheel down - zoom out
         self.numCandlesVisible = min(self.numCandlesVisible + 10, self.maxCandlesVisible)
      else:
         # wheel up - zoom in
         self.numCandlesVisible = max(self.numCandlesVisible - 10, self.minCandlesVisible)
      self.updateChart()


class CandlesUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, candles):
      super(CandlesUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.candles = candles



class MainWindow(QtWidgets.QMainWindow):
   def __init__(self, width, height):
      super(MainWindow, self).__init__()

      self.resize(width, height)
      self.setWindowTitle('Candle Chart')
      self.CandleGraph = ChartWidget()
      self.setCentralWidget(self.CandleGraph)

   def plotCandles(self, candles):
      self.CandleGraph.setData(candles)
      self.CandleGraph.updateChart()

   def customEvent(self, event):
      if event.type() == CandlesUpdateEvent.EVENT_TYPE:
         self.plotCandles(event.candles)

   def updateCandles(self, candles):
      QtWidgets.QApplication.postEvent(self, CandlesUpdateEvent(candles))



if __name__ == '__main__':
   QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling);
   app = QtWidgets.QApplication(sys.argv)
   GUI = MainWindow(800, 600)
   GUI.show()

   # subsribe to the bitfinex OrderBook
   client = bitfinexWS.BitfinexWSClient()
   client.connect()
   dispatcher.connect(GUI.updateCandles, sender='bitfinex', signal='candles_BTCUSD')

   try:
      app.exec_()
   except TypeError:
      import traceback
      traceback.print_exception()
      traceback.print_stack()
   except:
      import sys
      print("Unexpected error:", sys.exc_info()[0])

   client.disconnect()



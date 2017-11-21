import sys
from pydispatch import dispatcher
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import exchanges.bitfinex.bitfinex_v2_WebSockets as bitfinexWS



class CandleChart(QtChart.QChart):
   candleData = None
   numCandlesVisible = 50
   minCandlesVisible = 20
   maxCandlesVisible = 200
   minTicks = 5
   maxTicks = 10
   timeframes = [1, 3, 5, 10, 15, 30, 60, 120, 180, 360, 720, 1440, 4320, 10080]
   currTimeframeIndex = 0

   def __init__(self):
      super(CandleChart, self).__init__()

      self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
      self.setBackgroundPen(QtGui.QPen(QtGui.QColor(255, 80, 80), 0.5))
      self.setBackgroundRoundness(0)
      self.layout().setContentsMargins(0, 0, 0, 0)
      self.setMargins(QtCore.QMargins(0,0,0,0))
      self.setContentsMargins(0, 0, 0, 0)
      #self.setWindowFrameMargins(0,0,0,0)
      self.legend().hide()
      chartFont = QtGui.QFont(self.font())
      chartFont.setPixelSize(9)
      self.setFont(chartFont)
      self.setAcceptHoverEvents(True)

      self.candlestickSeries = QtChart.QCandlestickSeries()
      self.candlestickSeries.setIncreasingColor(QtCore.Qt.black)
      self.candlestickSeries.setDecreasingColor(QtCore.Qt.red)
      self.addSeries(self.candlestickSeries)

      self.hoverLinePriceTag = QtWidgets.QGraphicsSimpleTextItem(self)
      self.hoverLinePriceTag.setBrush(QtGui.QBrush(QtGui.QColor(255,255,255)))
      self.hoverLinePriceTag.setOpacity(1.0)
      self.hoverLine = QtChart.QLineSeries()
      hoverPen = QtGui.QPen(QtCore.Qt.DashLine)
      hoverPen.setColor(QtCore.Qt.white)
      hoverPen.setWidth(0)
      hoverPen.setDashPattern([5,10])
      self.hoverLine.setPen(hoverPen)
      self.hoverLineAxisX = QtChart.QValueAxis()
      self.hoverLineAxisX.hide()
      self.hoverLineAxisX.setRange(0,1)
      self.addSeries(self.hoverLine)
      self.addAxis(self.hoverLineAxisX, QtCore.Qt.AlignBottom)
      self.hoverLine.attachAxis(self.hoverLineAxisX)

      self.addOverlays()




   def setCandlestickData(self, data):
      self.candleData = data
      self.updateCandleChart()


   def updateCandleChart(self):
      data = self.candleData[-self.numCandlesVisible:]
      linuxTimestamps = [x[0]/1000 for x in data]
      timestamps = [QtCore.QDateTime.fromMSecsSinceEpoch(x[0]).toString('HH:mm') for x in data]
      categories = self.extractNiceCategories(linuxTimestamps)

      if self.candlestickSeries.count() > 0:
         self.candlestickSeries.remove(self.candlestickSeries.sets())

      self.candlestickSetList = [QtChart.QCandlestickSet(x[1], x[2], x[3], x[4], timestamp=x[0]) for x in data]
      for set in self.candlestickSetList:
         self.setCandleColors(set)
      self.candlestickSeries.append(self.candlestickSetList)

      axisXtime = QtChart.QBarCategoryAxis()
      axisXtime.setCategories([QtCore.QDateTime.fromMSecsSinceEpoch(x[0]).toString('HH:mm') for x in data])
      axisXtime.setGridLineVisible(False)
      axisXtime.hide()

      self.axisXvalue = QtChart.QValueAxis()
      self.axisXvalue.setRange(0, len(axisXtime))
      self.axisXvalue.setGridLineVisible(False)
      self.axisXvalue.hide()


      axisXticks = QtChart.QCategoryAxis()
      axisXticks.setLabelsPosition(QtChart.QCategoryAxis.AxisLabelsPositionOnValue)
      for tst in categories:
         axisXticks.append(tst, timestamps.index(tst))
      axisXticks.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      axisXticks.setGridLineVisible(False)
      axisXticks.setStartValue(-1)

      maxVal = max([x[2] for x in data])
      minVal = min([x[3] for x in data])
      self.ay = QtChart.QValueAxis()
      self.ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
      self.ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      self.ay.setMax(maxVal)
      self.ay.setMin(minVal)
      self.ay.applyNiceNumbers()

      for axis in self.candlestickSeries.attachedAxes():
         self.candlestickSeries.detachAxis(axis)
         self.removeAxis(axis)

      self.addAxis(axisXtime, QtCore.Qt.AlignTop)
      self.addAxis(self.axisXvalue, QtCore.Qt.AlignBottom)
      self.addAxis(axisXticks, QtCore.Qt.AlignBottom)
      self.addAxis(self.ay, QtCore.Qt.AlignRight)

      self.candlestickSeries.attachAxis(axisXtime)
      self.candlestickSeries.attachAxis(axisXticks)
      self.candlestickSeries.attachAxis(self.ay)

      for axis in self.hoverLine.attachedAxes():
         self.hoverLine.detachAxis(axis)
      self.hoverLine.attachAxis(self.ay)

      self.updateOverlays()




   def extractNiceCategories(self, timestamps):
      # we want to show approximately 5 ticks on the time axes
      for delta in self.timeframes[self.currTimeframeIndex : ]:
         minuteDelta = 60 * delta
         timestamps = [ t for t in timestamps if t%(minuteDelta) == 0 ]
         if len(timestamps) < self.maxTicks:
            break
      categories = [QtCore.QDateTime.fromSecsSinceEpoch(t).toString('HH:mm') for t in timestamps]
      return categories


   def setCandleColors(self, candleSet : QtChart.QCandlestickSet):
      if candleSet.close() < candleSet.open():
         candleSet.setPen(QtGui.QPen(QtCore.Qt.red, 1))
         candleSet.setBrush(QtGui.QBrush(QtCore.Qt.red))
      else:
         candleSet.setPen(QtGui.QPen(QtCore.Qt.green, 1))
         candleSet.setBrush(QtGui.QBrush(QtCore.Qt.black))


   def wheelEvent(self, QWheelEvent):
      if QWheelEvent.delta() < 0:
         # wheel down - zoom out
         self.numCandlesVisible = min(self.numCandlesVisible + 10, self.maxCandlesVisible)
         self.updateCandleChart()
      else:
         # wheel up - zoom in
         self.numCandlesVisible = max(self.numCandlesVisible - 10, self.minCandlesVisible)
         self.currTimeframeIndex = max(1, self.currTimeframeIndex - 1)
         self.updateCandleChart()


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


   def updateOverlays(self):
      if not self.candleData:
         return
      self.psarOverlay.clear()
      self.psarOverlay.attachAxis(self.axisXvalue)
      self.psarOverlay.attachAxis(self.ay)
      psarValues = self.parabolicSAR(self.candleData)
      psarValues = psarValues[-self.numCandlesVisible:]
      for i in range(self.numCandlesVisible):
         self.psarOverlay.append(i+0.5, psarValues[i])



   def parabolicSAR(self, data, iaf=0.02, maxaf=0.2):
      length = len(data)
      high = [x[2] for x in data]
      low = [x[3] for x in data]
      close = [x[4] for x in data]
      psar = close[0:len(close)]

      bull = True
      af = iaf
      ep = low[0]
      hp = high[0]
      lp = low[0]
      for i in range(2, length):
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

class Indicator(QtChart.QChart):
   type = None
   types = ['macd']

   def __init__(self):
      super(Indicator, self).__init__()
      self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
      self.setBackgroundPen(QtGui.QPen(QtGui.QColor(255, 80, 80), 0.5))
      self.setBackgroundRoundness(0)
      self.setMargins(QtCore.QMargins(0, 0, 0, 0))
      self.layout().setContentsMargins(0, 0, 0, 0);
      self.setContentsMargins(0, 0, 0, 0);
      self.legend().hide()
      chartFont = QtGui.QFont(self.font())
      chartFont.setPixelSize(9)
      self.setFont(chartFont)


   def setIndicator(self, type):
      if type not in self.types:
         return
      if type == 'macd':
         self.setMACD()
      self.type = type


   def setMACD(self):
      self.macdLine   = QtChart.QLineSeries()
      self.macdSignal = QtChart.QLineSeries()
      self.macdBars = QtChart.QCandlestickSeries()
      self.macdBars.setIncreasingColor(QtCore.Qt.black)
      self.macdBars.setDecreasingColor(QtCore.Qt.red)
      self.addSeries(self.macdLine)
      self.addSeries(self.macdSignal)
      self.addSeries(self.macdBars)


   def updateIndicator(self, data, N):
      if self.type == 'macd':
         self.updateMACD(data, N)

   def setCandleColors(self, candleSet : QtChart.QCandlestickSet):
      if candleSet.close() < candleSet.open():
         candleSet.setPen(QtGui.QPen(QtCore.Qt.red, 1))
         candleSet.setBrush(QtGui.QBrush(QtCore.Qt.red))
      else:
         candleSet.setPen(QtGui.QPen(QtCore.Qt.green, 1))
         candleSet.setBrush(QtGui.QBrush(QtCore.Qt.black))

   def updateMACD(self, data, N):
      macdLine, macdSignal, macdBars = self.macd(data)
      macdLine = macdLine[-N:]
      macdSignal = macdSignal[-N:]
      macdBars = macdBars[-N:]

      for ax in self.macdLine.attachedAxes():
         self.macdLine.detachAxis(ax)
      for ax in self.macdSignal.attachedAxes():
         self.macdSignal.detachAxis(ax)
      for ax in self.macdBars.attachedAxes():
         self.macdBars.detachAxis(ax)
      for ax in self.axes():
         self.removeAxis(ax)

      self.macdLine.clear()
      self.macdSignal.clear()
      if self.macdBars.count() > 0:
         self.macdBars.remove(self.macdBars.sets())

      macdBarSetList = []
      for i, bar in enumerate(macdBars):
         set = None
         if bar > 0:
            set = QtChart.QCandlestickSet(0, bar, 0, bar, timestamp=i)
         else:
            set = QtChart.QCandlestickSet(0, 0, bar, bar, timestamp=i)
         self.setCandleColors(set)
         macdBarSetList.append(set)
      self.macdBars.append(macdBarSetList)
      print(macdBarSetList)

      for i in range(N):
         self.macdLine.append(i + 0.5, macdLine[i])
         self.macdSignal.append(i + 0.5, macdSignal[i])

      ax = QtChart.QValueAxis()
      ax.setRange(0,N)
      ax.hide()

      ay = QtChart.QValueAxis()
      bound = max(abs(min(macdLine)), abs(max(macdLine)))
      ay.setRange(-bound, bound)
      ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
      ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      ay.applyNiceNumbers()

      ac = QtChart.QBarCategoryAxis()
      ac.append( [str(x) for x in range(N)] )
      ac.hide()

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




#=======================================================================================



class ChartWidget(QtWidgets.QWidget):
   def __init__(self):
      super(ChartWidget, self).__init__()

      self.setContentsMargins(0,0,0,0)


      self.mainLayout = QtWidgets.QVBoxLayout(self)
      self.mainLayout.setSpacing(0)
      self.mainLayout.setContentsMargins(0,0,0,0)

      self.candleGraph = CandleChart()
      chartView = QtChart.QChartView(self.candleGraph)
      chartView.setContentsMargins(0, 0, 0, 0)
      chartView.setRenderHint(QtGui.QPainter.Antialiasing)

      self.macd = Indicator()
      self.macd.setIndicator('macd')
      macdView = QtChart.QChartView(self.macd)
      macdView.setContentsMargins(0,0,0,0)
      macdView.setRenderHint(QtGui.QPainter.Antialiasing)

      self.mainLayout.addWidget(chartView, stretch=4)
      self.mainLayout.addWidget(macdView, stretch=1)


   def setCandlestickData(self, data):
      self.candleGraph.setCandlestickData(data)
      self.macd.updateIndicator([x[4] for x in data], 50)



class CandlesUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, candles):
      super(CandlesUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.candles = candles



class MainWindow(QtGui.QMainWindow):
   def __init__(self, width, height):
      super(MainWindow, self).__init__()

      self.resize(width, height)
      self.setWindowTitle('Candle Chart')

      self.CandleGraph = ChartWidget()
      self.setCentralWidget(self.CandleGraph)


   def plotCandles(self, candles):
      self.CandleGraph.setCandlestickData(candles)


   def customEvent(self, event):
      if event.type() == CandlesUpdateEvent.EVENT_TYPE:
         self.plotCandles(event.candles)

   def updateCandles(self, candles):
      QtGui.QApplication.postEvent(self, CandlesUpdateEvent(candles))



if __name__ == '__main__':
   QtGui.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling);
   app = QtGui.QApplication(sys.argv)
   GUI = MainWindow(800, 400)
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
import sys
from pydispatch import dispatcher
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import exchanges.bitfinex.bitfinex_v2_WebSockets as bitfinexWS
import math


# timestamp,  open,  high,  low,   close
ohclData = [
[1435708800000, 126.90, 126.94, 125.9, 126.60],
[1435795200000, 126.69, 126.69, 126.6, 126.69],
[1436140800000, 124.85, 126.23, 124.8, 126.00],
[1436227200000, 125.89, 126.15, 123.7, 125.69],
[1436313600000, 124.64, 124.64, 122.5, 122.54],
[1436400000000, 123.85, 124.06, 119.2, 120.07],
[1436486400000, 121.94, 123.85, 121.2, 123.28],
[1436745600000, 125.03, 125.76, 124.3, 125.66],
[1436832000000, 126.04, 126.37, 125.0, 125.61],
[1436918400000, 125.72, 127.15, 125.5, 126.82],
[1437004800000, 127.74, 128.57, 127.3, 128.51],
[1437091200000, 129.08, 129.62, 128.3, 129.62],
[1437350400000, 130.97, 132.97, 130.7, 132.07],
[1437436800000, 132.85, 132.92, 130.3, 130.75],
[1437523200000, 121.99, 125.50, 121.9, 125.22],
[1437609600000, 126.20, 127.09, 125.0, 125.16],
[1437696000000, 125.32, 125.74, 123.9, 124.50],
[1437955200000, 123.09, 123.61, 122.1, 122.77],
[1438041600000, 123.38, 123.91, 122.5, 123.38],
[1438128000000, 123.15, 123.50, 122.2, 122.99],
[1438214400000, 122.32, 122.57, 121.7, 122.37],
[1438300800000, 122.60, 122.64, 120.9, 121.30]
]



class ChartWidget(QtWidgets.QWidget):
   candleData = None
   numCandlesVisible = 50
   minCandlesVisible = 20
   maxCandlesVisible = 200
   minTicks = 5
   maxTicks = 10
   timeframes = [1, 3, 5, 10, 15, 30, 60, 120, 180, 360, 720, 1440, 4320, 10080]
   currTimeframeIndex = 0

   def __init__(self):
      super(ChartWidget, self).__init__()

      self.mainLayout = QtWidgets.QVBoxLayout(self)

      self.candleGraph = QtChart.QChart()
      self.candleGraph.legend().setVisible(True)
      self.candleGraph.legend().setAlignment(QtCore.Qt.AlignBottom)
      self.candleGraph.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
      self.candleGraph.setBackgroundPen(QtGui.QPen(QtGui.QColor(255, 80, 80), 0.5))
      self.candleGraph.setBackgroundRoundness(0)
      self.candleGraph.setContentsMargins(0,0,0,0)
      self.candleGraph.setWindowFrameMargins(0,0,0,0)
      self.candleGraph.legend().hide()
      chartFont = QtGui.QFont(self.candleGraph.font())
      chartFont.setPixelSize(9)
      self.candleGraph.setFont(chartFont)


      chartView = QtChart.QChartView(self.candleGraph)
      chartView.setRenderHint(QtGui.QPainter.Antialiasing)

      self.mainLayout.addWidget(chartView)

      self.candlestickSeries = QtChart.QCandlestickSeries()
      self.candlestickSeries.setIncreasingColor(QtCore.Qt.black)
      self.candlestickSeries.setDecreasingColor(QtCore.Qt.red)
      self.candleGraph.addSeries(self.candlestickSeries)



   def setCandlestickData(self, data):
      self.candleData = data
      self.updateCandleChart()

      # if self.candlestickSeries.count() == 0:
      #    data = data[-self.numCandlesVisible:]
      #    self.candlestickSetList = [QtChart.QCandlestickSet(x[1], x[2], x[3], x[4], timestamp=x[0]) for x in data]
      #    for set in self.candlestickSetList:
      #       self.setCandleColors(set)
      #
      #    self.candlestickSeries.append(self.candlestickSetList)
      #    self.candleGraph.addSeries(self.candlestickSeries)
      #    self.updateCandleChart()
      #
      # else:
      #    # update only the last candlestick item
      #    item = data[-1]
      #    newSet = QtChart.QCandlestickSet(item[1], item[2], item[3], item[4], timestamp=item[0])
      #    lastSet = self.candlestickSeries.sets()[-1]
      #    self.setCandleColors(newSet)
      #
      #    if newSet.timestamp() == lastSet.timestamp():
      #       # update
      #       self.candlestickSeries.remove(lastSet)
      #       self.candlestickSeries.append(newSet)
      #    else:
      #       # new candle
      #       self.candlestickSeries.remove(self.candlestickSeries.sets()[0])
      #       self.candlestickSeries.append(newSet)
      #       self.updateCandleChart()



   def updateCandleChart(self):
      data = self.candleData[-self.numCandlesVisible:]
      linuxTimestamps = [x[0]/1000 for x in data]
      timestamps = [QtCore.QDateTime.fromMSecsSinceEpoch(x[0]).toString('HH:mm') for x in data]
      categories = self.extractNiceCategories(linuxTimestamps)

      ax = QtChart.QBarCategoryAxis()
      ax.setCategories([QtCore.QDateTime.fromMSecsSinceEpoch(x[0]).toString('HH:mm') for x in data])
      ax.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      ax.setLabelsAngle(90)
      ax.setGridLineVisible(False)
      ax.hide()

      ax2 = QtChart.QCategoryAxis()
      ax2.setLabelsPosition(QtChart.QCategoryAxis.AxisLabelsPositionOnValue)
      for tst in categories:
         ax2.append(tst, timestamps.index(tst))
      ax2.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      ax2.setGridLineVisible(False)
      ax2.setStartValue(-1)

      maxVal = max([x[2] for x in data])
      minVal = min([x[3] for x in data])
      ay = QtChart.QValueAxis()
      ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
      ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      ay.setMax(maxVal)
      ay.setMin(minVal)
      ay.applyNiceNumbers()


      if self.candlestickSeries.count() > 0:
         self.candlestickSeries.remove(self.candlestickSeries.sets())

      self.candlestickSetList = [QtChart.QCandlestickSet(x[1], x[2], x[3], x[4], timestamp=x[0]) for x in data]
      for set in self.candlestickSetList:
         self.setCandleColors(set)
      self.candlestickSeries.append(self.candlestickSetList)

      for axis in self.candlestickSeries.attachedAxes():
         self.candlestickSeries.detachAxis(axis)
         self.candleGraph.removeAxis(axis)

      self.candleGraph.addAxis(ax, QtCore.Qt.AlignTop)
      self.candleGraph.addAxis(ax2, QtCore.Qt.AlignBottom)
      self.candleGraph.addAxis(ay, QtCore.Qt.AlignRight)

      self.candlestickSeries.attachAxis(ax)
      self.candlestickSeries.attachAxis(ax2)
      self.candlestickSeries.attachAxis(ay)


   def extractNiceCategories(self, timestamps):
      # we want to show approximately 5 ticks on the time axes
      for delta in self.timeframes[self.currTimeframeIndex : ]:
         minuteDelta = 60 * delta
         timestamps = [ t for t in timestamps if t%(minuteDelta) == 0 ]
         if len(timestamps) < self.maxTicks:
            break
      categories = [QtCore.QDateTime.fromSecsSinceEpoch(t).toString('HH:mm') for t in timestamps]
      return categories
      #return [tst for tst in timestamps if tst[-1] == '0' or tst[-1] == '5']


   def setCandleColors(self, candleSet : QtChart.QCandlestickSet):
      if candleSet.close() < candleSet.open():
         candleSet.setPen(QtGui.QPen(QtCore.Qt.red, 1))
         candleSet.setBrush(QtGui.QBrush(QtCore.Qt.red))
      else:
         candleSet.setPen(QtGui.QPen(QtCore.Qt.green, 1))
         candleSet.setBrush(QtGui.QBrush(QtCore.Qt.black))


   def wheelEvent(self, QWheelEvent):
      if QWheelEvent.angleDelta().y() < 0:
         # wheel down - zoom out
         self.numCandlesVisible = min(self.numCandlesVisible + 10, self.maxCandlesVisible)
         self.updateCandleChart()
      else:
         # wheel up - zoom in
         self.numCandlesVisible = max(self.numCandlesVisible - 10, self.minCandlesVisible)
         self.currTimeframeIndex = max(1, self.currTimeframeIndex - 1)
         self.updateCandleChart()


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
   app = QtGui.QApplication(sys.argv)
   GUI = MainWindow(800, 400)
   GUI.show()

   # subsribe to the bitfinex OrderBook
   client = bitfinexWS.BitfinexWSClient()
   client.connect()
   dispatcher.connect(GUI.updateCandles, sender='bitfinex', signal='candles_BTCUSD')

   app.exec_()
   client.disconnect()
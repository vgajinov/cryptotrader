import sys
from PyQt5 import QtCore, QtWidgets, QtChart, QtGui



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



class MainWindow(QtWidgets.QMainWindow):
   def __init__(self, width, height):
      super(MainWindow, self).__init__()

      self.resize(width, height)
      self.setWindowTitle('Candle Chart')

      self.candleGraph = QtChart.QChart()

      self.candlestickSeries = QtChart.QCandlestickSeries()
      self.candlestickSeries.setName('Acme Ltd')
      self.candlestickSeries.setIncreasingColor(QtCore.Qt.green)
      self.candlestickSeries.setDecreasingColor(QtCore.Qt.red)

      timestep = [x[0] for x in ohclData]
      open = [x[1] for x in ohclData]
      high = [x[2] for x in ohclData]
      low = [x[3] for x in ohclData]
      close = [x[4] for x in ohclData]

      self.candlestickSetList = [QtChart.QCandlestickSet(x[1], x[2], x[3], x[4], timestamp=x[0]) for x in ohclData]
      self.candlestickSeries.append(self.candlestickSetList)

      self.candleGraph.addSeries(self.candlestickSeries)
      self.candleGraph.setTitle('Acme')
      #self.candleGraph.setAnimationOptions(QtChart.QChart.SeriesAnimations)
      self.candleGraph.createDefaultAxes()

      ax = QtChart.QBarCategoryAxis(self.candleGraph.axisX())
      #ax.setCategories(QtCore.QDateTime.fromMSecsSinceEpoch(self.candlestickSet.timestamp()).toString('dd'))
      ay = QtChart.QValueAxis(self.candleGraph.axisY())
      ay.setMax(1.01 * ay.max())
      ay.setMin(0.99 * ay.min())

      self.candleGraph.legend().setVisible(True)
      self.candleGraph.legend().setAlignment(QtCore.Qt.AlignBottom)

      chartView = QtChart.QChartView(self.candleGraph)
      chartView.setRenderHint(QtGui.QPainter.Antialiasing)
      self.setCentralWidget(chartView)




if __name__ == '__main__':
   app = QtWidgets.QApplication(sys.argv)
   GUI = MainWindow(600, 400)
   GUI.show()
   app.exec_()

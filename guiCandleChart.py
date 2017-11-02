import sys
from pydispatch import dispatcher
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import exchanges.bitfinex.bitfinex_v2_WebSockets as bitfinexWS
import time


class CandlestickItem(pg.GraphicsObject):
   def __init__(self):
      pg.GraphicsObject.__init__(self)
      self.picture = QtGui.QPicture()
      self.painter = QtGui.QPainter(self.picture)
      self.painter.setPen(pg.mkPen('w'))
      self.data = None

   def generatePicture(self):
      if not self.data:
         return
      print('generate picture')
      w = (self.data[1][0] - self.data[0][0]) / 3.
      for candle in self.data:
         try:
            t, open, close, min, max, volume = candle
            self.painter.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            if open > close:
               self.painter.setBrush(pg.mkBrush('r'))
            else:
               self.painter.setBrush(pg.mkBrush('g'))
               self.painter.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
         except:
            print(candle)
            sys.exit(0)
      self.painter.end()

   def paint(self, p, *args):
      print('paint event')
      picture = QtGui.QPicture()
      painter = QtGui.QPainter(picture)
      painter.setPen(pg.mkPen('w'))
      if self.data:
         print('generate picture')
         w = (self.data[1][0] - self.data[0][0]) / 3.
         for candle in self.data:
            try:
               t, open, close, min, max, volume = candle
               self.painter.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
               if open > close:
                  self.painter.setBrush(pg.mkBrush('r'))
               else:
                  self.painter.setBrush(pg.mkBrush('g'))
                  self.painter.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
            except:
               print(candle)
               sys.exit(0)
      painter.end()
      #p.drawPicture(0, 0, self.picture)

   def boundingRect(self):
      return QtCore.QRectF(self.picture.boundingRect())


   def updateData(self, data):
      print('Data update')
      if self.data:
         self.data.append(data)
      else:
         self.data = data




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

      self.CandleGraph = pg.PlotWidget()
      self.setCentralWidget(self.CandleGraph)

      self.candlestickItem = CandlestickItem()
      self.CandleGraph.addItem(self.candlestickItem)

      tickFont = QtGui.QFont()
      tickFont.setPointSize(8)
      tickFont.setStretch(QtGui.QFont.Condensed)
      self.CandleGraph.getAxis('left').tickFont = tickFont
      self.CandleGraph.getAxis('bottom').tickFont = tickFont
      self.CandleGraph.showGrid(y=True, alpha=0.3)


   def plotCandles(self, candles):
      self.candlestickItem.updateData(candles)
      self.update()
      self.repaint()
      self.candlestickItem.update()
      self.candlestickItem.repaint()

   def customEvent(self, event):
      if event.type() == CandlesUpdateEvent.EVENT_TYPE:
         self.plotCandles(event.candles)

   def updateCandles(self, candles):
      QtGui.QApplication.postEvent(self, CandlesUpdateEvent(candles))



if __name__ == '__main__':
   app = QtGui.QApplication(sys.argv)
   GUI = MainWindow(600, 400)
   GUI.show()

   # subsribe to the bitfinex OrderBook
   client = bitfinexWS.BitfinexWSClient()
   client.connect()
   dispatcher.connect(GUI.updateCandles, sender='bitfinex', signal='candles_BTCUSD')

   app.exec_()
   client.disconnect()
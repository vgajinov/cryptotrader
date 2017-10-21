import sys
from pydispatch import dispatcher
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import exchanges.bitfinex.bitfinex_v2_WebSockets as bitfinexWS
import numpy as np

pg.mkQApp()
pw = pg.PlotWidget()
pw.show()

p1 = pw.plotItem
p2 = pg.ViewBox()
p1.scene().addItem(p2)
p2.setXLink(p1)

def updateViews():
   ## view has resized; update auxiliary views to match
   global p1, p2
   p2.setGeometry(p1.vb.sceneBoundingRect())
   p2.linkedViewChanged(p1.vb, p2.XAxis)

updateViews()
p1.vb.sigResized.connect(updateViews)

curve = pg.PlotCurveItem(fillLevel=0, brush=(0,0,55,150))
#hist = pg.BarGraphItem(x=[0,1], y1=[0,0], height=0, width=1, brush='r')
#hist = pg.PlotItem(stepMode=True, fillLevel=0, brush=(0,0,255,150))
hist = pg.PlotCurveItem( fillLevel=0, brush=(0,0,255,150))
p1.addItem(curve)
p2.addItem(hist)


def plotBook(bids,asks):
   global curve
   items = list(asks.items())[-15:]
   price = [item[0] for item in items]
   amount = [-item[1] for item in items]
   hist.setData(price, amount)
   for i in range(len(amount)-2,-1,-1):
      amount[i] = amount[i] + amount[i+1]
   curve.setData(price, amount)
   updateViews()


# listener for book updates
def handleBook(sender, bids, asks):
   plotBook(bids, asks)



client = bitfinexWS.BitfinexWSClient()
client.connect()

dispatcher.connect(handleBook, signal='book_BTCUSD', sender='bitfinex')



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
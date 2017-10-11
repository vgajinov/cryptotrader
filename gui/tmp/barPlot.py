import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

class MyBar(pg.BarGraphItem):
   def __init__(self, **opts):
      super(MyBar, self).__init__(**opts)

   def setData(self, **opts):
      self.opts.update(opts)
      self.picture = None
      self._shape = None
      self.update()
      self.informViewBoundsChanged()


win = pg.plot()
win.setWindowTitle('pyqtgraph example: BarGraphItem')

x = np.arange(10)
y1 = np.sin(x)
y2 = 1.1 * np.sin(x + 1)
y3 = 1.2 * np.sin(x + 2)


#bg1 = pg.BarGraphItem(x=x, height=y1, width=0.3, brush='r')
bg1 = MyBar(x=x, height=y1, width=0.3, brush='r')
bg2 = pg.BarGraphItem(x=x + 0.33, height=y2, width=0.3, brush='g')
bg3 = pg.BarGraphItem(x=x + 0.66, height=y3, width=0.3, brush='b')

y1 = 0.5*y1
bg1.setData(x=x, height=y1, width=0.4, brush='r')

win.addItem(bg1)
win.addItem(bg2)
win.addItem(bg3)


# Final example shows how to handle mouse clicks:
class BarGraph(pg.BarGraphItem):
   def mouseClickEvent(self, event):
      print("clicked")


bg = BarGraph(x=x, y=y1 * 0.3 + 2, height=0.4 + y1 * 0.2, width=0.8)
win.addItem(bg)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
   import sys

   if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
      QtGui.QApplication.instance().exec_()
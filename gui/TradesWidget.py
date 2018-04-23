from datetime import datetime
from PyQt5 import QtCore, QtWidgets, QtGui
from .CustomTableWidget import CustomTableWidget


# ======================================================================
# TradesWidget class provides the trades column display
# ======================================================================

class TradesWidget(CustomTableWidget):
   def __init__(self):
      super(TradesWidget, self).__init__()
      self.setObjectName('tradeTable')
      self.setColumnCount(3)


   # set trades data
   def setData(self, trades):
      if trades == []:
         return
      self.data = list(reversed(trades))
      priceStrings = ['{:.4f}'.format(x[2]) for x in self.data]
      amountStrings = ['{:.4f}'.format(abs(x[1])) for x in self.data]
      dateStrings = [datetime.fromtimestamp(x[0] / 1000).strftime('%H:%M:%S') for x in self.data]
      self.tableData = [priceStrings, amountStrings, dateStrings]
      self.fitDataAndColumns()

      # set items
      amountThreshold = 0.1 * sum([abs(x[1]) for x in self.data])
      for i in range(self.rowCount()):
         self.setRowHeight(i, self.rowHeight)

         # prices
         priceItem = QtWidgets.QTableWidgetItem(priceStrings[i])
         if self.data[i][1] < 0:
            priceItem.setForeground(QtCore.Qt.red)
         else:
            priceItem.setForeground(QtCore.Qt.green)
         self.setItem(i, 0, priceItem)

         # amounts
         amountItem = QtWidgets.QTableWidgetItem(amountStrings[i])
         amountItem.setTextAlignment(QtCore.Qt.AlignRight)
         if abs(self.data[i][1]) > amountThreshold:
            amountItem.setForeground(QtCore.Qt.yellow)
         self.setItem(i, 1, amountItem)

         # date/time
         dateItem = QtWidgets.QTableWidgetItem(dateStrings[i])
         dateItem.setTextAlignment(QtCore.Qt.AlignRight)
         self.setItem(i, 2, dateItem)

      # update tradesTable
      self.update()


   def resizeEvent(self, QResizeEvent):
      self.fitDataAndColumns()
      QtWidgets.QWidget.resizeEvent(self, QResizeEvent)
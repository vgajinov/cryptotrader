import math
from PyQt5 import QtCore, QtWidgets, QtGui
from .CustomTableWidget import CustomTableWidget




# ======================================================================
# OrderBookNumericWidget class provides
# the OrderBook numeric column display
# ======================================================================

class OrderBookNumericWidget(QtWidgets.QWidget):
   symbol_details = None
   pricePrec      = None
   amountPrec     = None

   def __init__(self):
      super(OrderBookNumericWidget, self).__init__()

      self.mainLayout = QtWidgets.QVBoxLayout(self)

      self.asksTable = CustomTableWidget()
      self.asksTable.setObjectName('asksTable')
      self.asksTable.setColumnCount(3)

      self.bidsTable = CustomTableWidget()
      self.bidsTable.setObjectName('bidsTable')
      self.bidsTable.setColumnCount(3)

      # last price
      self.priceLabel = QtWidgets.QLabel()
      self.priceLabel.setAlignment(QtCore.Qt.AlignCenter)

      # add widgets to layout
      self.mainLayout.addWidget(self.asksTable)
      self.mainLayout.addWidget(self.priceLabel)
      self.mainLayout.addWidget(self.bidsTable)
      self.mainLayout.setContentsMargins(0,0,0,0)


   def setSymbolDetails(self, details):
      self.symbol_details = details

      leftDigits, rightDigits = str(details['minAmount']).split('.')
      self.amountPrec = len(rightDigits.rstrip('0'))

      self.pricePrec = None
      pricePrec = details.get('minPrice', None)
      if pricePrec is not None:
         self.pricePrec = int(abs(math.log10(float(pricePrec))))


   # set OrderBook numeric data
   def setData(self, bids, asks):
      askItems = list(reversed(list(asks.items())))
      askSums = [abs(x[1]) for x in askItems]
      for i in range(len(askSums) - 2, -1, -1):
         askSums[i] = askSums[i] + askSums[i+1]

      if self.pricePrec is None:
         exp = math.ceil(math.log10(float(askItems[0][0])))
         self.pricePrec = min(abs(exp - int(self.symbol_details['precision'])), 8)

      askSumStrings    = ['{:.{prec}f}'.format(x, prec=self.amountPrec) for x in askSums]
      askPriceStrings  = ['{:.{prec}f}'.format(x[0], prec=self.pricePrec) for x in askItems]
      askAmountStrings = ['{:.{prec}f}'.format(abs(x[1]), prec=self.amountPrec) for x in askItems]

      self.asksTable.tableData = [askPriceStrings, askAmountStrings, askSumStrings]
      self.asksTable.fitDataAndColumns()

      bidItems = list(reversed(list(bids.items())))
      bidSums = [abs(x[1]) for x in bidItems]
      for i in range(len(bidSums) - 1):
         bidSums[i+1] = bidSums[i] + bidSums[i+1]
      bidSumStrings    = ['{:.{prec}f}'.format(x, prec=self.amountPrec) for x in bidSums]
      bidPriceStrings  = ['{:.{prec}f}'.format(x[0], prec=self.pricePrec) for x in bidItems]
      bidAmountStrings = ['{:.{prec}f}'.format(abs(x[1]), prec=self.amountPrec) for x in bidItems]

      self.bidsTable.tableData = [bidPriceStrings, bidAmountStrings, bidSumStrings]
      self.bidsTable.fitDataAndColumns()

      # set ask items
      numItems = self.asksTable.rowCount()
      for i in range(numItems):
         self.asksTable.setRowHeight(i, self.asksTable.rowHeight)

         # prices
         priceItem = QtWidgets.QTableWidgetItem(askPriceStrings[-numItems + i])
         priceItem.setForeground(QtCore.Qt.red)
         self.asksTable.setItem(i, 0, priceItem)

         # amounts
         amountItem = QtWidgets.QTableWidgetItem(askAmountStrings[-numItems + i])
         amountItem.setTextAlignment(QtCore.Qt.AlignRight)
         self.asksTable.setItem(i, 1, amountItem)

         # sums
         sumItem = QtWidgets.QTableWidgetItem(askSumStrings[-numItems + i])
         sumItem.setTextAlignment(QtCore.Qt.AlignRight)
         self.asksTable.setItem(i, 2, sumItem)

      # set bid items
      for i in range(self.bidsTable.rowCount()):
         self.bidsTable.setRowHeight(i, self.bidsTable.rowHeight)

         # prices
         priceItem = QtWidgets.QTableWidgetItem(bidPriceStrings[i])
         priceItem.setForeground(QtCore.Qt.green)
         self.bidsTable.setItem(i, 0, priceItem)

         # amounts
         amountItem = QtWidgets.QTableWidgetItem(bidAmountStrings[i])
         amountItem.setTextAlignment(QtCore.Qt.AlignRight)
         self.bidsTable.setItem(i, 1, amountItem)

         # sums
         sumItem = QtWidgets.QTableWidgetItem(bidSumStrings[i])
         sumItem.setTextAlignment(QtCore.Qt.AlignRight)
         self.bidsTable.setItem(i, 2, sumItem)

      # update asks and bids tables
      self.asksTable.update()
      self.bidsTable.update()


   # set price on the OrderBook numeric layout
   def setLastPrice(self, price):
      if self.pricePrec is not None:
         self.priceLabel.setText('{:.{prec}f}'.format(price, prec=self.pricePrec))

   # format LastPrice label
   def formatLastPrice(self):
      newHeight = min(40, int(0.07 * self.height()))
      self.priceLabel.setFixedHeight(newHeight)
      font = QtGui.QFont(self.priceLabel.font())
      font.setPixelSize(int(0.6 * newHeight))
      self.priceLabel.setFont(font)
      self.priceLabel.update()

   def clear(self):
      self.priceLabel.clear()
      self.asksTable.clear()
      self.bidsTable.clear()

   # ------------------------------------------------------------------------------------
   # Event Handlers
   # ------------------------------------------------------------------------------------

   def resizeEvent(self, QResizeEvent):
      self.formatLastPrice()
      self.asksTable.fitDataAndColumns()
      self.bidsTable.fitDataAndColumns()
      QtWidgets.QWidget.resizeEvent(self, QResizeEvent)
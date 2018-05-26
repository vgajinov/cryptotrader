import math
from PyQt5 import QtCore, QtWidgets, QtGui
from .CustomTables import OrderBookTableView


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

      # asks
      self.asksTable = OrderBookTableView(QtCore.Qt.red)
      self.asksTable.setObjectName('asksTable')

      # bids
      self.bidsTable = OrderBookTableView(QtCore.Qt.green)
      self.bidsTable.setObjectName('bidsTable')

      # last price
      self.priceLabel = QtWidgets.QLabel()
      self.priceLabel.setObjectName('lastPriceLabel')
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
      # determine the price precision
      if self.pricePrec is None:
         price = next(iter(asks.keys()))
         exp = math.ceil(math.log10(float(price)))
         self.pricePrec = min(abs(exp - int(self.symbol_details['precision'])), 8)

      total = 0.0
      askList = []
      for price, amount in list(asks.items()):
         total += abs(amount)
         askList.append(['{:.{prec}f}'.format(price, prec=self.pricePrec),
                         '{:,.{prec}f}'.format(abs(amount), prec=self.amountPrec),
                         '{:,.{prec}f}'.format(total, prec=self.amountPrec)])
      askList = list(reversed(askList))

      total = 0.0
      bidList = []
      for price, amount in list(reversed(list(bids.items()))):
         total += abs(amount)
         bidList.append(['{:.{prec}f}'.format(price, prec=self.pricePrec),
                         '{:,.{prec}f}'.format(abs(amount), prec=self.amountPrec),
                         '{:,.{prec}f}'.format(total, prec=self.amountPrec)])

      self.asksTable.model().setTableData(askList, True)
      self.bidsTable.model().setTableData(bidList, False)


   # set price on the OrderBook numeric layout
   def setLastPrice(self, price):
      if self.pricePrec is None:
         priceStr = '{:.8f}'.format(price)
         if len(priceStr) > 9:
            priceStr = priceStr[:9]
      else:
         priceStr = '{:.{prec}f}'.format(price, prec=self.pricePrec)

      self.priceLabel.setText(priceStr)


   # format LastPrice label
   def formatLastPrice(self, height):
      self.priceLabel.setFixedHeight(height)
      font = QtGui.QFont(self.priceLabel.font())
      font.setPixelSize(int(0.7 * height))
      self.priceLabel.setFont(font)
      self.priceLabel.update()



   def clear(self):
      self.priceLabel.clear()
      self.asksTable.model().clear()
      self.bidsTable.model().clear()

   # ------------------------------------------------------------------------------------
   # Event Handlers
   # ------------------------------------------------------------------------------------

   def resizeEvent(self, QResizeEvent):
      height = self.height() / 15
      self.formatLastPrice(height)
      self.asksTable.setMaximumHeight(7*height)
      self.bidsTable.setMaximumHeight(7*height)
      QtWidgets.QWidget.resizeEvent(self, QResizeEvent)
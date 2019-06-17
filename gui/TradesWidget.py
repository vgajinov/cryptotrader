import math
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, QtGui
from .CustomTables import CustomTableWidget



# ======================================================================
# TradesWidget class provides the trades column display
# ======================================================================

class TradesWidget(CustomTableWidget):
    symbol_details = None
    pricePrec      = None
    amountPrec     = None

    def __init__(self):
        super(TradesWidget, self).__init__()
        self.setObjectName('tradeTable')
        self.setColumnCount(3)


    def setSymbolDetails(self, details):
        self.symbol_details = details
        leftDigits, rightDigits = str(details['minAmount']).split('.')
        self.amountPrec = len(rightDigits.rstrip('0'))

        self.pricePrec = None
        pricePrec = details.get('minPrice', None)
        if pricePrec is not None:
            self.pricePrec = int(abs(math.log10(float(pricePrec))))


    # set trades data
    def setData(self, trades):
        if trades == []:
            return
        self.data = list(reversed(trades))

        if self.pricePrec is None:
            exp = math.ceil(math.log10(float(self.data[0][2])))
            self.pricePrec = min(abs(exp - int(self.symbol_details['precision'])), 8)

        priceStrings = ['{:.{prec}f}'.format(x[2], prec=self.pricePrec) for x in self.data]
        amountStrings = ['{:.{prec}f}'.format(abs(x[1]), prec=self.amountPrec) for x in self.data]
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


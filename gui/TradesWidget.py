import math
from collections import deque
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, QtGui
from .CustomTables import CustomTableWidget


# ======================================================================
# TradesWidget class provides the trades column display
# ======================================================================

class TradesWidget(CustomTableWidget):
    """The widget for displaying recent trades."""

    MAX_TRADES = 100
    trades = deque(maxlen=MAX_TRADES)
    symbol_details   = None
    price_precision  = None
    amount_precision = None


    def __init__(self):
        super(TradesWidget, self).__init__()
        self.setObjectName('tradeTable')
        self.setColumnCount(3)


    def setSymbolDetails(self, details):
        """Sets the symbol (pair details and determines price and amount precisions."""
        self.symbol_details = details

        left_digits, right_digits = str(details['minAmount']).split('.')
        self.amount_precision = len(right_digits.rstrip('0'))

        self.price_precision = None
        price_precision = details.get('minPrice', None)
        if price_precision:
            self.price_precision = int(abs(math.log10(float(price_precision))))


    # set trades data
    def setData(self, data):
        """Sets/updates the the trades data.
        :param data    trades snapshot or and update
        Data is received as one of the following two tuples
            ('snapshot', list(trades))    data is a a complete snapshot
            ('update', new_trade)         data is an update of the most recent trade
        """
        if not data:
            return

        # handle update
        if data[0] == 'update':
            self.trades.appendleft(data[1])
        elif data[0] == 'snapshot':
            self.trades.clear()
            self.trades = deque(list(reversed(data[1])), maxlen=self.MAX_TRADES)
        else:
            return
        self.displayTrades()


    def displayTrades(self):
        """Displays the current state of trades data."""

        # deduce the price precision if we didn't get it from the exchange
        if not self.price_precision:
            exp = math.ceil(math.log10(float(self.trades[0][2])))
            self.price_precision = min(abs(exp - int(self.symbol_details['precision'])), 8)

        # get string representations of the values in trades
        prices = [f'{x[2]:.{self.price_precision}f}' for x in self.trades]
        amounts = [f'{abs(x[1]):.{self.amount_precision}f}' for x in self.trades]
        timestamps = [datetime.fromtimestamp(x[0] / 1000).strftime('%H:%M:%S') for x in self.trades]

        # let Qt deduce the proper column dimensions for the trades
        self.tableData = [prices, amounts, timestamps]
        self.fitDataAndColumns()

        # the threshold for the amount to highlight
        amount_threshold = 0.1 * sum([abs(x[1]) for x in self.trades])

        # set table items
        for i in range(self.rowCount()):
            self.setRowHeight(i, self.rowHeight)

            # prices
            price_item = QtWidgets.QTableWidgetItem(prices[i])
            if self.trades[i][1] < 0:
                price_item.setForeground(QtCore.Qt.red)
            else:
                price_item.setForeground(QtCore.Qt.green)
            self.setItem(i, 0, price_item)

            # amounts
            amount_tem = QtWidgets.QTableWidgetItem(amounts[i])
            amount_tem.setTextAlignment(QtCore.Qt.AlignRight)
            if abs(self.trades[i][1]) > amount_threshold:
                amount_tem.setForeground(QtCore.Qt.yellow)
            self.setItem(i, 1, amount_tem)

            # date/time
            date_item = QtWidgets.QTableWidgetItem(timestamps[i])
            date_item.setTextAlignment(QtCore.Qt.AlignRight)
            self.setItem(i, 2, date_item)

        # update tradesTable
        self.update()


    def resizeEvent(self, QResizeEvent):
        self.fitDataAndColumns()
        QtWidgets.QWidget.resizeEvent(self, QResizeEvent)


import math
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, QtGui
from .Separators import *


class UserTradingWidget(QtWidgets.QWidget):
    """The widget for displaying user's open orders and trades.
    It is based on the tab widget with separate tabs for orders and trades."""
    rest_client     = None
    symbol_details = None

    def __init__(self):
        super(UserTradingWidget, self).__init__()

        self.tabOpenOrders = QtWidgets.QTableWidget()
        self._createOpenOrdersTab()

        self.tabHistory = QtWidgets.QTableWidget()
        self._createTradeHistoryTab()

        self.tabTradesWidget = QtWidgets.QTabWidget()
        self.tabTradesWidget.setObjectName('tradesTabWidget')
        self.tabTradesWidget.tabBar().setObjectName('tradesTabBar')
        self.tabTradesWidget.addTab(self.tabOpenOrders, "Open Orders")
        self.tabTradesWidget.addTab(self.tabHistory, "Trade History")

        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.addWidget(self.tabTradesWidget)
        self.mainLayout.setContentsMargins(0, 5, 0, 0)


    def _createOpenOrdersTab(self):
        """Creates tha tab for open orders that are displayed as a table."""
        open_orders_table_header = ['', 'Time', 'Pair', 'Type', 'Side', 'Price', 'Amount', 'Filled%', 'Total', '      ']
        self.tabOpenOrders.setObjectName('openOrdersTable')
        self.tabOpenOrders.setColumnCount(len(open_orders_table_header))
        self.tabOpenOrders.setHorizontalHeaderLabels(open_orders_table_header)
        self.tabOpenOrders.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tabOpenOrders.horizontalHeader().setResizeMode(self.tabOpenOrders.columnCount()-1,
                                                            QtWidgets.QHeaderView.ResizeToContents)
        self.tabOpenOrders.verticalHeader().setVisible(False)
        self.tabOpenOrders.setShowGrid(False)
        self.tabOpenOrders.setAlternatingRowColors(True)
        self.tabOpenOrders.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tabOpenOrders.setColumnHidden(0, True)


    def _createTradeHistoryTab(self):
        """Creates the tab for user trades displayed as a table."""
        tabHistoryLayout = QtWidgets.QHBoxLayout(self.tabHistory)
        tabHistoryControlsLayout = QtWidgets.QVBoxLayout()
        self.tabHistoryTable = QtWidgets.QTableWidget()
        self.tabHistoryTable.setObjectName('historyTable')
        tabHistoryLayout.addLayout(tabHistoryControlsLayout, stretch=1)
        tabHistoryLayout.addWidget(self.tabHistoryTable, stretch=40)
        tabHistoryLayout.setContentsMargins(0, 0, 0, 0)
        tabHistoryLayout.setSpacing(0)

        time_period = ['1d', '3d', '1w', '1M']
        self.historyPeriodCombo = QtWidgets.QComboBox()
        self.historyPeriodCombo.setObjectName('historyPeriodCombo')
        self.historyPeriodCombo.addItems(time_period)
        self.historyPeriodCombo.setMaxVisibleItems(len(time_period) + 1)
        self.historyPeriodCombo.setMinimumContentsLength(2)
        self.historyPeriodCombo.adjustSize()
        for i in range(self.historyPeriodCombo.count()):
            self.historyPeriodCombo.setItemData(i, QtCore.Qt.AlignCenter, QtCore.Qt.TextAlignmentRole)
        tabHistoryControlsLayout.addWidget(self.historyPeriodCombo)
        tabHistoryControlsLayout.addWidget(LineSeparator(orientation='horizontal', color='white', stroke=1))
        tabHistoryControlsLayout.setAlignment(QtCore.Qt.AlignTop)
        tabHistoryControlsLayout.setSpacing(3)
        tabHistoryControlsLayout.setContentsMargins(4, 4, 0, 0)

        trades_table_header = ['Time', 'Pair', 'Type', 'Side', 'Price', 'Amount', 'Filled', 'Total', 'Status']
        self.tabHistory.setObjectName('historyTab')
        self.tabHistoryTable.setColumnCount(len(trades_table_header))
        self.tabHistoryTable.setHorizontalHeaderLabels(trades_table_header)
        self.tabHistoryTable.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tabHistoryTable.verticalHeader().setVisible(False)
        self.tabHistoryTable.setShowGrid(False)
        self.tabHistoryTable.setAlternatingRowColors(True)
        self.tabHistoryTable.horizontalHeader().setStyleSheet( 'QHeaderView::s‌​ection { background-color: rgb(0,0,0); }')
        self.tabHistoryTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)


    # ------------------------------------------------------------------------------------
    # Update methods
    # ------------------------------------------------------------------------------------

    def _getPrecision(self, pair):
        """Determines the display precision of amount and price values."""
        if self.symbol_details is None:
            return 8, 8

        min_amount = self.symbol_details[pair]['minAmount']
        min_price = self.symbol_details[pair].get('minPrice', None)

        if min_price is not None:
            price_precision = int(abs(math.log10(float(min_price))))
        else:
            price_precision = 8

        amount_precision = 0
        if '.' in str(min_amount):
            _, decimals = str(min_amount).split('.')
            amount_precision = len(decimals.rstrip('0'))

        return price_precision, amount_precision


    def setClient(self, client):
        """Sets the rest client reference."""
        self.rest_client = client


    def setSymbolDetails(self, symbol_details):
        """Sets the details of the echnage symbols."""
        self.symbol_details = symbol_details


    def updateOrders(self, orders):
        """Updates open orders."""
        # sort orders by timestamp
        orders.sort(key=lambda x: x[1], reverse=True)
        # remove all rows
        self.tabOpenOrders.setRowCount(0)
        # add orders
        for row, order in enumerate(orders):
            self.tabOpenOrders.insertRow(row)
            self.tabOpenOrders.setRowHeight(row, 25)

            order_id = str(order[0])
            time = datetime.fromtimestamp(order[1] / 1000).strftime('%d-%m %H:%M:%S')
            pair = order[2]
            order_type = order[3].lower()
            side = order[4].lower()

            price_precision, amount_precision = self._getPrecision(pair)

            price = f'{order[5]:.{price_precision}f}'
            amount = f'{order[6]:.{amount_precision}f}'
            filled = order[7]
            total = f'{order[8]:.{price_precision}f}'

            order_row = [order_id, time, pair, order_type, side, price, amount, filled, total]

            for i, value in enumerate(order_row):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                if i == 4:
                    if value == 'sell':
                        item.setForeground(QtCore.Qt.red)
                    else:
                        item.setForeground(QtCore.Qt.green)
                self.tabOpenOrders.setItem(row, i, item)

            cancelButton = QtWidgets.QPushButton('Cancel')
            cancelButton.setObjectName('cancelButton')
            cancelButton.clicked.connect(self.cancelButtonClicked)
            cancelButton.adjustSize()
            self.tabOpenOrders.setCellWidget(row, len(order), cancelButton)
            self.tabOpenOrders.horizontalHeader().adjustSize()


    def updateUserTrades(self, trades):
        """Updates user trades."""
        # remove all rows
        self.tabHistoryTable.setRowCount(0)
        # add trades
        for row, trade in enumerate(trades):
            self.tabHistoryTable.insertRow(row)
            self.tabHistoryTable.setRowHeight(row, 25)

            time = datetime.fromtimestamp(trade[0] / 1000).strftime('%d-%m %H:%M:%S')
            pair = trade[1]
            order_type = trade[2].lower()
            side = trade[3].lower()

            price_precision, amount_precision = self._getPrecision(pair)

            price  = f'{trade[4]:.{price_precision}f}'
            amount = f'{trade[5]:.{amount_precision}f}'
            filled = f'{trade[6]:.{amount_precision}f}'
            total  = f'{trade[7]:.{price_precision}f}'
            status = trade[8]

            trade_row = [time, pair, order_type, side, price, amount, filled, total, status]

            for i, value in enumerate(trade_row):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                if i == 3:
                    if value == 'sell':
                        item.setForeground(QtCore.Qt.red)
                    else:
                        item.setForeground(QtCore.Qt.green)
                self.tabHistoryTable.setItem(row, i, item)


    def clear(self):
        """Clears the open order and trades tables.
        Should be called when changing the exchange"""
        self.tabOpenOrders.setRowCount(0)
        self.tabHistoryTable.setRowCount(0)


    # ------------------------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------------------------

    def cancelButtonClicked(self):
        """AN event for the click on the cancel trade button"""
        button = self.sender()
        index = self.tabOpenOrders.indexAt(button.pos())
        if index.isValid():
            order_id = self.tabOpenOrders.item(index.row(), 0).text()
            symbol  = self.tabOpenOrders.item(index.row(), 2).text()
            self.rest_client.cancel_order(order_id, symbol)

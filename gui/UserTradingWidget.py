import math
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, QtGui
from .Separators import *


class UserTradingWidget(QtWidgets.QWidget):
   restClient     = None
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


   # OpenOrders tab
   def _createOpenOrdersTab(self):
      tableOpenOrdersHeader = ['', 'Time', 'Pair', 'Type', 'Side', 'Price', 'Amount', 'Filled%', 'Total', '']
      self.tabOpenOrders.setObjectName('openOrdersTable')
      self.tabOpenOrders.setColumnCount(len(tableOpenOrdersHeader))
      self.tabOpenOrders.setHorizontalHeaderLabels(tableOpenOrdersHeader)
      self.tabOpenOrders.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
      self.tabOpenOrders.horizontalHeader().setResizeMode(self.tabOpenOrders.columnCount()-1, QtWidgets.QHeaderView.ResizeToContents)
      self.tabOpenOrders.verticalHeader().setVisible(False)
      self.tabOpenOrders.setShowGrid(False)
      self.tabOpenOrders.setAlternatingRowColors(True)
      self.tabOpenOrders.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
      self.tabOpenOrders.setColumnHidden(0, True)



   # Trade history tab
   def _createTradeHistoryTab(self):
      tabHistoryLayout = QtWidgets.QHBoxLayout(self.tabHistory)
      tabHistoryControlsLayout = QtWidgets.QVBoxLayout()
      self.tabHistoryTable = QtWidgets.QTableWidget()
      self.tabHistoryTable.setObjectName('historyTable')
      tabHistoryLayout.addLayout(tabHistoryControlsLayout, stretch=1)
      tabHistoryLayout.addWidget(self.tabHistoryTable, stretch=40)
      tabHistoryLayout.setContentsMargins(0,0,0,0)
      tabHistoryLayout.setSpacing(0)

      periodList = ['1d', '3d', '1w', '1m']
      self.historyPeriodCombo = QtWidgets.QComboBox()
      self.historyPeriodCombo.setObjectName('historyPeriodCombo')
      self.historyPeriodCombo.addItems(periodList)
      self.historyPeriodCombo.setMaxVisibleItems(len(periodList) + 1)
      self.historyPeriodCombo.adjustSize()
      for i in range(self.historyPeriodCombo.count()):
         self.historyPeriodCombo.setItemData(i, QtCore.Qt.AlignCenter, QtCore.Qt.TextAlignmentRole)
      tabHistoryControlsLayout.addWidget(self.historyPeriodCombo)
      tabHistoryControlsLayout.addWidget(LineSeparator(orientation='horizontal', color='white', stroke=1))
      tabHistoryControlsLayout.setAlignment(QtCore.Qt.AlignTop)
      tabHistoryControlsLayout.setSpacing(3)
      tabHistoryControlsLayout.setContentsMargins(4 ,4 ,0 ,0)

      tableHistoryHeader = ['Time', 'Pair', 'Type', 'Side', 'Price', 'Amount', 'Filled', 'Total', 'Status']
      self.tabHistory.setObjectName('historyTab')
      self.tabHistoryTable.setColumnCount(len(tableHistoryHeader))
      self.tabHistoryTable.setHorizontalHeaderLabels(tableHistoryHeader)
      self.tabHistoryTable.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
      self.tabHistoryTable.verticalHeader().setVisible(False)
      self.tabHistoryTable.setShowGrid(False)
      self.tabHistoryTable.setAlternatingRowColors(True)
      self.tabHistoryTable.horizontalHeader().setStyleSheet( 'QHeaderView::s‌​ection { background-color: rgb(0,0,0); }')
      self.tabHistoryTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)


   # ------------------------------------------------------------------------------------
   # Update methods
   # ------------------------------------------------------------------------------------

   def _getPrecision(self, pair):
      if self.symbol_details is None:
         return 8, 8

      minAmount = self.symbol_details[pair]['minAmount']
      minPrice = self.symbol_details[pair].get('minPrice', None)

      if minPrice is not None:
         pricePrec = int(abs(math.log10(float(minPrice))))
      else:
         pricePrec = 8

      amountPrec = 0
      if '.' in str(minAmount):
         leftDigits, rightDigits = str(minAmount).split('.')
         amountPrec = len(rightDigits.rstrip('0'))

      return pricePrec, amountPrec


   def setClient(self, client):
      self.restClient = client


   def setSymbolDetails(self, symbol_details):
      self.symbol_details = symbol_details


   def updateOrders(self, orders):
      # sort orders by timestamp
      orders.sort(key=lambda x: x[1], reverse=True)
      # remove all rows
      self.tabOpenOrders.setRowCount(0)
      # add orders
      for row, order in enumerate(orders):
         self.tabOpenOrders.insertRow(row)
         self.tabOpenOrders.setRowHeight(row, 25)

         orderId = str(order[0])
         time = datetime.fromtimestamp(order[1] / 1000).strftime('%d-%m %H:%M:%S')
         pair = order[2]
         orderType = order[3].lower()
         side = order[4].lower()

         pricePrec, amountPrec = self._getPrecision(pair)

         price = '{:.{prec}f}'.format(order[5], prec=pricePrec)
         amount = '{:.{prec}f}'.format(order[6], prec=amountPrec)
         filled = order[7]
         total = '{:.{prec}f}'.format(order[8], prec=pricePrec)

         orderStr = [orderId, time, pair, orderType, side, price, amount, filled, total]

         for i, data in enumerate(orderStr):
            item = QtWidgets.QTableWidgetItem(data)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            if i == 4:
               if orderStr[i] == 'sell':
                  item.setForeground(QtCore.Qt.red)
               else:
                  item.setForeground(QtCore.Qt.green)
            self.tabOpenOrders.setItem(row, i, item)

         cancelButton = QtWidgets.QPushButton('Cancel')
         cancelButton.setObjectName('cancelButton')
         cancelButton.clicked.connect(self.cancelButtonClicked)
         cancelButton.adjustSize()
         self.tabOpenOrders.setCellWidget(row, len(order), cancelButton)


   def updateUserTrades(self, trades):
      # remove all rows
      self.tabHistoryTable.setRowCount(0)
      # add trades
      for row, trade in enumerate(trades):
         self.tabHistoryTable.insertRow(row)
         self.tabHistoryTable.setRowHeight(row, 25)

         time = datetime.fromtimestamp(trade[0] / 1000).strftime('%d-%m %H:%M:%S')
         pair = trade[1]
         orderType = trade[2].lower()
         side = trade[3].lower()

         pricePrec, amountPrec = self._getPrecision(pair)

         price = '{:.{prec}f}'.format(trade[4], prec=pricePrec)
         amount = '{:.{prec}f}'.format(trade[5], prec=amountPrec)
         filled = '{:.{prec}f}'.format(trade[6], prec=amountPrec)
         total = '{:.{prec}f}'.format(trade[7], prec=pricePrec)
         status = trade[8]

         tradeStr = [time, pair, orderType, side, price, amount, filled, total, status]

         for i, data in enumerate(tradeStr):
            item = QtWidgets.QTableWidgetItem(data)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            if i == 3:
               if trade[i] == 'sell':
                  item.setForeground(QtCore.Qt.red)
               else:
                  item.setForeground(QtCore.Qt.green)
            self.tabHistoryTable.setItem(row, i, item)


   # should be called when changing the exchange
   def clear(self):
      self.tabOpenOrders.setRowCount(0)
      self.tabHistoryTable.setRowCount(0)


   # ------------------------------------------------------------------------------------
   # Events
   # ------------------------------------------------------------------------------------

   def cancelButtonClicked(self):
      button = self.sender()
      index = self.tabOpenOrders.indexAt(button.pos())
      if index.isValid():
         orderId = self.tabOpenOrders.item(index.row(), 0).text()
         symbol  = self.tabOpenOrders.item(index.row(), 2).text()
         self.restClient.cancel_order(orderId, symbol)

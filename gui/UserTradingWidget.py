from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot
from .Separators import *


class UserTradingWidget(QtWidgets.QWidget):
   def __init__(self):
      super(UserTradingWidget, self).__init__()

      self.mainLayout = QtWidgets.QHBoxLayout(self)
      self.tabTradesWidget = QtWidgets.QTabWidget()
      self.tabTradesWidget.setObjectName('tradesTabWidget')
      self.tabOpenOrders = QtWidgets.QTableWidget()
      self.tabHistory = QtWidgets.QTableWidget()
      self.tabTradesWidget.addTab(self.tabOpenOrders, "Open Orders")
      self.tabTradesWidget.addTab(self.tabHistory, "History")
      self.mainLayout.addWidget(self.tabTradesWidget)
      self.mainLayout.setContentsMargins(0, 5, 0, 0)
      self.tabTradesWidget.tabBar().setObjectName('tradesTabBar')

      # OpenOrders tab
      tableOpenOrdersHeader = ['Pair', 'Type', 'Amount', 'Price', 'Date', 'Filled%', '']
      self.tabOpenOrders.setColumnCount(len(tableOpenOrdersHeader))
      self.tabOpenOrders.setHorizontalHeaderLabels(tableOpenOrdersHeader)
      self.tabOpenOrders.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
      self.tabOpenOrders.horizontalHeader().setResizeMode(self.tabOpenOrders.columnCount( ) -1, QtWidgets.QHeaderView.ResizeToContents)
      self.tabOpenOrders.verticalHeader().setVisible(False)
      self.tabOpenOrders.setShowGrid(False)
      self.tabOpenOrders.setAlternatingRowColors(True)
      self.tabOpenOrders.horizontalHeader().setStyleSheet( 'QHeaderView::s‌​ection { background-color: rgb(0,0,0); }')
      self.tabOpenOrders.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

      # History tab
      tabHistoryLayout = QtWidgets.QHBoxLayout(self.tabHistory)
      tabHistoryControlsLayout = QtWidgets.QVBoxLayout()
      self.tabHistoryTable = QtWidgets.QTableWidget()
      self.tabHistoryTable.setObjectName('historyTable')
      tabHistoryLayout.addLayout(tabHistoryControlsLayout, stretch=1)
      tabHistoryLayout.addWidget(self.tabHistoryTable, stretch=40)
      #tabHistoryLayout.setMargin(0)
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

      tableHistoryHeader = ['Time', 'Pair', 'Type', 'Price', 'Amount', 'Total', 'Fee']
      self.tabHistoryTable.setColumnCount(len(tableHistoryHeader))
      self.tabHistoryTable.setHorizontalHeaderLabels(tableHistoryHeader)
      self.tabHistoryTable.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)
      self.tabHistoryTable.verticalHeader().setVisible(False)
      self.tabHistoryTable.setShowGrid(False)
      self.tabHistoryTable.setAlternatingRowColors(True)
      self.tabHistoryTable.horizontalHeader().setStyleSheet( 'QHeaderView::s‌​ection { background-color: rgb(0,0,0); }')
      self.tabHistoryTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)


      #parentLayout.addLayout(self.mainLayout)

      self.setOpenOrdersData(['WTC/BTC', 'Sell', '20', '0.00107880', '2017-10-15 16:06:12', '0.00'])
      self.setOpenOrdersData(['WTC/BTC', 'Buy', '40', '0.00107880', '2017-10-15 16:06:12', '0.00'])
      self.setHistoryData(['2017-10-16 06:43:53', 'WTC/BTC', 'Sell', '0.00115990', '20', '0.02319800', '0.04239456 BNB'])
      self.setHistoryData(['2017-10-16 06:36:53', 'WTC/BTC', 'Buy', '0.00113655', '20', '0.02273100', '0.04160735 BNB'])
      self.setHistoryData(['2017-10-16 06:35:53', 'WTC/BTC', 'Buy', '0.00113655', '20', '0.02273100', '0.04160735 BNB'])


   def setOpenOrdersData(self, rowData):
      self.tabOpenOrders.insertRow(0)
      self.tabOpenOrders.setRowHeight(0, 25)
      for i, data in enumerate(rowData):
         item = QtWidgets.QTableWidgetItem(data)
         item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
         item.setTextAlignment(QtCore.Qt.AlignCenter)
         if i == 1:
            if rowData[i] == 'Sell':
               item.setForeground(QtCore.Qt.red)
            else:
               item.setForeground(QtCore.Qt.green)
         self.tabOpenOrders.setItem(0, i, item)
      cancelButton = QtWidgets.QPushButton('Cancel')
      cancelButton.setObjectName('cancelButton')
      cancelButton.clicked.connect(self.cancelButtonClicked)
      cancelButton.adjustSize()
      self.tabOpenOrders.setCellWidget(0, len(rowData), cancelButton)


   def setHistoryData(self, rowData):
      self.tabHistoryTable.insertRow(0)
      self.tabHistoryTable.setRowHeight(0, 25)
      for i, data in enumerate(rowData):
         item = QtWidgets.QTableWidgetItem(data)
         item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
         item.setTextAlignment(QtCore.Qt.AlignCenter)
         if i == 2:
            if rowData[i] == 'Sell':
               item.setForeground(QtCore.Qt.red)
            else:
               item.setForeground(QtCore.Qt.green)
         self.tabHistoryTable.setItem(0, i, item)


   def cancelButtonClicked(self):
      button = QtWidgets.qApp.focusWidget()
      # or button = self.sender()
      index = self.tabOpenOrders.indexAt(button.pos())
      if index.isValid():
         self.tabOpenOrders.removeRow(index.row())
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot
from .Separators import *


class TradesWidget(QtGui.QWidget):
   def __init__(self):
      super(TradesWidget, self).__init__()

      self.mainLayout = QtGui.QHBoxLayout(self)
      self.tabTradesWidget = QtGui.QTabWidget()
      self.tabTradesWidget.setObjectName('tradesTabWidget')
      self.tabOpenOrders = QtGui.QTableWidget()
      self.tabHistory = QtGui.QTableWidget()
      self.tabTradesWidget.addTab(self.tabOpenOrders, "Open Orders")
      self.tabTradesWidget.addTab(self.tabHistory, "History")
      self.mainLayout.addWidget(self.tabTradesWidget)
      self.mainLayout.setContentsMargins(0, 5, 0, 0)
      self.tabTradesWidget.tabBar().setObjectName('tradesTabBar')

      # OpenOrders tab
      tableOpenOrdersHeader = ['Pair', 'Type', 'Amount', 'Price', 'Date', 'Filled%', '']
      self.tabOpenOrders.setColumnCount(len(tableOpenOrdersHeader))
      self.tabOpenOrders.setHorizontalHeaderLabels(tableOpenOrdersHeader)
      self.tabOpenOrders.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
      self.tabOpenOrders.horizontalHeader().setResizeMode(self.tabOpenOrders.columnCount( ) -1, QtGui.QHeaderView.ResizeToContents)
      self.tabOpenOrders.verticalHeader().setVisible(False)
      self.tabOpenOrders.setShowGrid(False)
      self.tabOpenOrders.setAlternatingRowColors(True)
      self.tabOpenOrders.horizontalHeader().setStyleSheet( 'QHeaderView::s‌​ection { background-color: rgb(0,0,0); }')
      self.tabOpenOrders.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

      # History tab
      tabHistoryLayout = QtGui.QHBoxLayout(self.tabHistory)
      tabHistoryControlsLayout = QtGui.QVBoxLayout()
      self.tabHistoryTable = QtGui.QTableWidget()
      self.tabHistoryTable.setObjectName('historyTable')
      tabHistoryLayout.addLayout(tabHistoryControlsLayout, stretch=1)
      tabHistoryLayout.addWidget(self.tabHistoryTable, stretch=40)
      tabHistoryLayout.setMargin(0)
      tabHistoryLayout.setSpacing(0)

      periodList = ['1d', '3d', '1w', '1m']
      self.historyPeriodCombo = QtGui.QComboBox()
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
      self.tabHistoryTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
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
         item = QtGui.QTableWidgetItem(data)
         item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
         item.setTextAlignment(QtCore.Qt.AlignCenter)
         if i == 1:
            if rowData[i] == 'Sell':
               item.setTextColor(QtCore.Qt.red)
            else:
               item.setTextColor(QtCore.Qt.green)
         self.tabOpenOrders.setItem(0, i, item)
      cancelButton = QtGui.QPushButton('Cancel')
      cancelButton.setObjectName('cancelButton')
      cancelButton.clicked.connect(self.cancelButtonClicked)
      cancelButton.adjustSize()
      self.tabOpenOrders.setCellWidget(0, len(rowData), cancelButton)


   def setHistoryData(self, rowData):
      self.tabHistoryTable.insertRow(0)
      self.tabHistoryTable.setRowHeight(0, 25)
      for i, data in enumerate(rowData):
         item = QtGui.QTableWidgetItem(data)
         item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
         item.setTextAlignment(QtCore.Qt.AlignCenter)
         if i == 2:
            if rowData[i] == 'Sell':
               item.setTextColor(QtCore.Qt.red)
            else:
               item.setTextColor(QtCore.Qt.green)
         self.tabHistoryTable.setItem(0, i, item)


   def cancelButtonClicked(self):
      button = QtGui.qApp.focusWidget()
      # or button = self.sender()
      index = self.tabOpenOrders.indexAt(button.pos())
      if index.isValid():
         self.tabOpenOrders.removeRow(index.row())
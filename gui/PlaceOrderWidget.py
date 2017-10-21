from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot



class PlaceOrderWidget(QtGui.QWidget):
   def __init__(self):
      super(PlaceOrderWidget, self).__init__()

      self.tabOrderLayout = QtGui.QHBoxLayout()
      self.tabOrderWidget = QtGui.QTabWidget()
      self.tabLimitOrder = QtGui.QWidget()
      self.tabMarketOrder = QtGui.QWidget()
      self.tabOrderWidget.addTab(self.tabLimitOrder, "Limit")
      self.tabOrderWidget.addTab(self.tabMarketOrder, "Market")
      self.tabOrderLayout.addWidget(self.tabOrderWidget)
      self.tabOrderLayout.setContentsMargins(0, 5, 0, 0)
      self.setLayout(self.tabOrderLayout)

      self.ctLimitOrderLayout = QtGui.QHBoxLayout(self.tabLimitOrder)
      self.ctMarketOrderLayout = QtGui.QHBoxLayout(self.tabMarketOrder)

      self.addLimitOrderLayout(self.ctLimitOrderLayout)
      self.setLimitData()

      self.addMarketOrderLayout(self.ctMarketOrderLayout)
      self.setMarketData()


   # Limit Order Layout
   # ---------------------------------------------------
   def addLimitOrderLayout(self, parentLayout):
      self.ctLimitOrderBuyLayout = QtGui.QGridLayout()
      self.ctLimitOrderSellLayout = QtGui.QGridLayout()

      self.addLimitBuyLayout(self.ctLimitOrderBuyLayout)
      self.addLimitSellLayout(self.ctLimitOrderSellLayout)

      parentLayout.addLayout(self.ctLimitOrderBuyLayout, stretch=1)
      parentLayout.addLayout(self.ctLimitOrderSellLayout, stretch=1)
      parentLayout.setSpacing(10)


   # Limit BUY Layout
   # ---------------------------------------------------
   def addLimitBuyLayout(self, parentLayout):
      self.limitBuyInfoLabel = QtGui.QLabel()
      self.limitBuyInfoLabel.setStyleSheet('font: bold 16px;')

      self.limitBuyBalanceLabel = QtGui.QLabel()
      self.limitBuyBalanceAmountLabel = QtGui.QLabel()
      self.limitBuyBalanceLabel.setObjectName('grayedLabel')
      self.limitBuyBalanceAmountLabel.setObjectName('grayedLabel')

      limitBuyPriceLabel = QtGui.QLabel('Price:')
      self.limitBuyPriceInput = QtGui.QLineEdit()
      self.limitBuyPriceInput.setValidator(QtGui.QDoubleValidator(0, 100000.0, 2))

      limitBuyAmountLabel = QtGui.QLabel('Amount:')
      self.limitBuyAmountInput = QtGui.QLineEdit()

      limitBuyTotalLabel = QtGui.QLabel('Total:')
      self.limitBuyTotalValueLabel = QtGui.QLabel()
      limitBuyTotalLabel.setObjectName('totalLabel')

      self.limitBuyButton = QtGui.QPushButton()
      self.limitBuyButton.setMinimumHeight(40)
      self.limitBuyButton.setText('BUY')
      self.limitBuyButton.setObjectName('limitBuyButton')

      parentLayout.addWidget(self.limitBuyInfoLabel, 0, 0)
      parentLayout.addWidget(self.limitBuyBalanceLabel, 1, 0)
      parentLayout.addWidget(self.limitBuyBalanceAmountLabel, 1, 1)
      parentLayout.addWidget(limitBuyPriceLabel, 2, 0)
      parentLayout.addWidget(self.limitBuyPriceInput, 2, 1)
      parentLayout.addWidget(limitBuyAmountLabel, 3, 0)
      parentLayout.addWidget(self.limitBuyAmountInput, 3, 1)
      parentLayout.addWidget(limitBuyTotalLabel, 4, 0)
      parentLayout.addWidget(self.limitBuyTotalValueLabel, 4, 1)
      parentLayout.addWidget(self.limitBuyButton, 5, 0, 1, 2)
      parentLayout.setMargin(15)
      parentLayout.setSpacing(10)
      parentLayout.setColumnStretch(0 ,1)
      parentLayout.setColumnStretch(1 ,3)
      parentLayout.setRowStretch(0, 2)
      parentLayout.setRowStretch(5, 2)


   # Limit SELL Layout
   # ---------------------------------------------------
   def addLimitSellLayout(self, parentLayout):
      self.limitSellInfoLabel = QtGui.QLabel()
      self.limitSellInfoLabel.setStyleSheet('font: bold 16px;')

      self.limitSellBalanceLabel = QtGui.QLabel()
      self.limitSellBalanceAmountLabel = QtGui.QLabel()
      self.limitSellBalanceLabel.setObjectName('grayedLabel')
      self.limitSellBalanceAmountLabel.setObjectName('grayedLabel')

      limitSellPriceLabel = QtGui.QLabel('Price:')
      self.limitSellPriceInput = QtGui.QLineEdit()
      self.limitSellPriceInput.setValidator(QtGui.QDoubleValidator(0, 100000.0, 2))

      limitSellAmountLabel = QtGui.QLabel('Amount:')
      self.limitSellAmountInput = QtGui.QLineEdit()

      limitSellTotalLabel = QtGui.QLabel('Total:')
      self.limitSellTotalValueLabel = QtGui.QLabel()
      limitSellTotalLabel.setObjectName('totalLabel')

      self.limitSellButton = QtGui.QPushButton()
      self.limitSellButton.setMinimumHeight(40)
      self.limitSellButton.setText('SELL')
      self.limitSellButton.setObjectName('limitSellButton')

      parentLayout.addWidget(self.limitSellInfoLabel, 0, 0)
      parentLayout.addWidget(self.limitSellBalanceLabel, 1, 0)
      parentLayout.addWidget(self.limitSellBalanceAmountLabel, 1, 1)
      parentLayout.addWidget(limitSellPriceLabel, 2, 0)
      parentLayout.addWidget(self.limitSellPriceInput, 2, 1)
      parentLayout.addWidget(limitSellAmountLabel, 3, 0)
      parentLayout.addWidget(self.limitSellAmountInput, 3, 1)
      parentLayout.addWidget(limitSellTotalLabel, 4, 0)
      parentLayout.addWidget(self.limitSellTotalValueLabel, 4, 1)
      parentLayout.addWidget(self.limitSellButton, 5, 0, 1, 2)
      parentLayout.setMargin(15)
      parentLayout.setSpacing(10)
      parentLayout.setColumnStretch(0 ,1)
      parentLayout.setColumnStretch(1 ,3)
      parentLayout.setRowStretch(0, 2)
      parentLayout.setRowStretch(5, 3)


   def setLimitData(self):
      self.limitBuyInfoLabel.setText('Buy BTC')
      self.limitBuyBalanceLabel.setText(('USD Balance:'))
      self.limitBuyBalanceAmountLabel.setText('1450.65')

      self.limitSellInfoLabel.setText('Sell BTC')
      self.limitSellBalanceLabel.setText(('BTC Balance:'))
      self.limitSellBalanceAmountLabel.setText('2.356')



   # Market Order Layout
   # ---------------------------------------------------
   def addMarketOrderLayout(self, parentLayout):
      self.ctMarketOrderBuyLayout = QtGui.QGridLayout()
      self.ctMarketOrderSellLayout = QtGui.QGridLayout()

      self.addMarketBuyLayout(self.ctMarketOrderBuyLayout)
      self.addMarketSellLayout(self.ctMarketOrderSellLayout)

      parentLayout.addLayout(self.ctMarketOrderBuyLayout, stretch=1)
      parentLayout.addLayout(self.ctMarketOrderSellLayout, stretch=1)
      parentLayout.setSpacing(10)

   # Market BUY Layout
   # ---------------------------------------------------
   def addMarketBuyLayout(self, parentLayout):
      self.marketBuyInfoLabel = QtGui.QLabel()
      self.marketBuyInfoLabel.setStyleSheet('font: bold 16px;')

      self.marketBuyBalanceLabel = QtGui.QLabel()
      self.marketBuyBalanceAmountLabel = QtGui.QLabel()
      self.marketBuyBalanceLabel.setObjectName('grayedLabel')
      self.marketBuyBalanceAmountLabel.setObjectName('grayedLabel')

      marketBuyPriceLabel = QtGui.QLabel('Price:')
      marketBuyPriceLabel.setObjectName('grayedLabel')
      self.marketBuyPriceInput = QtGui.QLineEdit()
      self.marketBuyPriceInput.setText('Market price')
      self.marketBuyPriceInput.setDisabled(True)
      self.marketBuyPriceInput.setObjectName('disabledInput')

      marketBuyAmountLabel = QtGui.QLabel('Amount:')
      self.marketBuyAmountInput = QtGui.QLineEdit()

      marketBuyTotalLabel = QtGui.QLabel('Total:')
      self.marketBuyTotalValueLabel = QtGui.QLabel()
      marketBuyTotalLabel.setObjectName('totalLabel')

      self.marketBuyButton = QtGui.QPushButton()
      self.marketBuyButton.setMinimumHeight(40)
      self.marketBuyButton.setText('BUY')
      self.marketBuyButton.setObjectName('marketBuyButton')

      parentLayout.addWidget(self.marketBuyInfoLabel, 0, 0)
      parentLayout.addWidget(self.marketBuyBalanceLabel, 1, 0)
      parentLayout.addWidget(self.marketBuyBalanceAmountLabel, 1, 1)
      parentLayout.addWidget(marketBuyPriceLabel, 2, 0)
      parentLayout.addWidget(self.marketBuyPriceInput, 2, 1)
      parentLayout.addWidget(marketBuyAmountLabel, 3, 0)
      parentLayout.addWidget(self.marketBuyAmountInput, 3, 1)
      parentLayout.addWidget(marketBuyTotalLabel, 4, 0)
      parentLayout.addWidget(self.marketBuyTotalValueLabel, 4, 1)
      parentLayout.addWidget(self.marketBuyButton, 5, 0, 1, 2)
      parentLayout.setMargin(15)
      parentLayout.setSpacing(10)
      parentLayout.setColumnStretch(0 ,1)
      parentLayout.setColumnStretch(1 ,3)
      parentLayout.setRowStretch(0, 2)
      parentLayout.setRowStretch(5, 2)


   # Market SELL Layout
   # ---------------------------------------------------
   def addMarketSellLayout(self, parentLayout):
      self.marketSellInfoLabel = QtGui.QLabel()
      self.marketSellInfoLabel.setStyleSheet('font: bold 16px;')

      self.marketSellBalanceLabel = QtGui.QLabel()
      self.marketSellBalanceAmountLabel = QtGui.QLabel()
      self.marketSellBalanceLabel.setObjectName('grayedLabel')
      self.marketSellBalanceAmountLabel.setObjectName('grayedLabel')

      marketSellPriceLabel = QtGui.QLabel('Price:')
      marketSellPriceLabel.setObjectName('grayedLabel')
      self.marketSellPriceInput = QtGui.QLineEdit()
      self.marketSellPriceInput.setText('Market price')
      self.marketSellPriceInput.setDisabled(True)
      self.marketSellPriceInput.setObjectName('disabledInput')

      marketSellAmountLabel = QtGui.QLabel('Amount:')
      self.marketSellAmountInput = QtGui.QLineEdit()

      marketSellTotalLabel = QtGui.QLabel('Total:')
      self.marketSellTotalValueLabel = QtGui.QLabel()
      marketSellTotalLabel.setObjectName('totalLabel')

      self.marketSellButton = QtGui.QPushButton()
      self.marketSellButton.setMinimumHeight(40)
      self.marketSellButton.setText('SELL')
      self.marketSellButton.setObjectName('marketSellButton')

      parentLayout.addWidget(self.marketSellInfoLabel, 0, 0)
      parentLayout.addWidget(self.marketSellBalanceLabel, 1, 0)
      parentLayout.addWidget(self.marketSellBalanceAmountLabel, 1, 1)
      parentLayout.addWidget(marketSellPriceLabel, 2, 0)
      parentLayout.addWidget(self.marketSellPriceInput, 2, 1)
      parentLayout.addWidget(marketSellAmountLabel, 3, 0)
      parentLayout.addWidget(self.marketSellAmountInput, 3, 1)
      parentLayout.addWidget(marketSellTotalLabel, 4, 0)
      parentLayout.addWidget(self.marketSellTotalValueLabel, 4, 1)
      parentLayout.addWidget(self.marketSellButton, 5, 0, 1, 2)
      parentLayout.setMargin(15)
      parentLayout.setSpacing(10)
      parentLayout.setColumnStretch(0 ,1)
      parentLayout.setColumnStretch(1 ,3)
      parentLayout.setRowStretch(0, 2)
      parentLayout.setRowStretch(5, 3)


   def setMarketData(self):
      self.marketBuyInfoLabel.setText('Buy BTC')
      self.marketBuyBalanceLabel.setText(('USD Balance:'))
      self.marketBuyBalanceAmountLabel.setText('1450.65')

      self.marketSellInfoLabel.setText('Sell BTC')
      self.marketSellBalanceLabel.setText(('BTC Balance:'))
      self.marketSellBalanceAmountLabel.setText('2.356')
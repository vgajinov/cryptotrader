from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot



class PlaceOrderWidget(QtWidgets.QWidget):
   restClient     = None
   baseCurrency   = ''
   quoteCurrency  = ''
   symbol_details = None
   marketBid      = None
   marketAsk      = None

   def __init__(self):
      super(PlaceOrderWidget, self).__init__()

      self.tabOrderLayout = QtWidgets.QHBoxLayout()
      self.tabOrderWidget = QtWidgets.QTabWidget()
      self.tabOrderWidget.setObjectName('placeOrderTabWidget')
      self.tabLimitOrder = QtWidgets.QWidget()
      self.tabMarketOrder = QtWidgets.QWidget()
      self.tabOrderWidget.addTab(self.tabLimitOrder, "Limit")
      self.tabOrderWidget.addTab(self.tabMarketOrder, "Market")
      self.tabOrderLayout.addWidget(self.tabOrderWidget)
      self.tabOrderLayout.setContentsMargins(0, 5, 0, 0)
      self.setLayout(self.tabOrderLayout)

      self.ctLimitOrderLayout = QtWidgets.QHBoxLayout(self.tabLimitOrder)
      self.ctMarketOrderLayout = QtWidgets.QHBoxLayout(self.tabMarketOrder)

      self.addLimitOrderLayout(self.ctLimitOrderLayout)
      self.addMarketOrderLayout(self.ctMarketOrderLayout)

      self.setLabels()


   # Limit Order Layout
   # ---------------------------------------------------
   def addLimitOrderLayout(self, parentLayout):
      self.ctLimitOrderBuyLayout = QtWidgets.QGridLayout()
      self.ctLimitOrderSellLayout = QtWidgets.QGridLayout()

      self.addLimitBuyLayout(self.ctLimitOrderBuyLayout)
      self.addLimitSellLayout(self.ctLimitOrderSellLayout)

      parentLayout.addLayout(self.ctLimitOrderBuyLayout, stretch=1)
      parentLayout.addLayout(self.ctLimitOrderSellLayout, stretch=1)
      parentLayout.setSpacing(10)


   # Limit BUY Layout
   # ---------------------------------------------------
   def addLimitBuyLayout(self, parentLayout):
      self.limitBuyInfoLabel = QtWidgets.QLabel()
      self.limitBuyInfoLabel.setStyleSheet('font: bold 16px;')

      self.limitBuyBalanceLabel = QtWidgets.QLabel()
      self.limitBuyBalanceAmountLabel = QtWidgets.QLabel()
      self.limitBuyBalanceLabel.setObjectName('grayedLabel')
      self.limitBuyBalanceAmountLabel.setObjectName('grayedLabel')

      limitBuyPriceLabel = QtWidgets.QLabel('Price:')
      self.limitBuyPriceInput = QtWidgets.QLineEdit()
      self.limitBuyPriceInput.setValidator(QtGui.QDoubleValidator(0, 100000.0, 2))

      limitBuyAmountLabel = QtWidgets.QLabel('Amount:')
      self.limitBuyAmountInput = QtWidgets.QLineEdit()

      limitBuyTotalLabel = QtWidgets.QLabel('Total:')
      self.limitBuyTotalValueLabel = QtWidgets.QLabel()
      limitBuyTotalLabel.setObjectName('totalLabel')

      self.limitBuyButton = QtWidgets.QPushButton()
      self.limitBuyButton.setMinimumHeight(40)
      self.limitBuyButton.setText('BUY')
      self.limitBuyButton.setObjectName('buyButton')

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

      self.limitBuyPriceInput.textChanged.connect(self.LimitBuyDataChange)
      self.limitBuyAmountInput.textChanged.connect(self.LimitBuyDataChange)

   def LimitBuyDataChange(self):
      if self.limitBuyPriceInput.text() != '' and self.limitBuyAmountInput.text() != '':
         self.limitBuyTotalValueLabel.setText('{}'.format( float(self.limitBuyPriceInput.text()) *
                                                           float(self.limitBuyAmountInput.text()) ))


   # Limit SELL Layout
   # ---------------------------------------------------
   def addLimitSellLayout(self, parentLayout):
      self.limitSellInfoLabel = QtWidgets.QLabel()
      self.limitSellInfoLabel.setStyleSheet('font: bold 16px;')

      self.limitSellBalanceLabel = QtWidgets.QLabel()
      self.limitSellBalanceAmountLabel = QtWidgets.QLabel()
      self.limitSellBalanceLabel.setObjectName('grayedLabel')
      self.limitSellBalanceAmountLabel.setObjectName('grayedLabel')

      limitSellPriceLabel = QtWidgets.QLabel('Price:')
      self.limitSellPriceInput = QtWidgets.QLineEdit()
      self.limitSellPriceInput.setValidator(QtGui.QDoubleValidator(0, 100000.0, 2))

      limitSellAmountLabel = QtWidgets.QLabel('Amount:')
      self.limitSellAmountInput = QtWidgets.QLineEdit()

      limitSellTotalLabel = QtWidgets.QLabel('Total:')
      self.limitSellTotalValueLabel = QtWidgets.QLabel()
      limitSellTotalLabel.setObjectName('totalLabel')

      self.limitSellButton = QtWidgets.QPushButton()
      self.limitSellButton.setMinimumHeight(40)
      self.limitSellButton.setText('SELL')
      self.limitSellButton.setObjectName('sellButton')

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

      self.limitSellPriceInput.textChanged.connect(self.LimitSellDataChange)
      self.limitSellAmountInput.textChanged.connect(self.LimitSellDataChange)

   def LimitSellDataChange(self):
      if self.limitSellPriceInput.text() != '' and self.limitSellAmountInput.text() != '':
         self.limitSellTotalValueLabel.setText('{}'.format( float(self.limitSellPriceInput.text()) *
                                                            float(self.limitSellAmountInput.text()) ))


   # Market Order Layout
   # ---------------------------------------------------
   def addMarketOrderLayout(self, parentLayout):
      self.ctMarketOrderBuyLayout = QtWidgets.QGridLayout()
      self.ctMarketOrderSellLayout = QtWidgets.QGridLayout()

      self.addMarketBuyLayout(self.ctMarketOrderBuyLayout)
      self.addMarketSellLayout(self.ctMarketOrderSellLayout)

      parentLayout.addLayout(self.ctMarketOrderBuyLayout, stretch=1)
      parentLayout.addLayout(self.ctMarketOrderSellLayout, stretch=1)
      parentLayout.setSpacing(10)


   # Market BUY Layout
   # ---------------------------------------------------
   def addMarketBuyLayout(self, parentLayout):
      self.marketBuyInfoLabel = QtWidgets.QLabel()
      self.marketBuyInfoLabel.setStyleSheet('font: bold 16px;')

      self.marketBuyBalanceLabel = QtWidgets.QLabel()
      self.marketBuyBalanceAmountLabel = QtWidgets.QLabel()
      self.marketBuyBalanceLabel.setObjectName('grayedLabel')
      self.marketBuyBalanceAmountLabel.setObjectName('grayedLabel')

      marketBuyPriceLabel = QtWidgets.QLabel('Price:')
      marketBuyPriceLabel.setObjectName('grayedLabel')
      self.marketBuyPriceInput = QtWidgets.QLineEdit()
      self.marketBuyPriceInput.setText('Market price')
      self.marketBuyPriceInput.setDisabled(True)
      self.marketBuyPriceInput.setObjectName('disabledInput')

      marketBuyAmountLabel = QtWidgets.QLabel('Amount:')
      self.marketBuyAmountInput = QtWidgets.QLineEdit()

      marketBuyTotalLabel = QtWidgets.QLabel('Total:')
      self.marketBuyTotalValueLabel = QtWidgets.QLabel()
      marketBuyTotalLabel.setObjectName('totalLabel')

      self.marketBuyButton = QtWidgets.QPushButton()
      self.marketBuyButton.setMinimumHeight(40)
      self.marketBuyButton.setText('BUY')
      self.marketBuyButton.setObjectName('buyButton')

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

      self.marketBuyAmountInput.textChanged.connect(self.MarketBuyDataChange)


   def MarketBuyDataChange(self):
      if self.marketBuyPriceInput.text() != '' and self.marketSellAmountInput.text() != '':
         self.marketBuyTotalValueLabel.setText('{}'.format( float(self.marketBuyPriceInput.text()) *
                                                            float(self.marketBuyAmountInput.text()) ))


   # Market SELL Layout
   # ---------------------------------------------------
   def addMarketSellLayout(self, parentLayout):
      self.marketSellInfoLabel = QtWidgets.QLabel()
      self.marketSellInfoLabel.setStyleSheet('font: bold 16px;')

      self.marketSellBalanceLabel = QtWidgets.QLabel()
      self.marketSellBalanceAmountLabel = QtWidgets.QLabel()
      self.marketSellBalanceLabel.setObjectName('grayedLabel')
      self.marketSellBalanceAmountLabel.setObjectName('grayedLabel')

      marketSellPriceLabel = QtWidgets.QLabel('Price:')
      marketSellPriceLabel.setObjectName('grayedLabel')
      self.marketSellPriceInput = QtWidgets.QLineEdit()
      self.marketSellPriceInput.setText('Market price')
      self.marketSellPriceInput.setDisabled(True)
      self.marketSellPriceInput.setObjectName('disabledInput')

      marketSellAmountLabel = QtWidgets.QLabel('Amount:')
      self.marketSellAmountInput = QtWidgets.QLineEdit()

      marketSellTotalLabel = QtWidgets.QLabel('Total:')
      self.marketSellTotalValueLabel = QtWidgets.QLabel()
      marketSellTotalLabel.setObjectName('totalLabel')

      self.marketSellButton = QtWidgets.QPushButton()
      self.marketSellButton.setMinimumHeight(40)
      self.marketSellButton.setText('SELL')
      self.marketSellButton.setObjectName('sellButton')

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

      self.marketSellAmountInput.textChanged.connect(self.MarketSellDataChange)


   def MarketSellDataChange(self):
      if self.marketSellPriceInput.text() != '' and self.marketSellAmountInput.text() != '':
         self.marketSellTotalValueLabel.setText('{}'.format( float(self.marketSellPriceInput.text()) *
                                                             float(self.marketSellAmountInput.text()) ))


   # ------------------------------------------------------------------------------------
   # Event Handlers
   # ------------------------------------------------------------------------------------




   # ------------------------------------------------------------------------------------
   # Data setters
   # ------------------------------------------------------------------------------------

   def setLabels(self):
      self.limitBuyInfoLabel.setText('Buy  {}'.format(self.baseCurrency))
      self.limitSellInfoLabel.setText('Sell  {}'.format(self.quoteCurrency))
      self.marketBuyInfoLabel.setText('Buy  {}'.format(self.baseCurrency))
      self.marketSellInfoLabel.setText('Sell  {}'.format(self.quoteCurrency))

   def setBalances(self):
      balances = self.parent().restClient.balance()
      self.marketBuyBalanceLabel.setText('{} Balance:'.format(self.baseCurrency))
      self.marketBuyBalanceAmountLabel.setText('{}'.format(balances[self.baseCurrency]))
      self.limitBuyBalanceLabel.setText('{} Balance:'.format(self.baseCurrency))
      self.limitBuyBalanceAmountLabel.setText('{}'.format(balances[self.baseCurrency]))

      self.marketSellBalanceLabel.setText('{} Balance:'.format(self.quoteCurrency))
      self.marketSellBalanceAmountLabel.setText('{}'.format(balances[self.quoteCurrency]))
      self.limitSellBalanceLabel.setText('{} Balance:'.format(self.quoteCurrency))
      self.limitSellBalanceAmountLabel.setText('{}'.format(balances[self.quoteCurrency]))


   def setData(self, base_currency, quote_currency, symbol_details):
      self.baseCurrency = base_currency
      self.quoteCurrency = quote_currency
      self.symbol_details = symbol_details

      self.setLabels()
      # self.setBalances()

   def setTicker(self, ticker):
      self.marketBid = ticker[0]
      self.marketAsk = ticker[2]
      self.marketBuyPriceInput.setText('{}'.format(ticker[2]))
      self.marketSellPriceInput.setText('{}'.format(ticker[0]))








import math
from PyQt5 import QtCore, QtWidgets, QtGui



class AmountValidator(QtGui.QDoubleValidator):
   def __init__(self, minAmount, maxAmount, precision):
      super(AmountValidator,self).__init__(minAmount, maxAmount, precision)
      self.baseValidator = QtGui.QDoubleValidator(minAmount, maxAmount, precision)
      self.setNotation(QtGui.QDoubleValidator.StandardNotation)

   def validate(self, p_str, p_int):
      baseValidate = self.baseValidator.validate(p_str, p_int)
      print(p_str, p_int, baseValidate)
      if baseValidate[0] == QtGui.QDoubleValidator.Invalid:
         return baseValidate

      if '.' in p_str:
         if len(p_str.split('.')[1]) > self.decimals():
            return (QtGui.QDoubleValidator.Invalid, p_str[:-1], p_int-1)
      return (QtGui.QValidator.Acceptable, p_str, p_int)


# ------------------------------------------------------------------------------------
# OrderFormWidget
# ------------------------------------------------------------------------------------

class OrderFormWidget(QtWidgets.QWidget):
   amountPrecision = 8
   pricePrecision  = 8

   def __init__(self, orderSide):
      super(OrderFormWidget, self).__init__()


      self.infoLabel = QtWidgets.QLabel()
      self.infoLabel.setStyleSheet('font: bold 16px;')

      self.balanceLabel = QtWidgets.QLabel()
      self.balanceLabel.setObjectName('grayedLabel')
      self.balanceAmountLabel = QtWidgets.QLabel()
      self.balanceAmountLabel.setObjectName('grayedLabel')

      priceLabel = QtWidgets.QLabel('Price:')
      self.priceInput = QtWidgets.QLineEdit()

      amountLabel = QtWidgets.QLabel('Amount:')
      self.amountInput = QtWidgets.QLineEdit()

      totalLabel = QtWidgets.QLabel('Total:')
      self.totalValueLabel = QtWidgets.QLabel()
      totalLabel.setObjectName('totalLabel')

      self.executeButton = QtWidgets.QPushButton()
      self.executeButton.setMinimumHeight(40)
      self.executeButton.setText(orderSide)
      self.executeButton.setObjectName(orderSide.lower() + 'Button')

      formLayout = QtWidgets.QGridLayout()
      self.setLayout(formLayout)

      formLayout.addWidget(self.infoLabel, 0, 0)
      formLayout.addWidget(self.balanceLabel, 1, 0)
      formLayout.addWidget(self.balanceAmountLabel, 1, 1)
      formLayout.addWidget(priceLabel, 2, 0)
      formLayout.addWidget(self.priceInput, 2, 1)
      formLayout.addWidget(amountLabel, 3, 0)
      formLayout.addWidget(self.amountInput, 3, 1)
      formLayout.addWidget(totalLabel, 4, 0)
      formLayout.addWidget(self.totalValueLabel, 4, 1)
      formLayout.addWidget(self.executeButton, 5, 0, 1, 2)
      formLayout.setMargin(15)
      formLayout.setSpacing(10)
      formLayout.setColumnStretch(0 ,1)
      formLayout.setColumnStretch(1 ,3)
      formLayout.setRowStretch(0, 2)
      formLayout.setRowStretch(5, 2)

      self.priceInput.textChanged.connect(self.dataChange)
      self.amountInput.textChanged.connect(self.dataChange)

   def dataChange(self):
      if self.priceInput.text() != '' and self.amountInput.text() != '':
         self.totalValueLabel.setText(
            '{:.{prec}f}'.format( float(self.priceInput.text()) * float(self.amountInput.text()),
                                  prec=self.pricePrecision )
         )

   def setPrecision(self, minAmount, priceP):
      leftDigits, rightDigits = str(minAmount).split('.')
      amountPrec = len(rightDigits.rstrip('0'))

      self.amountPrecision = amountPrec
      self.pricePrecision  = priceP

      self.amountInput.setValidator(AmountValidator(float(minAmount), 100000.0*float(minAmount), amountPrec))




# ------------------------------------------------------------------------------------
# PlaceOrderWidget
# ------------------------------------------------------------------------------------

class PlaceOrderWidget(QtWidgets.QWidget):
   restClient     = None
   baseCurrency   = ''
   quoteCurrency  = ''
   symbol_details = None


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

      self.addLimitOrderLayout()
      self.addMarketOrderLayout()

      self.setLabels()


   # Limit Order Layout
   # ---------------------------------------------------
   def addLimitOrderLayout(self):
      self.limitOrderBuyWidget = OrderFormWidget('BUY')
      self.limitOrderSellWidget = OrderFormWidget('SELL')

      limitOrderLayout = QtWidgets.QHBoxLayout(self.tabLimitOrder)
      limitOrderLayout.addWidget(self.limitOrderBuyWidget,  stretch=1)
      limitOrderLayout.addWidget(self.limitOrderSellWidget, stretch=1)
      limitOrderLayout.setSpacing(10)


   # Market Order Layout
   # ---------------------------------------------------
   def addMarketOrderLayout(self):
      self.marketOrderBuyWidget = OrderFormWidget('BUY')
      self.marketOrderSellWidget = OrderFormWidget('SELL')

      self.marketOrderBuyWidget.priceInput.setText('0.0')
      self.marketOrderBuyWidget.priceInput.setDisabled(True)
      self.marketOrderBuyWidget.priceInput.setObjectName('disabledInput')

      self.marketOrderSellWidget.priceInput.setText('0.0')
      self.marketOrderSellWidget.priceInput.setDisabled(True)
      self.marketOrderSellWidget.priceInput.setObjectName('disabledInput')

      marketOrderLayout = QtWidgets.QHBoxLayout(self.tabMarketOrder)
      marketOrderLayout.addWidget(self.marketOrderBuyWidget,  stretch=1)
      marketOrderLayout.addWidget(self.marketOrderSellWidget, stretch=1)
      marketOrderLayout.setSpacing(10)



   # ------------------------------------------------------------------------------------
   # Event Handlers
   # ------------------------------------------------------------------------------------




   # ------------------------------------------------------------------------------------
   # Data setters
   # ------------------------------------------------------------------------------------

   def setLabels(self):
      self.limitOrderBuyWidget.infoLabel.setText('Buy  {}'.format(self.baseCurrency))
      self.limitOrderSellWidget.infoLabel.setText('Sell  {}'.format(self.quoteCurrency))
      self.marketOrderBuyWidget.infoLabel.setText('Buy  {}'.format(self.baseCurrency))
      self.marketOrderSellWidget.infoLabel.setText('Sell  {}'.format(self.quoteCurrency))


   def setPrecisions(self):
      minAmount = self.symbol_details['minAmount']
      pricePrec = None
      pPrec = self.symbol_details.get('minPrice', None)
      if pPrec is not None:
         pricePrec = int(abs(math.log10(float(pPrec))))

      self.limitOrderBuyWidget.setPrecision(minAmount, pricePrec)
      self.limitOrderSellWidget.setPrecision(minAmount, pricePrec)
      self.marketOrderBuyWidget.setPrecision(minAmount, pricePrec)
      self.marketOrderSellWidget.setPrecision(minAmount, pricePrec)


   def setBalances(self):
      balances = self.parent().restClient.balance()
      self.marketOrderBuyWidget.balanceLabel.setText('{} Balance:'.format(self.baseCurrency))
      self.marketOrderBuyWidget.balanceAmountLabel.setText('{}'.format(balances[self.baseCurrency]))
      self.limitOrderBuyWidget.balanceLabel.setText('{} Balance:'.format(self.baseCurrency))
      self.limitOrderBuyWidget.balanceAmountLabel.setText('{}'.format(balances[self.baseCurrency]))

      self.marketOrderSellWidget.balanceLabel.setText('{} Balance:'.format(self.quoteCurrency))
      self.marketOrderSellWidget.balanceAmountLabel.setText('{}'.format(balances[self.quoteCurrency]))
      self.limitOrderSellWidget.balanceLabel.setText('{} Balance:'.format(self.quoteCurrency))
      self.limitOrderSellWidget.balanceAmountLabel.setText('{}'.format(balances[self.quoteCurrency]))


   # ------------------------------------------------------------------------------------
   # Data update methods (from parent)
   # ------------------------------------------------------------------------------------

   def setData(self, base_currency, quote_currency, symbol_details, ticker):
      self.baseCurrency = base_currency
      self.quoteCurrency = quote_currency
      self.symbol_details = symbol_details

      self.setLabels()
      self.setPrecisions()
      self.setBalances()


   def setTicker(self, ticker):
      self.marketOrderBuyWidget.priceInput.setText('{}'.format(ticker[2]))
      self.marketOrderSellWidget.priceInput.setText('{}'.format(ticker[0]))








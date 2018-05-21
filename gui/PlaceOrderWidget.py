import math
from enum import Enum
from PyQt5 import QtCore, QtWidgets, QtGui
from .InfoMessageBox import InfoMessageBox



class InputValidator(QtGui.QDoubleValidator):
   def __init__(self, minAmount, maxAmount, precision):
      super(InputValidator, self).__init__(minAmount, maxAmount, precision)
      self.baseValidator = QtGui.QDoubleValidator(minAmount, maxAmount, precision)
      self.setNotation(QtGui.QDoubleValidator.StandardNotation)

   def validate(self, p_str, p_int):
      baseValidate = self.baseValidator.validate(p_str, p_int)
      if baseValidate[0] == QtGui.QDoubleValidator.Invalid:
         return baseValidate

      if '.' in p_str:
         if len(p_str.split('.')[1]) > self.decimals():
            return (QtGui.QDoubleValidator.Invalid, p_str[:-1], p_int-1)
      return (QtGui.QValidator.Acceptable, p_str, p_int)


# ------------------------------------------------------------------------------------
# AmountLineEdit
# ------------------------------------------------------------------------------------

class AmountLineEdit(QtWidgets.QLineEdit):
   maxValue  = ''
   precision = 8

   def __init__(self):
      super(AmountLineEdit, self).__init__()

   def setMaxAmountLabel(self, label):
      self.maxLabel = label

   def setPrecision(self, prec):
      self.precision = prec

   def focusInEvent(self, event):
      if self.maxValue != '':
         self.maxLabel.setText( 'max:   {:.{prec}f}'.format(float(self.maxValue), prec=self.precision) )
         self.maxLabel.setStyleSheet('color: blue;')
      event.accept()

   def focusOutEvent(self, event):
      self.maxLabel.setStyleSheet('color: black;')
      event.accept()


# ------------------------------------------------------------------------------------
# OrderFormWidget
# ------------------------------------------------------------------------------------

class OrderSide(Enum):
   BUY  = 0
   SELL = 1

class OrderFormWidget(QtWidgets.QWidget):
   amountPrecision = 8
   pricePrecision  = 8
   orderSide       = OrderSide.BUY

   def __init__(self, orderSide, name):
      super(OrderFormWidget, self).__init__()

      self.setObjectName(name)
      self.orderSide = orderSide

      self.infoLabel = QtWidgets.QLabel()
      self.infoLabel.setStyleSheet('font: bold 16px;')

      self.balanceLabel = QtWidgets.QLabel()
      self.balanceLabel.setObjectName('grayedLabel')
      self.balanceAmountLabel = QtWidgets.QLabel()
      self.balanceAmountLabel.setObjectName('grayedLabel')

      priceLabel = QtWidgets.QLabel('Price:')
      self.priceInput = QtWidgets.QLineEdit()

      amountLabel = QtWidgets.QLabel('Amount:')
      self.amountInput = AmountLineEdit()

      self.maxAmountLabel =  QtWidgets.QLabel('max amount')
      self.maxAmountLabel.setStyleSheet('color: black;')
      self.maxAmountLabel.setFixedHeight(10)
      self.amountInput.setMaxAmountLabel(self.maxAmountLabel)

      totalLabel = QtWidgets.QLabel('Total:')
      self.totalValueLabel = QtWidgets.QLabel()
      totalLabel.setObjectName('totalLabel')

      self.executeButton = QtWidgets.QPushButton()
      self.executeButton.setMinimumHeight(40)
      self.executeButton.setText(orderSide.name)
      self.executeButton.setObjectName(orderSide.name.lower() + 'Button')

      formLayout = QtWidgets.QGridLayout()
      self.setLayout(formLayout)

      formLayout.addWidget(self.infoLabel, 0, 0)
      formLayout.addWidget(self.balanceLabel, 1, 0)
      formLayout.addWidget(self.balanceAmountLabel, 1, 1)
      formLayout.addWidget(priceLabel, 2, 0)
      formLayout.addWidget(self.priceInput, 2, 1)
      formLayout.addWidget(amountLabel, 3, 0)
      formLayout.addWidget(self.amountInput, 3, 1)
      formLayout.addWidget(self.maxAmountLabel, 4, 1)
      formLayout.addWidget(totalLabel, 5, 0)
      formLayout.addWidget(self.totalValueLabel, 5, 1)
      formLayout.addWidget(self.executeButton, 6, 0, 1, 2)

      formLayout.setMargin(15)
      formLayout.setVerticalSpacing(10)
      formLayout.setColumnStretch(0 ,2)
      formLayout.setColumnStretch(1 ,3)
      formLayout.setRowStretch(0, 2)
      formLayout.setRowStretch(6, 2)

      self.priceInput.textChanged.connect(self.dataChange)
      self.amountInput.textChanged.connect(self.dataChange)


   def dataChange(self):
      if self.priceInput.text() != '':
         price = float(self.priceInput.text())
         if price != 0 and self.balanceAmountLabel.text() != '':
            if self.orderSide == OrderSide.BUY:
               maxAmount = float(self.balanceAmountLabel.text()) / float(self.priceInput.text())
            else:
               maxAmount = float(self.balanceAmountLabel.text())
            self.amountInput.maxValue = '{:.{prec}f}'.format(maxAmount, prec=self.pricePrecision)


         if self.amountInput.text() != '':
            self.totalValueLabel.setText(
               '{:.{prec}f}'.format( float(self.priceInput.text()) * float(self.amountInput.text()),
                                     prec=self.pricePrecision )
            )

      try:
         if float(self.totalValueLabel.text()) > float(self.balanceAmountLabel.text()):
            self.totalValueLabel.setStyleSheet('color: red;')
         else:
            self.totalValueLabel.setStyleSheet('color: lime;')
      except:
         pass


   def setPrecision(self, minAmount, pricePrec):
      minPrice = float(minAmount) * pow(10, pricePrec)
      amountPrec = 0
      if '.' in str(minAmount):
         leftDigits, rightDigits = str(minAmount).split('.')
         amountPrec = len(rightDigits.rstrip('0'))

      self.priceInput.setValidator(InputValidator(minPrice, 100000.0 * minPrice, pricePrec))
      self.amountInput.setValidator(InputValidator(float(minAmount), 100000.0 * float(minAmount), amountPrec))
      self.amountInput.setPrecision(amountPrec)


   def clear(self):
      self.priceInput.blockSignals(True)
      self.amountInput.blockSignals(True)
      self.priceInput.clear()
      self.amountInput.clear()
      self.totalValueLabel.clear()
      self.priceInput.blockSignals(False)
      self.amountInput.blockSignals(False)




# ------------------------------------------------------------------------------------
# PlaceOrderWidget
# ------------------------------------------------------------------------------------

class PlaceOrderWidget(QtWidgets.QWidget):
   restClient     = None
   baseCurrency   = ''
   quoteCurrency  = ''
   symbol_details = None
   balances       = None


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

      self.updateInfoLabels()


   # Limit Order Layout
   # ---------------------------------------------------
   def addLimitOrderLayout(self):
      self.limitOrderBuyWidget = OrderFormWidget(OrderSide.BUY, 'limitOrder')
      self.limitOrderSellWidget = OrderFormWidget(OrderSide.SELL, 'limitOrder')

      self.limitOrderBuyWidget.executeButton.clicked.connect(self.placeOrder)
      self.limitOrderSellWidget.executeButton.clicked.connect(self.placeOrder)

      limitOrderLayout = QtWidgets.QHBoxLayout(self.tabLimitOrder)
      limitOrderLayout.addWidget(self.limitOrderBuyWidget,  stretch=1)
      limitOrderLayout.addWidget(self.limitOrderSellWidget, stretch=1)
      limitOrderLayout.setSpacing(10)


   # Market Order Layout
   # ---------------------------------------------------
   def addMarketOrderLayout(self):
      self.marketOrderBuyWidget = OrderFormWidget(OrderSide.BUY, 'marketOrder')
      self.marketOrderSellWidget = OrderFormWidget(OrderSide.SELL, 'marketOrder')

      self.marketOrderBuyWidget.executeButton.clicked.connect(self.placeOrder)
      self.marketOrderSellWidget.executeButton.clicked.connect(self.placeOrder)

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
   # Event Handlers & Slots
   # ------------------------------------------------------------------------------------

   def placeOrder(self):
      sender = self.sender()

      if sender.objectName() == 'buyButton':
         side = 'BUY'
      elif sender.objectName() == 'sellButton':
         side = 'SELL'
      else:
         print('Unknown place order sender!')
         return

      pair = self.baseCurrency + self.quoteCurrency
      size = sender.parent().amountInput.text()
      price = sender.parent().priceInput.text()

      if float(size) * float(price) > float(sender.parent().balanceAmountLabel.text()):
         msg = InfoMessageBox('Insufficient balance!')
         msg.exec()
         return

      if sender.parent().objectName() == 'limitOrder':
         self.restClient.place_limit_order(side, pair, float(size), float(price))
      elif sender.parent().objectName() == 'marketOrder':
         self.restClient.place_market_order(side, pair, float(size))


   # ------------------------------------------------------------------------------------
   # Widget update methods
   # ------------------------------------------------------------------------------------

   def updateInfoLabels(self):
      self.limitOrderBuyWidget.infoLabel.setText('Buy  {}'.format(self.baseCurrency))
      self.limitOrderSellWidget.infoLabel.setText('Sell  {}'.format(self.baseCurrency))
      self.marketOrderBuyWidget.infoLabel.setText('Buy  {}'.format(self.baseCurrency))
      self.marketOrderSellWidget.infoLabel.setText('Sell  {}'.format(self.baseCurrency))


   def updatePrecisions(self):
      minAmount = self.symbol_details['minAmount']
      pricePrec = None
      pPrec = self.symbol_details.get('minPrice', None)
      if pPrec is not None:
         pricePrec = int(abs(math.log10(float(pPrec))))
      else:
         pricePrec = 8

      self.limitOrderBuyWidget.setPrecision(minAmount, pricePrec)
      self.limitOrderSellWidget.setPrecision(minAmount, pricePrec)
      self.marketOrderBuyWidget.setPrecision(minAmount, pricePrec)
      self.marketOrderSellWidget.setPrecision(minAmount, pricePrec)


   def updateBalanceLables(self):
      if self.baseCurrency and self.quoteCurrency and self.balances:
         quoteBalance = self.balances.get(self.quoteCurrency, '0.0')
         baseBalance  = self.balances.get(self.baseCurrency, '0.0')
         self.limitOrderBuyWidget.balanceLabel.setText('{} Balance:'.format(self.quoteCurrency))
         self.limitOrderBuyWidget.balanceAmountLabel.setText('{}'.format(quoteBalance))
         self.marketOrderBuyWidget.balanceLabel.setText('{} Balance:'.format(self.quoteCurrency))
         self.marketOrderBuyWidget.balanceAmountLabel.setText('{}'.format(quoteBalance))

         self.limitOrderSellWidget.balanceLabel.setText('{} Balance:'.format(self.baseCurrency))
         self.limitOrderSellWidget.balanceAmountLabel.setText('{}'.format(baseBalance))
         self.marketOrderSellWidget.balanceLabel.setText('{} Balance:'.format(self.baseCurrency))
         self.marketOrderSellWidget.balanceAmountLabel.setText('{}'.format(baseBalance))


   def clear(self):
      self.limitOrderBuyWidget.clear()
      self.limitOrderSellWidget.clear()
      self.marketOrderBuyWidget.clear()
      self.marketOrderSellWidget.clear()


   # ------------------------------------------------------------------------------------
   # Data update methods (from parent)
   # ------------------------------------------------------------------------------------

   def setSymbolDetails(self, base_currency, quote_currency, symbol_details, ticker):
      self.baseCurrency = base_currency
      self.quoteCurrency = quote_currency
      self.symbol_details = symbol_details

      self.updateInfoLabels()
      self.updatePrecisions()
      self.updateBalanceLables()


   def setTicker(self, ticker):
      self.marketOrderBuyWidget.priceInput.setText('{}'.format(ticker[2]))
      self.marketOrderSellWidget.priceInput.setText('{}'.format(ticker[0]))

   def setBalances(self, balances):
      self.balances = balances
      self.updateBalanceLables()

   def setClient(self, client):
      self.restClient = client





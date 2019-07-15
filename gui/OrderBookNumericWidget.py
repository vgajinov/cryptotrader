import math
from PyQt5 import QtCore, QtWidgets, QtGui
from .CustomTables import OrderBookTableView


# ======================================================================
# OrderBookNumericWidget class provides
# the OrderBook numeric column display
# ======================================================================

class OrderBookNumericWidget(QtWidgets.QWidget):
    """The widget for the order book numeric display"""

    symbol_details   = None
    price_precision  = None
    amount_precision = None

    def __init__(self):
        super(OrderBookNumericWidget, self).__init__()

        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # asks
        self.asksTable = OrderBookTableView(QtCore.Qt.red)
        self.asksTable.setObjectName('asksTable')

        # bids
        self.bidsTable = OrderBookTableView(QtCore.Qt.green)
        self.bidsTable.setObjectName('bidsTable')

        # last price
        self.priceLabel = QtWidgets.QLabel()
        self.priceLabel.setObjectName('lastPriceLabel')
        self.priceLabel.setAlignment(QtCore.Qt.AlignCenter)

        # add widgets to layout
        self.mainLayout.addWidget(self.asksTable)
        self.mainLayout.addWidget(self.priceLabel)
        self.mainLayout.addWidget(self.bidsTable)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)


    def setSymbolDetails(self, details):
        """Sets the symbol (pair details and determines price and amount precisions."""
        self.symbol_details = details

        left_digits, right_digits = str(details['minAmount']).split('.')
        self.amount_precision = len(right_digits.rstrip('0'))

        self.price_precision = None
        price_precision = details.get('minPrice', None)
        if price_precision:
            self.price_precision = int(abs(math.log10(float(price_precision))))


    # set OrderBook numeric data
    def setData(self, data):
        """Sets/updates the order book values
        :param data    order book snapshot or and update
        """
        if not data or not self.symbol_details:
            return

        asks = data['asks']
        bids = data['bids']

        # deduce price precision if we didn't get it from the exchange
        if not self.price_precision:
            price = next(iter(asks.keys()))
            exp = math.ceil(math.log10(float(price)))
            self.price_precision = min(abs(exp - int(self.symbol_details['precision'])), 8)

        total = 0.0
        asks_list = []
        for price, amount in list(asks.items()):
            total += abs(amount)
            asks_list.append([f'{price:.{self.price_precision}f}',
                              f'{abs(amount):,.{self.amount_precision}f}',
                              f'{total:,.{self.amount_precision}f}'])
        asks_list = list(reversed(asks_list))

        total = 0.0
        bid_list = []
        for price, amount in list(reversed(list(bids.items()))):
            total += abs(amount)
            bid_list.append([f'{price:.{self.price_precision}f}',
                             f'{abs(amount):,.{self.amount_precision}f}',
                             f'{total:,.{self.amount_precision}f}'])

        self.asksTable.model().setTableData(asks_list, True)
        self.bidsTable.model().setTableData(bid_list, False)


    def setLastPrice(self, price):
        """Sets the last price on the OrderBook numeric layout"""
        if self.price_precision is None:
            price_str = f'{price:.8f}'
            if len(price_str) > 9:
                price_str = price_str[:9]
        else:
            price_str = f'{price:.{self.price_precision}f}'
        self.priceLabel.setText(price_str)


    def formatLastPrice(self, height):
        """Format the font for the LastPrice label
        :param height:  the height of the display area in pixels
        :return:
        """
        self.priceLabel.setFixedHeight(height)
        font = QtGui.QFont(self.priceLabel.font())
        font.setPixelSize(int(0.7 * height))
        self.priceLabel.setFont(font)
        self.priceLabel.update()


    def clear(self):
        """Clears the widget"""
        self.priceLabel.clear()
        self.asksTable.model().clear()
        self.bidsTable.model().clear()


    # ------------------------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------------------------

    def resizeEvent(self, QResizeEvent):
        height = int(self.height() / 15)
        self.formatLastPrice(height)
        self.asksTable.setMaximumHeight(7 * height)
        self.bidsTable.setMaximumHeight(7 * height)
        QtWidgets.QWidget.resizeEvent(self, QResizeEvent)

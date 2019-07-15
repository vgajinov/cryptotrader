from PyQt5 import QtCore


# Exchange events
# ==========================================================================

class OrderBookUpdateEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, data):
        super().__init__(self.EVENT_TYPE)
        self.book = data


class TradesUpdateEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, trades):
        super().__init__(self.EVENT_TYPE)
        self.trades = trades


class TickerUpdateEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, ticker):
        super().__init__(self.EVENT_TYPE)
        self.ticker = ticker


class CandlesUpdateEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, candles):
        super().__init__(self.EVENT_TYPE)
        self.candles = candles


class OrdersUpdateEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, orders):
        super().__init__(self.EVENT_TYPE)
        self.orders = orders


class UserTradesUpdateEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, trades):
        super().__init__(self.EVENT_TYPE)
        self.trades = trades


class BalancesUpdateEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
    def __init__(self, balances):
        super().__init__(self.EVENT_TYPE)
        self.balances = balances

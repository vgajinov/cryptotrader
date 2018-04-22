from PyQt5 import QtCore




# Exchange events
# ==========================================================================

class OrderBookUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, bids, asks):
      super(OrderBookUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.bids = bids
      self.asks = asks

class TradesUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, trades):
      super(TradesUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.trades = trades

class TickerUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, ticker):
      super(TickerUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.ticker = ticker

class CandlesUpdateEvent(QtCore.QEvent):
   EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())
   def __init__(self, candles):
      super(CandlesUpdateEvent, self).__init__(self.EVENT_TYPE)
      self.candles = candles
import sys
from PyQt5 import QtWidgets
from gui.ATMainWindow import ATMainWindow
from pydispatch import dispatcher
from exchanges.exchangeWSFactory import ExchangeWSFactory


def info(sender, data):
   print(data)

if __name__ == '__main__':
   app = QtWidgets.QApplication(sys.argv)
   screenSize = app.desktop().screenGeometry()
   GUI = ATMainWindow(screenSize.width(), screenSize.height())
   GUI.show()

   # subsribe to the bitfinex OrderBook
   client = ExchangeWSFactory.create_client('Bitfinex')
   client.connect(info_handler=info)
   client.subscribe_ticker('BTCUSD', update_handler=GUI.updateTicker)
   client.subscribe_order_book('BTCUSD', update_handler=GUI.updateOrderBook)
   client.subscribe_trades('BTCUSD', update_handler=GUI.updateTrades)
   client.subscribe_candles('BTCUSD', update_handler=GUI.updateCandles)

   app.exec_()
   client.disconnect()




import sys
from PyQt5 import QtWidgets
from gui.ATMainWindow import ATMainWindow
from pydispatch import dispatcher
import exchanges.bitfinex.bitfinex_v2_WebSockets as bitfinexWS




if __name__ == '__main__':
   app = QtWidgets.QApplication(sys.argv)
   screenSize = app.desktop().screenGeometry()
   GUI = ATMainWindow(screenSize.width(), screenSize.height())
   GUI.show()

   # subsribe to the bitfinex OrderBook
   client = bitfinexWS.BitfinexWSClient()
   client.connect()
   dispatcher.connect(GUI.updateOrderBook, sender='bitfinex', signal='book_BTCUSD')
   dispatcher.connect(GUI.updateCandles, sender='bitfinex', signal='candles_BTCUSD')
   dispatcher.connect(GUI.updateTrades, sender='bitfinex', signal='trades_BTCUSD')
   #dispatcher.connect(GUI.updateTicker, sender='bitfinex', signal='ticker_BTCUSD')

   app.exec_()
   client.disconnect()




import sys
from PyQt4 import QtGui
from gui.ATMainWindow import ATMainWindow
from pydispatch import dispatcher
import exchanges.bitfinex.bitfinex_v2_WebSockets as bitfinexWS



# =================================================================================
#   Run qt app
# =================================================================================
def run():
   app = QtGui.QApplication(sys.argv)
   screenSize = app.desktop().screenGeometry()
   GUI = ATMainWindow(screenSize.width(), screenSize.height())
   GUI.show()

   # subsribe to the bitfinex OrderBook
   client = bitfinexWS.BitfinexWSClient()
   client.connect()
   dispatcher.connect(GUI.updateOrderBook, sender='bitfinex', signal='book_BTCUSD')
   #dispatcher.connect(GUI.updateCandles, sender='bitfinex', signal='candles_BTCUSD')
   dispatcher.connect(GUI.updateTrades, sender='bitfinex', signal='trades_BTCUSD')
   #dispatcher.connect(GUI.updateTicker, sender='bitfinex', signal='ticker_BTCUSD')

   app.exec_()
   client.disconnect()



run()
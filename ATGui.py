import sys
from PyQt4 import QtGui
from gui import ATMainWindow
from gui.ATMainWindow import *





# =================================================================================
#   Run qt app
# =================================================================================
def run():
   app = QtGui.QApplication(sys.argv)
   screenSize = app.desktop().screenGeometry()
   GUI = ATMainWindow(screenSize.width(), screenSize.height())
   GUI.show()
   sys.exit(app.exec_())


run()
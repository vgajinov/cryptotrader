import sys
from PyQt5 import QtWidgets
from gui.ATMainWindow import ATMainWindow


def info(sender, data):
   print(data)

if __name__ == '__main__':
   app = QtWidgets.QApplication(sys.argv)
   screenSize = app.desktop().screenGeometry()
   GUI = ATMainWindow(screenSize.width(), screenSize.height())
   GUI.show()
   app.exec_()





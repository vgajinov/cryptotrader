import sys
from PyQt5 import QtWidgets
from gui.ATMainWindow import ATMainWindow


def info(sender, data):
    print(data)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    screen_size = app.desktop().screenGeometry()
    gui = ATMainWindow(screen_size.width(), screen_size.height())
    gui.show()
    app.exec_()





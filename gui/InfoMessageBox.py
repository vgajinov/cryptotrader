from PyQt5 import QtCore, QtWidgets, QtGui


class InfoMessageBox(QtWidgets.QMessageBox):
    def __init__(self, info):
        super(InfoMessageBox, self).__init__()
        self.setText("<p align='center'>" + info)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        maxLenLine = max(info.split('<br />'), key=len)
        font = QtGui.QFont(self.font())
        font.setPixelSize(20)
        fm = QtGui.QFontMetrics(font)
        infoWidth = fm.width(maxLenLine)

        style  = 'QMessageBox {background: yellow; border: 1px white; padding: 0; margin 0;} '
        style += 'QLabel {min-width: ' + '{}'.format(infoWidth+40) + 'px; font-size: 20px; padding: 0; margin 0;} '
        style += 'QPushButton { min-width: ' + '{}'.format(infoWidth+50) + 'px; font-size: 20px; background: white;}'

        self.setStyleSheet(style)

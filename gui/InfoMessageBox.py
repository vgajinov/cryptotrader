from PyQt5 import QtCore, QtWidgets, QtGui


class InfoMessageBox(QtWidgets.QMessageBox):
    """Custom info message box."""
    def __init__(self, info):
        super(InfoMessageBox, self).__init__()
        self.setText("<p align='center'>" + info)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        max_line_length = max(info.split('<br />'), key=len)
        font = QtGui.QFont(self.font())
        font.setPixelSize(20)
        fm = QtGui.QFontMetrics(font)
        info_width = fm.width(max_line_length)

        style  = 'QMessageBox {background: yellow; border: 1px white; padding: 0; margin 0;} '
        style += 'QLabel {min-width: ' + '{}'.format(info_width+40) + 'px; font-size: 20px; padding: 0; margin 0;} '
        style += 'QPushButton { min-width: ' + '{}'.format(info_width+50) + 'px; font-size: 20px; background: white;}'

        self.setStyleSheet(style)

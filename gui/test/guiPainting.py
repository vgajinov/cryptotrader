import sys
import string
import random
from PyQt5 import QtCore, QtWidgets, QtGui

class Delegate(QtWidgets.QStyledItemDelegate):
    def __init__(self):
        QtWidgets.QStyledItemDelegate.__init__(self)

    def paint(self, painter, option, index):
        painter.save()
        left_rect = QtCore.QRect(option.rect.left(), option.rect.top(),
                                 option.rect.width() / 2, option.rect.height())
        left_brush = QtGui.QBrush(QtCore.Qt.red)
        painter.fillRect(left_rect, left_brush)
        right_rect = QtCore.QRect(option.rect.left() + option.rect.width() / 2,
                                  option.rect.top(), option.rect.width() / 2,
                                  option.rect.height())
        right_brush = QtGui.QBrush(QtCore.Qt.blue)
        painter.fillRect(right_rect, right_brush)
        painter.restore()
        adjusted_option = option
        adjusted_option.backgroundBrush = QtGui.QBrush(QtCore.Qt.NoBrush)
        QtWidgets.QStyledItemDelegate.paint(self, painter, adjusted_option, index)

class Model(QtCore.QAbstractTableModel):
    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self)
        self.column_names = [ "First",
                              "Second",
                              "Third",
                              "Fourth" ]
        self.text_data = []
        for i in range(0, 10):
            row_data = []
            for j in range(0, len(self.column_names)):
                row_data.append(''.join(random.choice(string.ascii_uppercase +
                                        string.digits) for _ in range(6)))
            self.text_data.append(row_data)

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return len(self.text_data)

    def columnCount(self, parent):
        return len(self.column_names)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role != QtCore.Qt.DisplayRole:
            return None

        row = index.row()
        if row < 0 or row >= len(self.text_data):
            return None

        column = index.column()
        if column < 0 or column >= len(self.column_names):
            return None

        return self.text_data[row][column]

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation != QtCore.Qt.Horizontal:
            return None
        if section < 0 or section >= len(self.column_names):
            return None
        else:
            return self.column_names[section]

class MainForm(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.model = Model()
        self.delegate = Delegate()
        self.view = QtWidgets.QTableView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(self.delegate)
        self.setCentralWidget(self.view)

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MainForm()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
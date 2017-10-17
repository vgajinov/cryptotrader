from PyQt4.QtCore import Qt, QRect
from PyQt4.QtGui import QTableWidget, QApplication, QHeaderView, QStyleOptionButton, QStyle

import sys

class MyHeader(QHeaderView):

    isOn = False

    def __init__(self, orientation, parent=None):
        QHeaderView.__init__(self, orientation, parent)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        QHeaderView.paintSection(self, painter, rect, logicalIndex)
        painter.restore()

        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(10, 10, 10, 10)
            if self.isOn:
                option.state = QStyle.State_On
            else:
                option.state = QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        self.isOn = not self.isOn
        self.updateSection(0)
        QHeaderView.mousePressEvent(self, event)

class MyTable(QTableWidget):
    def __init__(self):
        QTableWidget.__init__(self, 3, 3)

        myHeader = MyHeader(Qt.Horizontal, self)
        self.setHorizontalHeader(myHeader)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myTable = MyTable()
    myTable.show()
    sys.exit(app.exec_())
from PyQt5 import QtGui, QtWidgets, QtCore
import operator
import os



class MyTableModel(QtCore.QAbstractTableModel):
   def __init__(self, header=None, data=None):
      super(MyTableModel, self).__init__()
      self.header = header
      self.tableData = data

   def rowCount(self, parent=None, *args, **kwargs):
      return len(self.tableData)

   def columnCount(self, parent=None, *args, **kwargs):
      return len(self.tableData[0])

   def data(self, index, role):
      if role == QtCore.Qt.DisplayRole:
         return self.tableData[index.row()][index.column()]

   def headerData(self, col, orientation, role):
      if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
         return self.header[col]
      return None

   def sort(self, col, order):
      """sort table by given column number col"""
      if col != 0:
         self.layoutAboutToBeChanged.emit()
         self.tableData = sorted(self.tableData, key=operator.itemgetter(col))
         if order == QtCore.Qt.DescendingOrder:
            self.tableData.reverse()
         self.layoutChanged.emit()


# ==================================================================================================

class MyHeader(QtWidgets.QHeaderView):
   def __init__(self, combo=None):
      super(MyHeader, self).__init__(QtCore.Qt.Horizontal)
      self.sectionResized.connect(self.handleSectionResized)
      self.setSectionsMovable(False)
      self.setMinimumHeight(30)
      self.setSectionsClickable(True)

      self.combo = combo


   def showEvent(self, event):
      self.combo.setGeometry(self.sectionViewportPosition(0) + 5, 3, 60, self.height()-6)
      self.combo.show()
      QtWidgets.QHeaderView.showEvent(self, event)


   def handleSectionResized(self, col):
      if col == 0:
         self.combo.setGeometry(self.sectionViewportPosition(0) + 3, 5, 60, self.height()-6)




def pairComboTextChanged(text):
   print(text)

# ==================================================================================================

class ControlComboBox(QtWidgets.QComboBox):
   def __init__(self):
      super(ControlComboBox, self).__init__()

      # this is unsuccessful try to make the popup background translucent
      # self.view().setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint);
      # self.view().setParent(None);
      # self.view().setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
      # self.view().setAttribute(QtCore.Qt.WA_TranslucentBackground, True)


   def showPopup(self):
      super(ControlComboBox, self).showPopup()
      popup = self.findChild(QtWidgets.QFrame)
      # set popup position bellow combobox
      itemHeight = self.view().visualRect(self.model().index(1,0)).height()
      popup.move(popup.x(), self.frameGeometry().bottomLeft().y()+self.height())
      popup.setMaximumHeight(5 * itemHeight)


class MainWindow(QtWidgets.QMainWindow):
   def __init__(self, width, height):
      super(MainWindow, self).__init__()

      self.resize(width, height)
      self.setWindowTitle('ComboBox')
      mainWidget = QtWidgets.QWidget()
      self.setCentralWidget(mainWidget)

      self.combo = ControlComboBox()
      self.combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.combo.setObjectName('testCombo')

      self.pairCombo = QtWidgets.QComboBox()
      self.pairCombo.addItems(['All', 'BTC', 'USD'])
      self.pairCombo.currentTextChanged.connect(pairComboTextChanged)

      comboModel = MyTableModel(['', 'Price'], [['BTC',1],['LTC',2],['ETH',3],['BNB',4],['TRX',5],['ICX',6],['QTUM',7],['BTG',8]])


      comboView = QtWidgets.QTableView()
      comboView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
      comboView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
      comboView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
      comboView.setSortingEnabled(True)
      comboView.setShowGrid(False)

      comboView.setHorizontalHeader(MyHeader(self.pairCombo))
      comboView.horizontalHeader().setStretchLastSection(True)
      comboView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
      comboView.verticalHeader().hide()

      self.combo.setView(comboView)
      self.combo.setModel(comboModel)

      i = self.combo.model().index(0,0)
      self.combo.view().horizontalHeader().setIndexWidget(i, self.pairCombo)

      mainLayout = QtWidgets.QHBoxLayout()
      mainLayout.addWidget(self.combo)
      mainWidget.setLayout(mainLayout)




      qss = open(os.path.join(os.path.dirname(__file__),'qtv.qss'), 'r')
      self.setStyleSheet(qss.read())
      qss.close()



# ==================================================================================================


if __name__ == '__main__':
   import sys
   app = QtWidgets.QApplication(sys.argv)
   # app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
   GUI = MainWindow(600, 400)
   GUI.show()
   app.exec_()
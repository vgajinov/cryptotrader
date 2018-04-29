from PyQt5 import QtGui, QtWidgets, QtCore
import operator


class MainWindow(QtWidgets.QMainWindow):
   def __init__(self, width, height):
      super(MainWindow, self).__init__()

      self.resize(width, height)
      self.setWindowTitle('TableView')
      mainWidget = QtWidgets.QWidget()
      self.setCentralWidget(mainWidget)

      self.myTable = QtWidgets.QTableView()

      self.model = TableModel()
      self.myTable.setModel(self.model)
      self.myTable.setShowGrid(False)

      self.hView = HeaderView(self.model)
      self.myTable.setHorizontalHeader(self.hView)
      self.myTable.verticalHeader().hide()

      # adding alternate colours
      self.myTable.setAlternatingRowColors(True)
      self.myTable.setStyleSheet("alternate-background-color: rgb(209, 209, 209)"
                                 "; background-color: rgb(244, 244, 244);")

      # self.myTable.setSortingEnabled(True)
      # self.myTable.sortByColumn(1, Qt.AscendingOrder)

      mainLayout = QtWidgets.QHBoxLayout()
      mainLayout.addWidget(self.myTable)
      mainWidget.setLayout(mainLayout)


class HeaderView(QtWidgets.QHeaderView):
   def __init__(self, model):
      super(HeaderView, self).__init__(QtCore.Qt.Horizontal)
      self.model = TableModel()
      # self.model = model
      self.setModel(self.model)

      # Setting font for headers only
      self.font = QtGui.QFont("Helvetica", 12)
      self.setFont(self.font)

      # Changing section backgroud color. font color and font weight
      self.setStyleSheet("::section{background-color: pink; color: green; font-weight: bold}")

      self.setSectionResizeMode(1)
      self.setSectionsClickable(True)


class TableModel(QtCore.QAbstractTableModel):
   def __init__(self):
      super(TableModel, self).__init__()

      self.headers = ["Name", "Age", "Grades"]
      self.stocks = [["George", "26", "80%"],
                     ["Bob", "16", "95%"],
                     ["Martha", "22", "98%"]]
      self.data = [self.headers] + self.stocks

   def update(self, in_data):
      self.data = in_data

   def rowCount(self, parent=None):
      return len(self.data)

   def columnCount(self, parent=None):
      return len(self.data[0])

   def setData(self, index, value, role=None):
      if role == QtGui.Qt.EditRole:
         row = index.row()
         col = index.column()
         self.data.set_value(row, col, value)
         self.update(self.data)
         return True

   def data(self, index, role=None):
      try:
         if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            value = self.data[row][col]
            return value
      except:
         print(row, col)

   def headerData(self, section, orientation, role=None):
      if role == QtCore.Qt.DisplayRole:
         if orientation == QtCore.Qt.Horizontal:
            return self.data[0]

   def sort(self, Ncol, order):
      """Sort table by given column number."""
      self.layoutAboutToBeChanged.emit()
      # self.data = self.data.sort_values(self.headers[Ncol],
      #                                   ascending=order == Qt.AscendingOrder)
      self.layoutChanged.emit()


if __name__ == '__main__':
   import sys

   app = QtWidgets.QApplication(sys.argv)
   app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
   main_window = MainWindow(800, 600)
   main_window.show()
   app.exec_()
   sys.exit()

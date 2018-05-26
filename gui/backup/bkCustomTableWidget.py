from PyQt5 import QtCore, QtWidgets, QtGui



# OrderBookTableModel
# ----------------------------------------------------------------------

class OrderBookTableModel(QtCore.QAbstractTableModel):
   numRows = 15

   def __init__(self, color=QtCore.Qt.white):
      super(OrderBookTableModel, self).__init__()
      self.priceColor = color
      self.tableData = []

   def rowCount(self, parent):
      if not self.tableData:
         return 0
      else:
         return self.numRows

   def columnCount(self, parent):
      return 3

   def data(self, index, role):
      if not index.isValid() or not self.tableData:
         return None

      row = index.row()
      if row < 0 or row >= self.numRows:
         return None

      column = index.column()
      if column < 0 or column >= 3:
         return None

      if role == QtCore.Qt.DisplayRole:
         return self.tableData[row][column]
      elif role == QtCore.Qt.TextAlignmentRole:
         return QtCore.Qt.AlignRight + QtCore.Qt.AlignVCenter
      elif role == QtCore.Qt.TextColorRole and column == 0:
         return self.priceColor
      else:
         return None


   def headerData(self, section, orientation, role):
      return None

   def setTableData(self, data, fromTail = False):
      self.clear()
      self.beginInsertRows(QtCore.QModelIndex(), 1, self.numRows)
      if fromTail:
         self.tableData = data[-self.numRows:]
      else:
         self.tableData = data[:self.numRows]
      self.endInsertRows()

   def clear(self):
      self.beginRemoveRows(QtCore.QModelIndex(), 1, self.numRows)
      self.tableData = []
      self.endRemoveRows()



# OrderBookTableView
# ----------------------------------------------------------------------

class OrderBookTableView(QtWidgets.QTableView):
   def __init__(self, priceColor):
      super(OrderBookTableView, self).__init__()

      self.setEnabled(False)
      self.setShowGrid(False)
      self.setContentsMargins(0,0,0,0)
      self.setTextElideMode(QtCore.Qt.ElideNone)
      self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

      self.verticalHeader().hide()
      self.verticalHeader().setStretchLastSection(True)
      self.horizontalHeader().hide()
      self.horizontalHeader().setStretchLastSection(True)

      self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
      self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
      self.setSizeAdjustPolicy(QtWidgets.QTableView.AdjustToContents)

      font = QtGui.QFont(self.font())
      font.setPointSize(8)
      self.setFont(font)

      self.setModel(OrderBookTableModel(priceColor))


   def resizeEvent(self, QResizeEvent):
      tableWidth = self.width()
      self.setColumnWidth(0, 1.1 * tableWidth / 3)
      self.setColumnWidth(1, 0.9 * tableWidth / 3)
      self.setColumnWidth(2, tableWidth / 3)
      self.verticalHeader().setDefaultSectionSize(self.height() / self.model().numRows)

   def paintEvent(self, event):
      painter = QtGui.QPainter(self.viewport())

      tableData = self.model().tableData
      if tableData:
         amounts = [float(x[1]) for x in tableData]
         maxAmount = max(amounts)

         top    = self.rect().top()
         left   = self.rect().left()
         right  = self.rect().right()
         width  = right - left
         rowHeight = self.rowHeight(0)

         for row in range(self.model().rowCount(self)):
            ratio = amounts[row] / maxAmount
            rowTop = top + row * rowHeight
            leftRect = QtCore.QRect(left, rowTop, left + (1 - ratio) * width, rowTop + rowHeight)
            rightRect = QtCore.QRect(left + (1-ratio) * width, rowTop, right, rowTop + rowHeight)
            painter.fillRect(leftRect, QtGui.QBrush(QtCore.Qt.black))
            painter.fillRect(rightRect, QtGui.QBrush(QtCore.Qt.darkBlue))

      QtWidgets.QTableView.paintEvent(self, event)



# ======================================================================
# Class that defines a TableWidget customized for displaying
# OrderBook column data. It adjusts the column widths and the
# font size for displaying content. Table data must be suplied
# in the from of a list of list of strings, one for each column.
# ======================================================================
class CustomTableWidget(QtWidgets.QTableWidget):
   minFontSize = 8
   maxFontSize = 12
   rowHeight = 10
   tableData = None
   callCnt = 0

   def __init__(self):
      super(CustomTableWidget, self).__init__()

      self.setColumnCount(3)
      self.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Fixed)
      self.horizontalHeader().setVisible(False)
      self.verticalHeader().setVisible(False)
      self.setShowGrid(False)
      self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
      self.setTextElideMode(QtCore.Qt.ElideNone)
      self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
      self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)




   def fitDataAndColumns(self):
      if not self.tableData:
         return

      # find the string with maximum length for each column and total length of all max strings
      maxStrLen = []
      for i in range(len(self.tableData)):
         maxStrLen.append(max(self.tableData[i], key=len))
      maxJoinStr = ''.join(maxStrLen)

      # set the font size and column widths
      font = QtGui.QFont(self.font())
      font.setPointSize(int(self.width()/21))
      self.setFont(font)
      fm = QtGui.QFontMetrics(font)
      fullStrWidth = fm.width(maxJoinStr)
      for i in range(len(self.tableData)):
         newWidth = int((float(fm.width(maxStrLen[i])) / fullStrWidth) * self.width())
         self.horizontalHeader().resizeSection(i, newWidth)

      # find and set the number of rows
      self.rowHeight = fm.height()
      numRows = int(self.height() / self.rowHeight)
      numRows = min(numRows, len(self.tableData[0]))
      self.setRowCount(numRows)



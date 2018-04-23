from PyQt5 import QtCore, QtWidgets, QtGui


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
      if self.tableData == None or self.tableData == []:
         return

      # find the string with maximum length for each column and total length of all max strings
      maxStrLen = []
      for i in range(len(self.tableData)):
         maxStrLen.append(max(self.tableData[i], key=len))
      maxJoinStr = ''.join(maxStrLen)

      # find the most suitable font size based on strings and the table width
      tableWidth = self.width()
      font = QtGui.QFont(self.font())
      fontSize = self.minFontSize
      while(fontSize <= self.maxFontSize):
         font.setPixelSize(fontSize+1)
         fm = QtGui.QFontMetrics(font)
         if fm.width(maxJoinStr) < 0.7*tableWidth:
            fontSize += 1
         else:
            break

      # set the font size and column widths
      self.setFont(font)
      fm = QtGui.QFontMetrics(font)
      fullStrWidth = fm.width(maxJoinStr)
      for i in range(len(self.tableData)):
         newWidth = int((float(fm.width(maxStrLen[i])) / fullStrWidth) * tableWidth)
         self.horizontalHeader().resizeSection(i, newWidth)

      # find and set the number of rows
      self.rowHeight = fm.height()
      numRows = int(self.height() / self.rowHeight)
      numRows = min(numRows, len(self.tableData[0]))
      self.setRowCount(numRows)

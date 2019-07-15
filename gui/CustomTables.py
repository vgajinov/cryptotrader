from PyQt5 import QtCore, QtWidgets, QtGui


# ======================================================================
# Model/View implementation of tables for displaying order book
# Supports drawing per-row color bars depending on the amount
# at a given price value
# ======================================================================

# OrderBookTableModel
# ----------------------------------------------------------------------

class OrderBookTableModel(QtCore.QAbstractTableModel):
    """A model class for the Model/View implementation of tables for displaying order book"""
    numRows = 15

    def __init__(self, color=QtCore.Qt.white):
        super().__init__()
        self.priceColor = color
        self.tableData = []

    def rowCount(self, parent):
        """Returns the number of rows in the model"""
        return self.numRows if self.tableData else 0

    def columnCount(self, parent):
        """Returns the number of columns in the model
        The model uses 3 columns: price_level, amount and total amount
        """
        return 3

    def data(self, index, role):
        """Overrides the data method of the QAbstractTableModel.
        Performs number formatting, text alignment and coloring based on the role
        """
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
        elif role == QtCore.Qt.ForegroundRole and column == 0:
            return QtGui.QColor(self.priceColor)
        else:
            return None


    def headerData(self, section, orientation, role):
        """Effectively removes the header."""
        return None


    def setTableData(self, data, fromTail = False):
        """Set the model data (order book values)."""
        self.clear()
        self.beginInsertRows(QtCore.QModelIndex(), 1, self.numRows)
        if fromTail:
            self.tableData = data[-self.numRows:]
        else:
            self.tableData = data[:self.numRows]
        self.endInsertRows()

    def clear(self):
        """Removes the data from the model."""
        self.beginRemoveRows(QtCore.QModelIndex(), 1, self.numRows)
        self.tableData = []
        self.endRemoveRows()


# OrderBookTableView
# ----------------------------------------------------------------------

class OrderBookTableView(QtWidgets.QTableView):
    """A view class for the Model/View implementation of tables for displaying order book"""

    def __init__(self, color):
        super(OrderBookTableView, self).__init__()
        # define the color of bars
        self.color = QtGui.QColor(color).darker(500)

        self.setEnabled(False)
        self.setShowGrid(False)
        self.setContentsMargins(0, 0, 0, 0)
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
        font.setPointSize(9)
        self.setFont(font)

        self.setModel(OrderBookTableModel(color))


    def resizeEvent(self, QResizeEvent):
        """Handles the resize event by setting the widths of columns."""
        table_width = self.width()
        self.setColumnWidth(0, int(1.1 * table_width / 3))
        self.setColumnWidth(1, int(0.9 * table_width / 3))
        self.setColumnWidth(2, int(table_width / 3))
        self.verticalHeader().setDefaultSectionSize(self.height() / self.model().numRows)

    def paintEvent(self, event):
        """Uses the paint event to paint the bars based on the amount at a given price level."""
        painter = QtGui.QPainter(self.viewport())

        table_data = self.model().tableData
        if table_data:
            amounts = [float(x[1].replace(',', '')) for x in table_data]
            max_amount = max(amounts)

            top    = self.rect().top()
            left   = self.rect().left()
            right  = self.rect().right()
            width  = right - left
            row_height = self.rowHeight(0)

            painter.fillRect(self.rect(), QtGui.QBrush(QtCore.Qt.black))
            painter.setPen(QtGui.QColor(QtCore.Qt.black))

            for row in range(self.model().rowCount(self)):
                ratio = amounts[row] / max_amount
                row_top = top + row * row_height

                price_rect = QtCore.QRect(left, row_top, left + (1 - ratio) * width, row_top + row_height)
                painter.fillRect(price_rect, QtGui.QBrush(QtCore.Qt.black))

                amount_rect = QtCore.QRect(left + (1-ratio) * width, row_top, right, row_top + row_height)
                painter.fillRect(amount_rect, QtGui.QBrush(self.color))
                painter.drawRect(amount_rect)

        QtWidgets.QTableView.paintEvent(self, event)


# CustomTableWidget
# ----------------------------------------------------------------------

class CustomTableWidget(QtWidgets.QTableWidget):
    """Defines a TableWidget customized for displaying Trade column data.
    It adjusts the column widths and the font size for displaying content.
    Table data must be supplied in the from of a list of list of strings, one for each column.
    """
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
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setTextElideMode(QtCore.Qt.ElideNone)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


    def fitDataAndColumns(self):
        """The main method for adjusting columns of the table to fit the values of the trades."""
        if not self.tableData:
            return

        # find the string with maximum length for each column and total length of all max strings
        max_str_len = []
        for i in range(len(self.tableData)):
            max_str_len.append(max(self.tableData[i], key=len))
        max_join_str = ''.join(max_str_len)

        # set the font size and column widths
        font = QtGui.QFont(self.font())
        font.setPointSize(int(self.width()/21))
        self.setFont(font)
        fm = QtGui.QFontMetrics(font)
        full_str_width = fm.width(max_join_str)
        for i in range(len(self.tableData)):
            new_width = int((float(fm.width(max_str_len[i])) / full_str_width) * self.width())
            self.horizontalHeader().resizeSection(i, new_width)

        # find and set the number of rows
        self.rowHeight = fm.height()
        num_rows = int(self.height() / self.rowHeight)
        num_rows = min(num_rows, len(self.tableData[0]))
        self.setRowCount(num_rows)



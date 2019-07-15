import math
import operator
from PyQt5 import QtCore, QtWidgets, QtGui

"""
This module defines a set of classes for customized combo boxes
"""

# ------------------------------------------------------------------------------------
# Control ComboBox class
# ------------------------------------------------------------------------------------

class ControlComboBox(QtWidgets.QComboBox):
    """A combo box that shows the popup list bellow the box."""
    def __init__(self, fixed_item_count=-1):
        super().__init__()
        self.fixedItemCount = fixed_item_count

    def showPopup(self):
        """Displays the combobox popup bellow combobox.
        Uses global position to position the popup rather then relative to combobox
        """
        super().showPopup()
        popup = self.findChild(QtWidgets.QFrame)
        # set popup position bellow combobox using global positioning
        popup.move(popup.x(), self.mapToGlobal(self.frameGeometry().topLeft()).y() + self.height() - 5 )
        item_height = self.view().visualRect(self.model().index(1, 0)).height()
        if self.fixedItemCount == -1:
            # fit all items
            popup.setMinimumHeight((self.count()-1) * item_height)
        else:
            popup.setFixedHeight(self.fixedItemCount * item_height)

    def wheelEvent(self, event):
        """Handles vertical mouse scrolling."""
        self.verticalScrollBar().setMaximum(self.model().rowCount())
        num_steps = - event.angleDelta().y() / 120
        new_scroll_bar_value = min(self.verticalScrollBar().value() + num_steps, self.verticalScrollBar().maximum())
        self.verticalScrollBar().setValue(new_scroll_bar_value)
        event.accept()


# ------------------------------------------------------------------------------------
# Checkable ComboBox class
# ------------------------------------------------------------------------------------

class CheckableControlComboBox(QtWidgets.QComboBox):
    """A combo box in which list elements are checkable (have check-boxes associated to them)."""
    def __init__(self):
        super().__init__()

    def showPopup(self):
        """Displays the combobox popup bellow combobox.
        Uses global position to position the popup rather then relative to combobox
        """
        super().showPopup()
        popup = self.findChild(QtWidgets.QFrame)
        # set popup position bellow combobox
        popup.move(popup.x(), self.mapToGlobal(self.frameGeometry().topLeft()).y() + self.height() - 5 )

    def resizeEvent(self, QResizeEvent):
        """Handles the resize event.
        Sets the dimension of the rows.
        """
        font_size = self.font().pixelSize()
        row_height = font_size + 10
        row_width = int(1.2 * self.view().sizeHintForColumn(0))
        self.view().setResizeMode(QtWidgets.QListView.Adjust)
        self.view().setMinimumWidth(row_width)

        self.model().blockSignals(True)
        for i in range(self.model().rowCount())[1:]:
            self.setItemData(i, QtCore.QSize(row_width, row_height), QtCore.Qt.SizeHintRole)
        self.model().blockSignals(False)


# ------------------------------------------------------------------------------------
# Classes for the pair combobox
# ------------------------------------------------------------------------------------

class PairComboBoxModel(QtCore.QAbstractTableModel):
    """A combo box for displaying the exchange pairs.
    Each pair is displayed with the daily change percentage and daily volume.
    It is possible to sort the list of pairs based on the name of the pair or
    daily change percentage or daily volume.
    """
    header    = ['', 'Price', 'Change', 'Volume']
    hiddenRow = [['PAIR', '', '', '']]

    def __init__(self, data=None):
        super(PairComboBoxModel, self).__init__()
        if data is not None:
            self.tableData = self.hiddenRow + data
        else:
            self.tableData = self.hiddenRow

    def setTableData(self, data):
        """Sets the table data.
        :param data:  A list of pairs with the price, daily percentage change and volume.
        """
        self.clear()
        # clear the data from non-traded pairs
        data = [d for d in data if d[1]]
        self.beginInsertRows(QtCore.QModelIndex(), 1, len(data))
        self.tableData = self.hiddenRow + data
        self.endInsertRows()

    def clear(self):
        """Clears the table items (removes all the rows)."""
        self.beginRemoveRows(QtCore.QModelIndex(), 1, self.rowCount()-1)
        self.tableData = self.hiddenRow
        self.endRemoveRows()


    def rowCount(self, parent=None, *args, **kwargs):
        """Returns the number of rows."""
        return len(self.tableData)

    def columnCount(self, parent=None, *args, **kwargs):
        """Returns the number of columns"""
        return len(self.tableData[0])

    def data(self, index, role):
        """Overrides the data method of the QTableView.
        Formats the table items (floats) for the DisplayRole.
        Uses Foreground role to color percentage changed to
        red or green the based on the sign of the change.
         Aligns the column items using the TextAlign role.
        """
        if not index.isValid():
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            data = self.tableData[index.row()][index.column()]
            if index.row() == 0:   # hidden row
                return data
            if index.column() == 1:
                exp = math.ceil(math.log10(float(data)))
                data_precision = min(abs(exp - 6), 8)
                return f'{data:.{data_precision}f}'
            elif index.column() == 2:
                return f'{data:.2f}%'
            else:
                return data

        if role == QtCore.Qt.ForegroundRole:
            if index.column() == 2:
                data = self.tableData[index.row()][index.column()]
                if float(data) < 0.0:
                    return QtGui.QBrush(QtGui.QColor('red'))
                else:
                    return QtGui.QBrush(QtGui.QColor('lime'))

        if role == QtCore.Qt.TextAlignmentRole:
            if index.column() == 0:
                return QtCore.Qt.AlignLeft + QtCore.Qt.AlignVCenter
            else:
                return QtCore.Qt.AlignRight + QtCore.Qt.AlignVCenter

        return QtCore.QVariant()


    def headerData(self, column, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[column]
        return QtCore.QVariant()

    def sort(self, column, order):
        """Sorts table rows by a given column"""
        if column == 0:
            return
        self.layoutAboutToBeChanged.emit()
        reverse = order == QtCore.Qt.DescendingOrder
        self.tableData = self.hiddenRow + sorted(self.tableData[1:], key=operator.itemgetter(column), reverse=reverse)
        self.layoutChanged.emit()


# Filter Proxy model for the PairComboBoxModel
# ------------------------------------------------------------------------------------

class PairFilterProxyModel(QtCore.QSortFilterProxyModel):
    """A proxy model for the pair combo box that implements pair filtering based on quote currency.
    Uses the filterChanged signal to notify the view that the filter setting have been changed.
    """
    pairFilter = 'BTC'
    filterChanged = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def headerData(self, section, orientation, role=None):
        return self.sourceModel().headerData(section, orientation, role)

    def filterAcceptsRow(self, row, source_parent):
        """Implements actual filtering of pairs."""
        if row == 0:  # hidden row
            return True
        row_pair = self.sourceModel().data(self.sourceModel().index(row, 0, source_parent), QtCore.Qt.DisplayRole)
        if isinstance(row_pair, str) and self.pairFilter in row_pair and not row_pair.startswith(self.pairFilter):
            return True
        return False

    def setPairFilter(self, new_filter):
        """Sets a new filter."""
        self.invalidateFilter()
        self.sourceModel().layoutAboutToBeChanged.emit()
        self.pairFilter = new_filter
        self.sourceModel().layoutChanged.emit()
        self.filterChanged.emit(self.rowCount())

    def sort(self, column, order):
        """A proxy for row sorting based on selected column."""
        self.sourceModel().sort(column, order)


class PairComboBoxHeader(QtWidgets.QHeaderView):
    """A header view widget for the pair combo box header."""
    def __init__(self, combo=None):
        super().__init__(QtCore.Qt.Horizontal)
        self.sectionResized.connect(self.handleSectionResized)
        self.setSectionsMovable(False)
        self.setSectionsClickable(True)
        self.combo = combo

    def showEvent(self, event):
        """Header show event handler"""
        self.combo.setGeometry(self.sectionViewportPosition(0) + 5, 3, 60, self.height() - 10)
        self.combo.show()
        QtWidgets.QHeaderView.showEvent(self, event)

    def handleSectionResized(self, col):
        """An event handler that handles the column resizing"""
        if col == 0:
            self.combo.setGeometry(self.sectionViewportPosition(0) + 3, 5, 60, self.height() - 10)


# Filter Proxy model for the PairComboBoxModel
# ------------------------------------------------------------------------------------

class PairTableView(QtWidgets.QTableView):
    def __init__(self):
        super().__init__()

    def handleFilterChanged(self, row_count):
        """An event handler that handles the change in the filter settings.
        The only purpose is to adjust the vertical scroll bar to new number of rows.
        """
        self.verticalScrollBar().setMaximum(row_count)
        self.verticalScrollBar().setValue(0)
        self.scrollTo(QtCore.QModelIndex(), QtWidgets.QAbstractItemView.PositionAtTop)

    def wheelEvent(self, event):
        """Handles vertical mouse scrolling."""
        self.verticalScrollBar().setMaximum(self.model().rowCount() - self.height() // self.rowHeight(1))
        num_steps = - event.angleDelta().y() / 120
        new_scroll_bar_value = self.verticalScrollBar().value() + num_steps
        self.verticalScrollBar().setValue(min(new_scroll_bar_value, self.verticalScrollBar().maximum()))
        event.accept()

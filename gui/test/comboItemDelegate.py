import sip

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt5 import QtCore, QtGui, QtWidgets


class TableModel(QtCore.QAbstractTableModel):
   """
   A simple 5x4 table model to demonstrate the delegates
   """
   def __init__(self):
      super(TableModel, self).__init__()

   def rowCount(self, parent=QtCore.QModelIndex()):
      return 5

   def columnCount(self, parent=QtCore.QModelIndex()):
      return 4

   def data(self, index, role=QtCore.Qt.DisplayRole):
      if not index.isValid(): return None
      if not role == QtCore.Qt.DisplayRole: return None
      return "{0:02d}".format(index.row())

   def setData(self, index, value, role=QtCore.Qt.DisplayRole):
      print("setData", index.row(), index.column(), value)

   def headerData(self, col, orientation, role):
      if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
         # if col == 0:
         #    return self.pairCombo
         # else:
         #    return self.header[col]

         return HeaderComboDelegate(self)
      return None

   def flags(self, index):
      if (index.column() == 0):
         return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
      else:
         return QtCore.Qt.ItemIsEnabled


class ComboDelegate(QtWidgets.QItemDelegate):
   """
   A delegate that places a fully functioning QComboBox in every
   cell of the column to which it's applied
   """
   def __init__(self, parent):
      super(ComboDelegate, self).__init__(parent)
      # QtWidgets.QItemDelegate.__init__(self, parent)

   def createEditor(self, parent, option, index):
      combo = QtWidgets.QComboBox(parent)
      li = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five']
      combo.addItems(li)
      combo.currentIndexChanged.connect(self.currentIndexChanged)
      return combo

   def setEditorData(self, editor, index):
      editor.blockSignals(True)
      editor.setCurrentIndex(int(index.model().data(index)))
      editor.blockSignals(False)

   def setModelData(self, editor, model, index):
      model.setData(index, editor.currentIndex())

   def currentIndexChanged(self):
      self.commitData.emit(self.sender())

class HeaderComboDelegate(QtWidgets.QStyledItemDelegate):
   """
   A delegate that places a fully functioning QComboBox in every
   cell of the column to which it's applied
   """
   def __init__(self, parent):
      super(HeaderComboDelegate, self).__init__(parent)
      self.setObjectName('h')

   def createEditor(self, parent, option, index):
      self.combo = QtWidgets.QComboBox(parent)
      li = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five']
      self.combo.addItems(li)
      self.combo.currentIndexChanged.connect(self.currentIndexChanged)
      self.combo.show()
      return self.combo

   def setEditorData(self, editor, index):
      editor.blockSignals(True)
      editor.setCurrentIndex(int(index.model().data(index)))
      editor.blockSignals(False)

   def setModelData(self, editor, model, index):
      model.setData(index, editor.currentIndex())

   def currentIndexChanged(self):
      self.commitData.emit(self.sender())

   def paint(self, painter, option, index):
      if index.column() == 0:
         QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, self.combo, painter)
      else:
         self.parent().paint(painter, option, index)


class MyHeader(QtWidgets.QHeaderView):
   def __init__(self, combo=None):
      super(MyHeader, self).__init__(QtCore.Qt.Horizontal)

      # Set the delegate for column 0 of our table
      self.setItemDelegateForColumn(0, ComboDelegate(self))

class TableView(QtWidgets.QTableView):
   """
   A simple table to demonstrate the QComboBox delegate.
   """
   def __init__(self):
      super(TableView, self).__init__()

      # Set the delegate for column 0 of our table
      self.setItemDelegateForColumn(0, ComboDelegate(self))
      self.horizontalHeader().setItemDelegateForColumn(0, HeaderComboDelegate(self))



class Widget(QtWidgets.QWidget):
   """
   A simple test widget to contain and own the model and table.
   """
   def __init__(self):
      super(Widget, self).__init__()

      l = QtWidgets.QVBoxLayout(self)
      self.tableModel = TableModel()
      self.tableView = TableView()
      self.tableView.horizontalHeader().setItemDelegateForColumn(0, HeaderComboDelegate(self))
      self.tableView.setModel(self.tableModel)
      for row in range(0, self.tableModel.rowCount()):
         self.tableView.openPersistentEditor(self.tableModel.index(row, 0))
      self.tableView.horizontalHeader().openPersistentEditor(self.tableView.horizontalHeader().model().index(0, 0))

      l.addWidget(self.tableView)

if __name__ == "__main__":
   from sys import argv, exit

   a = QtWidgets.QApplication(argv)
   w = Widget()
   w.show()
   w.raise_()
   exit(a.exec_())
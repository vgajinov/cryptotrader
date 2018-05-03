import math
import operator
from PyQt5 import QtCore, QtWidgets, QtGui
from .Overlays import OverlayFactory
from .Indicators import IndicatorFactory




# ------------------------------------------------------------------------------------
# Custom ComboBox classes
# ------------------------------------------------------------------------------------

class ControlComboBox(QtWidgets.QComboBox):
   def __init__(self, fixedItemCnt=-1):
      super(ControlComboBox, self).__init__()
      self.fixedItemCnt = fixedItemCnt

   def showPopup(self):
      super(ControlComboBox, self).showPopup()
      popup = self.findChild(QtWidgets.QFrame)
      # set popup position bellow combobox
      # (note that it uses global positioning, rather than relative to combobox)
      popup.move(popup.x(), self.mapToGlobal(self.frameGeometry().topLeft()).y() + self.height() - 5 )
      itemHeight = self.view().visualRect(self.model().index(1,0)).height()
      if self.fixedItemCnt == -1:
         # fit all items
         popup.setMinimumHeight((self.count()-1) * itemHeight)
      else:
         popup.setFixedHeight(self.fixedItemCnt * itemHeight)

   def wheelEvent(self, event):
      self.verticalScrollBar().setMaximum(self.model().rowCount())
      numSteps = - event.angleDelta().y() / (120)
      newScrollBarValue = min(self.verticalScrollBar().value() + numSteps, self.verticalScrollBar().maximum())
      self.verticalScrollBar().setValue(newScrollBarValue)
      event.accept()

      vs = self.verticalScrollBar()
      print(self.model().rowCount(), vs.maximum(), vs.value())


class CheckableControlComboBox(QtWidgets.QComboBox):
   def __init__(self):
      super(CheckableControlComboBox, self).__init__()

   def showPopup(self):
      super(CheckableControlComboBox, self).showPopup()
      popup = self.findChild(QtWidgets.QFrame)
      # set popup position bellow combobox
      popup.move(popup.x(), self.mapToGlobal(self.frameGeometry().topLeft()).y() + self.height() - 5 )

   def resizeEvent(self, QResizeEvent):
      fontSize = self.font().pixelSize()
      rowHeight = fontSize + 10
      rowWidth = 1.2 * self.view().sizeHintForColumn(0)
      self.view().setResizeMode(QtWidgets.QListView.Adjust)
      self.view().setMinimumWidth(rowWidth)

      self.model().blockSignals(True)
      for i in range(self.model().rowCount())[1:]:
         self.setItemData(i, QtCore.QSize(rowWidth, rowHeight), QtCore.Qt.SizeHintRole)
      self.model().blockSignals(False)

# ------------------------------------------------------------------------------------
# Classes for the pair combobox
# ------------------------------------------------------------------------------------

class PairComboBoxModel(QtCore.QAbstractTableModel):
   header    = ['', 'Price', 'Change', 'Volume']
   hiddenRow = [['PAIR', '', '', '']]

   def __init__(self, data=None):
      super(PairComboBoxModel, self).__init__()
      if data is not None:
         self.tableData = self.hiddenRow + data
      else:
         self.tableData = self.hiddenRow

   def setTableData(self, data):
      self.clear()
      self.beginInsertRows(QtCore.QModelIndex(), 1, len(data))
      self.tableData = self.hiddenRow + data
      self.endInsertRows()

   def clear(self):
      # oldCnt = self.rowCount()
      self.beginRemoveRows(QtCore.QModelIndex(), 1, self.rowCount()-1)
      self.tableData = self.hiddenRow
      self.endRemoveRows()
      # self.rowsRemoved.emit(self.index(1,0),1,oldCnt-1)

   def rowCount(self, parent=None, *args, **kwargs):
      return len(self.tableData)

   def columnCount(self, parent=None, *args, **kwargs):
      return len(self.tableData[0])

   def data(self, index, role):
      if not index.isValid():
         return QtCore.QVariant()

      if role == QtCore.Qt.DisplayRole:
         data = self.tableData[index.row()][index.column()]
         if index.row() == 0:   # hidden row
            return data
         if index.column() == 1:
            exp = math.ceil(math.log10(data))
            dataPrec = min(abs(exp - 6), 8)
            return '{:.{prec}f}'.format(data, prec=dataPrec)
         elif index.column() == 2:
               return '{:.2f}%'.format(data)
         else:
            return data

      if role == QtCore.Qt.ForegroundRole:
         if index.column() == 2:
            data = self.tableData[index.row()][index.column()]
            if data < 0.0:
               return QtGui.QBrush(QtGui.QColor('red'))
            else:
               return QtGui.QBrush(QtGui.QColor('lime'))

      if role == QtCore.Qt.TextAlignmentRole:
         if index.column() == 0:
            return QtCore.Qt.AlignLeft + QtCore.Qt.AlignVCenter
         else:
            return QtCore.Qt.AlignRight + QtCore.Qt.AlignVCenter

      return QtCore.QVariant()

   def headerData(self, col, orientation, role):
      if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
         return self.header[col]
      return QtCore.QVariant()

   def sort(self, col, order):
      # sort table by given column
      if col != 0:
         self.layoutAboutToBeChanged.emit()
         reverse = order==QtCore.Qt.DescendingOrder
         self.tableData = self.hiddenRow + sorted(self.tableData[1:], key=operator.itemgetter(col), reverse=reverse)
         self.layoutChanged.emit()


class PairFilterProxyModel(QtCore.QSortFilterProxyModel):
   pairFilter = 'BTC'
   filterChanged = QtCore.pyqtSignal(int)

   def __init__(self):
      super(PairFilterProxyModel, self).__init__()

   def headerData(self, section, orientation, role=None):
      return self.sourceModel().headerData(section, orientation, role)

   def filterAcceptsRow(self, row, sourceParent):
      if row == 0:  # hidden row
         return True
      rowPair = self.sourceModel().data(self.sourceModel().index(row, 0, sourceParent), QtCore.Qt.DisplayRole)
      if self.pairFilter in rowPair and not rowPair.startswith(self.pairFilter):
         return True
      return False

   def setPairFilter(self, newFilter):
      self.invalidateFilter()
      self.sourceModel().layoutAboutToBeChanged.emit()
      self.pairFilter = newFilter
      self.sourceModel().layoutChanged.emit()
      self.filterChanged.emit(self.rowCount())

   def sort(self, col, order):
      self.sourceModel().sort(col, order)


class PairComboBoxHeader(QtWidgets.QHeaderView):
   def __init__(self, combo=None):
      super(PairComboBoxHeader, self).__init__(QtCore.Qt.Horizontal)
      self.sectionResized.connect(self.handleSectionResized)
      self.setSectionsMovable(False)
      self.setSectionsClickable(True)
      self.combo = combo

   def showEvent(self, event):
      self.combo.setGeometry(self.sectionViewportPosition(0) + 5, 3, 60, self.height() - 10)
      self.combo.show()
      QtWidgets.QHeaderView.showEvent(self, event)

   def handleSectionResized(self, col):
      if col == 0:
         self.combo.setGeometry(self.sectionViewportPosition(0) + 3, 5, 60, self.height() - 10)


class PairTableView(QtWidgets.QTableView):
   def __init__(self):
      super(PairTableView, self).__init__()

   def rowCountChanged(self, old, new):
      print('rowCnt', old, new)
      self.verticalScrollBar().setMaximum(self.model().rowCount())

   def handleRowsRemoved(self, parent, first, last):
      print('rows removed: ', first, last)

   def handleFilterChanged(self, rowCnt):
      print('Filter changed', rowCnt)
      # self.viewport().setSizeHint(QtCore.QSize(24*rowCnt, self.viewportSizeHint().width()))
      self.verticalScrollBar().setMaximum(rowCnt)
      self.verticalScrollBar().setValue(0)
      self.scrollTo(QtCore.QModelIndex(), QtWidgets.QAbstractItemView.PositionAtTop)
      vs = self.verticalScrollBar()
      print(vs.minimum(), vs.maximum(), vs.value())


   def wheelEvent(self, event):
      self.verticalScrollBar().setMaximum(self.model().rowCount())
      numSteps = - event.angleDelta().y() / (120)
      newScrollBarValue = self.verticalScrollBar().value() + numSteps
      self.verticalScrollBar().setValue(min(newScrollBarValue, self.verticalScrollBar().maximum()))
      event.accept()

      vs = self.verticalScrollBar()
      print(self.viewportSizeHint().height(), vs.sizeHint().height(), vs.sizeHint().width(), self.model().rowCount(), vs.maximum(), vs.value())




# ------------------------------------------------------------------------------------
# ControlBarWidget
# ------------------------------------------------------------------------------------

class ControlBarWidget(QtWidgets.QWidget):
   itemChangedByUser = True

   def __init__(self, parent):
      super(ControlBarWidget, self).__init__()

      self.ctrlExchange = ControlComboBox()
      self.ctrlExchange.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlExchange.setObjectName('exchangeCombo')

      self.ctrlPair = ControlComboBox(15)
      self.ctrlPair.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlPair.setObjectName('pairCombo')

      self.ctrlTime = ControlComboBox()
      self.ctrlTime.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlTime.setObjectName('timeCombo')

      self.ctrlOverlay = CheckableControlComboBox()
      self.ctrlOverlay.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlOverlay.setObjectName('overlayCombo')

      self.ctrlIndicator = CheckableControlComboBox()
      self.ctrlIndicator.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlIndicator.setObjectName('indicatorCombo')

      mainLayout = QtWidgets.QHBoxLayout(self)
      mainLayout.setContentsMargins(0,0,0,0)
      mainLayout.setSpacing(0)
      ctrlLeftLayout = QtWidgets.QHBoxLayout()
      ctrlRightLayout = QtWidgets.QHBoxLayout()

      ctrlLeftLayout.addWidget(self.ctrlExchange)
      ctrlLeftLayout.addWidget(self.ctrlPair)
      ctrlLeftLayout.addWidget(self.ctrlTime)
      ctrlLeftLayout.setSpacing(10)
      ctrlLeftLayout.setContentsMargins(5,5,5,5)
      ctrlLeftLayout.setAlignment(QtCore.Qt.AlignLeft)

      ctrlRightLayout.addWidget(self.ctrlOverlay)
      ctrlRightLayout.addWidget(self.ctrlIndicator)
      ctrlRightLayout.setSpacing(10)
      ctrlRightLayout.setContentsMargins(5,5,5,5)
      ctrlRightLayout.setAlignment(QtCore.Qt.AlignRight)

      mainLayout.addLayout(ctrlLeftLayout)
      mainLayout.addLayout(ctrlRightLayout)

      self.setControls()


   def setControls(self):
      # Intitialize exchange combo
      self.ctrlExchange.addItem('EXCHANGE')

      # Intitialize interval combo
      self.ctrlTime.setView(QtWidgets.QListView())
      self.ctrlTime.addItem('TIME')
      self.ctrlTime.setEnabled(False)

      self.setPairCombo()
      self.setOverlayCombo()
      self.setIndicatorCombo()

      # connect event handlers
      self.ctrlExchange.currentTextChanged.connect(self.exchangeChanged)
      self.ctrlPair.currentTextChanged.connect(self.pairChanged)
      self.ctrlTime.currentTextChanged.connect(self.intervalChanged)
      self.ctrlOverlay.model().itemChanged.connect(self.overlayChanged)
      self.ctrlIndicator.model().itemChanged.connect(self.indicatorChanged)


   def setPairCombo(self):
      # self.ctrlPair.setEnabled(False)

      self.pairComboFilter = ControlComboBox()
      self.pairComboFilter.setObjectName('pairComboFilter')
      # self.pairComboFilter.addItems(['BTC', 'USD', 'ETH', 'BNB'])

      # create the main and the proxy models
      pairModel = PairComboBoxModel([])
      pairFilterModel = PairFilterProxyModel()
      pairFilterModel.setSourceModel(pairModel)
      pairFilterModel.setDynamicSortFilter(True)
      self.pairComboFilter.currentTextChanged.connect(pairFilterModel.setPairFilter)

      # create table view
      pairView = PairTableView() #QtWidgets.QTableView()
      pairView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
      pairView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
      pairView.setSortingEnabled(True)
      pairView.setShowGrid(False)
      pairView.setMinimumWidth(500)
      # pairView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
      # pairView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)

      # create the header for the table view
      pairView.setHorizontalHeader(PairComboBoxHeader(self.pairComboFilter))
      pairView.horizontalHeader().setStretchLastSection(True)
      pairView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
      pairView.horizontalHeader().setMinimumHeight(35)
      pairView.verticalHeader().setDefaultSectionSize(24);
      pairView.verticalHeader().setMaximumHeight(360)
      pairView.verticalHeader().hide()

      pairFilterModel.rowsRemoved.connect(pairView.handleRowsRemoved)
      pairFilterModel.filterChanged.connect(pairView.handleFilterChanged)

      # set model and view to pairCombo
      self.ctrlPair.setView(pairView)
      self.ctrlPair.view().setRowHidden(0, True)
      self.ctrlPair.setModel(pairFilterModel)

      # set pairComboFilter
      i = self.ctrlPair.model().index(0,0)
      self.ctrlPair.view().horizontalHeader().setIndexWidget(i, self.pairComboFilter)



   def setOverlayCombo(self):
      # Set overlays
      overlayList = OverlayFactory.getOverlayNames()
      self.ctrlOverlay.setView(QtWidgets.QListView())  # this is a workaround for the known Qt > 5.5 bug
                                                       # which happens only with Fusion style
      overlayModel = self.ctrlOverlay.model()
      # set the sticky name 'Overlay' as the first item and hide it
      item = QtGui.QStandardItem('Overlays')
      item.setSelectable(False)
      overlayModel.setItem(0, item)
      self.ctrlOverlay.view().setRowHidden(0, True)
      # set actual overlay items
      for i in range(len(overlayList)):
         item = QtGui.QStandardItem(overlayList[i])
         item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
         item.setCheckState(QtCore.Qt.Unchecked)
         overlayModel.setItem(i+1, item)


   def setIndicatorCombo(self):
      # Set indicators
      indicatorList = IndicatorFactory.getIndicatorNames()
      self.ctrlIndicator.setView(QtWidgets.QListView())  # this is a workaround for the known Qt > 5.5 bug
                                                         # which happens only with Fusion style
      indicatorModel = self.ctrlIndicator.model()
      # set the sticky name 'Indicator' as the first item and hide it
      item = QtGui.QStandardItem('Indicators')
      item.setSelectable(False)
      indicatorModel.setItem(0, item)
      self.ctrlIndicator.view().setRowHidden(0, True)
      # set actual indicator items
      for i in range(len(indicatorList)):
         item = QtGui.QStandardItem(indicatorList[i])
         item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
         item.setCheckState(QtCore.Qt.Unchecked)
         indicatorModel.setItem(i+1, item)

   # ------------------------------------------------------------------------------------
   # Event Handlers
   # ------------------------------------------------------------------------------------

   def exchangeChanged(self, currItem):
      self.parent().exchangeChanged(currItem)
      self.ctrlPair.setEnabled(True)

   def pairChanged(self, currItem):
      # self.ctrlTime.setEnabled(True)
      # self.parent().pairChanged(currItem)
      pass

   def intervalChanged(self, currItem):
      self.parent().intervalChanged(currItem)

   def overlayChanged(self, itemChanged):
      if self.itemChangedByUser:
         if (itemChanged.checkState() == QtCore.Qt.Checked):
            self.parent().chartWidget.addOverlay(itemChanged.text())
         else:
            self.parent().chartWidget.removeOverlay(itemChanged.text())

   def indicatorChanged(self, itemChanged):
      if self.itemChangedByUser:
         if (itemChanged.checkState() == QtCore.Qt.Checked):
            self.parent().chartWidget.showIndicator(itemChanged.text())
         else:
            self.parent().chartWidget.hideIndicator(itemChanged.text())
      


   # ------------------------------------------------------------------------------------
   # Public methods
   # ------------------------------------------------------------------------------------

   def setExchangeList(self, exchangeList):
      self.ctrlExchange.blockSignals(True)
      self.ctrlExchange.view().setRowHidden(0, True)
      self.ctrlExchange.addItems(exchangeList)
      self.ctrlExchange.blockSignals(False)

   def setPairList(self, tickers, quote_currencies):
      try:
         # set quote currencies to the filter combo
         self.pairComboFilter.blockSignals(True)
         self.pairComboFilter.clear()
         self.pairComboFilter.addItems(quote_currencies)
         self.pairComboFilter.blockSignals(False)

         # update pair combo model
         self.ctrlPair.blockSignals(True)
         self.ctrlPair.model().sourceModel().clear()
         pairList = []
         for symbol,data in tickers.items():
            price  = float(data[4])
            change = float(data[7])
            volume = int(price * float(data[5]))
            pairList.append( [ symbol, price, change, volume ] )
         self.ctrlPair.model().setPairFilter(quote_currencies[0])
         self.ctrlPair.model().sourceModel().setTableData(pairList)
         self.ctrlPair.view().setRowHidden(0, True)
         self.ctrlTime.setEnabled(False)
         self.ctrlPair.blockSignals(False)
      except Exception as e:
         print(e)

   def setIntervalList(self, intervalList):
      self.ctrlTime.blockSignals(True)
      self.ctrlTime.clear()
      self.ctrlTime.addItems(['TIME'] + intervalList)
      self.ctrlTime.view().setRowHidden(0, True)
      for i in range(0,self.ctrlTime.model().rowCount()):
         self.ctrlTime.model().item(i).setData(QtCore.Qt.AlignHCenter, QtCore.Qt.TextAlignmentRole)
      self.ctrlTime.blockSignals(False)


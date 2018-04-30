import operator
from PyQt5 import QtCore, QtWidgets, QtGui
from .Overlays import OverlayFactory
from .Indicators import IndicatorFactory


# ------------------------------------------------------------------------------------
# Custom ComboBox classes
# ------------------------------------------------------------------------------------

class ControlComboBox(QtWidgets.QComboBox):
   def __init__(self):
      super(ControlComboBox, self).__init__()

   def showPopup(self):
      super(ControlComboBox, self).showPopup()
      popup = self.findChild(QtWidgets.QFrame)
      # set popup position bellow combobox
      # (note that it uses global positioning, rather than relative to combobox)
      popup.move(popup.x(), self.mapToGlobal(self.frameGeometry().topLeft()).y() + self.height() - 5 )
      itemHeight = self.view().visualRect(self.model().index(1,0)).height()
      popup.setMinimumHeight((self.count()-1) * (itemHeight))


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
   def __init__(self, data=None):
      super(PairComboBoxModel, self).__init__()
      self.header = ['', 'Price', 'Change', 'Volume']
      self.tableData = data

   def rowCount(self, parent=None, *args, **kwargs):
      return len(self.tableData)

   def columnCount(self, parent=None, *args, **kwargs):
      return len(self.tableData[0])

   def data(self, index, role):
      if role == QtCore.Qt.DisplayRole:
         return self.tableData[index.row()][index.column()]
      if role == QtCore.Qt.TextAlignmentRole:
         if index.column() == 0:
            return QtCore.Qt.AlignLeft + QtCore.Qt.AlignVCenter
         else:
            return QtCore.Qt.AlignRight + QtCore.Qt.AlignVCenter

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


class PairComboBoxHeader(QtWidgets.QHeaderView):
   def __init__(self, combo=None):
      super(PairComboBoxHeader, self).__init__(QtCore.Qt.Horizontal)
      self.sectionResized.connect(self.handleSectionResized)
      self.setSectionsMovable(False)
      self.setMinimumHeight(30)
      self.setSectionsClickable(True)
      self.combo = combo

   def showEvent(self, event):
      self.combo.setGeometry(self.sectionViewportPosition(0) + 5, 3, 60, self.height() - 10)
      self.combo.show()
      QtWidgets.QHeaderView.showEvent(self, event)

   def handleSectionResized(self, col):
      if col == 0:
         self.combo.setGeometry(self.sectionViewportPosition(0) + 3, 5, 60, self.height() - 10)

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

      self.ctrlPair = ControlComboBox()
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
      self.ctrlPair.addItem('PAIR')
      # self.ctrlPair.setEnabled(False)

      self.pairComboFilter = ControlComboBox() #QtWidgets.QComboBox()
      self.pairComboFilter.setObjectName('pairComboFilter')
      self.pairComboFilter.addItems(['All', 'BTC', 'USD'])

      pairModel = PairComboBoxModel([['BTC','1.234','3.1','4.12'], ['LTC','4.56','3.1','4.153'], ['ETH','2.1','3.15','4.789']])

      pairView = QtWidgets.QTableView()
      pairView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
      pairView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
      pairView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
      pairView.setSortingEnabled(True)
      pairView.setShowGrid(False)

      pairView.setHorizontalHeader(PairComboBoxHeader(self.pairComboFilter))
      pairView.horizontalHeader().setStretchLastSection(True)
      pairView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
      pairView.horizontalHeader().setMinimumHeight(35)
      pairView.verticalHeader().setDefaultSectionSize(24);
      pairView.verticalHeader().hide()
      pairView.setMinimumWidth(400)

      self.ctrlPair.setView(pairView)
      self.ctrlPair.setModel(pairModel)

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
      print(currItem)

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

   def setPairList(self, pairList):
      try:
         self.ctrlPair.blockSignals(True)
         self.ctrlPair.clear()
         self.ctrlPair.addItems(['PAIR'] + pairList)
         self.ctrlPair.view().setRowHidden(0, True)
         self.ctrlTime.setEnabled(False)
         self.ctrlPair.blockSignals(False)
      except:
         print(pairList)

   def setIntervalList(self, intervalList):
      self.ctrlTime.blockSignals(True)
      self.ctrlTime.clear()
      self.ctrlTime.addItems(['TIME'] + intervalList)
      self.ctrlTime.view().setRowHidden(0, True)
      # setAlignment(QtCore.Qt.AlignCenter)
      for i in range(0,self.ctrlTime.model().rowCount()):
         self.ctrlTime.model().item(i).setData(QtCore.Qt.AlignHCenter, QtCore.Qt.TextAlignmentRole)
      self.ctrlTime.blockSignals(False)


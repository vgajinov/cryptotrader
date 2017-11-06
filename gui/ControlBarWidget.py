from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot


class ControlComboBox(QtWidgets.QComboBox):
   def __init__(self):
      super(ControlComboBox, self).__init__()

      # this is unsuccessful try to make the popup background translucent
      #self.view().setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint);
      #self.view().setParent(None);
      #self.view().setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
      #self.view().setAttribute(QtCore.Qt.WA_TranslucentBackground, True)


   def showPopup(self):
      super(ControlComboBox, self).showPopup()
      popup = self.findChild(QtWidgets.QFrame)
      # set popup position bellow combobox
      # (note that it uses global positioning, rather than relative to combobox)
      popup.move(popup.x(), self.mapToGlobal(self.frameGeometry().topLeft()).y() + self.height() - 5 )
      itemHeight = self.view().visualRect(self.model().index(1,0)).height()
      popup.setFixedHeight(self.count() * (itemHeight - 1))


class ControlBarWidget(QtWidgets.QWidget):
   itemChangedByUser = True

   def __init__(self, parent):
      super(ControlBarWidget, self).__init__()

      self.myParent = parent
      mainLayout = QtWidgets.QHBoxLayout(self)
      mainLayout.setContentsMargins(0,0,0,0)
      mainLayout.setSpacing(0)
      ctrlLeftLayout = QtWidgets.QHBoxLayout()
      ctrlRightLayout = QtWidgets.QHBoxLayout()

      self.ctrlExchange = ControlComboBox()
      self.ctrlExchange.setObjectName('exchangeCombo')
      self.ctrlExchange.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

      self.ctrlPair = ControlComboBox()
      self.ctrlPair.setObjectName('pairCombo')
      self.ctrlPair.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

      self.ctrlTime = ControlComboBox()
      self.ctrlTime.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlTime.setObjectName('timeCombo')

      # This centers the text but adds a scrollbar and the drop-down has to be enabled (only Qt4)
      #self.ctrlTime.setEditable(True)
      #self.ctrlTime.lineEdit().setReadOnly(True)
      #self.ctrlTime.lineEdit().setAlignment(QtCore.Qt.AlignCenter)

      ctrlLeftLayout.addWidget(self.ctrlExchange)
      ctrlLeftLayout.addWidget(self.ctrlPair)
      ctrlLeftLayout.addWidget(self.ctrlTime)
      ctrlLeftLayout.setSpacing(10)
      ctrlLeftLayout.setContentsMargins(5,5,5,5)
      ctrlLeftLayout.setAlignment(QtCore.Qt.AlignLeft)

      self.ctrlOverlay = ControlComboBox()
      self.ctrlOverlay.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlOverlay.setObjectName('overlayCombo')

      self.ctrlIndicator = ControlComboBox()
      self.ctrlIndicator.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlIndicator.setObjectName('indicatorCombo')

      ctrlRightLayout.addWidget(self.ctrlOverlay)
      ctrlRightLayout.addWidget(self.ctrlIndicator)
      ctrlRightLayout.setSpacing(10)
      ctrlRightLayout.setContentsMargins(5,5,5,5)
      ctrlRightLayout.setAlignment(QtCore.Qt.AlignRight)

      mainLayout.addLayout(ctrlLeftLayout)
      mainLayout.addLayout(ctrlRightLayout)

      self.setControlsData()


   def setControlsData(self):
      # Set exchange list
      exchangeList = ['Bitfinex', 'Kraken', 'Binance']
      self.ctrlExchange.addItems(exchangeList)

      # Set pair list
      pairList = ['BTCUSD', 'ETHBTC', 'DASHBTC', 'BCHBTC', 'ETCBTC', 'RPMBTC', 'ETHUSD', 'IOTABTC']
      self.ctrlPair.addItems(pairList)

      # Set time spans
      timeList = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w']
      self.ctrlTime.addItems(timeList)
      for i in range(self.ctrlTime.count()):
         self.ctrlTime.setItemData(i, QtCore.Qt.AlignCenter, QtCore.Qt.TextAlignmentRole)

      # Set overlays
      overlayList = ['Grid', 'EMA', 'SMA', 'Parabolic SAR', 'SomeLongOverlayExample',  'Grid', 'EMA', 'SMA', 'Parabolic SAR', 'SomeLongOverlayExample', 'Grid', 'EMA', 'SMA', 'Parabolic SAR', 'SomeLongOverlayExample']
      self.ctrlOverlay.setView(QtWidgets.QListView())  # this is a workaround for the known Qt > 5.5 bug
                                                       # which happens only with Fusion style
      self.ctrlOverlay.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
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

      # Set indicators
      indicatorList = ['MACD', 'RSA', 'StockRSA']
      self.ctrlIndicator.setView(QtWidgets.QListView())  # this is a workaround for the known Qt > 5.5 bug
                                                         # which happens only with Fusion style
      self.ctrlIndicator.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
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

      self.ctrlIndicator.model().itemChanged.connect(self.indicatorChanged)


   #@pyqtSlot(QtGui.QStandardItem)
   def indicatorChanged(self, itemChanged):
      if self.itemChangedByUser:
         if (itemChanged.checkState() == QtCore.Qt.Checked):
            self.myParent.ChartWidget.showIndicator(itemChanged.text())
         else:
            self.myParent.ChartWidget.hideIndicator(itemChanged.text())


   def resizeEvent(self, QResizeEvent):
      self.itemChangedByUser = False

      # common for all comboboxes
      fontSize = self.ctrlOverlay.font().pixelSize()

      # set the Overlay combobox popup size
      rowHeight = fontSize + 10
      rowWidth = 1.2*self.ctrlOverlay.view().sizeHintForColumn(0)
      self.ctrlOverlay.view().setMinimumWidth(rowWidth)
      self.ctrlOverlay.view().setMinimumHeight(rowHeight * (self.ctrlOverlay.model().rowCount()-1))
      for i in range(self.ctrlOverlay.model().rowCount())[1:]:
         #self.ctrlOverlay.model().setData(self.ctrlOverlay.model().index(i, 0), QtCore.QSize(200, 30), QtCore.Qt.SizeHintRole)
         self.ctrlOverlay.setItemData(i, QtCore.QSize(rowWidth, rowHeight), QtCore.Qt.SizeHintRole)


      # set the Indicator combobox popup size
      rowHeight = fontSize + 10
      rowWidth = 1.2*self.ctrlIndicator.view().sizeHintForColumn(0)
      self.ctrlIndicator.view().setMinimumWidth(rowWidth)
      self.ctrlIndicator.view().setMinimumHeight(rowHeight * (self.ctrlIndicator.model().rowCount() - 1))
      self.ctrlIndicator.setItemData(0, QtCore.QSize(rowWidth, 0), QtCore.Qt.SizeHintRole)
      for i in range(self.ctrlIndicator.model().rowCount())[1:]:
         self.ctrlIndicator.setItemData(i, QtCore.QSize(rowWidth, rowHeight), QtCore.Qt.SizeHintRole)

      self.itemChangedByUser = True

      # propagate event
      super(ControlBarWidget, self).resizeEvent(QResizeEvent)
      

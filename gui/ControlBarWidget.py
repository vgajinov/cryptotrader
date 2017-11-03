from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot


class ControlBarWidget(QtWidgets.QWidget):
   def __init__(self, parent):
      super(ControlBarWidget, self).__init__()

      self.myParent = parent
      mainLayout = QtWidgets.QHBoxLayout(self)
      mainLayout.setContentsMargins(0,0,0,0)
      mainLayout.setSpacing(0)
      ctrlLeftLayout = QtWidgets.QHBoxLayout()
      ctrlRightLayout = QtWidgets.QHBoxLayout()

      self.ctrlExchange = QtWidgets.QComboBox()
      self.ctrlExchange.setObjectName('exchangeCombo')
      self.ctrlExchange.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlExchangeView = QtWidgets.QListView()
      self.ctrlExchangeView.setObjectName('exchangeComboView')
      self.ctrlExchangeView.setSpacing(2)
      self.ctrlExchange.setView(self.ctrlExchangeView)


      self.ctrlPair = QtWidgets.QComboBox()
      self.ctrlPair.setObjectName('pairCombo')
      self.ctrlPair.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlPairView = QtWidgets.QListView()
      self.ctrlPairView.setObjectName('pairComboView')
      self.ctrlPairView.setSpacing(2)
      self.ctrlPair.setView(self.ctrlPairView)

      self.ctrlTime = QtWidgets.QComboBox()
      self.ctrlTime.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlTime.view().setSpacing(2)
      self.ctrlTime.setObjectName('timeCombo')

      # This centers the text but adds a scrollbar and the drop-down has to be enabled
      #self.ctrlTime.setEditable(True)
      #self.ctrlTime.lineEdit().setReadOnly(True)
      #self.ctrlTime.lineEdit().setAlignment(QtCore.Qt.AlignCenter)

      ctrlLeftLayout.addWidget(self.ctrlExchange)
      ctrlLeftLayout.addWidget(self.ctrlPair)
      ctrlLeftLayout.addWidget(self.ctrlTime)
      ctrlLeftLayout.setSpacing(10)
      ctrlLeftLayout.setContentsMargins(5,5,5,5)
      ctrlLeftLayout.setAlignment(QtCore.Qt.AlignLeft)

      self.ctrlOverlay = QtWidgets.QComboBox()
      self.ctrlOverlay.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlOverlay.view().setSpacing(2)
      self.ctrlOverlay.setObjectName('overlayCombo')

      self.ctrlIndicator = QtWidgets.QComboBox()
      self.ctrlIndicator.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlIndicator.view().setSpacing(2)
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
      self.ctrlExchange.addItems(['Bitfinex', 'Kraken', 'Binance'])

      # Set pair list
      pairList = ['BTCUSD', 'ETHBTC', 'DASHBTC', 'BCHBTC', 'ETCBTC', 'RPMBTC', 'ETHUSD', 'IOTABTC']
      self.ctrlPair.addItems(pairList)
      self.ctrlPairView.setMinimumHeight((len(pairList) + 1) * (self.ctrlPairView.sizeHintForRow(0) + 6))
      self.ctrlPairView.updateGeometry()

      # Set time spans
      timeList = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w']
      self.ctrlTime.addItems(timeList)
      self.ctrlTime.setMaxVisibleItems(len(timeList)+1)
      for i in range(self.ctrlTime.count()):
         self.ctrlTime.setItemData(i, QtCore.Qt.AlignCenter, QtCore.Qt.TextAlignmentRole)

      # Set overlays
      overlayList = ['Grid', 'EMA', 'SMA', 'Parabolic SAR', 'SomeLongOverlayExample']
      overlayModel = QtGui.QStandardItemModel(len(overlayList), 1)
      item = QtGui.QStandardItem('Overlays')
      item.setSelectable(False)
      overlayModel.setItem(0, item)
      for i in range(len(overlayList)):
         item = QtGui.QStandardItem(overlayList[i])
         item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
         item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
         overlayModel.setItem(i+1, item)
      self.ctrlOverlay.setModel(overlayModel)
      self.ctrlOverlay.view().setMinimumWidth(1.5 * self.ctrlOverlay.view().sizeHintForColumn(0))
      self.ctrlOverlay.view().setMinimumHeight(overlayModel.rowCount() * (self.ctrlOverlay.view().sizeHintForRow(1) + 3))
      self.ctrlOverlay.model().item(0,0).setSizeHint(QtCore.QSize(0,0))

      # Set indicators
      indicatorList = ['MACD', 'RSA', 'StockRSA']
      indicatorModel = QtGui.QStandardItemModel(len(indicatorList), 1)
      item = QtGui.QStandardItem('Indicators')
      item.setSelectable(False)
      indicatorModel.setItem(0, item)
      for i in range(len(indicatorList)):
         item = QtGui.QStandardItem(indicatorList[i])
         item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
         item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
         indicatorModel.setItem(i+1, item)
      self.ctrlIndicator.setModel(indicatorModel)
      self.ctrlIndicator.view().setMinimumWidth( 1.5 * self.ctrlIndicator.view().sizeHintForColumn(0))
      self.ctrlIndicator.view().setMinimumHeight((indicatorModel.rowCount()) * (self.ctrlIndicator.view().sizeHintForRow(1) + 3))
      self.ctrlIndicator.model().item(0,0).setSizeHint(QtCore.QSize(0,0))

      self.ctrlIndicator.model().itemChanged.connect(self.indicatorChanged)


   #@pyqtSlot(QtGui.QStandardItem)
   def indicatorChanged(self, itemChanged):
      if (itemChanged.checkState() == QtCore.Qt.Checked):
         self.myParent.ChartWidget.showIndicator(itemChanged.text())
      else:
         self.myParent.ChartWidget.hideIndicator(itemChanged.text())
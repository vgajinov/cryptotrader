from PyQt5 import QtCore, QtWidgets, QtGui
from .Overlays import OverlayFactory
from .Indicators import IndicatorFactory


class ControlComboBox(QtWidgets.QComboBox):
   def __init__(self):
      super(ControlComboBox, self).__init__()

      # this is unsuccessful try to make the popup background translucent
      # self.view().setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint);
      # self.view().setParent(None);
      # self.view().setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
      # self.view().setAttribute(QtCore.Qt.WA_TranslucentBackground, True)


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


class ControlBarWidget(QtWidgets.QWidget):
   itemChangedByUser = True

   def __init__(self, parent):
      super(ControlBarWidget, self).__init__()

      mainLayout = QtWidgets.QHBoxLayout(self)
      mainLayout.setContentsMargins(0,0,0,0)
      mainLayout.setSpacing(0)
      ctrlLeftLayout = QtWidgets.QHBoxLayout()
      ctrlRightLayout = QtWidgets.QHBoxLayout()

      self.ctrlExchange = ControlComboBox()
      self.ctrlExchange.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlExchange.setObjectName('exchangeCombo')

      self.ctrlPair = ControlComboBox()
      self.ctrlPair.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlPair.setObjectName('pairCombo')

      self.ctrlTime = ControlComboBox()
      self.ctrlTime.setView(QtWidgets.QListView())
      self.ctrlTime.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlTime.setObjectName('timeCombo')

      ctrlLeftLayout.addWidget(self.ctrlExchange)
      ctrlLeftLayout.addWidget(self.ctrlPair)
      ctrlLeftLayout.addWidget(self.ctrlTime)
      ctrlLeftLayout.setSpacing(10)
      ctrlLeftLayout.setContentsMargins(5,5,5,5)
      ctrlLeftLayout.setAlignment(QtCore.Qt.AlignLeft)

      self.ctrlOverlay = CheckableControlComboBox()
      self.ctrlOverlay.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.ctrlOverlay.setObjectName('overlayCombo')

      self.ctrlIndicator = CheckableControlComboBox()
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
      exchangeList = ['EXCHANGE']
      self.ctrlExchange.addItems(exchangeList)

      # Set pair list
      pairList = ['PAIR']
      self.ctrlPair.addItems(pairList)
      self.ctrlPair.setEnabled(False)

      # Set time spans
      timeList = ['TIME']
      self.ctrlTime.addItems(timeList)
      self.ctrlTime.setEnabled(False)

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

      self.ctrlExchange.currentTextChanged.connect(self.exchangeListChanged)
      self.ctrlPair.currentTextChanged.connect(self.pairListChanged)
      self.ctrlTime.currentTextChanged.connect(self.timeListChanged)
      self.ctrlOverlay.model().itemChanged.connect(self.overlayChanged)
      self.ctrlIndicator.model().itemChanged.connect(self.indicatorChanged)


   def exchangeListChanged(self, currItem):
      self.parent().exchangeChanged(currItem)
      self.ctrlPair.setEnabled(True)

   def pairListChanged(self, currItem):
      self.ctrlTime.setEnabled(True)
      self.parent().pairChanged(currItem)

   def timeListChanged(self, currItem):
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


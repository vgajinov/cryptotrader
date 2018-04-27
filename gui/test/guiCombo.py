import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets



class IndicatorComboBox(QtWidgets.QComboBox):
   def __init__(self):
      super(IndicatorComboBox, self).__init__()

   def showPopup(self):
      super(IndicatorComboBox, self).showPopup()
      popup = self.findChild(QtWidgets.QFrame)
      popup.move(popup.x(), self.mapToGlobal(self.geometry().topLeft()).y() + self.height())

   def setModel(self):
      # Set indicators
      self.setView(QtWidgets.QListView())
      self.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      indicatorList = ['Grid', 'EMA', 'SMA', 'Parabolic SAR', 'SomeLongOverlayExample',  'Grid', 'EMA', 'SMA', 'Parabolic SAR', 'SomeLongOverlayExample']
      indicatorModel = self.model()
         #QtGui.QStandardItemModel(len(indicatorList), 1)
      item = QtGui.QStandardItem('Indicators')
      item.setSelectable(False)
      indicatorModel.setItem(0, item)
      for i in range(len(indicatorList)):
         item = QtGui.QStandardItem(indicatorList[i])
         item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
         item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
         item.setCheckable(True)
         item.setCheckState(QtCore.Qt.Unchecked)
         indicatorModel.setItem(i+1, item)
         indicatorModel.setData(indicatorModel.index(i+1,0), QtCore.QSize(200,40), QtCore.Qt.SizeHintRole)
      self.view().setRowHidden(0, True)
      #super(ControlComboBox, self).setModel(indicatorModel)


class TimeComboBox(QtWidgets.QComboBox):
   def __init__(self):
      super(TimeComboBox, self).__init__()
      # self.setEditable(True)
      # self.lineEdit().setReadOnly(True)
      # self.lineEdit().setAlignment(QtCore.Qt.AlignHCenter)


   def showPopup(self):
      super(TimeComboBox, self).showPopup()
      popup = self.findChild(QtWidgets.QFrame)
      # set popup position bellow combobox
      # (note that it uses global positioning, rather than relative to combobox)
      popup.move(popup.x(), self.mapToGlobal(self.frameGeometry().topLeft()).y() + self.height() - 5 )
      itemHeight = self.view().visualRect(self.model().index(1,0)).height()
      popup.setMinimumHeight((self.count()-1) * (itemHeight))






class MainWindow(QtWidgets.QMainWindow):
   def __init__(self, width, height):
      super(MainWindow, self).__init__()

      print(QtWidgets.QStyleFactory.keys())
      self.resize(width, height)
      self.setWindowTitle('ComboBox')
      mainWidget = QtWidgets.QWidget()
      self.setCentralWidget(mainWidget)

      # time combo (center aligned)
      self.comboTime = TimeComboBox()
      self.comboTime.setView(QtWidgets.QListView())
      self.comboTime.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      self.comboTime.setObjectName('timeCombo')
      timeList = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w']
      self.comboTime.addItems(timeList)
      for i in range(0, self.comboTime.model().rowCount()):
         self.comboTime.model().item(i).setData(QtCore.Qt.AlignHCenter, QtCore.Qt.TextAlignmentRole)
         self.comboTime.model().item(i).setTextAlignment(QtCore.Qt.AlignHCenter)


      # indicator combo (checkable)
      comboInd = IndicatorComboBox()
      comboInd.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      comboInd.setObjectName('indicatorCombo')
      comboInd.setModel()


      mainLayout = QtWidgets.QHBoxLayout()
      mainWidget.setLayout(mainLayout)
      mainLayout.addWidget(self.comboTime)

      qss = open(os.path.join(os.path.dirname(__file__),'combo.qss'), 'r')
      self.setStyleSheet(qss.read())
      qss.close()





if __name__ == '__main__':
   app = QtWidgets.QApplication(sys.argv)
   # app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
   GUI = MainWindow(600, 400)
   GUI.show()
   app.exec_()

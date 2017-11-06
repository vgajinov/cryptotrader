import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets



class ControlComboBox(QtWidgets.QComboBox):
   def __init__(self):
      super(ControlComboBox, self).__init__()

   def showPopup(self):
      super(ControlComboBox, self).showPopup()
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



class MainWindow(QtWidgets.QMainWindow):
   def __init__(self, width, height):
      super(MainWindow, self).__init__()

      print(QtWidgets.QStyleFactory.keys())
      self.resize(width, height)
      self.setWindowTitle('ComboBox')
      mainWidget = QtWidgets.QWidget()
      self.setCentralWidget(mainWidget)

      combo = ControlComboBox()
      combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
      combo.setObjectName('timeCombo')
      #timeList = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w']
      #combo.addItems(timeList)
      combo.setModel()

#      combo = QtWidgets.QComboBox()
#      combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
#      combo.setObjectName('timeCombo')
#      combo.setView(QtWidgets.QListView())
#
#      indicatorList = ['MACD', 'RSA', 'StockRSA']
#      indicatorModel = combo.model()
#      item = QtGui.QStandardItem('Indicators')
#      item.setSelectable(False)
#      indicatorModel.setItem(0, item)
#      for i in range(len(indicatorList)):
#         item = QtGui.QStandardItem(indicatorList[i])
#         item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
#         item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
#         item.setCheckable(True)
#         item.setCheckState(QtCore.Qt.Unchecked)
#         indicatorModel.setItem(i+1, item)





      mainLayout = QtWidgets.QHBoxLayout()
      mainWidget.setLayout(mainLayout)
      mainLayout.addWidget(combo)

      #qss = open(os.path.join(os.path.dirname(__file__),'combo.qss'), 'r')
      #self.setStyleSheet(qss.read())
      #qss.close()







if __name__ == '__main__':
   app = QtWidgets.QApplication(sys.argv)
   app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
   GUI = MainWindow(600, 400)
   GUI.show()
   app.exec_()

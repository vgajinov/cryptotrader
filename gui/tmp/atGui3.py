# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'atGui.ui'
#
# Created: Sun Sep  3 00:32:10 2017
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import numpy as np
import pyqtgraph as pg

try:
   _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
   def _fromUtf8(s):
      return s

try:
   _encoding = QtGui.QApplication.UnicodeUTF8
   def _translate(context, text, disambig):
      return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
   def _translate(context, text, disambig):
      return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
   def setupUi(self, MainWindow):
      MainWindow.setObjectName(_fromUtf8("MainWindow"))
      MainWindow.resize(800, 600)
      MainWindow.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);\n"
""))
      self.centralwidget = QtGui.QWidget(MainWindow)
      self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
      self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
      self.verticalLayout.setSpacing(0)
      self.verticalLayout.setMargin(0)
      self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
      self.tabWidget = QtGui.QTabWidget(self.centralwidget)
      self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
      self.tabCharts = QtGui.QWidget()
      self.tabCharts.setObjectName(_fromUtf8("tabCharts"))
      self.gridLayout = QtGui.QGridLayout(self.tabCharts)
      self.gridLayout.setSpacing(0)
      self.gridLayout.setContentsMargins(0, -1, 0, -1)
      self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
      self.mainTabGrid = QtGui.QGridLayout()
      self.mainTabGrid.setSpacing(0)
      self.mainTabGrid.setObjectName(_fromUtf8("mainTabGrid"))
      self.frameCandles = QtGui.QFrame(self.tabCharts)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.frameCandles.sizePolicy().hasHeightForWidth())
      self.frameCandles.setSizePolicy(sizePolicy)
      self.frameCandles.setMinimumSize(QtCore.QSize(500, 300))
      self.frameCandles.setFrameShape(QtGui.QFrame.StyledPanel)
      self.frameCandles.setFrameShadow(QtGui.QFrame.Raised)
      self.frameCandles.setLineWidth(0)
      self.frameCandles.setObjectName(_fromUtf8("frameCandles"))
      self.horizontalLayout = QtGui.QHBoxLayout(self.frameCandles)
      self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
      self.mainTabGrid.addWidget(self.frameCandles, 0, 0, 1, 1)
      self.gridLayout.addLayout(self.mainTabGrid, 0, 0, 1, 1)
      self.tabWidget.addTab(self.tabCharts, _fromUtf8(""))
      self.tabPredictors = QtGui.QWidget()
      self.tabPredictors.setObjectName(_fromUtf8("tabPredictors"))
      self.tabWidget.addTab(self.tabPredictors, _fromUtf8(""))
      self.verticalLayout.addWidget(self.tabWidget)
      MainWindow.setCentralWidget(self.centralwidget)
      self.menubar = QtGui.QMenuBar(MainWindow)
      self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
      self.menubar.setObjectName(_fromUtf8("menubar"))
      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setObjectName(_fromUtf8("menuFile"))
      MainWindow.setMenuBar(self.menubar)
      self.statusbar = QtGui.QStatusBar(MainWindow)
      self.statusbar.setObjectName(_fromUtf8("statusbar"))
      MainWindow.setStatusBar(self.statusbar)
      self.menubar.addAction(self.menuFile.menuAction())

      pview = pg.PlotWidget(self.frameCandles)
      self.horizontalLayout.addWidget(pview)
      p2 = pview
      p2.plot(np.random.normal(size=100), pen=(255, 0, 0), name="Red curve")
      p2.plot(np.random.normal(size=110) + 5, pen=(0, 255, 0), name="Green curve")
      p2.plot(np.random.normal(size=120) + 10, pen=(0, 0, 255), name="Blue curve")

      self.retranslateUi(MainWindow)
      self.tabWidget.setCurrentIndex(0)
      QtCore.QMetaObject.connectSlotsByName(MainWindow)

   def retranslateUi(self, MainWindow):
      MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
      self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCharts), _translate("MainWindow", "Charts", None))
      self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPredictors), _translate("MainWindow", "Predictors", None))
      self.menuFile.setTitle(_translate("MainWindow", "File", None))

from pyqtgraph import PlotWidget

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
   def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
      QtGui.QMainWindow.__init__(self, parent, f)

      self.setupUi(self)


if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   MainWindow = QtGui.QMainWindow()
   ui = Ui_MainWindow()
   ui.setupUi(MainWindow)
   MainWindow.show()
   sys.exit(app.exec_())


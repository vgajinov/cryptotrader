import os
import configparser
from PyQt5 import QtCore, QtWidgets, QtGui
from .Separators import *
from .TradingTab import TradingTab

from .InfoMessageBox import InfoMessageBox


class ATMainWindow(QtWidgets.QMainWindow):
   keysDirectory = ''

   def __init__(self, width, height):
      super(ATMainWindow, self).__init__()

      # window properties
      self.setWindowTitle('AutoTrader')
      self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'style', 'logo.png')))
      self.setMinimumSize(1280, 720)
      width = max(1280, width)
      height = max(720,height)
      self.resize(width, height)

      # menu
      self.createMenu()

      # set central widget
      self.centralwidget = QtWidgets.QWidget(self)
      self.setCentralWidget(self.centralwidget)
      self.horizontalLayout = QtWidgets.QVBoxLayout(self.centralwidget)

      # add Tab widget
      self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
      self.tabWidget.setObjectName('mainTabWidget')
      self.tabTrade = TradingTab()
      self.tabPredictors = QtWidgets.QWidget()
      self.tabWidget.addTab(self.tabTrade, "Trade")
      self.tabWidget.addTab(self.tabPredictors, "Predictors")
      self.horizontalLayout.addWidget(self.tabWidget)
      self.horizontalLayout.setContentsMargins(0,5,0,0)

      #import stylesheet file
      qss = open(os.path.join(os.path.dirname(__file__), 'style', 'style.qss'), 'r')
      self.setStyleSheet(qss.read())
      qss.close()

      # load configuration
      self.loadConfiguration()


   def createMenu(self):
      loadKeysAction = QtWidgets.QAction('Load exchange keys', self)
      loadKeysAction.triggered.connect(self.loadKeysPopup)

      loadConfiguration = QtWidgets.QAction('Load configuration', self)
      loadConfiguration.triggered.connect(self.loadConfigurationFromFile)
      saveConfiguration = QtWidgets.QAction('Save configuration', self)
      saveConfiguration.triggered.connect(self.saveConfigurationToFile)

      quitAction = QtWidgets.QAction('Quit', self)
      quitAction.setShortcut('Ctrl+q')
      quitAction.setStatusTip('Quit AutoTrader')
      quitAction.triggered.connect(self.close)

      self.menubar = QtWidgets.QMenuBar(self)
      self.menuFile = QtWidgets.QMenu(self.menubar)
      self.menuFile.setTitle("File")
      self.setMenuBar(self.menubar)

      self.menubar.addAction(self.menuFile.menuAction())
      self.menuFile.addAction(loadKeysAction)
      self.menuFile.addSeparator()
      self.menuFile.addAction(loadConfiguration)
      self.menuFile.addAction(saveConfiguration)
      self.menuFile.addSeparator()
      self.menuFile.addAction(quitAction)


   # ------------------------------------------------------------------------------------
   # Event Handlers
   # ------------------------------------------------------------------------------------

   def closeEvent(self, event):
      self.saveConfiguration()
      self.tabTrade.closeConnections()
      event.accept()

   def loadKeysPopup(self):
      dlg = QtWidgets.QFileDialog()
      dlg.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
      if dlg.exec_() == QtWidgets.QDialog.Accepted:
         self.keysDirectory = dlg.selectedFiles()[0]
         self.tabTrade.setKeysDirectory(self.keysDirectory)

   def loadConfigurationFromFile(self):
      dlg = QtWidgets.QFileDialog()
      dlg.setWindowTitle('Load configuration from file')
      if dlg.exec_() == QtWidgets.QDialog.Accepted:
         self.loadConfiguration(dlg.selectedFiles()[0])

   def saveConfigurationToFile(self):
      dlg = QtWidgets.QFileDialog()
      dlg.setWindowTitle('Save configuration to file')
      dlg.setAcceptMode(QtGui.QFileDialog.AcceptSave)
      dlg.setNameFilter('*.ini')
      if dlg.exec_() == QtWidgets.QDialog.Accepted:
         self.saveConfiguration(dlg.selectedFiles()[0])


   # ------------------------------------------------------------------------------------
   # Configuration
   # ------------------------------------------------------------------------------------

   def loadConfiguration(self, file='config.ini'):
      self.setCursor(QtCore.Qt.WaitCursor)
      try:
         config = configparser.ConfigParser()
         config.read(file)
         keys = config['KEYS']['keyDirectory']
         if keys:
            self.keysDirectory = keys
            self.tabTrade.setKeysDirectory(self.keysDirectory)
         self.tabTrade.controlBarWidget.loadConfiguration(config)
      except Exception as e:
         print(e)
      self.setCursor(QtCore.Qt.ArrowCursor)


   def saveConfiguration(self, file='config.ini'):
      config = configparser.ConfigParser()
      config['KEYS'] = {'keyDirectory': self.keysDirectory}
      self.tabTrade.controlBarWidget.saveConfiguration(config)
      with open(file, 'w') as cfgFile:
         config.write(cfgFile)






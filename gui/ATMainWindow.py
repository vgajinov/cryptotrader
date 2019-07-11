import os
import configparser
import traceback
from PyQt5 import QtCore, QtWidgets, QtGui
from .Separators import *
from .TradingTab import TradingTab


class ATMainWindow(QtWidgets.QMainWindow):
    """The main GUI window."""
    keysDirectory = ''

    def __init__(self, width, height):
        super(ATMainWindow, self).__init__()

        # window properties
        self.setWindowTitle('AutoTrader')
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'style', 'logo.png')))
        self.setMinimumSize(1280, 720)
        width = max(1280, width)
        height = max(720, height)
        self.resize(width, height)

        # menu
        self.createMenu()

        # set central widget
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.horizontalLayout = QtWidgets.QVBoxLayout(self.central_widget)

        # add Tab widget
        self.tabWidget = QtWidgets.QTabWidget(self.central_widget)
        self.tabWidget.setObjectName('mainTabWidget')
        self.tabTrade = TradingTab(self)
        self.tabPredictors = QtWidgets.QWidget()
        self.tabWidget.addTab(self.tabTrade, "Trade")
        self.tabWidget.addTab(self.tabPredictors, "Predictors")
        self.horizontalLayout.addWidget(self.tabWidget)
        self.horizontalLayout.setContentsMargins(0, 5, 0, 0)

        # import stylesheet file
        qss = open(os.path.join(os.path.dirname(__file__), 'style', 'style.qss'), 'r')
        self.setStyleSheet(qss.read())
        qss.close()

        # load configuration
        self.loadConfiguration()


    def createMenu(self):
        """Create the main window menu."""
        load_keys_action = QtWidgets.QAction('Load exchange keys', self)
        load_keys_action.triggered.connect(self.load_keys_popup)

        load_config_action = QtWidgets.QAction('Load configuration', self)
        load_config_action.triggered.connect(self.load_config_dialog)
        save_config_action = QtWidgets.QAction('Save configuration', self)
        save_config_action.triggered.connect(self.save_config_dialog)

        quit_action = QtWidgets.QAction('Quit', self)
        quit_action.setShortcut('Ctrl+q')
        quit_action.setStatusTip('Quit AutoTrader')
        quit_action.triggered.connect(self.close)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setTitle("File")
        self.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(load_keys_action)
        self.menuFile.addSeparator()
        self.menuFile.addAction(load_config_action)
        self.menuFile.addAction(save_config_action)
        self.menuFile.addSeparator()
        self.menuFile.addAction(quit_action)


    # ------------------------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------------------------

    def closeEvent(self, event):
        """Handles application closing event.
        Saves the current configuration to a config file and closes all connection to exchange clients.
        """
        self.saveConfiguration()
        self.tabTrade.closeConnections()
        event.accept()

    def load_keys_popup(self):
        """Displays a popup dialog for loading the exchange keys"""
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.keysDirectory = dlg.selectedFiles()[0]
            self.tabTrade.setKeysDirectory(self.keysDirectory)

    def load_config_dialog(self):
        """Displays a popup dialog for loading the configuration file"""
        dlg = QtWidgets.QFileDialog()
        dlg.setWindowTitle('Load configuration from file')
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.loadConfiguration(dlg.selectedFiles()[0])

    def save_config_dialog(self):
        """Displays a popup dialog for saving the configuration file"""
        dlg = QtWidgets.QFileDialog()
        dlg.setWindowTitle('Save configuration to file')
        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dlg.setNameFilter('*.ini')
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.saveConfiguration(dlg.selectedFiles()[0])


    # ------------------------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------------------------

    def loadConfiguration(self, file='config.ini'):
        """Loads the configuration from a file"""
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
            self.showExceptionPopup(e)
        self.setCursor(QtCore.Qt.ArrowCursor)


    def saveConfiguration(self, file='config.ini'):
        """Saves the configuration to a file"""
        config = configparser.ConfigParser()
        config['KEYS'] = {'keyDirectory': self.keysDirectory}
        self.tabTrade.controlBarWidget.saveConfiguration(config)
        with open(file, 'w') as cfgFile:
            config.write(cfgFile)


    # ------------------------------------------------------------------------------------
    # Exception handling
    # ------------------------------------------------------------------------------------

    def showExceptionPopup(self, exception):
        """Displays an exception warning popup"""
        self.tabTrade.blockSignals(True)
        self.tabTrade.setDisabled(True)

        popup = QtWidgets.QMessageBox()
        popup.setWindowTitle("Warning")
        popup.setIcon(QtWidgets.QMessageBox.Warning)
        popup.setText(f"Exception caught:\n\n{exception}\n\n{''.join(traceback.format_exc())}")
        ignoreButton = popup.addButton(QtWidgets.QMessageBox.Ignore)
        abortButton  = popup.addButton(QtWidgets.QMessageBox.Abort)
        popup.exec()
        if popup.clickedButton() == abortButton:
            self.close()
            exit(-1)

        self.tabTrade.setDisabled(False)
        self.tabTrade.blockSignals(False)



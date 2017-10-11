import sys
from PyQt4 import QtGui, QtCore

class Window(QtGui.QMainWindow):
   def __init__(self):
      super(Window, self).__init__()
      self.setGeometry(50, 50, 500, 300)
      self.setWindowTitle('AutoTrader')
      self.setWindowIcon(QtGui.QIcon('logo.png'))

      self.statusBar()

      self.createMenu()
      self.createToolBar()

      self.checkBox = QtGui.QCheckBox('Enlarge window', self)
      self.checkBox.stateChanged.connect(self.enlargeWindow)
      self.checkBox.move(100, 22)
      self.checkBox.setFixedWidth(150)

      # Styles
      self.styleChoice = QtGui.QLabel(self.style().objectName(), self)
      self.comboBox = QtGui.QComboBox(self)
      for style in QtGui.QStyleFactory.keys():
         self.comboBox.addItem(style)
      self.comboBox.move(50,250)
      self.styleChoice.move(50,220)
      self.comboBox.activated[str].connect(self.style_choice)

      self.home()


   def createMenu(self):
      quitAction = QtGui.QAction('&Quit', self)
      quitAction.setShortcut('Ctrl+q')
      quitAction.setStatusTip('Quit AutoTrader')
      quitAction.triggered.connect(self.close)

      mainMenu = self.menuBar()
      fileMenu = mainMenu.addMenu('&File')
      fileMenu.addAction(quitAction)


   def createToolBar(self):
      quitAction = QtGui.QAction(QtGui.QIcon('quit.png'), 'Quit', self)
      quitAction.triggered.connect(self.close)
      self.toolBar = self.addToolBar('Extraction')
      self.toolBar.addAction(quitAction)


   def enlargeWindow(self, state):
      if state:
         self.setGeometry(50, 50, 1000, 600)
      else:
         self.setGeometry(50, 50, 500,300)


   def style_choice(self, choice):
      self.styleChoice.setText(choice)
      QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(choice))


   def home(self):
      btn = QtGui.QPushButton('Quit', self)
      btn.clicked.connect(self.close)

      btn.resize(100,100)
      btn.move(100,100)

      self.show()


   def close(self):
      choice = QtGui.QMessageBox.question(self, 'AutoTrader', 'Are you sure you want to exit?',
                                 QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
      if choice == QtGui.QMessageBox.Yes:
         sys.exit()



def run():
   app = QtGui.QApplication(sys.argv)
   GUI = Window()
   sys.exit(app.exec_())

run()
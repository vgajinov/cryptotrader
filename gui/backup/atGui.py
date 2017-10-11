import sys
import numpy as np
from PyQt4 import QtCore, QtGui
from pyqtgraph import PlotWidget

class ATMainWindow(QtGui.QMainWindow):
   def __init__(self, width, height):
      super(ATMainWindow, self).__init__()

      # window properties
      self.setWindowTitle('AutoTrader')
      self.setWindowIcon(QtGui.QIcon('logo.png'))
      self.resize(width, height)
      self.setStyleSheet(
         "background-color: rgb(0, 0, 0);\n"
         "color: rgb(255, 255, 255);\n")

      self.createMenu()

      # set central widget
      self.centralwidget = QtGui.QWidget(self)
      self.setCentralWidget(self.centralwidget)
      self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)

      # add Tab widget
      self.tabWidget = QtGui.QTabWidget(self.centralwidget)
      self.tabCharts = QtGui.QWidget()
      self.tabPredictors = QtGui.QWidget()
      self.tabWidget.addTab(self.tabCharts, "Charts")
      self.tabWidget.addTab(self.tabPredictors, "Predictors")
      self.verticalLayout.addWidget(self.tabWidget)

      # create tabs
      self.createChartTab()
      self.createPredictorTab()



      #self.statusbar = QtGui.QStatusBar(MainWindow)
      #MainWindow.setStatusBar(self.statusbar)


   # createMenu
   # ---------------------------------------------------------
   def createMenu(self):
      quitAction = QtGui.QAction('Quit', self)
      quitAction.setShortcut('Ctrl+q')
      quitAction.setStatusTip('Quit AutoTrader')
      #quitAction.triggered.connect(self.close)

      self.menubar = QtGui.QMenuBar(self)
      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setTitle("File")
      self.setMenuBar(self.menubar)
      self.menubar.addAction(self.menuFile.menuAction())
      self.menuFile.addAction(quitAction)


   # createChartTab
   # ---------------------------------------------------------
   def createChartTab(self):
      self.chartTabGrid = QtGui.QGridLayout(self.tabCharts)
      #self.frameCandles = QtGui.QFrame(self.tabCharts)
      #self.frameCandles.setMinimumSize(QtCore.QSize(500, 300))
      #self.frameCandles.setFrameShape(QtGui.QFrame.StyledPanel)
      #self.frameCandles.setFrameShadow(QtGui.QFrame.Raised)
      #self.frameCandles.setLineWidth(0)

      #p1 = PlotWidget(self.frameCandles)
      p1 = PlotWidget()
      p1.plot(np.random.normal(size=100), pen=(255, 0, 0), name="Red curve")
      p1.plot(np.random.normal(size=110) + 5, pen=(0, 255, 0), name="Green curve")
      p1.plot(np.random.normal(size=120) + 10, pen=(0, 0, 255), name="Blue curve")

      self.frame2 = QtGui.QFrame(self.tabCharts)
      #p2 = PlotWidget(self.frame2)
      p2 = PlotWidget()
      x = np.cos(np.linspace(0, 2 * np.pi, 1000))
      y = np.sin(np.linspace(0, 4 * np.pi, 1000))
      p2.plot(x, y)
      p2.showGrid(x=True, y=True)

      self.chartTabGrid.addWidget(p1, 0, 0, 1, 1)
      self.chartTabGrid.addWidget(p2, 0, 1, 1, 1)
      self.chartTabGrid.setColumnStretch(0,3)
      self.chartTabGrid.setColumnStretch(1,1)


   # createPredictorTab
   # ---------------------------------------------------------
   def createPredictorTab(self):
      pass



# =================================================================================
#   Run qt app
# =================================================================================
def run():
   app = QtGui.QApplication(sys.argv)
   screenSize = app.desktop().screenGeometry()
   GUI = ATMainWindow(screenSize.width(), screenSize.height())
   GUI.show()
   sys.exit(app.exec_())


run()

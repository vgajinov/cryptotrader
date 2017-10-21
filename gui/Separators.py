from PyQt4 import QtGui

COLOR_SEPARATOR = 'rgb(167, 174, 186, 50)'


class LineSeparator(QtGui.QLabel):
   def __init__(self, orientation='', color='white', stroke=1):
      super(LineSeparator, self).__init__()

      if orientation not in ['vertical', 'v', 'horizontal', 'h']:
         raise ValueError("orientation parameter only accepts values from the following list ['vertical', 'v', 'horizontal', 'h'].")
      if stroke <= 0:
         raise ValueError("the value of stroke parameter has to be positive.")

      if orientation=='vertical' or orientation=='v':
         self.setFixedWidth(stroke)
      else:
         self.setFixedHeight(stroke)
      self.setStyleSheet('background-color:' + color + ';')




class DoubleLineSeparator(QtGui.QWidget):
   def __init__(self, orientation='', linecolor='white', spacecolor='black', stroke=1, width=3):
      super(DoubleLineSeparator, self).__init__()

      if orientation not in ['vertical', 'v', 'horizontal', 'h']:
         raise ValueError("orientation parameter only accepts values from the following list ['vertical', 'v', 'horizontal', 'h'].")
      if stroke <= 0:
         raise ValueError("the value of stroke parameter has to be positive.")
      if width <= 0:
         raise ValueError("the value of width parameter has to be positive.")

      if orientation=='vertical' or orientation=='v':
         layout = QtGui.QHBoxLayout()
         layout.setMargin(0)
         layout.setSpacing(0)
         layout.addWidget(LineSeparator(orientation='v', color=linecolor, stroke=stroke))
         layout.addWidget(LineSeparator(orientation='v', color=spacecolor, stroke=width))
         layout.addWidget(LineSeparator(orientation='v', color=linecolor, stroke=stroke))
         self.setLayout(layout)
      else:
         layout = QtGui.QVBoxLayout()
         layout.setMargin(0)
         layout.setSpacing(0)
         layout.addWidget(LineSeparator(orientation='h', color=linecolor, stroke=stroke))
         layout.addWidget(LineSeparator(orientation='h', color=spacecolor, stroke=width))
         layout.addWidget(LineSeparator(orientation='h', color=linecolor, stroke=stroke))
         self.setLayout(layout)

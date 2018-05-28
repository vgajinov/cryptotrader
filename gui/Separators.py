from PyQt5 import QtWidgets

COLOR_SEPARATOR = 'rgb(167, 174, 186, 50)'


class LineSeparator(QtWidgets.QLabel):
   def __init__(self, orientation='', color=COLOR_SEPARATOR, stroke=1):
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




class DoubleLineSeparator(QtWidgets.QWidget):
   def __init__(self, orientation='', linecolor=COLOR_SEPARATOR, spacecolor='black', stroke=1, width=3):
      super(DoubleLineSeparator, self).__init__()

      if orientation not in ['vertical', 'v', 'horizontal', 'h']:
         raise ValueError("orientation parameter only accepts values from the following list ['vertical', 'v', 'horizontal', 'h'].")
      if stroke <= 0:
         raise ValueError("the value of stroke parameter has to be positive.")
      if width <= 0:
         raise ValueError("the value of width parameter has to be positive.")

      if orientation=='vertical' or orientation=='v':
         layout = QtWidgets.QHBoxLayout()
         layout.setMargin(0)
         layout.setSpacing(0)
         layout.addWidget(LineSeparator(orientation='v', color=linecolor, stroke=stroke))
         layout.addWidget(LineSeparator(orientation='v', color=spacecolor, stroke=width))
         layout.addWidget(LineSeparator(orientation='v', color=linecolor, stroke=stroke))
         self.setLayout(layout)
      else:
         layout = QtWidgets.QVBoxLayout()
         layout.setContentsMargins(0,0,0,0)
         layout.setSpacing(0)
         layout.addWidget(LineSeparator(orientation='h', color=linecolor, stroke=stroke))
         layout.addWidget(LineSeparator(orientation='h', color=spacecolor, stroke=width))
         layout.addWidget(LineSeparator(orientation='h', color=linecolor, stroke=stroke))
         self.setLayout(layout)

from abc import ABC, abstractmethod
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
import talib
from .Separators import *

# check https://mrjbq7.github.io/ta-lib/func.html for ta-lib function documentation

# # list of TA-lib indicators
# 'Cycle Indicators'     : ['HT_DCPERIOD', 'HT_DCPHASE', 'HT_PHASOR', 'HT_SINE', 'HT_TRENDMODE'],
# 'Math Operators'       : ['ADD', 'DIV', 'MAX', 'MAXINDEX', 'MIN', 'MININDEX', 'MINMAX', 'MINMAXINDEX', 'MULT', 'SUB', 'SUM'],
# 'Math Transform'       : ['ACOS', 'ASIN', 'ATAN', 'CEIL', 'COS', 'COSH', 'EXP', 'FLOOR', 'LN', 'LOG10', 'SIN', 'SINH', 'SQRT', 'TAN', 'TANH'],
# 'Momentum Indicators'  : ['ADX', 'ADXR', 'APO', 'AROON', 'AROONOSC', 'BOP', 'CCI', 'CMO', 'DX', 'MACD', 'MACDEXT', 'MACDFIX', 'MFI', 'MINUS_DI', 'MINUS_DM', 'MOM', 'PLUS_DI', 'PLUS_DM', 'PPO', 'ROC', 'ROCP', 'ROCR', 'ROCR100', 'RSI', 'STOCH', 'STOCHF', 'STOCHRSI', 'TRIX', 'ULTOSC', 'WILLR'],
# 'Overlap Studies'      : ['BBANDS', 'DEMA', 'EMA', 'HT_TRENDLINE', 'KAMA', 'MA', 'MAMA', 'MAVP', 'MIDPOINT', 'MIDPRICE', 'SAR', 'SAREXT', 'SMA', 'T3', 'TEMA', 'TRIMA', 'WMA'],
# 'Pattern Recognition'  : ['CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE', 'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS', 'CDLABANDONEDBABY', 'CDLADVANCEBLOCK', 'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL', 'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI', 'CDLDOJISTAR', 'CDLDRAGONFLYDOJI', 'CDLENGULFING', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN', 'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS', 'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH', 'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI', 'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW', 'CDLMATHOLD', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR', 'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS', 'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR', 'CDLSHORTLINE', 'CDLSPINNINGTOP', 'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP', 'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS'],
# 'Price Transform'      : ['AVGPRICE', 'MEDPRICE', 'TYPPRICE', 'WCLPRICE'],
# 'Statistic Functions'  : ['BETA', 'CORREL', 'LINEARREG', 'LINEARREG_ANGLE', 'LINEARREG_INTERCEPT', 'LINEARREG_SLOPE', 'STDDEV', 'TSF', 'VAR'],
# 'Volatility Indicators': ['ATR', 'NATR', 'TRANGE'],
# 'Volume Indicators'    : ['AD', 'ADOSC', 'OBV']}
#
#
# AD                  Chaikin A/D Line
# ADOSC               Chaikin A/D Oscillator
# ADX                 Average Directional Movement Index
# ADXR                Average Directional Movement Index Rating
# APO                 Absolute Price Oscillator
# AROON               Aroon
# AROONOSC            Aroon Oscillator
# ATR                 Average True Range
# AVGPRICE            Average Price
# BBANDS              Bollinger Bands
# BETA                Beta
# BOP                 Balance Of Power
# CCI                 Commodity Channel Index
# CDL2CROWS           Two Crows
# CDL3BLACKCROWS      Three Black Crows
# CDL3INSIDE          Three Inside Up/Down
# CDL3LINESTRIKE      Three-Line Strike
# CDL3OUTSIDE         Three Outside Up/Down
# CDL3STARSINSOUTH    Three Stars In The South
# CDL3WHITESOLDIERS   Three Advancing White Soldiers
# CDLABANDONEDBABY    Abandoned Baby
# CDLADVANCEBLOCK     Advance Block
# CDLBELTHOLD         Belt-hold
# CDLBREAKAWAY        Breakaway
# CDLCLOSINGMARUBOZU  Closing Marubozu
# CDLCONCEALBABYSWALL Concealing Baby Swallow
# CDLCOUNTERATTACK    Counterattack
# CDLDARKCLOUDCOVER   Dark Cloud Cover
# CDLDOJI             Doji
# CDLDOJISTAR         Doji Star
# CDLDRAGONFLYDOJI    Dragonfly Doji
# CDLENGULFING        Engulfing Pattern
# CDLEVENINGDOJISTAR  Evening Doji Star
# CDLEVENINGSTAR      Evening Star
# CDLGAPSIDESIDEWHITE Up/Down-gap side-by-side white lines
# CDLGRAVESTONEDOJI   Gravestone Doji
# CDLHAMMER           Hammer
# CDLHANGINGMAN       Hanging Man
# CDLHARAMI           Harami Pattern
# CDLHARAMICROSS      Harami Cross Pattern
# CDLHIGHWAVE         High-Wave Candle
# CDLHIKKAKE          Hikkake Pattern
# CDLHIKKAKEMOD       Modified Hikkake Pattern
# CDLHOMINGPIGEON     Homing Pigeon
# CDLIDENTICAL3CROWS  Identical Three Crows
# CDLINNECK           In-Neck Pattern
# CDLINVERTEDHAMMER   Inverted Hammer
# CDLKICKING          Kicking
# CDLKICKINGBYLENGTH  Kicking - bull/bear determined by the longer marubozu
# CDLLADDERBOTTOM     Ladder Bottom
# CDLLONGLEGGEDDOJI   Long Legged Doji
# CDLLONGLINE         Long Line Candle
# CDLMARUBOZU         Marubozu
# CDLMATCHINGLOW      Matching Low
# CDLMATHOLD          Mat Hold
# CDLMORNINGDOJISTAR  Morning Doji Star
# CDLMORNINGSTAR      Morning Star
# CDLONNECK           On-Neck Pattern
# CDLPIERCING         Piercing Pattern
# CDLRICKSHAWMAN      Rickshaw Man
# CDLRISEFALL3METHODS Rising/Falling Three Methods
# CDLSEPARATINGLINES  Separating Lines
# CDLSHOOTINGSTAR     Shooting Star
# CDLSHORTLINE        Short Line Candle
# CDLSPINNINGTOP      Spinning Top
# CDLSTALLEDPATTERN   Stalled Pattern
# CDLSTICKSANDWICH    Stick Sandwich
# CDLTAKURI           Takuri (Dragonfly Doji with very long lower shadow)
# CDLTASUKIGAP        Tasuki Gap
# CDLTHRUSTING        Thrusting Pattern
# CDLTRISTAR          Tristar Pattern
# CDLUNIQUE3RIVER     Unique 3 River
# CDLUPSIDEGAP2CROWS  Upside Gap Two Crows
# CDLXSIDEGAP3METHODS Upside/Downside Gap Three Methods
# CMO                 Chande Momentum Oscillator
# CORREL              Pearson's Correlation Coefficient (r)
# DEMA                Double Exponential Moving Average
# DX                  Directional Movement Index
# EMA                 Exponential Moving Average
# HT_DCPERIOD         Hilbert Transform - Dominant Cycle Period
# HT_DCPHASE          Hilbert Transform - Dominant Cycle Phase
# HT_PHASOR           Hilbert Transform - Phasor Components
# HT_SINE             Hilbert Transform - SineWave
# HT_TRENDLINE        Hilbert Transform - Instantaneous Trendline
# HT_TRENDMODE        Hilbert Transform - Trend vs Cycle Mode
# KAMA                Kaufman Adaptive Moving Average
# LINEARREG           Linear Regression
# LINEARREG_ANGLE     Linear Regression Angle
# LINEARREG_INTERCEPT Linear Regression Intercept
# LINEARREG_SLOPE     Linear Regression Slope
# MA                  All Moving Average
# MACD                Moving Average Convergence/Divergence
# MACDEXT             MACD with controllable MA type
# MACDFIX             Moving Average Convergence/Divergence Fix 12/26
# MAMA                MESA Adaptive Moving Average
# MAX                 Highest value over a specified period
# MAXINDEX            Index of highest value over a specified period
# MEDPRICE            Median Price
# MFI                 Money Flow Index
# MIDPOINT            MidPoint over period
# MIDPRICE            Midpoint Price over period
# MIN                 Lowest value over a specified period
# MININDEX            Index of lowest value over a specified period
# MINMAX              Lowest and highest values over a specified period
# MINMAXINDEX         Indexes of lowest and highest values over a specified period
# MINUS_DI            Minus Directional Indicator
# MINUS_DM            Minus Directional Movement
# MOM                 Momentum
# NATR                Normalized Average True Range
# OBV                 On Balance Volume
# PLUS_DI             Plus Directional Indicator
# PLUS_DM             Plus Directional Movement
# PPO                 Percentage Price Oscillator
# ROC                 Rate of change : ((price/prevPrice)-1)*100
# ROCP                Rate of change Percentage: (price-prevPrice)/prevPrice
# ROCR                Rate of change ratio: (price/prevPrice)
# ROCR100             Rate of change ratio 100 scale: (price/prevPrice)*100
# RSI                 Relative Strength Index
# SAR                 Parabolic SAR
# SAREXT              Parabolic SAR - Extended
# SMA                 Simple Moving Average
# STDDEV              Standard Deviation
# STOCH               Stochastic
# STOCHF              Stochastic Fast
# STOCHRSI            Stochastic Relative Strength Index
# SUM                 Summation
# T3                  Triple Exponential Moving Average (T3)
# TEMA                Triple Exponential Moving Average
# TRANGE              True Range
# TRIMA               Triangular Moving Average
# TRIX                1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
# TSF                 Time Series Forecast
# TYPPRICE            Typical Price
# ULTOSC              Ultimate Oscillator
# VAR                 Variance
# WCLPRICE            Weighted Close Price
# WILLR               Williams' %R
# WMA                 Weighted Moving Average


# implement:
# RSI, Stochastic RSI, stochastic
# Money Flow Index, Momentum, Rate of change Percentage, BOP - Balance Of Power,
# AROON - Aroon, AROONOSC - Aroon Oscillator
# ADOSC - Chaikin A/D Oscillator


# CCI                 Commodity Channel Index


# ------------------------------------------------------------------------------------
# Indicator Factory
# ------------------------------------------------------------------------------------

class IndicatorFactory(object):
   indicators = None

   @staticmethod
   def createIndicator(name):
      if not IndicatorFactory.indicators:
         IndicatorFactory.indicators = {}
         for ind in Indicator.__subclasses__():
            IndicatorFactory.indicators[ind.__name__] = ind
      if name in IndicatorFactory.indicators.keys():
         return IndicatorFactory.indicators[name]()
      else:
         print('Indicator not defined')

   @staticmethod
   def getIndicatorNames():
      if not IndicatorFactory.indicators:
         IndicatorFactory.indicators = {}
         for ind in Indicator.__subclasses__():
            IndicatorFactory.indicators[ind.__name__] = ind
      return sorted(list(IndicatorFactory.indicators.keys()))


# ------------------------------------------------------------------------------------
# Indicator base class
# ------------------------------------------------------------------------------------

class Indicator(QtChart.QChart):
   frame = None

   def __init__(self):
      super(Indicator, self).__init__()
      self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
      self.setBackgroundRoundness(0)
      self.setMargins(QtCore.QMargins(0, 0, 0, 0))
      self.layout().setContentsMargins(0, 0, 0, 0);
      self.legend().hide()
      chartFont = QtGui.QFont(self.font())
      chartFont.setPixelSize(9)
      self.setFont(chartFont)

      self.IndicatorName = QtWidgets.QGraphicsSimpleTextItem(self)
      self.IndicatorName.setBrush(QtGui.QBrush(QtGui.QColor(255,255,255)))
      self.IndicatorName.setOpacity(1.0)
      self.IndicatorName.setPos(0,0)

      indView = QtChart.QChartView(self)
      indView.setRenderHint(QtGui.QPainter.Antialiasing)

      indLayout = QtWidgets.QVBoxLayout()
      indLayout.setSpacing(0)
      indLayout.setContentsMargins(0,0,0,0)
      indLayout.addWidget(DoubleLineSeparator(orientation='horizontal', linecolor=COLOR_SEPARATOR,
                                              spacecolor='rgb(0,0,0)', stroke=1, width=3))
      indLayout.addWidget(indView)

      self.frame = QtWidgets.QFrame()
      self.frame.setLayout(indLayout)


   @abstractmethod
   def updateIndicator(self, data, N):
      pass

   def clear(self):
      for ser in self.series():
         ser.clear()


# ------------------------------------------------------------------------------------
# Volume
# ------------------------------------------------------------------------------------

class Volume(Indicator):
   def __init__(self):
      super(Volume, self).__init__()
      self.volumeBars = QtChart.QCandlestickSeries()
      self.volumeBars.setIncreasingColor(QtCore.Qt.black)
      self.volumeBars.setDecreasingColor(QtCore.Qt.red)
      self.volumeBars.setBodyWidth(0.7)
      self.addSeries(self.volumeBars)
      self.IndicatorName.setText('Volume')

   def updateIndicator(self, data, N):
      open   = data[1,-N:].tolist()
      close  = data[4,-N:].tolist()
      volume = data[5,-N:].tolist()

      # remove old set
      if self.volumeBars.count() > 0:
         self.volumeBars.remove(self.volumeBars.sets())

      # add new volume bar data
      for i, val in enumerate(volume):
         set = None
         if close[i] > open[i]:
            set = QtChart.QCandlestickSet(0, val, 0, val, timestamp=i)
            set.setPen(QtGui.QPen(QtCore.Qt.green, 1))
            set.setBrush(QtGui.QBrush(QtCore.Qt.black))
         else:
            set = QtChart.QCandlestickSet(val, val, 0, 0, timestamp=i)
            set.setPen(QtGui.QPen(QtCore.Qt.red, 1))
            set.setBrush(QtGui.QBrush(QtCore.Qt.red))
         self.volumeBars.append(set)

      # detach and remove old axes
      for ax in self.volumeBars.attachedAxes():
         self.volumeBars.detachAxis(ax)
      for ax in self.axes():
         self.removeAxis(ax)

      # set hidden x axis for volume bars
      ac = QtChart.QBarCategoryAxis()
      ac.append( [str(x) for x in range(len(volume))] )
      ac.hide()

      # set y volume axis
      ay = QtChart.QValueAxis()
      ay.setRange(0, max(volume))
      ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
      ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      ay.setLabelFormat("%-6.2f")
      ay.applyNiceNumbers()
      ay.setTickCount(2)

      # add and attach new axes
      self.addAxis(ac, QtCore.Qt.AlignBottom)
      self.addAxis(ay, QtCore.Qt.AlignRight)
      self.volumeBars.attachAxis(ac)
      self.volumeBars.attachAxis(ay)


# ------------------------------------------------------------------------------------
# MACD
# ------------------------------------------------------------------------------------

class MACD(Indicator):
   def __init__(self):
      super(MACD, self).__init__()
      self.macdBars = QtChart.QCandlestickSeries()
      self.macdBars.setIncreasingColor(QtCore.Qt.black)
      self.macdBars.setDecreasingColor(QtCore.Qt.red)
      self.macdBars.setBodyWidth(0.7)
      self.macdLine   = QtChart.QLineSeries()
      self.macdLine.setColor(QtCore.Qt.yellow)
      self.macdSignal = QtChart.QLineSeries()
      self.macdSignal.setColor(QtCore.Qt.blue)
      self.addSeries(self.macdBars)
      self.addSeries(self.macdLine)
      self.addSeries(self.macdSignal)
      self.IndicatorName.setText('MACD')


   def updateIndicator(self, data, N):
      close  = data[4]
      macdLine, macdSignal, macdBars = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
      macdLine = macdLine[-N:]
      macdSignal = macdSignal[-N:]
      macdBars = macdBars[-N:]

      # clear old data
      self.macdLine.clear()
      self.macdSignal.clear()
      if self.macdBars.count() > 0:
         self.macdBars.remove(self.macdBars.sets())

      # add new macd bar data
      for i, bar in enumerate(macdBars):
         set = None
         if bar > 0:
            set = QtChart.QCandlestickSet(0, bar, 0, bar, timestamp=i)
            set.setPen(QtGui.QPen(QtCore.Qt.green, 1))
            set.setBrush(QtGui.QBrush(QtCore.Qt.black))
         else:
            set = QtChart.QCandlestickSet(0, 0, bar, bar, timestamp=i)
            set.setPen(QtGui.QPen(QtCore.Qt.red, 1))
            set.setBrush(QtGui.QBrush(QtCore.Qt.red))
         self.macdBars.append(set)

      # add new macd line and signal data
      for i in range(N):
         self.macdLine.append(i + 0.5, macdLine[i])
         self.macdSignal.append(i + 0.5, macdSignal[i])

      # detach and remove old axes
      for ax in self.macdLine.attachedAxes():
         self.macdLine.detachAxis(ax)
      for ax in self.macdSignal.attachedAxes():
         self.macdSignal.detachAxis(ax)
      for ax in self.macdBars.attachedAxes():
         self.macdBars.detachAxis(ax)
      for ax in self.axes():
         self.removeAxis(ax)

      # set hidden x axis
      ax = QtChart.QValueAxis()
      ax.setRange(0,N)
      ax.hide()

      # set y price delta axis
      ay = QtChart.QValueAxis()
      bound = max(abs(min(macdLine)), abs(max(macdLine)))
      ay.setRange(-bound, bound)
      ay.setGridLinePen(QtGui.QPen(QtGui.QColor(80, 80, 80), 0.5))
      ay.setLinePen(QtGui.QPen(QtGui.QColor(0, 0, 0), 0.5))
      ay.setLabelFormat("%-6.2f")
      ay.applyNiceNumbers()
      ay.setTickCount(3)

      # set hidden x axis for macd bars
      ac = QtChart.QBarCategoryAxis()
      ac.append( [str(x) for x in range(N)] )
      ac.hide()

      # add and attach new axes
      self.addAxis(ax, QtCore.Qt.AlignBottom)
      self.addAxis(ac, QtCore.Qt.AlignBottom)
      self.addAxis(ay, QtCore.Qt.AlignRight)
      self.macdLine.attachAxis(ax)
      self.macdLine.attachAxis(ay)
      self.macdSignal.attachAxis(ax)
      self.macdSignal.attachAxis(ay)
      self.macdBars.attachAxis(ac)
      self.macdBars.attachAxis(ay)





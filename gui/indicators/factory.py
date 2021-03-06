from .base import Indicator
from .macd import MACD
from .volumeIndicator import Volume
from .trueRange import TrueRange
from .trueRangeAverage import TrueRange_AVG
from .obv import OBV_OnBalanceVolume
from .chaikinMoneyFlow import ChaikinMoneyFlow
from .chaikinOscillator import ChaikinOscillator
from .averageDirectionaIndex import ADX_AverageDirectionalIndex
from .absolutePriceOscillator import Absolute_Price_Oscillator
from .aroon import AROON_Oscillator
from .commodityChannelIndex import CommodityChannelIndex
from .chandeOscillator import Chande_Momentum_Oscillator
from .momentum import Momentum
from .moneyFlowIndex import Money_Flow_Index
from .percentagePriceOscillator import PPO_PercentagePriceOscillator
from .rsi import RSI_RelativeStrengthIndex
from .stochasticSlow import StochasticSlow
from .stochasticFast import StochasticFast
from .stochasticRSI import StochasticRSI
from .ultimateOscillator import UltimateOscillator
from .williams import Williams_pR
from .trix import TRIX_1dayRateOfChange


# ------------------------------------------------------------------------------------
# Indicator Factory
# ------------------------------------------------------------------------------------

class IndicatorFactory(object):
    indicators = {indicator.__name__: indicator for indicator in Indicator.__subclasses__()}

    @staticmethod
    def get_indicators():
        """A method that returns a sorted list of supported indicators.
        :return: list of strings (names)
        """
        return sorted(IndicatorFactory.indicators.keys())

    @staticmethod
    def create_indicator(name) -> Indicator:
        """Create an indicator object.
        :param name:      name of the indicator
        :return:          an indicator object.
        :raises KeyError
        """
        try:
            return IndicatorFactory.indicators[name]()
        except KeyError as e:
            raise KeyError('Indicator not supported') from e

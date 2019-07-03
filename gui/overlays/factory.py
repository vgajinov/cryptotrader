from .base import Overlay
from .ema import EMA
from .sma import SMA
from .wma import WMA
from .parabolicSAR import ParabolicSAR
from .hilbertTransform import HTTrendline
from .priceAverage import PriceAverage
from .priceMedian import PriceMedian
from .priceWeighted import PriceWeighted
from .forecast import TSForecast
from .regression import *
#from .variance import Variance
#from .bolingerBands import BolingerBands


# ------------------------------------------------------------------------------------
# Overlay Factory
# ------------------------------------------------------------------------------------

class OverlayFactory(object):
    overlays = {overlay.__name__: overlay for overlay in Overlay.__subclasses__()}

    @staticmethod
    def get_overlays():
        """A method that returns a sorted list of supported overlay indicators.
        :return: list of strings (names)
        """
        return sorted(OverlayFactory.overlays.keys())

    @staticmethod
    def create_overlay(name) -> Overlay:
        """Create an Overlay object.
        :param name:      name of the overlay
        :return:          an overlay object.
        :raises KeyError
        """
        try:
            return OverlayFactory.overlays[name]()
        except KeyError as e:
            raise KeyError('Overlay not supported') from e

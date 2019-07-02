from .base import Overlay
from .ema import EMA
from .sma import SMA
from .parabolicSAR import ParabolicSAR


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

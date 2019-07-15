from abc import ABC, abstractmethod
from PyQt5 import QtChart


# ------------------------------------------------------------------------------------
# Overlay base class
# ------------------------------------------------------------------------------------

class Overlay(ABC):
    """A base class for overlays.
    Overlays are indicators that are display directly on the main candle chart.
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def addToChart(self, chart: QtChart.QChart):
        """Adds an overlay to the main candle chart"""
        pass

    @abstractmethod
    def removeFromChart(self):
        """Removes an overlay from the chart"""
        pass

    @abstractmethod
    def update(self, data, N):
        """Updates the candle data for the overlay"""
        pass

    @abstractmethod
    def clear(self):
        """"Clears all data values for an overlay."""
        pass
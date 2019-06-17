from exchanges.WS.api import WSClientAPI
from exchanges.WS.binance import BinanceWSClient
from exchanges.WS.bitfinex import BitfinexWSClient


class ExchangeWSFactory(object):
    """Websocket exchange client factory class.

    Exposes the names of supported exchanges with the websocket interface to a user
    and creates the exchange handling object using the name of an exchange provided by a user
    """
    exchanges = {ex.name(): ex for ex in WSClientAPI.__subclasses__()}

    @staticmethod
    def get_exchanges():
        """A method that returns a sorted list of supported exchanges.

        :return: list of strings (names)
        """
        return sorted(ExchangeWSFactory.exchanges.keys())


    @staticmethod
    def create_client(name, key_file=None) -> WSClientAPI:
        """Create an exchange handling object.

        :param name:      name of the exchange
        :param key_file:  an file with private API keys
        :return:          an object for handling requested exchange.
        :raises KeyError

        WSClientAPI is an abstract class implemented by all websocket-based exchange client classes
        """
        try:
            return ExchangeWSFactory.exchanges[name](key_file=key_file)
        except KeyError as e:
            raise KeyError('Exchange name not recognized') from e

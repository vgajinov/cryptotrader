from exchanges.REST.api import RESTClientAPI
from exchanges.REST.binance import BinanceRESTClient
from exchanges.REST.bitfinex import BitfinexRESTClient


class ExchangeRESTFactory(object):
    """REST exchange client factory class.

    Exposes to a user the names of supported exchanges with the REST interface
    and creates the exchange handling object using the name of an exchange provided by a user
    """
    exchanges = {ex.name(): ex for ex in RESTClientAPI.__subclasses__()}

    @staticmethod
    def get_exchanges():
        """
        A method that returns a sorted list of supported exchanges

        :return: list of strings (names)
        """
        return sorted(ExchangeRESTFactory.exchanges.keys())


    @staticmethod
    def create_client(name, key_file=None) -> RESTClientAPI:
        """
        Create an exchange handling object

        :param name:      name of the exchange
        :param key_file:  an file with private API keys
        :return:          an object for handling requested exchange
        :raises KeyError

        RESTClientAPI is an abstract class implemented by all REST-based exchange client classes
        """
        try:
            return ExchangeRESTFactory.exchanges[name](key_file=key_file)
        except KeyError as e:
            raise KeyError('Exchange name not recognized') from e

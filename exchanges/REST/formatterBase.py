from abc import ABCMeta, abstractmethod


class Formatter:
    """
    Base Class for formatters. Does nothing with passed data by default;
    Children should implement formatters as necessary
    """
    def __init__(self):
        pass

    @staticmethod
    def format_pair(input_pair):
        """
        Returns the pair properly formatted for the exchange's API.
        :param input_pair: str
        :return: str
        """
        return input_pair

    @staticmethod
    def symbols(data, *args, **kwargs):
        """
        Returns the list of symbols
           ['btcusd', 'ltcusd', 'ltcbtc', 'ethusd', 'ethbtc',...]
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: list
        """
        return data

    @staticmethod
    def symbols_details(data, *args, **kwargs):
        """
        Returns a dictionary with details for each symbol in the following format
           { 'btcusd' : {
                         'precision': 8,
                         'minAmount': 0.01
                        }
            }
        There can be other details beside the above two (precision and minAmount)
        but they may be specific to an exchange.
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: dict(dict)
        """
        return data

    @staticmethod
    def ticker(data, *args, **kwargs):
        """
        Returns list of ticker data in following format:
            [bid_price, ask_price, high, low, last, 24h_vol, daily_change, daily_change_percent]
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: list
        """
        return data

    @staticmethod
    def tickers(data, *args, **kwargs):
        """
        Returns a dictionary with a list of ticker data for each symbol:
            { symbol : [bid_price, ask_price, high, low, last, 24h_vol, daily_change, daily_change_percent] }
        or a dictionary
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: list
        """
        return data

    @staticmethod
    def order_book(data, *args, **kwargs):
        """
        Returns dict of lists of lists of quotes in format [price, size]
        ex.:
            {'bids': [['0.014', '10'],
                      ['0.013', '0.66'],
                      ['0.012', '3']],
             'asks': [['0.015', '1'],
                      ['0.016', '0.67'],
                      ['0.017', '23']]}
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: dict
        """
        return data

    @staticmethod
    def trades(data, *args, **kwargs):
        """
        Returns list of trades in format [ts, price, size, side]
        ex.:
            [['1480941692', '0.014', '10', 'sell'],
            ['1480941690', '0.013', '0.66', 'buy'],
            ['1480941688', '0.012', '3', 'buy']]
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: list
        """
        return data

    @staticmethod
    def candles(data, *args, **kwargs):
        """
        Returns a list of candles in the order oldest..newest. The format is:
             [ [timestamp, open, high, low, close, volume] ]
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: list
        """
        return data

    @staticmethod
    def order(data, *args, **kwargs):
        """
        Returns a dictionary with the order details
           {
             'symbol':      'btcusd,
             'orderId':     1234,
             'price':       6100,
             'amount':      1,
             'filled':      0.23,
             'type':        'MARKET',
             'side':        'BUY' or 'SELL',
             'timestamp':   123456789,
             'status':      'LIVE', 'CANCELED' or 'EXECUTED'
           }

        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: str
        """
        return data

    @staticmethod
    def order_status(data, *args, **kwargs):
        """
        Returns a dictionary with the status details for an order
           {
             'symbol':      'btcusd,
             'orderId':     1234,
             'price':       6100,
             'stopPrice':   6000,
             'amount':      1,
             'filled':      0.23,
             'type':        'MARKET',
             'side':        'BUY' or 'SELL',
             'timestamp':   123456789,
             'status':      'LIVE', 'CANCELED' or 'EXECUTED'
           }
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: bool
        """
        return data

    @staticmethod
    def multi_order_status(data, *args, **kwargs):
        """
        Returns a list of dictionaries with order status details
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: bool
        """


    @staticmethod
    def cancel(data, *args, **kwargs):
        """
        returns True if it was cancelled successfully, else False
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: bool
        """
        return data

    @staticmethod
    def my_trades(data, *args, **kwargs):
        """
        returns a list of dictionaries that each represents a single trade
           [{
               'orderId':    1234,
               'price':      6000,
               'amount':     1,
               'fee':        0.002,
               'feeAsset':   'btc',
               'side':       'buy' or 'sell'
            }]
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: bool
        """
        return data


    @staticmethod
    def balance(data, *args, **kwargs):
        """
        Returns dict of available balances, with currency names as keys
        ex.:
            {'BTC': '12.04', 'LTC': '444.12'}
        :param data: requests.response() obj
        :param args:
        :param kwargs:
        :return: dict
        """
        return data


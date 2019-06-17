class Formatter:
    """Base class for data formatters.
    Does nothing with passed data by default;
    """
    def __init__(self):
        pass


    @staticmethod
    def forward(data):
        """Forwards passed data unchanged.
        :param data: Arbitrary data response from the exchange
        :return: data

        """
        return data


    @staticmethod
    def format_symbol(symbol):
        """Returns the pair properly formatted for the exchange's API.
        :param symbol:  String representing a symbol (pair).
        :return: Formatted symbol string
        """
        return symbol

    @staticmethod
    def symbols(data, *args, **kwargs):
        """Formats the data into a list of symbols.
        :param data:   Response from the exchange.
        :param args:
        :param kwargs:
        :return: list
        :raises: ExchangeException
        Example of the returned list of symbols:
            ['btcusd', 'ltcusd', 'ltcbtc', 'ethusd', 'ethbtc',...]
        """
        return data

    @staticmethod
    def symbols_details(data, *args, **kwargs):
        """Returns a dictionary with details for each symbol
        :param data:   Response from the exchange.
        :param args:
        :param kwargs:
        :return: dict(dict)
        :raises: ExchangeException
        The return format is the following:
           { 'btcusd' : {
                         'precision': 8,
                         'minAmount': 0.01
                        }
            }
        There can be other details beside the above two (precision and minAmount)
        but they may be specific to an exchange.
        """
        return data

    @staticmethod
    def ticker(data, *args, **kwargs):
        """Returns list of formatted ticker data:
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: list
        :raises: ExchangeException
        The return format is the following:
            [bid_price, ask_price, high, low, last, 24h_vol, daily_change, daily_change_percent]
        """
        return data

    @staticmethod
    def tickers(data, *args, **kwargs):
        """Returns a dictionary with a list of ticker data for each symbol.
        or a dictionary
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: list
        :raises: ExchangeException
        Return format:
            { symbol : [bid_price, ask_price, high, low, last, 24h_vol, daily_change, daily_change_percent] }
        """
        return data

    @staticmethod
    def order_book(data, *args, **kwargs):
        """Returns a dictionary of lists of lists of quotes in format [price, size].
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: dict
        :raises: ExchangeException
        Return format:
            {
                'bids': [[price, size], ... ]
                'asks': [[price, size], ... ]
             }
        """
        return data

    @staticmethod
    def trades(data, *args, **kwargs):
        """Returns a list of trades in format [ts, price, size, side].
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: list
        :raises: ExchangeException
        Return format:
            [ [ts, price, size, side], ... ]
        """
        return data

    @staticmethod
    def candles(data, *args, **kwargs):
        """Returns a list of candles in the order oldest..newest.
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: list
        :raises: ExchangeException
        Return format:
            [ [timestamp, open, high, low, close, volume], ... ]
        """
        return data

    @staticmethod
    def order(data, *args, **kwargs):
        """Returns a dictionary with the order details.
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: str
        :raises: ExchangeException
        Return format:
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
        """
        return data

    @staticmethod
    def order_status(data, *args, **kwargs):
        """Returns a dictionary with status details for an order.
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: bool
        :raises: ExchangeException
        Return format:
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
        """
        return data

    @staticmethod
    def multi_order_status(data, *args, **kwargs):
        """Returns a list of dictionaries with order status details
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: bool
        :raises: ExchangeException
        Return format:
            [
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
                },
                ...
            ]
        """


    @staticmethod
    def cancel(data, *args, **kwargs):
        """Returns True if an order was cancelled successfully, else False.
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: bool
        """
        return data

    @staticmethod
    def my_trades(data, *args, **kwargs):
        """Returns a list of dictionaries that each represents a single trade
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: bool
        :raises: ExchangeException
        Return format:
           [
                {
                   'orderId':    1234,
                   'price':      6000,
                   'amount':     1,
                   'fee':        0.002,
                   'feeAsset':   'btc',
                   'side':       'buy' or 'sell'
                },
                ...
            ]
        """
        return data


    @staticmethod
    def balance(data, *args, **kwargs):
        """Returns a dictionary of available balances, with currency names as keys.
        :param data:    Response from the exchange.
        :param args:
        :param kwargs:
        :return: dict
        :raises: ExchangeException
        Return format:
            {
                'BTC': '6.78',
                'LTC': '213.45',
                'USD': '4700'
            }
        """
        return data


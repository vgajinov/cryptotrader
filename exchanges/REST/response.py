import logging
import json
import requests
from functools import wraps
from ..exception import ExchangeException


class APIResponse(requests.Response):
    """Extends a Response object with data formatters."""

    __attrs__ = [
        '_content',
        '_formatted',
        'cookies',
        'elapsed',
        'encoding',
        'headers',
        'history',
        'status_code',
        'reason',
        'request',
        'url',
    ]

    def __init__(self, req_response, formatted_json=None):
        super(APIResponse, self).__init__()
        self.__dict__.update(req_response.__dict__)
        self._formatted = formatted_json

    @property
    def formatted(self):
        return self._formatted

    @formatted.setter
    def formatted(self, val):
        self._formatted = val


# Utility functions
# ----------------------------------------------------------------------------

def get_response(exchange_name, log, func, *args, **kwargs):
    try:
        response = func(*args, **kwargs)
    except Exception as e:
        msg = "response_formatter: Error during call to {0}({1}, {2})".format(func.__name__, args, kwargs)
        raise ExchangeException(exchange_name, msg, orig_exception=e, logger=log)
    return response


def check_status(exchange_name, log, response, func, *args, **kwargs):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        msg = "response_formatter: HTTPError for url: {}".format(response.url)
        raise ExchangeException(exchange_name, msg, orig_exception=e, logger=log)
    except AttributeError as e:
        msg = "response_formatter: Bad response from the exchange.\n" + \
              "Method {0} returned response: {1}".format(func.__name__, response)
        raise ExchangeException(exchange_name, msg, orig_exception=e, logger=log)
    except Exception as e:
        msg = "response_formatter: Unexpected exchange response".format(func.__name__, args, kwargs)
        raise ExchangeException(exchange_name, msg, orig_exception=e, logger=log)


def get_json_content(exchange_name, log, response):
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        msg = "response_formatter: Error while parsing json. " + \
              "Request url was: {0}, result is: {1}".format(response.url, response.text)
        raise ExchangeException(exchange_name, msg, orig_exception=e, logger=log)
    except Exception as e:
        msg = "response_formatter: Unexpected error while parsing " + \
              "json from {}".format(response.url)
        raise ExchangeException(exchange_name, msg, orig_exception=e, logger=log)
    return data


def format_data(exchange_name, log, data, formatter, func, *args, **kwargs):
    if formatter and data:
        try:
            formatted = formatter(data, *args, **kwargs)
        except Exception as e:
            msg = "response_formatter: Error while applying data formatter {}!\n".format(func.__name__)
            raise ExchangeException(exchange_name, msg, orig_exception=e, logger=log)
    else:
        formatted = data
    return formatted


# response_formatter Decorator
# ----------------------------------------------------------------------------

def response_formatter(formatter=None, log=logging.getLogger(__name__)):
    """Decorator that applies a formatter to a data response from the exchange.
    :param formatter:  A Formatter object specific to each exchange.
    :param log:        A logging handler.
    :return: APIResponse object.
    This decorator takes the raw response data from an exchange and formats it
    into a corresponding unified format for a given request. It stores the result
    into APIResponse 'formatted' attribute.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This hack checks if the function is the method of a class that has method 'name',
            # in which case 'self' should be the first argument. # If true, we use it to provide
            #  the user with the name of the exchange within exception. If it fails no big deal!
            exchange_name = 'Unknown'
            try:
                exchange_name = args[0].name()
                # method_cls = func.__qualname__.split('.')[-2]
                # getattr(sys.modules[__name__], cls).name()
                # globals()[cls].name()
            except:
                pass

            response = get_response(exchange_name, log, func, *args, **kwargs)
            check_status(exchange_name, log, response, func, *args, **kwargs)
            data = get_json_content(exchange_name, log, response)
            response.formatted = format_data(exchange_name, log, data, formatter, func, *args, **kwargs)

            return response.formatted

        return wrapper
    return decorator





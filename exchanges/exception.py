import sys
import traceback


class ExchangeException(Exception):
    def __init__(self, name, msg, data=None, orig_exception=None, logger=None):
        exception_msg = "Exception in handling the response from {0} exchange:\n{1}".format(name, msg)
        if orig_exception:
            exception_msg += "\nOriginal exception:\n{0} with arguments {1}".format(orig_exception.__class__, orig_exception.args)
            self.with_traceback(orig_exception.__traceback__)  # or sys.exc_info()[2]
        if logger:
            self._log_exception(logger, exception_msg, data)
        super().__init__(exception_msg)
        self.msg = exception_msg

    @staticmethod
    def _log_exception(log, msg, data):
        try:
            if data:
                msg += "\nData received:\n{}".format(data)
            # log our exception message
            msg += '\n\n'
            log.exception(msg)
            # also log a stack trace of the exception
            logfile = log.handlers[0].stream
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=logfile)
            #traceback.print_stack(file=logfile)
        except:
            # ignore any exception while logging the current one.
            pass

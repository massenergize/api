"""
This utility lets us flush our logs to both sentry and cloudwatch.
"""
import logging
import sentry_sdk
from _main_.settings import EnvConfig
from _main_.utils.utils import run_in_background

class MassenergizeLogger:
    def __init__(self):
        self.logger = logging.getLogger(EnvConfig.get_logger_identifier())


    @run_in_background
    def _log(self, level, message, exception=None, extra={}):

        if not EnvConfig.can_send_logs_to_cloudwatch():
            return
        
        if not message:
            return 


        if exception:
            extra['exception'] = exception

        # log through the python django logger which goes to Cloudwatch
        if level >= logging.ERROR:
            # send to cw
            self.logger.log(
                level,
                message, 
                exc_info=True,
                stack_info=True, 
                stacklevel=2,
                extra=extra
            )

            # send to sentry
            if extra:
                with sentry_sdk.push_scope() as sentry_scope:
                    for k,v in extra.items():
                        sentry_scope.set_extra(k, v)
            sentry_sdk.capture_message(message, level)
        else:
            # send to cw
            self.logger.log(level, message, extra=extra)

            # send log to sentry
            if extra:
                with sentry_sdk.push_scope() as sentry_scope:
                    for k,v in extra.items():
                        sentry_scope.set_extra(k, v)
            sentry_sdk.capture_message(message, level)
            

    def info(self, message, extra={}):
        self._log(logging.INFO, message, extra=extra)

    def error(self, message=None, exception=None, extra={}):
        self._log(logging.ERROR, message or str(exception), exception, extra)

    def exception(self, exception):
        self.error(str(exception), exception)
        return exception


log = MassenergizeLogger()

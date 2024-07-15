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


    def _log(self, level, message, exception=None, extra={}):

        if exception:
            extra['exception'] = exception

        def _send_to_cw_and_log_files():
            # log through the python django logger which logs to Cloudwatch (for dev, canary, prod)
            # and to log files (for other modes like test, local)
            if level >= logging.ERROR:
                self.logger.log(
                    level,
                    message, 
                    exc_info=True,
                    stack_info=True, 
                    extra=extra
                )
            else:
                self.logger.log(level, message, extra=extra)

        def _send_to_sentry():
            if extra:
                with sentry_sdk.push_scope() as sentry_scope:
                    for k,v in extra.items():
                        sentry_scope.set_extra(k, v)
            sentry_sdk.capture_message(message, level)

        # write to log files and send to cw
        _send_to_cw_and_log_files()

        # don't send to sentry
        if EnvConfig.can_send_logs_to_external_watchers():
            _send_to_sentry()

    def info(self, message, extra={}):
        self._log(logging.INFO, message, extra=extra)

    def error(self, message=None, exception=None, extra={}):
        self._log(logging.ERROR, message or str(exception), exception, extra)

    def exception(self, exception, message=None, extra={}):
        self.error(message, exception, extra)
        return exception


log = MassenergizeLogger()

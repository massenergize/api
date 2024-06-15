import time
import boto3
import logging
from django.utils.deprecation import MiddlewareMixin
from botocore.exceptions import NoCredentialsError, ClientError
from _main_.settings import EnvConfig


from _main_.utils.utils import run_in_background
logger = logging.getLogger(EnvConfig.get_logger_identifier())

class MetricsMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.cloudwatch = boto3.client('cloudwatch')

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        self.log_the_time_taken_to_complete_request(request)
        return response

    @run_in_background
    def log_the_time_taken_to_complete_request(self, request):
        if not hasattr(request, 'start_time'):
            return
        latency = (time.time() - request.start_time) * 1000 # convert to milliseconds
        logger.info(f"Path: {request.path} Latency(ms): {latency}")
        logger.info()


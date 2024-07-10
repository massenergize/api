import time
import boto3
from _main_.utils.massenergize_logger import log
from django.utils.deprecation import MiddlewareMixin
from _main_.utils.utils import run_in_background

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
        
        log.info(
            f"Path: {request.path} Latency(ms): {latency}", 
            extra={"path": request.path, "latency": latency}
        )


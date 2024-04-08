import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("Latency: ")

class LatencyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        try:
            request_latency = time.time() - request.start_time
            logger.warning(f"[{request.path}] ==> {request_latency} seconds.")
            # print(f"Request to {request.path} took {request_latency} seconds.")
        except AttributeError:
            print("AttributeError")
        return response
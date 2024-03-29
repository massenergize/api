import time
import boto3
import logging
from django.utils.deprecation import MiddlewareMixin
from botocore.exceptions import NoCredentialsError, ClientError
from _main_.settings import STAGE


from _main_.utils.utils import run_in_background
logger = logging.getLogger(STAGE.get_logger_identifier())

class MetricsMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.cloudwatch = boto3.client('cloudwatch')

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        self.send_cw_metrics(request)
        return response

    @run_in_background
    def send_cw_metrics(self, request):
        if hasattr(request, 'start_time'):
            latency = (time.time() - request.start_time) * 1000 # convert to milliseconds

        try:
            self.cloudwatch.put_metric_data(
                        Namespace='ApiService',
                        MetricData=[
                        {
                            'MetricName': 'Latency',
                            'Dimensions': [
                                {
                                    'Name': 'Endpoint',
                                    'Value': request.path
                                },
                                {
                                    'Name': 'Stage',
                                    'Value': STAGE.name
                                }
                            ],
                            'Unit': 'Milliseconds',
                            'Value': latency                            
                        },
                        {
                            'MetricName': 'Count',
                            'Dimensions': [
                                {
                                    'Name': 'Endpoint',
                                    'Value': request.path
                                },
                                {
                                    'Name': 'Stage',
                                    'Value': STAGE.name
                                }
                            ],
                            'Unit': 'Count',
                            'Value': 1
                        },
                    ]
                    )
        except Exception:
            logging.error("AWS credentials not configured properly.")
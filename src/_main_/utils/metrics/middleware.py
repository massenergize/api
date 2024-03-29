import time
from django.utils.deprecation import MiddlewareMixin
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from _main_.settings import STAGE

import logging
logger = logging.getLogger(STAGE.get_logger_identifier())

class MetricsMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.cloudwatch = boto3.client('cloudwatch')

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            latency = (time.time() - request.start_time) * 1000 # convert to milliseconds
            logging.info(f"[Latency: {latency}]", extra={'latency2': latency})
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
        return response
 
import time
import functools
import boto3
import threading
import random 
from _main_.settings import EnvConfig
from _main_.utils.massenergize_logger import log

DEFAULT_CAPTURE_RATE = .7 # for now we want to capture 50% of the logs.
FUNCTION_LATENCY_NAMESPACE = "ApiService/FunctionPerformance"

def timed(func):
    """
    When you add this annotation on top of a function, it will compute the latency of that
    function and send it to cloudwatch for logging and tracking.

    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            # Decide whether to run based on the specified chance
            if random.random() < DEFAULT_CAPTURE_RATE:
                # If the random number exceeds the chance/capture_rate, just just stop
                # calculate the execution time in milliseconds
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # we don't want to wait for the metrics to be sent before returning
                # so we do it in a different thread.
                threading.Thread(target=send_metric, args=(func, execution_time,)).start()

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap

def send_metric(func, execution_time, name_space=FUNCTION_LATENCY_NAMESPACE, extra_dimensions=[]):
    function_name = get_function_name(func)
    metric_name = function_name
    dimensions = []

    if extra_dimensions:
        dimensions.extend(extra_dimensions)

    metric_data=[
        {
            'MetricName': metric_name,
            'Dimensions': dimensions,
            'Unit': 'Milliseconds',
            'Value': execution_time
        },
    ]

    env_name_space = f"{EnvConfig.name.title()}/{name_space}"
    put_metric_data(env_name_space, metric_data)


def put_metric_data(name_space, metric_data):
    if not EnvConfig.can_send_logs_to_cloudwatch():
        return 

    try:
        client = boto3.client('cloudwatch')
        client.put_metric_data(
            Namespace=name_space,
            MetricData=metric_data
        )
        print(f"Metric {metric_data[0]['MetricName']} sent to CloudWatch: {metric_data[0]['Value']} ms\n")
    except Exception as e:
        log.exception(e)

def timed_with_dimensions(dimensions=None, capture_rate=DEFAULT_CAPTURE_RATE):
    
    if dimensions is None:
        dimensions = []
    
    def decorator_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                # Decide whether to run based on the specified chance
                if random.random() < capture_rate:
                    # If the random number exceeds the chance/capture_rate, just just stop
                    execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                    # Start a new thread to send the metric without waiting for it to complete
                    threading.Thread(target=send_metric, args=(func, execution_time,)).start()

        return wrapper
    
    return decorator_function

def get_function_name(func):
    return f"{func.__module__}.{func.__name__}"

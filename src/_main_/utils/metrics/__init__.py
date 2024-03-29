import time
import functools
import boto3
import threading
import random 

def capture_execution_time_to_cloudwatch(metric_name=None, dimensions=None, capture_rate=0.5):
    
    if dimensions is None:
        dimensions = []
    
    def decorator_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Decide whether to run based on the specified chance
            if random.random() > capture_rate:
                # If the random number exceeds the chance/capture_rate, just just stop
                return func(*args, **kwargs)

            # if we are here then we want to capture the metrics and send to cloudwatch
            start_time = time.time()
            # This is the function that will run in a background thread
            def send_metric(execution_time):
                client = boto3.client('cloudwatch')
                client.put_metric_data(
                    Namespace="ApiService/FunctionPerformance",
                    MetricData=[
                        {
                            'MetricName': metric_name or func.__name__,
                            'Dimensions': dimensions or [{'Name': 'FunctionName', 'Value': func.__name__}],
                            'Unit': 'Milliseconds',
                            'Value': execution_time
                        },
                    ]
                )
                print(f"Metric {metric_name} sent to CloudWatch: {execution_time} ms")

            try:
                return func(*args, **kwargs)
            finally:
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                # Start a new thread to send the metric without waiting for it to complete
                threading.Thread(target=send_metric, args=(execution_time,)).start()

        return wrapper
    
    return decorator_function
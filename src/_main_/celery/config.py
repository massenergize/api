import os
from _main_.settings import RUN_CELERY_LOCALLY


class CeleryConfig:

    def get_config(self):

        if RUN_CELERY_LOCALLY:
            return {
                "broker_url": os.environ.get("CELERY_LOCAL_REDIS_BROKER_URL", "redis://localhost:6379/0"),
                "task_serializer": "json",
                "result_serializer": "json",
                "accept_content": ["json"],
                'celery_beat_scheduler': 'django_celery_beat.schedulers:DatabaseScheduler',

            }
        else:
            sqs_url = os.environ.get("SQS_AWS_ENDPOINT", None)
            assert sqs_url is not None, "Please set SQS_AWS_ENDPOINT in the environment."
            broker_url = f'sqs://{sqs_url.replace("https://", "")}'

            return {
                "broker_url": broker_url ,
                "result_backend": None,
                "task_serializer": "json",
                "result_serializer": "json",
                "accept_content": ["json"],
                "broker_transport_options": {
                    "region": "us-east-2",
                    "predefined_queues": {"celery": {"url": sqs_url}},
                },
            }

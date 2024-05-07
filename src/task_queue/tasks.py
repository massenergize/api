import datetime
from celery import shared_task
from django.db import transaction
from .models import Task
from task_queue.helpers import is_time_to_run
from .jobs import FUNCTIONS
from api.services.utils import send_slack_message
from _main_.settings import SLACK_CELERY_TASKS_WEBHOOK_URL, IS_PROD, IS_LOCAL, IS_CANARY

ENV = "LOCAL" if IS_LOCAL else "CANARY" if IS_CANARY else "PRODUCTION" if IS_PROD else "DEVELOPMENT"


def send_slack_notification(status, task_name, message):
    today = datetime.date.today()
    try:
        send_slack_message(SLACK_CELERY_TASKS_WEBHOOK_URL, {
            "task": task_name,
            "status": "✅" if status == "SUCCEEDED" else "❌",
            "date": str(today),
            "message": message,
            "environment": ENV
        })
    except Exception as e:
        print(f"Failed to send slack notification: {e}")


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 5})
def run_some_task(self, task_id):
    try:
        today = datetime.date.today()
        should_run = False
        task = None
        with transaction.atomic():
            task = Task.objects.select_for_update().get(id=task_id)  # locks task instance until transaction is committed
            if is_time_to_run(task):
                task.last_run = today
                task.save()
                should_run = True

        if task and should_run:
            func = FUNCTIONS.get(task.job_name)
            if func:
                task.status = "SCHEDULED"
                task.save()
                try:
                    res = func(task)
                    task.status = "SUCCEEDED" if res else "FAILED"
                    send_slack_notification(task.status, task.job_name, "Task ran successfully" if res else "Task failed")
                except Exception as e:
                    task.status = "FAILED"
                    send_slack_notification(task.status, task.job_name, today, str(e))
            else:
                task.status = "FAILED"
                send_slack_notification(task.status, task.job_name,  "No function found for job_name")
            task.save()
    except Exception as e:
        send_slack_notification("FAILED", "unknown", str(e))

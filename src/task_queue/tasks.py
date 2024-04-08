import datetime
from celery import shared_task
from django.db import transaction
from .models import Task
from task_queue.helpers import is_time_to_run
from .jobs import FUNCTIONS
from api.services.utils import send_slack_message
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL, IS_PROD, IS_LOCAL, IS_CANARY

ENV = "API Local" if IS_LOCAL else "API CANARY" if IS_CANARY else "API PROD" if IS_PROD else "API DEV"


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 5})
def run_some_task(self, task_id):
    try:
        today = datetime.date.today()
        should_run = False
        task = None
        with transaction.atomic():
            task = Task.objects.select_for_update().get(
                id=task_id)  # locks task instance until transaction is committed
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
                    if IS_PROD:
                        send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {
                            "text": f"({ENV}): Task '{task.job_name}' was run on {today}. Status: {task.status} "})
                except Exception as e:
                    task.status = "FAILED"
                    if IS_PROD:
                        send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {
                            "text": f"({ENV}): Task '{task.job_name}' was run on {today}. Status: {task.status}. Reason: {str(e)} "})
            else:
                task.status = "FAILED"
                if IS_PROD:
                    send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {
                        "text": f"({ENV}): Task '{task.job_name}' was run on {today}. Status: {task.status}. Reason: No function found for job_name '{task.job_name}'"})
            task.save()
    except Exception as e:
        if IS_PROD:
            send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {
                "text": f"({ENV}): Task '{task.job_name}' was run on {today}. Status: FAILED. Reason: {str(e)} "})

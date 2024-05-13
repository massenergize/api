import datetime
import logging

from celery import shared_task
from django.db import transaction

from _main_.settings import IS_PROD
from task_queue.helpers import is_time_to_run
from .jobs import FUNCTIONS
from .models import Task

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SUCCESS_LOG_KEY = "CELERY_TASK_SUCCESS"
FAILURE_LOG_KEY = "CELERY_TASK_FAILURE"


def log_status(status, task_name, message):
	# if not IS_PROD:
	# 	return
	if status == "SUCCEEDED":
		logger.info(f"Task: {task_name}, Status: ✅, Info: {message}, key:{SUCCESS_LOG_KEY}")
	else:
		logger.error(f"Task: {task_name}, Status: ❌, Info: {message}, key:{FAILURE_LOG_KEY}")


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
					log_status(task.status, task.job_name, "Task ran successfully" if res else "Task failed")
				except Exception as e:
					task.status = "FAILED"
					log_status(task.status, task.job_name, today, str(e))
			else:
				task.status = "FAILED"
				log_status(task.status, task.job_name, "No function found for job_name")
			task.save()
	except Exception as e:
		log_status("FAILED", "unknown", str(e))

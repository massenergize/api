import datetime
import logging

from celery import shared_task
from django.db import transaction

from _main_.settings import IS_PROD, SLACK_SUPER_ADMINS_WEBHOOK_URL
from api.services.utils import send_slack_message
from task_queue.helpers import is_time_to_run
from .jobs import FUNCTIONS
from .models import Task
from _main_.utils.massenergize_logger import log


FAILED = "FAILED"
SUCCEEDED = "SUCCEEDED"
SKIPPED = "SKIPPED"

def get_task_info(task):
	if task:
		return f"task: {task.name}, job: {task.job_name}, task_id: {task.id}"
	
def log_status(task, message):
	task_name = get_task_info(task)

	if task.status == FAILED:
		log.error(f"Task: {task_name}, Status: {task.status}, Info: {message}")
		if IS_PROD:
			send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {"text": f"Task: {task_name}, Status: {task.status}, Info: {message}"})
	else:
		log.info(f"Task: {task_name}, Status: {task.status}, Info: {message}")


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 5})
def run_some_task(self, task_id):
	task = None
	task_run = None
	try:
		today = datetime.date.today()
		should_run = False
		
		with transaction.atomic():
			task = Task.objects.select_for_update().get(id=task_id)
			# Create a TaskRun instance at the start
			task_run = task.runs.create()
			
			if is_time_to_run(task):
				task.last_run = today
				task.save()
				should_run = True
			else:
				task.status = SKIPPED
				log_status(task, "Another instance of the task is already running")
			
		if task and should_run:
			func = FUNCTIONS.get(task.job_name)
			if func:
				try:
					res = func(task)
					if res:
						task.status = SUCCEEDED
						task_run.mark_complete(result=res if isinstance(res, (dict, list)) else None)
					else:
						task.status = FAILED
						task_run.mark_failed("Task returned False")
					log_status(task, "Task ran successfully" if res else "Task failed")
				
				except Exception as e:
					error_msg = str(e)
					task.status = FAILED
					task_run.mark_failed(error_msg)
					log_status(task, error_msg)
			else:
				error_msg = "Task not found in FUNCTIONS"
				task.status = FAILED
				task_run.mark_failed(error_msg)
				log_status(task, error_msg)
			task.save()
			
	except Exception as e:
		error_msg = str(e)
		log.error(f"Task: {task_id}, Status: ❌, Info: {error_msg}")
		if task_run:
			task_run.mark_failed(error_msg)

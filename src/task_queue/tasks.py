import datetime
import traceback
from celery import shared_task
from django.db import transaction

from _main_.settings import IS_PROD, SLACK_SUPER_ADMINS_WEBHOOK_URL
from api.services.utils import send_slack_message
from task_queue.helpers import is_time_to_run
from .jobs import FUNCTIONS, AUTOMATIC_TASK_FUNCTIONS
from .models import Task, TaskRun
from _main_.utils.massenergize_logger import log
from django.utils import timezone


FAILED = "FAILED"
SUCCEEDED = "SUCCEEDED"
SKIPPED = "SKIPPED"

def get_task_info(task):
	if not task:
		return "Unknown Task"
	return f"task: {task.name}, job: {task.job_name}, task_id: {task.id}"

def log_status(task, message, extra_context=None):
	task_name = get_task_info(task)
	log_message = f"Task: {task_name}, Status: {task.status}, Info: {message}"
	if extra_context:
		log_message += f", Context: {extra_context}"

	if task.status == FAILED:
		log.error(log_message)
		if IS_PROD:
			send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {"text": log_message})
	else:
		log.info(log_message)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 5})
def run_some_task(self, task_id):
	task = None
	task_run = None
	try:
		today = datetime.date.today()
		
		with transaction.atomic():
			try:
				task = Task.objects.select_for_update().get(id=task_id)
			except Task.DoesNotExist:
				log.error(f"Task with id {task_id} not found")
				return False

			if not is_time_to_run(task):
				task.status = SKIPPED
				task.save()
				log_status(task, "Task skipped - Another instance is running or not scheduled")
				return False

			task.last_run = today
			task.save()

		task_run = TaskRun.objects.create(
			task=task,
			started_at=timezone.now()
		)
		log_status(task, "Task execution started", {"run_id": task_run.id})

		all_functions = FUNCTIONS | AUTOMATIC_TASK_FUNCTIONS
		func = all_functions.get(task.job_name)
		if not func:
			error_msg = f"Task function '{task.job_name}' not found in FUNCTIONS"
			task.status = FAILED
			task_run.mark_failed(error_msg)
			log_status(task, error_msg)
			task.save()
			return False

		try:
			res, err = func(task)

			task.status = SUCCEEDED if not err else FAILED
			
			if res:
				task_run.mark_complete(result=res)
				log_status(task, "Task completed successfully", {"result": str(res)})
			else:
				task_run.mark_failed(err)
				log_status(task, "Task failed", {"error": str(err)})
			
			task.save()
			return True

		except Exception as e:
			task.status = FAILED
			stack_trace = traceback.format_exc()
			task_run.mark_failed(stack_trace)
			log_status(task, "Task failed with exception", {"error": stack_trace, "type": type(e).__name__})
			task.save()
			raise

	except Exception as e:
		stack_trace = traceback.format_exc()
		log.error(f"Critical error in task execution. Task ID: {task_id}, Error: {stack_trace}")
		if task_run:
			task_run.mark_failed(stack_trace)
		return False
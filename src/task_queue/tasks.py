import datetime
from celery import shared_task
from .jobs import FUNCTIONS
from .models import Task
from django.db import transaction



WEEKLY= "weekly"
BI_WEEKLY = "bi-weekly"
MONTHLY = "monthly"

today = datetime.date.today()
@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2, 'countdown': 5})
def run_some_task(self, task_id):
    with transaction.atomic():
        task = Task.objects.select_for_update().get(id=task_id) # locks task instance until transaction is committed
        if(task.last_run == None or task.last_run != today):
                task.last_run = today
                task.save()
                func = FUNCTIONS.get(task.job_name)
                if func:
                    task.status= "SCHEDULED"
                    task.save()
                    res = func()
                    task.status = "SUCCEEDED" if res else "FAILED"
                else:
                    task.status = "FAILED"
                task.save()
 

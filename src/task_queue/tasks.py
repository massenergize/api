import datetime
from celery import shared_task

from task_queue.helpers import is_time_to_run
from .jobs import FUNCTIONS
from .models import Task
from django.db import transaction

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 5})
def run_some_task(self, task_id):
    today = datetime.date.today()
    should_run = False
    task = None
    with transaction.atomic():
        task = Task.objects.select_for_update().get(id=task_id) # locks task instance until transaction is committed
        if(is_time_to_run(task)): 
                task.last_run = today
                task.save()
                should_run = True
                
    if task and should_run:
        func = FUNCTIONS.get(task.job_name)
        if func:
            task.status= "SCHEDULED"
            task.save()
            # res = func()
            # task.status = "SUCCEEDED" if res else "FAILED"
            task.status = "SUCCEEDED"
        else:
            task.status = "FAILED"
        task.save()
 



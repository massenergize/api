from celery import shared_task
from task_queue.async_functions import FUNCTIONS
from task_queue.type_constants import TaskStatus

from .models import Task


@shared_task(bind=True)
def run_some_task(self,task_id):
    task = Task.objects.get(id=task_id)
    func = FUNCTIONS.get(task.job_name)
    if func:
        task.status = TaskStatus.RUNNING
        func()
        task.status = TaskStatus.SUCCEEDED
    else:
        task.status = TaskStatus.FAILED

    task.save()

        

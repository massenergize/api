from celery import shared_task
from task_queue.async_functions import FUNCTIONS
from task_queue.type_constants import TaskStatus

from .models import Task


@shared_task(bind=True)
def run_some_task(self,task_id):
    task = Task.objects.get(id=task_id)
    if task.job_name:
        FUNCTIONS[task.job_name]()
        task.status = TaskStatus.active
    print('''Running task with title {title} .'''.format(title=task.name))

        

from celery import shared_task
from .jobs import FUNCTIONS
from .models import Task
from .type_constants import TaskStatus


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def run_some_task(self, task_id):
    task = Task.objects.get(id=task_id)
    func = FUNCTIONS.get(task.job_name)
    if func:
        task.status = TaskStatus.RUNNING
        func()
        task.status = TaskStatus.SUCCEEDED
    else:
        task.status = TaskStatus.FAILED

    task.save()



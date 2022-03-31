from celery import shared_task
from .jobs import FUNCTIONS
from .models import Task


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2, 'countdown': 5})
def run_some_task(self, task_id):
    task = Task.objects.get(id=task_id)
    func = FUNCTIONS.get(task.job_name)
    if func:
        task.status = "SCHEDULED"
        task.save()
        res = func()
        task.status = "SUCCEEDED" if res else "FAILED"
    else:
        task.status = "FAILED"

    task.save()



# celery tasks specific to api app
from celery import shared_task

@shared_task(bind=True)
# create any function I want to be allocated to celery
# can import this function by using a statement like : from .tasks import [function_name
def test_func(self):
    for i in range(10):
        print(i)
    return "Done"
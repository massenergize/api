from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery import shared_task

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_main_.settings")

app = Celery('_main_')

app.config_from_object("django.conf:settings", namespace='CELERY')


# celery beats conf
app.conf.beat_schedule = {

}

app.autodiscover_tasks()


@shared_task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

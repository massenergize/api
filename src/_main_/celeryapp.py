from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery import shared_task
from . import celeryconfig

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_main_.settings")
app = Celery('massenergize_celeryapp')
celery_config = celeryconfig.CeleryConfig().get_config()

app.config_from_object(celery_config)
app.autodiscover_tasks()

@shared_task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

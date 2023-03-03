from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery import shared_task
from _main_.celery.config import CeleryConfig
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_main_.settings")
app = Celery('massenergize_celeryapp')

app.conf.enable_utc = False
app.conf.update( timezone= 'US/Eastern')
celery_config = CeleryConfig().get_config()

app.config_from_object(celery_config)

app.autodiscover_tasks()
app.conf.beat_schedule = {}

@shared_task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

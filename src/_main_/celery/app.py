from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery import shared_task
from _main_.celery.config import CeleryConfig
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_main_.settings")
app = Celery('massenergize_celeryapp')
celery_config = CeleryConfig().get_config()

app.config_from_object(celery_config)
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'generate_and_send_weekly_report_to_sadmins': {
        'task': 'api.tasks.generate_and_send_weekly_report_to_sadmins',
        'schedule': crontab(day_of_week=1, hour=0, minute=0),
    }
}

@shared_task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

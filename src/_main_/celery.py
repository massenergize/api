from __future__ import absolute_import, unicode_literals
import os
from time import timezone

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_main_.settings")

app = Celery('_main_')

# app.conf.enable_utc = False
# app.conf.update(timezone=os.environ.get("CELERY_TIMEZONE"))
app.config_from_object(settings, namespace='CELERY')


# celery beats conf
app.conf.beat_schedule = {

}

app.autodiscover_tasks()
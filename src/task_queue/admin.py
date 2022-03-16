from django.contrib import admin
from task_queue.models import Task

admin.site.register(Task)

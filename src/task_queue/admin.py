from django.contrib import admin
from task_queue.models import Task, TaskRun

# Register your models here.

admin.site.register(Task)
admin.site.register(TaskRun)
from django.apps import AppConfig


class TaskQueueConfig(AppConfig):
    name = 'task_queue'


    def ready(self):
       from .  import signals
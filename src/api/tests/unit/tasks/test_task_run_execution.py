from django.test import TestCase
from task_queue.models import Task, TaskRun
from task_queue.tasks import run_some_task
from task_queue.type_constants import TaskStatus
from celery import shared_task

class TaskExecutionTest(TestCase):

    def setUp(self):
        # Create a Task instance for testing
        self.task = Task.objects.create(
            name="Test Task",
            status=TaskStatus.CREATED.value,
            job_name="Test",
            frequency="ONE_OFF"
        )

    def test_run_some_task(self):
        # Simulate running the task
        run_some_task.apply(args=[self.task.id])

        # Fetch the latest TaskRun
        task_run = self.task.runs.latest('started_at')        
        self.assertEqual(task_run.status, TaskStatus.SUCCEEDED.value)
        self.assertIsNotNone(task_run.completed_at)
        self.assertEqual(task_run.result, True) 
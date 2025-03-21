from django.test import TestCase
from django.utils import timezone
from task_queue.models import Task, TaskRun
from task_queue.type_constants import TaskStatus

class TaskRunModelTest(TestCase):

    def setUp(self):
        # Create a Task instance for testing
        self.task = Task.objects.create(
            name="Test Task",
            status=TaskStatus.CREATED.value,
            job_name="test_job",
            frequency="ONE_OFF"
        )

    def test_create_task_run(self):
        task_run = TaskRun.objects.create(task=self.task)
        self.assertIsInstance(task_run, TaskRun)
        self.assertEqual(task_run.task, self.task)
        self.assertIsNotNone(task_run.started_at)
        self.assertEqual(task_run.status, TaskStatus.RUNNING.value)

    def test_mark_complete(self):
        task_run = TaskRun.objects.create(task=self.task)
        task_run.mark_complete(result={"output": "success"})
        
        self.assertIsNotNone(task_run.completed_at)
        self.assertEqual(task_run.status, TaskStatus.SUCCEEDED.value)
        self.assertEqual(task_run.result, {"output": "success"})

    def test_mark_failed(self):
        task_run = TaskRun.objects.create(task=self.task)
        task_run.mark_failed("An error occurred")
        
        self.assertIsNotNone(task_run.completed_at)
        self.assertEqual(task_run.status, TaskStatus.FAILED.value)
        self.assertEqual(task_run.error_message, "An error occurred")

    def test_str_representation(self):
        task_run = TaskRun.objects.create(task=self.task)
        self.assertEqual(str(task_run), f'Test Task - {task_run.started_at}') 
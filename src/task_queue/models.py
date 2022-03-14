import json
from time import timezone
from django.db import models
from django.forms import model_to_dict
from database.utils.constants import SHORT_STR_LEN
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from task_queue.type_constants import ScheculeInterval, TaskStatus, schedules

# Create your models here.


class Task(models.Model):
    """
    
    """
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=SHORT_STR_LEN, blank=False)

    status = models.CharField(
        max_length=SHORT_STR_LEN,
        choices=TaskStatus.choices(),
        blank=True,
        null=True,
        default=TaskStatus.active,
    )

    job_name = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    recurring_interval = models.CharField(
        max_length=SHORT_STR_LEN,
        choices=ScheculeInterval.choices(),
        blank=True,
        null=True
    )

    schedule = models.OneToOneField(
        PeriodicTask,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='task_queue_schedule',
    )

    info = models.JSONField(blank=True, null=True)

    def simple_json(self):
       return model_to_dict(self, exclude=['schedule'])



    def delete(self, *args, **kwargs):
        if self.schedule is not None:
            self.schedule.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def create_task(self):
        self.schedule = PeriodicTask.objects.create(
            name=self.name,
            task='task_queue.tasks.run_some_task',
            crontab=self.interval_schedule,
            args=json.dumps([self.id]),
        )
        self.save()
        self.start()

    def __str__(self) -> str:
        return f'{self.name} || {self.status} || {self.recurring_interval}'

    @property
    def interval_schedule(self):
        """returns the interval schedule"""

        print("===== self.recurring_interval: ", self.name)
        if self.recurring_interval == schedules["EVERY_MINUTE"]:
            minutes, created = CrontabSchedule.objects.get_or_create(
                minute='*')
            return minutes
        if self.recurring_interval == schedules["EVERY_HOUR"]:
            hour, created = CrontabSchedule.objects.get_or_create(hour='*')
            return hour
        if self.recurring_interval == schedules["EVERY_DAY"]:
            day, created = CrontabSchedule.objects.get_or_create(
                day_of_week='*')
            return day

        if self.recurring_interval == schedules["EVERY_MONTH"]:
            month, created = CrontabSchedule.objects.get_or_create(
                month_of_year='*')
            return month
        if self.recurring_interval == schedules["EVERY_YEAR"]:
            year, created = CrontabSchedule.objects.get_or_create(
                month_of_year='1')
            return year
        if self.recurring_interval == schedules["EVERY_QUARTER"]:
            quarter, created = CrontabSchedule.objects.get_or_create(
                month_of_year='1,4,7,10', day_of_month='*', hour='*', minute='*')
            return quarter

        raise NotImplementedError(
            '''Interval Schedule for {interval} is not added.'''.format(
                interval=self.recurring_interval))

    def stop(self):
        """pauses the task"""
        schedule = self.schedule
        schedule.enabled = False
        schedule.save()

    def start(self):
        """starts the task"""
        schedule = self.schedule
        schedule.enabled = True
        schedule.save()

    def terminate(self):
        """terminates the task"""
        self.stop()
        schedule = self.schedule
        self.delete()
        schedule.delete()

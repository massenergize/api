import json
from django.db import models
from django.forms import model_to_dict
from database.models import UserProfile
from database.utils.common import get_summary_info
from database.utils.constants import SHORT_STR_LEN
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from task_queue.type_constants import ScheduleInterval, TaskStatus, schedules


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
        default=TaskStatus.CREATED,
    )

    job_name = models.CharField(max_length=SHORT_STR_LEN, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    frequency = models.CharField(
        max_length=SHORT_STR_LEN,
        choices=ScheduleInterval.choices(),
        blank=True,
        null=True
    )

    schedule = models.OneToOneField(
        PeriodicTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_queue_schedule',
    )

    recurring_details = models.JSONField(blank=True, null=True)

    creator = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='task_queue_creator',
        to=UserProfile
    )
    last_run = models.DateField(blank=True, null=True)

    def simple_json(self):
        res = model_to_dict(self, exclude=['schedule'])
        res["creator"] = get_summary_info(self.creator)["full_name"]
        res["is_active"] = self.schedule.enabled if self.schedule else False
        res["last_run_at"] = self.schedule.last_run_at if self.schedule else None
        return res


        # helper functions

    def delete(self, *args, **kwargs):
        if self.schedule is not None:
            self.schedule.delete()
        return super(self.__class__, self).delete(*args, **kwargs)


    def delete_periodic_task(self):
        if self.schedule is not None:
            self.schedule.delete()


    def create_task(self):
        self.schedule = PeriodicTask.objects.create(
            name=self.name,
            task='task_queue.tasks.run_some_task',
            crontab=self.interval_schedule,
            args=json.dumps([self.id]),
            one_off=True if self.frequency == schedules["ONE_OFF"] else False,
        )
        
        self.save()
        self.start()

    def __str__(self) -> str:
        return f'{self.name} || {self.status} || {self.frequency}'


    @property
    def interval_schedule(self):
        """returns the interval schedule"""
        details = json.loads(self.recurring_details)

        if self.frequency == schedules["EVERY_MINUTE"]:
            minutes, created = CrontabSchedule.objects.get_or_create(minute=details["minute"] if details["minute"] else "*")
            return minutes
        if self.frequency == schedules["EVERY_HOUR"]:
            hour, created = CrontabSchedule.objects.get_or_create(
                hour=details["hour"] if details["hour"] else "*", minute=details['minute'] if details['minute'] else "0")
            return hour
        if self.frequency == schedules["EVERY_DAY"]:
            day, created = CrontabSchedule.objects.get_or_create(
                hour=details["hour"] if details["hour"] else "0",
                minute=details["minute"] if details["minute"] else "0",
            )
            return day

        if self.frequency == schedules["EVERY_WEEK"]:
            week, created = CrontabSchedule.objects.get_or_create(
                day_of_week=details["day_of_week"] if details["day_of_week"] else "1",
                hour=details["hour"] if details["hour"] else "0",
                minute=details["minute"] if details["minute"] else "0",
            )
            return week

        if self.frequency == schedules["EVERY_MONTH"]:
            month, created = CrontabSchedule.objects.get_or_create(
                day_of_month=details["day_of_month"] if details["day_of_month"] else "1",
                hour=details["hour"] if details["hour"] else "0",
                minute=details["minute"] if details["minute"] else "0",
            )
            return month
        if self.frequency == schedules["EVERY_YEAR"]:
            year, created = CrontabSchedule.objects.get_or_create(
                month_of_year=details["month_of_year"] if details["month_of_year"] else "1",
                day_of_month=details["day_of_month"] if details["day_of_month"] else "1",
                hour=details["hour"] if details["hour"] else "0",
                minute=details["minute"] if details["minute"] else "0",
            )
            return year
        if self.frequency == schedules["EVERY_QUARTER"]:
            quarter, created = CrontabSchedule.objects.get_or_create(
                month_of_year=details["month_of_year"] if details["month_of_year"] else "*/3",
                day_of_month=details["day_of_month"] if details["day_of_month"] else "1",
                hour=details["hour"] if details["hour"] else "0",
                minute=details["minute"] if details["minute"] else "0",

            )
            return quarter

        if self.frequency == schedules["ONE_OFF"]:
            one_off, created = CrontabSchedule.objects.get_or_create(
                month_of_year=details["month_of_year"] if details["month_of_year"] else "*",
                day_of_month=details["day_of_month"] if details["day_of_month"] else "*",
                hour=details["hour"] if details["hour"] else "0",
                minute=details["minute"] if details["minute"] else "0",
            )
            return one_off

        raise NotImplementedError(
            '''Interval Schedule for {interval} is not added.'''.format(
                interval=self.frequency))

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

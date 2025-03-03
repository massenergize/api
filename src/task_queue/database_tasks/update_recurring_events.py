from datetime import datetime, timedelta
import json
from _main_.utils.common import custom_timezone_info, parse_datetime_to_aware
from _main_.utils.massenergize_logger import log
from database.models import Event, RecurringEventException
from task_queue.models import Task
from django.utils import timezone
import calendar
from task_queue.type_constants import ScheduleInterval, TaskStatus


# ------------------- START OF UTILS ------------------- #
def get_final_date(event, today):
    start_time = event.start_date_and_time.strftime("%H:%M:%S+00:00")
    final_date_str = event.recurring_details.get('final_date')
    
    if final_date_str and final_date_str != 'None':
        final_date = datetime.strptime(f"{final_date_str} {start_time}", "%Y-%m-%d %H:%M:%S+00:00")
        return final_date.replace(tzinfo=custom_timezone_info())
    
    return None


def update_event_dates(event, today):
    sep_count = int(event.recurring_details['separation_count'])
    start_date = event.start_date_and_time
    end_date = event.end_date_and_time
    duration = end_date - start_date
    
    if event.recurring_details['recurring_type'] == "week":
        update_weekly_event(event, start_date, duration, sep_count, today)
    elif event.recurring_details['recurring_type'] == "month":
        update_monthly_event(event, start_date, duration, sep_count, today)


def update_weekly_event(event, start_date, duration, sep_count, today):
    while start_date <= today:
        start_date += timedelta(7 * sep_count)
    event.start_date_and_time = start_date
    event.end_date_and_time = start_date + duration
    event.save()


def update_monthly_event(event, start_date, duration, sep_count, today):
    converter = {"first": 1, "second": 2, "third": 3, "fourth": 4}
    while start_date <= today:
        new_month = start_date + timedelta((sep_count * 31) + 1)
        date_of_first_weekday = get_date_of_first_weekday(new_month, event.recurring_details['day_of_week'])
        upcoming_date = date_of_first_weekday + ((converter[event.recurring_details['week_of_month']] - 1) * 7)
        start_date = datetime(new_month.year, new_month.month, upcoming_date, start_date.hour, start_date.minute,
                              tzinfo=custom_timezone_info())
    
    event.start_date_and_time = start_date
    event.end_date_and_time = start_date + duration
    event.save()


def get_date_of_first_weekday(new_month, day_of_week):
    obj = calendar.Calendar()
    for day in obj.itermonthdates(new_month.year, new_month.month):
        if day.day >= 8:
            continue
        d1 = datetime(day.year, day.month, day.day, tzinfo=custom_timezone_info())
        if calendar.day_name[d1.weekday()] == day_of_week:
            return day.day
    return 1


def handle_recurring_event_exception(event):
    exception = RecurringEventException.objects.filter(event=event).first()
    if exception:
        exception_former_time = exception.former_time.replace(tzinfo=custom_timezone_info())
        event_start_date_and_time = event.start_date_and_time.replace(tzinfo=custom_timezone_info())
        if exception_former_time < event_start_date_and_time:
            exception.delete()


def get_eta_from_datetime(_datetime):
    if not _datetime:
        return None
    
    if timezone.is_aware(_datetime):
        return _datetime
    parsed_datetime = datetime.strptime(_datetime, '%a, %d %b %Y %H:%M:%S %Z')
    formatted_date_string = timezone.make_aware(parsed_datetime)
    return formatted_date_string


# ------------------- END OF UTILS ------------------- #

def update_recurring_event(event_id):
    today = parse_datetime_to_aware()

    if not event_id:
        return False

    event = Event.objects.filter(id=event_id).first()
    if not event or not event.is_recurring or not event.recurring_details:
        return False

    key = f"update_recurring_events_task_for_{event.id}_{event.name}"
    task = Task.objects.filter(name=key).first()
    
    try:
        if not event.recurring_details.get('separation_count'):
            return False

        final_date = get_final_date(event, today)
        if final_date and today > final_date:
            return False

        if not task and event.start_date_and_time > today:
            create_task_for_event(event, key)
        else:
            if event.start_date_and_time > today:
                return False

            update_event_dates(event, today)
            handle_recurring_event_exception(event)
            update_or_create_task(task, event, key)

        return True
    except Exception as e:
        log.exception(e)
        return False


def create_task_for_event(event, key):
    recurring_details = get_recurring_details_from_date(event.end_date_and_time)
    recurring_details_str = json.dumps(recurring_details) if recurring_details else None
    task = Task(
        name=key,
        job_name="Update Recurring Events",
        status=TaskStatus.PENDING.value,
        recurring_details=recurring_details_str,
        frequency=ScheduleInterval.ONE_OFF.value,
        is_automatic_task=True
    )
    task.create_task()
    task.save()


def update_or_create_task(task, event, key):
    recurring_details = get_recurring_details_from_date(event.end_date_and_time)
    recurring_details_str = json.dumps(recurring_details) if recurring_details else None

    if not task:
        task: Task = Task(
            name=key,
            job_name="Update Recurring Events",
            status=TaskStatus.PENDING.value,
            recurring_details=recurring_details_str,
            frequency=ScheduleInterval.ONE_OFF.value,
            is_automatic_task=True,
            args=json.dumps([event.id]),
        )
        task.create_task()
    else:
        task.recurring_details = recurring_details
        task.start()
    task.save()


def get_recurring_details_from_date(date_time):
    if not date_time:
        return None

    if isinstance(date_time, str):
        try:
            date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

    return {
        'month_of_year': date_time.month,
        'day_of_month': date_time.day,
        'hour': date_time.hour,
        'minute': date_time.minute,
        'year': date_time.year,
        'actual': date_time.isoformat()
    }
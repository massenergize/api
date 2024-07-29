import calendar
from datetime import datetime, timedelta

from _main_.utils.common import custom_timezone_info, parse_datetime_to_aware
from _main_.utils.massenergize_logger import log
from database.models import Event, RecurringEventException


def get_all_recurring_events():
    return Event.objects.filter(is_recurring=True, is_deleted=False, recurring_details__isnull=False)


def update_recurring_events(task=None):
    """
    Update Recurring Events

    This method updates recurring events based on certain criteria.

    :param task: The specific task to be updated.
    :return: True if the update is successful.

    """
    events = get_all_recurring_events()
    today = parse_datetime_to_aware()
    
    for event in events:
        try:
            if not event.recurring_details.get('separation_count'):
                continue

            if event.start_date_and_time > today:
                continue
            
            final_date = get_final_date(event, today)
            if final_date and today > final_date:
                continue

            update_event_dates(event, today)
            handle_recurring_event_exception(event)
        except Exception as e:
            log.exception(f"Error updating event {event.id}: {str(e)}")
    return True


def get_final_date(event, today):
    """
    :param event: Event object containing information about the event.
    :param today: Date when the method is invoked.
    :return: The final date of the event, adjusted for the custom time zone, if applicable. If no final date is provided or if it is set to 'None', it returns None.

    This method takes an event object and the current date as parameters. It retrieves the start time of the event and the final date from the recurring details of the event. If a valid final date is provided, it constructs a datetime object combining the final date and the start time. It then adjusts the datetime object to the custom time zone using the custom_timezone_info() function. Finally, it returns the adjusted final date. If no final date is provided or if it is set to 'None', it returns None.
    """
    start_time = event.start_date_and_time.strftime("%H:%M:%S+00:00")
    final_date_str = event.recurring_details.get('final_date')
    
    if final_date_str and final_date_str != 'None':
        final_date = datetime.strptime(f"{final_date_str} {start_time}", "%Y-%m-%d %H:%M:%S+00:00")
        return final_date.replace(tzinfo=custom_timezone_info())
    
    return None


def update_event_dates(event, today):
    """
    :param event: The event object to update the dates for.
    :param today: The current date to use for updating the event dates.
    :return: None

    This method updates the start and end dates of the given event object based on its recurring details. It takes into account the current date to determine the appropriate updates.

    If the recurring type of the event is "week", the method calls the update_weekly_event function to handle the update process. Otherwise, if the recurring type is "month", the method calls the update_monthly_event function.

    Note: This method does not return any value.
    """
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
        start_date = datetime(new_month.year, new_month.month, upcoming_date, start_date.hour, start_date.minute, tzinfo=custom_timezone_info())
    
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
            
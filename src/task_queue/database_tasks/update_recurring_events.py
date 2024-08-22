from datetime import datetime

from _main_.utils.common import parse_datetime_to_aware
from _main_.utils.massenergize_logger import log
from api.utils.api_utils import get_eta_from_datetime, get_final_date, handle_recurring_event_exception, \
	update_event_dates
from database.models import Event
from task_queue.models import Task


def get_recurring_details_from_date(date_time):
	if not date_time: return None
	
	if isinstance(date_time, str):
		try:
			date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
		except ValueError:
			return None
	
	month_of_year = date_time.month
	day_of_month = date_time.day
	hour = date_time.hour
	minute = date_time.minute
	return {
		'month_of_year': month_of_year,
		'day_of_month': day_of_month,
		'hour': hour,
		'minute': minute
	}


def update_recurring_event(event_id):
	today = parse_datetime_to_aware()
	
	if not event_id:
		return False
	
	event = Event.objects.filter(id=event_id).first()
	if not event:
		return False
	
	if not event.is_recurring or not event.recurring_details:
		return False
	
	key = "update_recurring_events_task_for_{event_id}_{event_name}".format(event_id=str(event.id), event_name=event.name)
	task = Task.objects.filter(name=key).first()
	try:
		
		if not event.recurring_details.get('separation_count'):
			return False
		
		if event.start_date_and_time > today:
			return False
		
		final_date = get_final_date(event, today)
		if final_date and today > final_date:
			return False
		
		update_event_dates(event, today)
		handle_recurring_event_exception(event)
		
		recurring_details = get_recurring_details_from_date(event.end_date_and_time)
		
		if not task:
			task = Task(
				name=key,
				job_name="Update Recurring Events",
				status="PENDING",
				recurring_details=recurring_details if recurring_details else None,
				frequency="ONE_OFF",
			)
			task.create_task()
			task.save()
			
		else:
			task.recurring_details = recurring_details
			task.activate()
			task.save()
		
		return True
	except Exception as e:
		log.exception(e)
		return False
	

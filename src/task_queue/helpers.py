import datetime
import re

from dateutil.relativedelta import relativedelta

WEEKLY = "EVERY_WEEK"
BI_WEEKLY = "bi-weekly"
MONTHLY = "EVERY_MONTH"
YEARLY = "EVERY_YEAR"
DAILY = "EVERY_DAY"
ONE_OFF = 'ONE_OFF'


# it is time to run if the previous time is at least the time period before the current date
def is_time_to_run(task):
  
	today = datetime.date.today()
	last_run = task.last_run
	freq = task.frequency
	
	if last_run is None:
		return True
	
	if freq == ONE_OFF and not last_run == today:
		return True
	
	if freq == DAILY:
		a_day_ago = today - relativedelta(days=1)
		if last_run <= a_day_ago:
			return True
	
	if freq == WEEKLY:
		one_week_ago = today - relativedelta(weeks=1)
		if last_run <= one_week_ago:
			return True
	
	elif freq == BI_WEEKLY:
		two_weeks_ago = today - relativedelta(weeks=2)
		if last_run <= two_weeks_ago:
			return True
	
	elif freq == MONTHLY:
		one_month_ago = today - relativedelta(months=1)
		if last_run <= one_month_ago:
			return True
	
	elif freq == YEARLY:
		a_year_ago = today - relativedelta(year=1)
		if last_run <= a_year_ago:
			return True
	
	else:
		
		return False


def get_event_location(event):
	evnt_type = event.get("event_type", "").lower()
	location_mapping = {
		"both": "Hybrid",
		"in-person": "In-Person",
		"online": "Online",
	}
	location = location_mapping.get(evnt_type, None)
	if location:
		return location
	
	if event.get("location"): return "In-Person"
	if event.get("online_location"): return "Online"
	return "N/A"


def get_summary(text, word_limit):
	clean_text = re.sub('<[^<]+?>', '', text)
	words = clean_text.split()
	
	if len(words) <= word_limit:
		return clean_text
	summary = ' '.join(words[:word_limit]) + '...'
	return summary
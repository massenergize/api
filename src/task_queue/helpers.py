import datetime
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

    if last_run == None or freq == ONE_OFF:
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
from celery import shared_task

from task_queue.events_nudge.query_builder import get_domain, get_email_list, get_live_events_within_the_week
from .jobs import FUNCTIONS
from .models import Task

from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.utils.constants import WEEKLY_EVENTS_NUDGE_TEMPLATE_ID

WEEKLY= "weekly"
BI_WEEKLY = "bi-weekly"
MONTHLY = "monthly"

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2, 'countdown': 5})
def run_some_task(self, task_id):
    task = Task.objects.get(id=task_id)
    func = FUNCTIONS.get(task.job_name)
    if func:
        task.status = "SCHEDULED"
        task.save()
        res = func()
        task.status = "SUCCEEDED" if res else "FAILED"
    else:
        task.status = "FAILED"

    task.save()


@shared_task(bind=True)
def send_weekly_events_report(self):
    email_list =  get_email_list(WEEKLY) 
    data = get_live_events_within_the_week()
    change_preference_link = get_domain()+"/admin/profile/settings"
    if data.get("events"):
        for name, email in email_list.items():
            data["name"]= name
            data["change_preference_link"] = change_preference_link
            send_massenergize_email_with_attachments(WEEKLY_EVENTS_NUDGE_TEMPLATE_ID, data, [email], None, None)

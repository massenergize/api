import csv
import os
from django.http import HttpResponse
import requests
from _main_.settings import POSTMARK_ACCOUNT_TOKEN, POSTMARK_EMAIL_SERVER_TOKEN
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.utils import is_test_mode
from django.utils import timezone

from api.utils.api_utils import generate_email_tag
from api.utils.constants import DATA_DOWNLOAD_TEMPLATE
from database.models import Community
from task_queue.type_constants import CADMIN_EVENTS_NUDGE, CADMIN_TESTIMONIALS_NUDGE, USER_EVENTS_NUDGE


def get_stats_from_postmark(tag, start, end):


    url = f"https://api.postmarkapp.com/stats/outbound?fromdate={start}&todate={end}"
    if is_test_mode():
        return 
    headers = {"Accept": "application/json","X-Postmark-Server-Token": POSTMARK_EMAIL_SERVER_TOKEN}
    response = requests.get(url, headers=headers)
    return response



def main(period=250):
    '''
        2. number of requests to change communication preference per nudge per community
        date: 2024-01-31 yyyy-mm-dd
    '''
    if not isinstance(period, int):
        period = 30

    today = timezone.now().date()
    start_date = today - timezone.timedelta(days=period)

    communities = Community.objects.filter(is_published=True, is_deleted=False, subdomain="wayland")

    for com in communities:
        cadmin_event_nudge_tag = generate_email_tag(com.subdomain, CADMIN_EVENTS_NUDGE)
        cadmin_testimonials_nudge_tag = generate_email_tag(com.subdomain, CADMIN_TESTIMONIALS_NUDGE)
        user_event_nudge_tag = generate_email_tag(com.subdomain, USER_EVENTS_NUDGE)
        
        cadmin_event_nudge_res = get_stats_from_postmark(cadmin_event_nudge_tag, start_date, today)
        cadmin_testimonials_nudge_res = get_stats_from_postmark(cadmin_testimonials_nudge_tag, start_date, today)
        user_event_nudge_res = get_stats_from_postmark(user_event_nudge_tag, start_date, today)

        rows = [
            ["Nudge", "Total Sent", "Number of emails opened by unique users","Number of delivery failures (bounces)",  "Number of spam complaints", "Number of clicks on content in emails", "Number of actual unsubscribes", "change communication preferences"],
            ["Community Admin Events Nudge", 
             cadmin_event_nudge_res.json()["Sent"],
             cadmin_event_nudge_res.json()["UniqueOpens"], 
             cadmin_event_nudge_res.json()["Bounced"],
             cadmin_event_nudge_res.json()["SpamComplaints"],
             cadmin_event_nudge_res.json()["TotalClicks"],
             0,  
             0], 
            ["Community Admin Testimonials Nudge",
             cadmin_testimonials_nudge_res.json()["Sent"],
             cadmin_testimonials_nudge_res.json()["UniqueOpens"],
             cadmin_testimonials_nudge_res.json()["Bounced"], 
             cadmin_testimonials_nudge_res.json()["SpamComplaints"],
             cadmin_testimonials_nudge_res.json()["TotalClicks"],
             0,  
             0], 
            ["User Events Nudge",
             user_event_nudge_res.json()["Sent"],
             user_event_nudge_res.json()["UniqueOpens"],
             user_event_nudge_res.json()["Bounced"],
             user_event_nudge_res.json()["SpamComplaints"], 
             user_event_nudge_res.json()["TotalClicks"],
             0,  
             0]  
        ]
 
        response = HttpResponse(content_type="text/csv")
        writer = csv.writer(response)
        for row in rows:
            writer.writerow(row)

        # Format filename
        filename = f"{com.name} Nudge Report {start_date.strftime('%B %d, %Y')} to {today.strftime('%B %d, %Y')}.csv"

        # Send email with CSV attachment
        temp_data = {
            'data_type': 'Nudge Report',
            'name': 'Admin'
        }

        send_massenergize_email_with_attachments(
            DATA_DOWNLOAD_TEMPLATE,
            temp_data,
            ["abdullai.tahiru@gmail.com"],
            response.content,
            filename,
            None
        )





'''
from task_queue.nudges.postmark_nudge_report import main
'''
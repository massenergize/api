import csv
from django.http import HttpResponse
import requests
from _main_.settings import POSTMARK_EMAIL_SERVER_TOKEN
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.utils import is_test_mode
from django.utils import timezone

from api.utils.api_utils import generate_email_tag
from api.utils.constants import DATA_DOWNLOAD_TEMPLATE
from database.models import Community, CommunityAdminGroup, UserProfile
from task_queue.type_constants import CADMIN_EVENTS_NUDGE, CADMIN_TESTIMONIALS_NUDGE, USER_EVENTS_NUDGE
from _main_.utils.massenergize_logger import log



def get_stats_from_postmark(tag, start, end):
    try:
        url = f"https://api.postmarkapp.com/stats/outbound?fromdate={start}&todate={end}"
        if is_test_mode():
            return 
        headers = {"Accept": "application/json","X-Postmark-Server-Token": POSTMARK_EMAIL_SERVER_TOKEN}
        response = requests.get(url, headers=headers)
        return response
    except Exception as e:
        print(f"Error in get_stats_from_postmark: {str(e)}")
        log.error(f"Error in get_stats_from_postmark: {str(e)}")
        return None 


def get_community_admins(community):
    try:
        all_community_admins = CommunityAdminGroup.objects.filter(community=community).values_list("members__email", "members__full_name")

        name_and_emails = {}

        for (email, name) in list(all_community_admins):
            if email:
                name_and_emails[email] = name
        return name_and_emails
    except Exception as e:
        print(f"Error in get_community_admins: {str(e)}")
        log.error(f"Error in get_community_admins: {str(e)}")
        return {}



def generate_csv_file(rows):
    try:
        response = HttpResponse(content_type="text/csv")
        writer = csv.writer(response)
        for row in rows:
            writer.writerow(row)
     
        return response.content
    except Exception as e:
        print(f"Error in generate_csv_file: {str(e)}")
        log.error(f"Error in generate_csv_file: {str(e)}")
        return None



def generate_community_report_data(community, period=30):
    try:
        if not isinstance(period, int):
            period = 30

        today = timezone.now().date()
        start_date = today - timezone.timedelta(days=period)

        cadmin_event_nudge_tag = generate_email_tag(community.subdomain, CADMIN_EVENTS_NUDGE)
        cadmin_testimonials_nudge_tag = generate_email_tag(community.subdomain, CADMIN_TESTIMONIALS_NUDGE)
        user_event_nudge_tag = generate_email_tag(community.subdomain, USER_EVENTS_NUDGE)
        
        cadmin_event_nudge_res = get_stats_from_postmark(cadmin_event_nudge_tag, start_date, today)
        cadmin_testimonials_nudge_res = get_stats_from_postmark(cadmin_testimonials_nudge_tag, start_date, today)
        user_event_nudge_res = get_stats_from_postmark(user_event_nudge_tag, start_date, today)

        cadmin_event_nudge_data = cadmin_event_nudge_res.json() if cadmin_event_nudge_res else {}
        cadmin_testimonials_nudge_data = cadmin_testimonials_nudge_res.json() if cadmin_testimonials_nudge_res else {}
        user_event_nudge_data = user_event_nudge_res.json() if user_event_nudge_res else {}

        rows = [
                ["Nudge", "Total Sent", "Number of emails opened by unique users","Number of delivery failures (bounces)",  "Number of spam complaints", "Number of clicks on content in emails", "Number of actual unsubscribes", "change communication preferences"],
                ["Community Admin Events Nudge", 
                 cadmin_event_nudge_data.get("Sent", 0),
                 cadmin_event_nudge_data.get("UniqueOpens", 0), 
                 cadmin_event_nudge_data.get("Bounced", 0),
                 cadmin_event_nudge_data.get("SpamComplaints", 0),
                 cadmin_event_nudge_data.get("TotalClicks", 0),
                 0,  
                 0], 
                ["Community Admin Testimonials Nudge",
                 cadmin_testimonials_nudge_data.get("Sent", 0),
                 cadmin_testimonials_nudge_data.get("UniqueOpens", 0),
                 cadmin_testimonials_nudge_data.get("Bounced", 0), 
                 cadmin_testimonials_nudge_data.get("SpamComplaints", 0),
                 cadmin_testimonials_nudge_data.get("TotalClicks", 0),
                 0,  
                 0], 
                ["User Events Nudge",
                 user_event_nudge_data.get("Sent", 0),
                 user_event_nudge_data.get("UniqueOpens", 0),
                 user_event_nudge_data.get("Bounced", 0),
                 user_event_nudge_data.get("SpamComplaints", 0), 
                 user_event_nudge_data.get("TotalClicks", 0),
                 0,  
                 0]  
            ]
        
        filename = f"{community.name} Nudge Report {start_date.strftime('%B %d, %Y')} to {today.strftime('%B %d, %Y')}.csv"
        
        return rows, filename
    except Exception as e:
        print(f"Error in generate_community_report_data: {str(e)}")
        log.error(f"Error in generate_community_report_data: {str(e)}")
        return [], ""


def send_community_report(report, community, filename, user=None):
    try:
        if not report and not filename: return 
        
        def send_email(name, email):
            temp_data = {'data_type': f'{community.name} Nudge Report', 'name': name}
            send_massenergize_email_with_attachments(
                DATA_DOWNLOAD_TEMPLATE,
                temp_data,
                ["abdullai.tahiru@gmail.com"],
                # [email],
                report,
                filename,
                None
            )

        if user:
            send_email(user.preferred_name or user.full_name, user.email)
        else:
            admins = get_community_admins(community)
            for email, name in admins.items():
                send_email(name, email)
    except Exception as e:
        print(f"Error in send_community_report: {str(e)}")
        log.error(f"Error in send_community_report: {str(e)}")



def send_user_requested_postmark_nudge_report(community_id, email, period=45):
    try:
        print("== com = ", community_id)
        print("== email ===", email)

        if email and community_id:
            user =  UserProfile.objects.filter(email=email).first()
            community = Community.objects.filter(id=community_id, is_published=True).first()

            if user and community:
                rows, file_name= generate_community_report_data(community, period=period)
                report_file  =  generate_csv_file(rows=rows)
                send_community_report(report_file, community, file_name, user)
    except Exception as e:
        print(f"Error in send_user_requested_nudge: {str(e)}")
        log.error(f"Error in send_user_requested_nudge: {str(e)}")


def generate_postmark_nudge_report(task=None):
    try:
        communities = Community.objects.filter(is_published=True, is_deleted=False, subdomain="wayland")
        for com in communities:
            rows , file_name= generate_community_report_data(com)
            report_file  =  generate_csv_file(rows=rows)
            send_community_report(report_file, com, file_name)

        return True
    except Exception as e:
        log.error(f"Error in Nudge report main func: {str(e)}")
        print(f"Error in Nudge report main func: {str(e)}")
        return False 
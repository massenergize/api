from _main_.utils.common import serialize_all
from database.models import *
from django.utils import timezone
import datetime
from django.utils.timezone import utc
from _main_.settings import DJANGO_ENV


today = datetime.datetime.utcnow().replace(tzinfo=utc)
in_30_days = today + timezone.timedelta(days=30)


def is_viable(item):
    if item[0] is not None and item[1]is not None:
        if  not item[0]=={}:
            return True
    return False



def get_comm_emails_and_pref():
    communities = Community.objects.all()
    admins = []
    for com in communities:
        all_community_admins = CommunityAdminGroup.objects.filter(community=com).values_list('members__preferences', "members__email")
        for i in list(all_community_admins):
            if is_viable(i):
                admins.append({
                    "pref":i[0],
                    "email":i[1]
                })
    return admins



def remove_admin_duplicates():
    cadmins = get_comm_emails_and_pref()
    no_duplicates = list({dictionary['email']: dictionary for dictionary in cadmins }.values())
    return no_duplicates

def human_readable_date(start, end):
    if all(getattr(start,x) == getattr(end,x) for x in ["year", "month", "day"]):
        return start.strftime("%b %d, %H:%M") +" - "+ end.strftime( "%H:%M")
    else:
        return start.strftime("%b %d, %H:%M") +" - "+ end.strftime( "%b %d, %H:%M")



def generate_redirect_url(id):
    domain = ''

    if DJANGO_ENV == "local":
        domain = 'http://localhost:3001/'
    elif DJANGO_ENV == "canary":
        domain ="https://admin-canary.massenergize.org/"
    else:
        domain = "https://admin.massenergize.org/"

    return domain + f"admin/read/event/{id}/event-view"


def get_email_list(frequency):
    admins = remove_admin_duplicates()
    email_list = []
    for admin in admins:
        admin_settings = admin.get("pref", {}).get("admin_portal_settings", {}).get("general_settings")
        freq = admin_settings.get("notifications")
        if freq.get(frequency).get("value") ==True:
            email_list.append(admin.get("email"))

    return email_list



def get_live_events_within_the_week():
    events_query = Event.objects.filter(
        start_date_and_time__gte=today,
        start_date_and_time__lte=in_30_days,
        is_deleted=False
        ) 
    events = serialize_all(events_query, full=True)
    data={
        "events":[{
            "logo": event.get("community",{}).get("logo") if event.get("community") else None,
            "title": event.get("name"),
            "community": event.get("community",{}).get("name") if event.get("community") else "N/A",
            "period":human_readable_date(event.get("start_date_and_time"), event.get("end_date_and_time")),
            "location":"Online" if event.get("location") else "In person",
            "link":generate_redirect_url(event.get("id"))
        } for event in events]
    }
    return data
 
 


from _main_.utils.common import serialize_all
from database.models import *
from django.utils import timezone
import datetime
from django.utils.timezone import utc
from _main_.settings import DJANGO_ENV


today = datetime.datetime.utcnow().replace(tzinfo=utc)
in_30_days = today + timezone.timedelta(days=30)
WEEKLY_EVENT_NUDGE="WEEKLY_EVENT_NUDGE"

def is_viable(item):
    if item[0] is not None and item[1]is not None:
        if  not item[0]=={}:
            return True
    return False



def get_comm_emails_and_pref():
    communities = Community.objects.all()
    flag = FeatureFlag.objects.filter(key=WEEKLY_EVENT_NUDGE).first()
    allowed_communities = list(flag.communities.all())
    admins = []

    for com in communities:
        if com in allowed_communities:
            all_community_admins = CommunityAdminGroup.objects.filter(community=com).values_list('members__preferences', "members__email", "members__full_name")
            for i in list(all_community_admins):
                if is_viable(i):
                    admins.append({
                        "pref":i[0],
                        "email":i[1],
                        "name":i[2]
                    })
    return admins


def human_readable_date(start):
    return start.strftime("%b %d")



def get_domain():
    if DJANGO_ENV == "local": return 'http://localhost:3001'
    elif DJANGO_ENV == "canary":return "https://admin-canary.massenergize.org"
    return "https://admin.massenergize.org"



def generate_redirect_url(type=None,id=""):
    domain = get_domain()
    if type == "SHARING": return f'{domain}/admin/read/event/{id}/event-view?from=others&dialog=open'
    return f"{domain}/admin/read/event/{id}/event-view?from=main"


def get_email_list(frequency):
    admins = get_comm_emails_and_pref()
    email_list = {}
    for admin in admins:
        admin_settings = admin.get("pref", {}).get("admin_portal_settings", {}).get("general_settings")
        freq = admin_settings.get("notifications")
        if freq.get(frequency).get("value") ==True:
            email_list[admin.get("name")] = admin.get("email")

    return email_list



def get_live_events_within_the_week():
    
    events_query = Event.objects.filter(
        start_date_and_time__gte=today,
        start_date_and_time__lte=in_30_days,
        is_deleted=False,

        ) 
    events = serialize_all(events_query, full=True)

    data={
        "events":[{
            "logo": event.get("community",{}).get("logo").get('url') if event.get("community") else None,
            "title": event.get("name"),
            "community": event.get("community",{}).get("name") if event.get("community") else "N/A",
            "date":human_readable_date(event.get("start_date_and_time")),
            "location":"Online" if event.get("location") else "In person",
            "share_link":generate_redirect_url("SHARING",event.get("id")),
            "view_link":generate_redirect_url(event.get("id")),
        } for event in events]
    }
    return data
 
 


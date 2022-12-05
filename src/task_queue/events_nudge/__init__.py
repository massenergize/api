from _main_.utils.common import serialize_all
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.utils.constants import WEEKLY_EVENTS_NUDGE_TEMPLATE_ID
from database.models import *
from django.utils import timezone
import datetime
from django.utils.timezone import utc
from _main_.settings import DJANGO_ENV
from django.db.models import Q


WEEKLY= "weekly"
BI_WEEKLY = "bi-weekly"
MONTHLY = "monthly"


today = datetime.datetime.utcnow().replace(tzinfo=utc)
in_30_days = today + timezone.timedelta(days=30)
WEEKLY_EVENT_NUDGE="WEEKLY_EVENT_NUDGE"

def is_viable(item):
    if item[0] is not None and item[1]is not None:
        if  not item[0]=={}:
            return True
    return False



def generate_event_for_community():
    data = []
    communities = Community.objects.filter(is_published=True, is_deleted=False)
    open = Q(publicity=EventConstants.open())
    for com in communities:
        events = Event.objects.filter(
            open|Q(publicity=EventConstants.is_open_to("OPEN_TO"), 
            communities_under_publicity__id= com.id),
            start_date_and_time__gte=today,
            start_date_and_time__lte=in_30_days,
            is_deleted=False).exclude(community=com, shared_to__id=com.id)
        data.append({
            "events":prepare_events_email_data(events),
            "admin":get_comm_admins(com)
        })

    return data



def get_comm_admins(com):
    flag = FeatureFlag.objects.filter(key=WEEKLY_EVENT_NUDGE).first()
    allowed_communities = list(flag.communities.all())
    admins = []
    if com in allowed_communities:
        all_community_admins = CommunityAdminGroup.objects.filter(community=com).values_list('members__preferences', "members__email", "members__full_name", "members__notification_dates")
        for i in list(all_community_admins):
            if is_viable(i):
                admins.append({
                    "pref":i[0],
                    "email":i[1],
                    "name":i[2],
                    "notification_dates":i[3]
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


def get_email_list(frequency, admins):
    '''
    Have a field on the user models called last_notified.
    when preparing the email list, check for communication pref and calculated from last_notified till now 
    if it is equal to the selected communication pref add user
    
    '''
    email_list = {}
    for admin in admins:
        admin_settings = admin.get("pref", {}).get("admin_portal_settings", {}).get("general_settings")
        freq = admin_settings.get("notifications")
        if freq.get(frequency).get("value") ==True:
            email_list[admin.get("name")] = admin.get("email")

    return email_list



def prepare_events_email_data(events):
    events = serialize_all(events, full=True)
    data=[{
            "logo": event.get("community",{}).get("logo").get('url') if event.get("community") else None,
            "title": event.get("name"),
            "community": event.get("community",{}).get("name") if event.get("community") else "N/A",
            "date":human_readable_date(event.get("start_date_and_time")),
            "location":"Online" if event.get("location") else "In person",
            "share_link":generate_redirect_url("SHARING",event.get("id")),
            "view_link":generate_redirect_url(event.get("id")),
        } for event in events]
    return data
 
 

def send_events_report():
    data = {}
    change_preference_link = get_domain()+"/admin/profile/settings"
    d = generate_event_for_community()
    for item in d:
        if len(item.get("admins", []))>0:
            admins = get_email_list(WEEKLY,item.get("admins", []))
            if item.get("events"):
                for name, email in admins.items():
                    data = {}
                    data["name"]= name
                    data["change_preference_link"] = change_preference_link
                    data["events"] = item.get("events")
                    send_massenergize_email_with_attachments(WEEKLY_EVENTS_NUDGE_TEMPLATE_ID, data, [email], None, None)

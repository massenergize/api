from _main_.utils.common import serialize_all
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.constants import ADMIN_URL_ROOT, COMMUNITY_URL_ROOT
from api.utils.constants import WEEKLY_EVENTS_NUDGE_TEMPLATE_ID
from database.models import *
from django.utils import timezone
import datetime
import pytz
from django.utils.timezone import utc
from django.db.models import Q
from dateutil.relativedelta import relativedelta


WEEKLY= "weekly"
BI_WEEKLY = "bi-weekly"
MONTHLY = "monthly"

#kludge - current communities are in Massachusetts, so for now all dates shown are eastern us time zone
eastern_tz  = pytz.timezone("US/Eastern")

default_pref={
    "user_portal_settings": UserPortalSettings.Defaults,
    "admin_portal_settings": AdminPortalSettings.Defaults,
}

today = datetime.datetime.utcnow().replace(tzinfo=utc)
in_30_days = today + timezone.timedelta(days=30)
WEEKLY_EVENT_NUDGE="weekly_event_nudge-feature-flag"

def is_viable(item):
    if item[0] is not None and item[1]is not None:
        if  not item[0]=={}:
            return True
    return False

def generate_event_list_for_community(com):
    open = Q(publicity=EventConstants.open())
    events = Event.objects.filter(
            open|Q(publicity=EventConstants.is_open_to("OPEN_TO"), 
            communities_under_publicity__id= com.id),
            start_date_and_time__gte=today,
            start_date_and_time__lte=in_30_days,
            community__is_published=True,
            is_published=True,
            is_deleted=False
            ).exclude(community=com, shared_to__id=com.id)

    return {
            "events":prepare_events_email_data(events),
            "admins":get_comm_admins(com)
            }



def get_comm_admins(com):
    """
    only get admins whose communities have been allowed in the feature flag to receive events
    nudge
    """
    admins = []

    all_community_admins = CommunityAdminGroup.objects.filter(community=com).values_list('members__preferences', "members__email", "members__full_name", "members__notification_dates")
    for i in list(all_community_admins):
        admins.append({
                "pref":i[0] if is_viable(i) else default_pref,
                "email":i[1],
                "name":i[2],
                "notification_dates":i[3]
            })

    return admins


def human_readable_date(start):
    return start.astimezone(eastern_tz).strftime("%b %d")



def generate_redirect_url(type=None,id="",community=None):
    url = ''
    if type == "SHARING":
        url = f'{ADMIN_URL_ROOT}/admin/read/event/{id}/event-view?from=others'
    if community:
        subdomain = community.get("subdomain") 
        url = f"{COMMUNITY_URL_ROOT}/{subdomain}/events/{id}"
    return url


def update_last_notification_dates(email):
    new_date = str(datetime.date.today())
    notification_dates = {"cadmin_nudge":new_date}
    UserProfile.objects.filter(email=email).update(**{"notification_dates":notification_dates })


def get_email_list(admins):
    email_list = {}
    for admin in admins:
        name = admin.get("name")
        email = admin.get("email")
        if not name or not email:
            print("Missing name or email for admin: "+ str(admin))
            continue

        # BHN - fixed crash on this next line if communication_prefs didn't exist
        admin_settings = admin.get("pref", {}).get("admin_portal_settings", {}).get("communication_prefs", {})
        freq = admin_settings.get("reports_frequency", {})
        last_notified = admin.get("notification_dates",{}).get("cadmin_nudge", None)
        if last_notified:
            freq_keys = freq.keys()

            if len(freq_keys)==0 or WEEKLY in freq_keys:
               in_a_week_from_last_nudge =  datetime.datetime.strptime(last_notified, '%Y-%m-%d')+ relativedelta(weeks=1)
               if in_a_week_from_last_nudge.date() <= datetime.date.today():
                 email_list[name] = email

            if BI_WEEKLY in freq_keys:
               in_two_weeks_from_last_nudge =  datetime.datetime.strptime(last_notified, '%Y-%m-%d')+ relativedelta(weeks=2)
               if in_two_weeks_from_last_nudge.date() <= datetime.date.today():
                 email_list[admin.get("name")] = email

            if MONTHLY in freq_keys:
               in_a_month_from_last_nudge =  datetime.datetime.strptime(last_notified, '%Y-%m-%d')+ relativedelta(months=1)
               if in_a_month_from_last_nudge.date() <= datetime.date.today():
                  email_list[admin.get("name")] = admin.get("email")
                 
        else:
           email_list[admin.get("name")] = admin.get("email")

    return email_list



def prepare_events_email_data(events):
    events = serialize_all(events, full=True)
    data=[{
            "logo": event.get("community",{}).get("logo").get('url') if event.get("community") else None,
            "title": event.get("name"),
            "community": event.get("community",{}).get("name") if event.get("community") else "N/A",
            "date":human_readable_date(event.get("start_date_and_time")),
            "location":"In person" if event.get("location") else "Online",
            "share_link":generate_redirect_url("SHARING",event.get("id")),
            "view_link":generate_redirect_url("VIEW", event.get("id"),event.get("community")),
        } for event in events]
    #sort list of events by date
    data = (sorted(data, key=lambda i: i['date']))
    return data
 
#  this is the function called in jobs.py
def send_events_nudge():
    try:
        flag = FeatureFlag.objects.filter(key=WEEKLY_EVENT_NUDGE).first()
        allowed_communities = list(flag.communities.all())

        communities = Community.objects.filter(is_published=True, is_deleted=False)
        for com in communities:
            if flag.audience == "EVERYONE" or com in allowed_communities:
                print("Sending nudge to admins from community: "+str(com))
                d = generate_event_list_for_community(com)
                admins = d.get("admins",[])
                event_list = d.get("events",[])
                if len(admins)>0 and len(event_list)>0:
                    email_list = get_email_list(admins)
                    for name, email in email_list.items():
                        stat = send_events_report(name, email, event_list)
                        if not stat:
                            print("send_events_report error return")
                            return False

        return True
    except Exception as e: 
        print("Community admin nudge exception: " + str(e))
        return False

def send_events_report(name, email, event_list):
    try:                            
        change_preference_link = ADMIN_URL_ROOT+"/admin/profile/preferences"
        data = {}
        data["name"]= name.split(" ")[0]
        data["change_preference_link"] = change_preference_link
        data["events"] = event_list
        send_massenergize_email_with_attachments(WEEKLY_EVENTS_NUDGE_TEMPLATE_ID, data, [email], None, None)
        update_last_notification_dates(email)
        return True
    except Exception as e:
        print("send_events_report exception: " + str(e))
        return False

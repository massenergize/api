import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.utils import timezone

from _main_.utils.common import custom_timezone_info, encode_data_for_URL, serialize_all
from _main_.utils.constants import ADMIN_URL_ROOT, COMMUNITY_URL_ROOT
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.feature_flag_keys import COMMUNITY_ADMIN_WEEKLY_EVENTS_NUDGE_FF
from api.utils.constants import WEEKLY_EVENTS_NUDGE_TEMPLATE
from database.models import Community, CommunityAdminGroup, Event, FeatureFlag, UserProfile
from database.utils.settings.admin_settings import AdminPortalSettings
from database.utils.settings.model_constants.events import EventConstants
from database.utils.settings.user_settings import UserPortalSettings
from task_queue.helpers import get_event_location

WEEKLY = "weekly"
BI_WEEKLY = "bi-weekly"
MONTHLY = "monthly"

#kludge - current communities are in Massachusetts, so for now all dates shown are eastern us time zone
eastern_tz = custom_timezone_info("US/Eastern")

default_pref = {
    "user_portal_settings": UserPortalSettings.Defaults,
    "admin_portal_settings": AdminPortalSettings.Defaults,
}


def is_viable(item):
    if item[0]  and item[1]:
        if not item[0] == {} or not item[0] == "":
            return True
    return False


def generate_event_list_for_community(com):
    today = timezone.now()
    in_30_days = today + timezone.timedelta(days=30)
    open = Q(publicity=EventConstants.open())
    events = Event.objects.filter(
        open | Q(publicity=EventConstants.is_open_to("OPEN_TO"),
                 communities_under_publicity__id=com.id),
        start_date_and_time__gte=today,
        start_date_and_time__lte=in_30_days,
        community__is_published=True,
        is_published=True,
        is_deleted=False
    ).exclude(shared_to__id=com.id).distinct().order_by("start_date_and_time")
    
    return {
        "events": prepare_events_email_data(events),
        "admins": get_comm_admins(com)
    }


def get_comm_admins(com):
    """
    only get admins whose communities have been allowed in the feature flag to receive events
    nudge
    """
    flag = FeatureFlag.objects.filter(key=COMMUNITY_ADMIN_WEEKLY_EVENTS_NUDGE_FF).first()

    all_community_admins = CommunityAdminGroup.objects.filter(community=com).values_list('members__preferences', "members__email", "members__full_name", "members__notification_dates", "members__user_info")

    admins = []
    for i in list(all_community_admins):
        admins.append({
            "pref": i[0] if is_viable(i) else default_pref,
            "email": i[1],
            "name": i[2],
            "notification_dates": i[3],
            "user_info":i[4]
        })

    # TODO: use flag.enabled_users() instead
    user_list = []   
    if flag.user_audience == "SPECIFIC":
        user_list = [str(u.email) for u in flag.users.all()]
        admins = list(filter(lambda admin: admin.get("email") in user_list,admins ))
    elif flag.user_audience == "ALL_EXCEPT":
        user_list = [str(u.email) for u in flag.users.all()]
        admins = list(filter(lambda admin: admin.get("email") not in user_list,admins ))

    return admins


def human_readable_date(start):
    return start.astimezone(eastern_tz).strftime("%b %d")


def generate_redirect_url(type=None, id="", community=None):
    url = ''
    if type == "SHARING":
        url = f'{ADMIN_URL_ROOT}/admin/read/event/{id}/event-view?from=others'
    if community:
        subdomain = community.get("subdomain")
        url = f"{COMMUNITY_URL_ROOT}/{subdomain}/events/{id}"
    return url


def update_last_notification_dates(emails):
    new_date = str(datetime.date.today())
    for email in emails:
        user = UserProfile.objects.filter(email=email).first()
        user_notification_dates = user.notification_dates if user.notification_dates else {}
        notification_dates = {**user_notification_dates,"cadmin_nudge":new_date}
        UserProfile.objects.filter(email=email).update(**{"notification_dates":notification_dates })



def get_email_list(admins):
    email_list = {}
    for admin in admins:
        name = admin.get("name")
        email = admin.get("email")
        if not name or not email:
            print("Missing name or email for admin: " + str(admin))
            continue

        # BHN - fixed crash on this next line if communication_prefs didn't exist
        admin_preferences = admin.get("pref", default_pref)

        admin_settings = admin_preferences.get("admin_portal_settings", {}).get("communication_prefs", {})
        freq = admin_settings.get("reports_frequency", {})
        notification_dates = admin.get("notification_dates", {})
        last_notified = notification_dates.get("cadmin_nudge", "") if notification_dates else None

        if last_notified:
            freq_keys = freq.keys()

            if len(freq_keys) == 0 or WEEKLY in freq_keys:
               in_a_week_from_last_nudge = datetime.datetime.strptime(
                   last_notified, '%Y-%m-%d') + relativedelta(weeks=1)
               if in_a_week_from_last_nudge.date() <= datetime.date.today():
                 email_list[name] = email

            if BI_WEEKLY in freq_keys:
               in_two_weeks_from_last_nudge = datetime.datetime.strptime(
                   last_notified, '%Y-%m-%d') + relativedelta(weeks=2)
               if in_two_weeks_from_last_nudge.date() <= datetime.date.today():
                 email_list[admin.get("name")] = email

            if MONTHLY in freq_keys:
               in_a_month_from_last_nudge = datetime.datetime.strptime(
                   last_notified, '%Y-%m-%d') + relativedelta(months=1)
               if in_a_month_from_last_nudge.date() <= datetime.date.today():
                  email_list[admin.get("name")] = admin.get("email")

        else:
           email_list[admin.get("name")] = admin.get("email")

    return email_list

def get_logo(event):
    if event.get("community", {}).get("logo"):
        return event.get("community").get("logo").get("url")
    return ""

def prepare_events_email_data(events):
    events = serialize_all(events, full=True)
    data = [{
            "logo": get_logo(event),
            "title": event.get("name"),
            "community": event.get("community", {}).get("name") if event.get("community") else "N/A",
            "date": human_readable_date(event.get("start_date_and_time")),
            "location": get_event_location(event),
            "share_link": generate_redirect_url("SHARING", event.get("id")),
            "view_link": generate_redirect_url("VIEW", event.get("id"), event.get("community")),
            } for event in events]
    #sort list of events by date
    data = (sorted(data, key=lambda i: i['date'], reverse=True))
    return data

#  this is the function called in jobs.py


def send_events_nudge(task=None):
    try:
        admins_emailed=[]
        flag = FeatureFlag.objects.get(key=COMMUNITY_ADMIN_WEEKLY_EVENTS_NUDGE_FF)
        if not flag or not flag.enabled():
            return False

        communities = Community.objects.filter(is_published=True, is_deleted=False)
        communities = flag.enabled_communities(communities)
        for com in communities:
            d = generate_event_list_for_community(com)
            admins = d.get("admins", [])
            event_list = d.get("events", [])
            if len(admins) > 0 and len(event_list) > 0:
                email_list = get_email_list(admins)

                #for name, email, user_info in email_list.items():
                #    stat = send_events_report(name, email, event_list, user_info)
                for name, email in email_list.items():
                    stat = send_events_report(name, email, event_list)
                    if not stat:
                        print("send_events_report error return")
                        return False
                    admins_emailed.append(email)
        update_last_notification_dates(admins_emailed)
        return True
    except Exception as e:
        print("Community admin nudge exception: " + str(e))
        return False


#def send_events_report(name, email, event_list, user_info):
def send_events_report(name, email, event_list):
    try:
        # 14-Dec-23 - fix for user_info not provided
        user = UserProfile.objects.filter(email=email).first()
        login_method= (user.user_info or {}).get("login_method", None)
        cred = encode_data_for_URL({"email": email, "login_method":login_method})
        change_preference_link = ADMIN_URL_ROOT+f"/admin/profile/preferences/?cred={cred}"
        data = {}
        data["name"] = name.split(" ")[0]
        data["change_preference_link"] = change_preference_link
        data["events"] = event_list
        # sent from MassEnergize to cadmins
        send_massenergize_email_with_attachments(WEEKLY_EVENTS_NUDGE_TEMPLATE, data, [email], None, None, None)
        return True
    except Exception as e:
        print("send_events_report exception: " + str(e))
        return False

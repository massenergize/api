import datetime
import pytz
from _main_.utils.common import serialize_all
from _main_.utils.constants import COMMUNITY_URL_ROOT
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.utils.constants import USER_EVENTS_NUDGE_TEMPLATE_ID
from database.models import Community, Event, UserProfile, FeatureFlag
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from database.utils.common import get_json_if_not_none

from database.utils.settings.model_constants.events import EventConstants
from django.utils import timezone

WEEKLY = "per_week"
BI_WEEKLY = "biweekly"
MONTHLY = "per_month"
DAILY="per_day"

LIMIT=5

USER_PREFERENCE_DEFAULTS = {
        "communication_prefs": {
            "update_frequency": {"per_week": {"value": True}},
            "news_letter": {"as_posted": {"value": True}},
            "messaging": {"yes": {"value": True}},
        },
        "notifications": {
            "upcoming_events": {"never": {"value": True}},
            "upcoming_actions": {"never": {"value": True}},
            "news_teams": {"never": {"value": True}},
            "new_testimonials": {"never": {"value": True}},
            "your_activity_updates": {"never": {"value": True}},
        },
    }



USER_EVENT_NUDGE_KEY = "communication-prefs-feature-flag"

def should_user_get_nudged(user):

    user_communication_preferences = user.get("preferences", {}).get("user_portal_settings", {}).get("communication_prefs", {})
    freq = user_communication_preferences.get("update_frequency", {})
    last_notified = user.get("notification_dates", {}).get("user_event_nudge", "")
    if last_notified:
        freq_keys = freq.keys()

        if len(freq_keys) == 0 or WEEKLY in freq_keys:
            in_a_week_from_last_nudge = datetime.datetime.strptime(last_notified, '%Y-%m-%d') + relativedelta(weeks=1)
            if in_a_week_from_last_nudge.date() <= datetime.date.today():
                return True

        if BI_WEEKLY in freq_keys:
            in_two_weeks_from_last_nudge = datetime.datetime.strptime(
                last_notified, '%Y-%m-%d') + relativedelta(weeks=2)
            if in_two_weeks_from_last_nudge.date() <= datetime.date.today():
                return True

        if MONTHLY in freq_keys:
            in_a_month_from_last_nudge = datetime.datetime.strptime(
                last_notified, '%Y-%m-%d') + relativedelta(months=1)
            if in_a_month_from_last_nudge.date() <= datetime.date.today():
                return True
            
        if DAILY in freq_keys:
            in_a_day_from_last_nudge = datetime.datetime.strptime(
                last_notified, '%Y-%m-%d') + relativedelta(days=1)
            if in_a_day_from_last_nudge.date() <= datetime.date.today():
                return True

    else:
        return True
          


def update_last_notification_dates(email):
    new_date = str(datetime.date.today())
    user =  UserProfile.objects.filter(email=email).first()

    notification_dates = {**user.notification_dates,"user_event_nudge":new_date}
    UserProfile.objects.filter(email=email).update(**{"notification_dates":notification_dates })


def user_has_correct_preferences(user):
    if user.preferences is not None and user.email is not None:
        if  not user.preferences=={}:
            return True
    return False

def format_users_list(all_users):
    users = []
    for user in all_users:
        users.append({
            "preferences": user.preferences if user_has_correct_preferences(user) else USER_PREFERENCE_DEFAULTS,
            "email": user.email,
            "name": user.full_name,
            "notification_dates": user.notification_dates,
        })

    return users


def get_community_events(community_id):
    events = Event.objects.filter(
        Q(community__id=community_id) | # parent community events
        Q(shared_to__id=community_id) | # events shared to community
        Q(publicity=EventConstants.open()) | # open events
        Q(publicity=EventConstants.is_open_to("OPEN_TO"),communities_under_publicity__id=community_id), # events that are opened to community
        is_published=True, 
        is_deleted=False, 
        exclude_from_nudge=False,
        start_date_and_time__gte=timezone.now(),
        )
    
    return events


def get_community_users(community_id):
   users = UserProfile.objects.filter(communities__id=community_id, is_super_admin=False, is_community_admin=False, is_vendor=False)
   return format_users_list(users)


eastern_tz = pytz.timezone("US/Eastern")
def human_readable_date(start):
    return start.astimezone(eastern_tz).strftime("%b %d")


def generate_change_pref_url(subdomain):
    url = f"{COMMUNITY_URL_ROOT}/{subdomain}/profile/settings"
    return url

def get_logo(event):
    if event.get("image"):
       return event.get("image").get("url")
    elif event.get("community", {}).get("logo"):
        return event.get("community").get("logo").get("url")
    return ""


def truncate_title(title):
    if len(title) > 50:
        return title[:50] + "..."
    return title
    
def prepare_events_email_data(events):
    events = serialize_all(events, full=True)

    data = [{
            "logo": get_logo(event),
            "title": truncate_title(event.get("name")),
            "date": human_readable_date(event.get("start_date_and_time")),
            "location": "In person" if event.get("location") else "Online",
            "view_link": f'{COMMUNITY_URL_ROOT}/{event.get("community", {}).get("subdomain")}/events/{event.get("id")}',
            } for event in events]
    #sort list of events by date
    data = (sorted(data, key=lambda i: i['date']))
    return data




def send_events_report_email(name, email, event_list, comm):
    try:
        events = prepare_events_email_data(event_list[:LIMIT])
        has_more_events = len(event_list) > LIMIT
        change_pref_link = generate_change_pref_url(comm.subdomain)
        data = {}
        data["name"] = name.split(" ")[0]
        data["change_preference_link"] = change_pref_link
        data["events"] = events
        data["has_more_events"] = {
            "view_more_link": f'{COMMUNITY_URL_ROOT}/{comm.subdomain}/events?ids={"-".join([str(event.id) for event in event_list[LIMIT:]])}',
        } if has_more_events else None 

        data["community_logo"] = get_json_if_not_none(comm.logo).get("url") if comm.logo else ""
        data["cadmin_email"]=comm.owner_email if comm.owner_email else ""
        data["community"] = comm.name
        send_massenergize_email_with_attachments(USER_EVENTS_NUDGE_TEMPLATE_ID, data, [email], None, None)
        return True
    except Exception as e:
        print("send_events_report exception: " + str(e))
        return False


def send_automated_nudge(events, user, community):
    if len(events) > 0 and user:
        name = user.get("name")
        email = user.get("email")
        if not name or not email:
            print("Missing name or email for user: " + str(user))
            return False

        user_is_ready_for_nudge = should_user_get_nudged(user)

        if user_is_ready_for_nudge:
    
            is_sent = send_events_report_email(name, email, events, community)
            if not is_sent:
                print(
                    f"**** Failed to send email to {name} for community {community.name} ****")
                return False
            update_last_notification_dates(email)
    return True


def send_user_requested_nudge(events, user, community):
    if len(events) > 0 and user:
        name = user.full_name
        email = user.email
        is_sent = send_events_report_email(name, email, events, community)
        if not is_sent:
            print(f"**** Failed to send email to {name} for community {community.name} ****")
            return False
    return True
        


def get_user_events(notification_dates, community_events):
    today = timezone.now()
    a_week_ago = today - relativedelta(weeks=1)
    date_aware =None
    user_event_nudge = notification_dates.get("user_event_nudge")
    if user_event_nudge:
        last_received_at = datetime.datetime.strptime(user_event_nudge, '%Y-%m-%d')
        date_aware = timezone.make_aware(last_received_at, timezone=timezone.get_default_timezone())
 
    #  if user hasn't received a nudge before, get all events that went live within the week
    # else use the last nudge date
    last_time = date_aware if date_aware else a_week_ago

    return community_events.filter(Q(published_at__range=[last_time, today]))

'''
Note: This function only get email as argument when the
nudge is requested on demand by a cadmin on user portal.
'''
# Entry point
def prepare_user_events_nudge(email=None, community_id=None):
    try:
        user = None

        flag = FeatureFlag.objects.filter(key=USER_EVENT_NUDGE_KEY).first()
        allowed_communities = list(flag.communities.all())

        communities = Community.objects.filter(is_published=True, is_deleted=False)
        #  process on demand request
        if email and community_id:
            all_community_events = get_community_events(community_id)
            user = UserProfile.objects.filter(email=email).first()
            community = Community.objects.filter(id=community_id).first()
            events = get_user_events(user.notification_dates, all_community_events)
            send_user_requested_nudge(events, user, community)

            return True

        for community in communities:
            if flag.audience == "EVERYONE" or community in allowed_communities:
                events = get_community_events(community.id)
                users = get_community_users(community.id)
                for user in users:
                    events = get_user_events(user.get("notification_dates", {}), events)
                    send_automated_nudge(events, user, community)

        return True   
    except Exception as e:
        print("Community member nudge exception: " + str(e))
        return False
    
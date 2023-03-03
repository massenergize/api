import datetime
import pytz
from _main_.utils.common import serialize_all
from database.models import Community, Event, UserProfile, FeatureFlag
from django.db.models import Q
from dateutil.relativedelta import relativedelta


WEEKLY = "weekly"
BI_WEEKLY = "bi-weekly"
MONTHLY = "monthly"

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



USER_EVENT_NUDGE_KEY = "user-event-nudge-feature-flag"
'''
1. get all communities
2. get all users of a community and newly created events that are live
3. prepare events data for postMark
'''


def get_user_email_list(users):
    email_list = {}
    for user in users:
        name = user.get("name")
        email = user.get("email")
        if not name or not email:
            print("Missing name or email for user: " + str(user))
            continue

        # BHN - fixed crash on this next line if communication_prefs didn't exist
        user_communication_preferences = user.get("preferences", {}).get("user_portal_settings", {}).get("communication_prefs", {})
        freq = user_communication_preferences.get("update_frequency", {})
        last_notified = user.get("notification_dates", {}).get("user_event_nudge", None)
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
                 email_list[name] = email

            if MONTHLY in freq_keys:
               in_a_month_from_last_nudge = datetime.datetime.strptime(
                   last_notified, '%Y-%m-%d') + relativedelta(months=1)
               if in_a_month_from_last_nudge.date() <= datetime.date.today():
                  email_list[name] = email

        else:
           email_list[name] = email

    return email_list


def update_last_notification_dates(email):
    new_date = str(datetime.date.today())
    user =  UserProfile.objects.filter(email=email).first()
    # TODO: add id's of events that were sent to this user
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


def get_all_users_and_events_for_community(community_id):
    users = UserProfile.objects.filter(communities__id=community_id, is_super_admin=False, is_community_admin=False, is_vendor=False)

    events = Event.objects.filter(Q(community__id=community_id)|Q(shared_to__id=community_id), is_published=True,is_deleted=False)
    return format_users_list(users), events


eastern_tz = pytz.timezone("US/Eastern")
def human_readable_date(start):
    return start.astimezone(eastern_tz).strftime("%b %d")



def generate_change_pref_url(community_id, user_id):
    pass

def prepare_events_email_data(events):
    events = serialize_all(events, full=True)

    data = [{
            "logo": event.get("image", {}).get("url", {}) if event.get("image") else "",
            "title": event.get("name"),
            "community": event.get("community", {}).get("name") if event.get("community") else "N/A",
            "date": human_readable_date(event.get("start_date_and_time")),
            "location": "In person" if event.get("location") else "Online",
            "change_pref_link":"",
            } for event in events]
    #sort list of events by date
    data = (sorted(data, key=lambda i: i['date']))
    return data



def send_user_event_nudge():
    communities = Community.objects.filter(is_published=True,)
    _users = {}
    for community in communities:
        users, events = get_all_users_and_events_for_community(community.id)
        if len(events) > 0 or len(users) > 0:
            _users[community.name] = {
                "users": get_user_email_list(users),
                "events": prepare_events_email_data(events)
                }

    return _users


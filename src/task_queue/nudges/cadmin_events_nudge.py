import traceback
from typing import Tuple
from django.db.models import Q
from django.utils import timezone

from _main_.utils.common import custom_timezone_info, encode_data_for_URL, serialize_all
from _main_.utils.constants import ADMIN_URL_ROOT, COMMUNITY_URL_ROOT
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from _main_.utils.feature_flag_keys import COMMUNITY_ADMIN_WEEKLY_EVENTS_NUDGE_FF
from api.utils.api_utils import generate_email_tag
from api.utils.constants import WEEKLY_EVENTS_NUDGE_TEMPLATE
from database.models import Community, CommunityAdminGroup, Event, FeatureFlag, UserProfile
from database.utils.settings.model_constants.events import EventConstants
from task_queue.helpers import get_event_location
from task_queue.nudges.nudge_utils import get_admin_email_list, update_last_notification_dates
from _main_.utils.massenergize_logger import log
from task_queue.type_constants import CADMIN_EVENTS_NUDGE



#kludge - current communities are in Massachusetts, so for now all dates shown are eastern us time zone
eastern_tz = custom_timezone_info("US/Eastern")
CADMIN_NUDGE_KEY="cadmin_nudge"


def generate_event_list_for_community(com) -> dict:
    try:
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
    except Exception as e:
        log.error(f"Error in generate_event_list_for_community: {str(e)}")
        return {
            "events": [],
            "admins": {}
        }


def get_comm_admins(com) -> dict:
    """
        only get admins whose communities have been allowed in the feature flag to receive events
        nudge
    """
    try:

        flag = FeatureFlag.objects.filter(key=COMMUNITY_ADMIN_WEEKLY_EVENTS_NUDGE_FF).first()

        all_community_admins = CommunityAdminGroup.objects.filter(community=com).values_list('members__preferences', "members__email", "members__full_name", "members__notification_dates", "members__user_info")

        name_emails = {}

        for (preferences, email, name, notification_dates, user_info) in list(all_community_admins):
            if email:
                name_emails[email] = {"name": name,"preferences": preferences, "nudge_dates": notification_dates, "user_info": user_info}

        # TODO: use flag.enabled_users() instead
        user_list = []
        admin_list = [] 
        if flag.user_audience == "SPECIFIC":
            user_list = [str(u.email) for u in flag.users.all()]
            admin_list =  list(filter(lambda admin: admin in user_list, name_emails.keys()))
        elif flag.user_audience == "ALL_EXCEPT":
            user_list = [str(u.email) for u in flag.users.all()]
            admin_list =  list(filter(lambda admin: admin not in user_list, name_emails.keys()))

        else:
            return name_emails
        
        return {k: v for k, v in name_emails.items() if k in admin_list}
    except Exception as e:
        log.error(f"Error in get_comm_admins: {str(e)}")
        return {}


def human_readable_date(start) -> str:
    return start.astimezone(eastern_tz).strftime("%b %d")


def generate_redirect_url(type=None, id="", community=None) -> str:
    url = ''
    if type == "SHARING":
        url = f'{ADMIN_URL_ROOT}/admin/read/event/{id}/event-view?from=others'
    if community:
        subdomain = community.get("subdomain")
        url = f"{COMMUNITY_URL_ROOT}/{subdomain}/events/{id}"
    return url


def get_logo(event) -> str:
    if event.get("community", {}).get("logo"):
        return event.get("community").get("logo").get("url")
    return ""

def prepare_events_email_data(events) -> list: 
    try:
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
    except Exception as e:
        log.error(f"Error in prepare_events_email_data: {str(e)}")
        return []


def send_events_nudge(task=None) -> Tuple[bool, str]:
    try:
        admins_emailed=[]
        flag = FeatureFlag.objects.get(key=COMMUNITY_ADMIN_WEEKLY_EVENTS_NUDGE_FF)
        if not flag or not flag.enabled():
            return  None, "Feature flag not enabled"

        communities = Community.objects.filter(is_published=True, is_deleted=False)
        communities = flag.enabled_communities(communities)
        for com in communities:
            d = generate_event_list_for_community(com)
            admins = d.get("admins", {})

            event_list = d.get("events", [])


            if len(admins) > 0 and len(event_list) > 0:
                email_list = get_admin_email_list(admins, CADMIN_NUDGE_KEY)
                for email, data in email_list.items():
                    name = data.get("name")

                    stat, err = send_events_report(name, email, event_list, com)

                    if err:
                        log.error(f"send_events_report error return: {err}")
                        return False, err
                    admins_emailed.append(email)

        update_last_notification_dates(admins_emailed, CADMIN_NUDGE_KEY)
        result = {
            "audience": ",".join(admins_emailed),
            "scope": "CADMIN",
        }

        return result, None
    except Exception as e:
        stacktrace = traceback.format_exc()
        log.error(f"Community admin nudge exception: {stacktrace}")
        return None, stacktrace


def send_events_report(name, email, event_list, com) -> bool:
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

        tag = generate_email_tag(com.subdomain, CADMIN_EVENTS_NUDGE)

        ok, err = send_massenergize_email_with_attachments(WEEKLY_EVENTS_NUDGE_TEMPLATE, data, [email], None, None, None, tag)

        if err:
            log.error(f"Failed to send Cadmin Nudge to '{email}' || ERROR: {err}")

            return None, err
        log.info(f"Sent Cadmin Nudge to '{email}'  ")
        return True, None
    
    except Exception as e:
        log.error("send_events_report exception: " + str(e))
        return None, str(e)

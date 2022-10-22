from _main_.utils.common import serialize_all
from _main_.utils.emailer.send_email import send_massenergize_email_with_attachments
from api.utils.constants import WEEKLY_EVENTS_NUDGE_TEMPLATE_ID
from database.models import *
from django.utils import timezone
import datetime
from django.utils.timezone import utc


today = datetime.datetime.utcnow().replace(tzinfo=utc)
one_week_ago = today - timezone.timedelta(days=7)


def is_viable(item):
    if item[0] is not None and item[1]is not None:
        if  not item[0]=={}:
            return True
    return False

def get_events_created_within_the_week():
    events = Event.objects.filter(live_at__gte=one_week_ago, live_at__lte=today, is_deleted=False)
    return serialize_all(events)

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


def get_sadmin_emails_and_pre():
    sadmins = []
    admins = UserProfile.objects.filter(is_super_admin=True, is_deleted=False).values_list( "preferences","email")
    for i in list(admins):
    # push a check to exclude cadmins with no sound pref
        if is_viable(i):
            sadmins.append({
                "pref":i[0],
                "email":i[1]
            })
    return sadmins


def remove_dups():
    sadmins = get_sadmin_emails_and_pre()
    cadmins = get_comm_emails_and_pref()

    all = sadmins+cadmins
    result = list(
    {
        dictionary['email']: dictionary
        for dictionary in all
    }.values()
)


    return result


def human_readable_date(start, end):
    if all(getattr(start,x) == getattr(end,x) for x in ["year", "month", "day"]):
        return start.strftime("%b %d, %H:%M") +" - "+ end.strftime( "%H:%M")
    else:
        return start.strftime("%b %d, %H:%M") +" - "+ end.strftime( "%b %d, %H:%M")

def test_email():
    all= remove_dups()
    email_list = [i.get("email") for i in all]
    events = get_events_created_within_the_week()
    if events==[] or events ==None:
        return
    t_model={
        "events":[{
            "title": event.get("name"),
            "community": event.get("community",{}).get("name") if event.get("community") else "N/A",
            "period":human_readable_date(event.get("start_date_and_time"), event.get("end_date_and_time")),
            "location":"Online" if event.get("location") else "In person",
            "id":event.get("id"),
            "link":"https://www.geeksforgeeks.org/python-datetime-module/"
        } for event in events]
    }
    send_massenergize_email_with_attachments(WEEKLY_EVENTS_NUDGE_TEMPLATE_ID, t_model, email_list, None, None)


# construct a link to view event details
# construct a link to copy event to community :: hide this if user is from host community
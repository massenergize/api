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
    events = Event.objects.filter(created_at__gte=one_week_ago, created_at__lte=today, is_deleted=False)
    return events

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


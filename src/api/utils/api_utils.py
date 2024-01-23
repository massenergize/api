from math import atan2, cos, radians, sin, sqrt
from database.models import Community, CommunityAdminGroup, Media, UserProfile
import pyshorteners


def is_admin_of_community(context, community_id):
    # super admins are admins of any community
    if context.user_is_super_admin:
        return True
    if not context.user_is_community_admin:
        return False

    user_id = context.user_id
    user_email = context.user_email
    if not community_id:
        return False
    if user_id:
        user = UserProfile.objects.filter(id=user_id).first()
    else:
        user = UserProfile.objects.filter(email=user_email).first()
    community_admins = CommunityAdminGroup.objects.filter(
        community__id=community_id
    ).first()
    if not community_admins:
        return False
    is_admin = community_admins.members.filter(id=user.id).exists()
    return is_admin


def get_user_community_ids(context):
    user_id = context.user_id
    user_email = context.user_email
    if user_id:
        user = UserProfile.objects.filter(id=user_id).first()
    else:
        user = UserProfile.objects.filter(email=user_email).first()
    if not user:
        return None
    ids = user.communityadmingroup_set.all().values_list("community__id", flat=True)
    return list(ids)


def get_key(name):
    arr = name.lower().split(" ")
    return "-".join(arr) + "-template-id"


def get_distance_between_coords(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    difference_long = lon2 - lon1
    difference_lat = lat2 - lat1

    a = (
        sin(difference_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(difference_long / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def is_null(val):
    if val in ["", None, [], {}, "undefined", "null"]:
        return True
    return False


def get_sender_email(community_id):
    DEFAULT_SENDER = "no-reply@massenergize.org"
    if not community_id:
        return DEFAULT_SENDER
    community = Community.objects.filter(id=community_id).first()
    if not community:
        return DEFAULT_SENDER
    postmark_info = community.contact_info if community.contact_info else {}
    if not community.owner_email:
        return DEFAULT_SENDER

    if postmark_info.get("is_validated"):
        return community.owner_email

    return DEFAULT_SENDER


def create_media_file(file, name):
    if not file:
        return None
    if file == "reset":
        return None
    media = Media.objects.create(name=name, file=file)
    media.save()
    return media

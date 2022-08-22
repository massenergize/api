from _main_.utils.footage.FootageConstants import FootageConstants
from database.models import Footage
from django.db.models import Q


def is_array(item):
    return isinstance(item, list)


class Spy:
    def __init__(self) -> None:
        pass

    @staticmethod
    def create_footage(**kwargs):
        footage = Footage.objects.create({**kwargs})
        footage.save()
        return footage

    @staticmethod
    def fetch_footages_for_community(**kwargs):
        community = kwargs.get("community") or kwargs.get("communities")
        if not community:
            return None
        query = None
        if is_array(community):
            query = Q(community__id__in=community)
        else:
            query = Q(community__id=community)
        return Footage.objects.filter(query)

    @staticmethod
    def fetch_footages_of_user(**kwargs):
        user = kwargs.get("user") or kwargs.get("users")
        if not user:
            return None
        query = None
        if is_array(user):
            query = Q(actor__id=user)
        else:
            query = Q(actor__id__in=user)
        return Footage.objects.filter(query)

    @staticmethod
    def fetch_footages_for_super_admins():
        return Footage.objects.filter(
            platform=FootageConstants.on_admin_portal()
        ).order_by("-id")[:200]

from turtle import update
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.utils import Console
from database.models import CommunityAdminGroup, Footage
from django.db.models import Q

LIMIT = 200


def is_array(item):
    return isinstance(item, list)


class Spy:
    def __init__(self) -> None:
        pass

    @staticmethod
    def create_footage(**kwargs):
        try:
            footage = Footage.objects.create({**kwargs})
            footage.save()
            return footage
        except Exception as e:
             Console.log("Could not create action footage..." ,str(e), kwargs)
            # Dont do anything else, errors while saving footage should not hinder more
            # more important processes

    # @staticmethod
    # def update_footage(**kwargs):
    #     try:
    #         id  = kwargs.id
    #         pass
    #     except:
    #         Console.log("Could not update footage...", kwargs)

    @staticmethod
    def create_action_footage(**kwargs):
        """
        Capture
        1. The admin creating the action----
        2. The id of the action being created ---
        3. Whether or not the admin is a super_admin -----
        4. Link the communities that are involved with the action to the footage-----
        5. Set activty type as "CREATE"---
        6.
        """
        try:
            description = ""
            action = kwargs.get("action")
            ctx = kwargs.get("context")
            is_update = kwargs.get("is_update")
            _type = (
                FootageConstants.updating() if is_update else FootageConstants.creating()
            )
            actor = ctx.user
            footage = Spy.create_footage(
                actor=actor,
                action=action,
                description = description,
                activity_type=_type,
                by_super_admin=ctx.is_super_admin,
            )
            footage.communities.set(action.community)
            return footage
        except Exception as e: 
            Console.log("Could not create action footage..." ,str(e))

  

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
        """
        Fetches list of recent footages for super admins.
        And these will be footages from other super admins
        """
        return Footage.objects.filter(
            platform=FootageConstants.on_admin_portal(), by_super_admin=True
        ).order_by("-id")[:LIMIT]

    @staticmethod
    def fetch_footages_for_community_admins(**kwargs):
        """
        Fetches list of recent footages for community admins.
        All footages that involve admins of a given list of communities
        """
        communities = kwargs.get("communities")

        if not communities:
            return None
        return Footage.objects.filter(
            platform=FootageConstants.on_admin_portal(), communities__id__in=communities
        ).order_by("-id")[:LIMIT]

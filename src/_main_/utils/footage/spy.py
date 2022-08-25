from turtle import update
from _main_.utils.feature_flags.FeatureFlagConstants import FeatureFlagConstants
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.utils import Console
from database.models import CommunityAdminGroup, Footage, UserProfile
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
            footage = Footage.objects.create(**kwargs)
            footage.save()
            return footage
        except Exception as e:
            Console.log("Could not create footage...", str(e), kwargs)
        # Dont do anything else, errors while saving footage should not hinder more
        # more important processes

    @staticmethod
    def create_action_footage(**kwargs):
        try:
            actions = kwargs.get("actions")
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            notes = kwargs.get("notes", "")
            communities = []
            if not FootageConstants.is_copying(act_type): 
                for a in actions:
                    if a and a.community:
                        communities.append(a.community)
            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type = FootageConstants.ITEM_TYPES["ACTION"]["key"]
            )
            footage.actions.set(actions)
            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create action footage...", str(e))

    @staticmethod
    def create_event_footage(**kwargs):
        try:
            events = kwargs.get("events")
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            notes = kwargs.get("notes", "")
            communities = []
            if not FootageConstants.is_copying(act_type): 
                for a in events:
                    if a and a.community:
                        communities.append(a.community)
                        
            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type = FootageConstants.ITEM_TYPES["EVENT"]["key"]
            )
            footage.events.set(events)
            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create event footage...", str(e))

    @staticmethod
    def create_vendor_footage(**kwargs):
        try:
            items = kwargs.get("vendors")
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            notes = kwargs.get("notes", "")
            communities = []
            if not FootageConstants.is_copying(act_type): 
                for a in items:
                    if a and a.communities:
                        coms = [a for a in a.communities.all()]
                        communities = communities + coms
            
            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type = FootageConstants.ITEM_TYPES["VENDOR"]["key"]
            )
            footage.vendors.set(items)
            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create vendor footage...", str(e))

    @staticmethod
    def create_sign_in_footage(**kwargs):
        try:
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            footage = Spy.create_footage(
                actor=actor,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type = FootageConstants.ITEM_TYPES["AUTH"]["key"]
            )
            return footage
        except Exception as e:
            Console.log("Could not create sign in footage...", str(e))

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

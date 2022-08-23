from turtle import update
from _main_.utils.feature_flags.FeatureFlagConstants import FeatureFlagConstants
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
            Console.log("Could not create action footage...", str(e), kwargs)
        # Dont do anything else, errors while saving footage should not hinder more
        # more important processes

    @staticmethod
    def create_action_footage(**kwargs):
        try:
            actions = kwargs.get("actions")
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            act_type = kwargs.get("type", None)
            _type = FootageConstants.get_type(act_type)
            # description = ""
            # if FootageConstants.is_deleting(act_type):
            #     description = f"{actor.user.preferred_name or '...'} {_type.get('action_word','...')} action(s) with IDs({', '.join([a.id for a in actions])})"
            # else:
            #     action = actions[0]
            #     description = f"{actor.user.preferred_name or '...'} {_type.get('action_word','...')} an action. With ID({action.id})"
                
            footage = Spy.create_footage(
                actor=actor,
                activity_type=_type.get("key"),
                by_super_admin=ctx.is_super_admin,
            )
            footage.actions.set(actions)
            footage.communities.set(actions.community)
            return footage
        except Exception as e:
            Console.log("Could not create action footage...", str(e))

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

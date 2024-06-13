from datetime import datetime,timezone
from turtle import update
from _main_.utils.context import Context
from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.utils import Console, run_in_background
from api.store.utils import get_user_from_context
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
    @run_in_background
    def create_mou_footage(**kwargs):
        try:
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            notes = kwargs.get("notes", "")
            communities = kwargs.get("communities",[])
            
            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type=FootageConstants.ITEM_TYPES["MOU"]["key"],
            )
            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create action footage...", str(e))

    @staticmethod
    @run_in_background
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
            communities = kwargs.get("communities",[])
            if not FootageConstants.is_copying(act_type):
                for a in actions:
                    if a and a.community:
                        communities.append(a.community)
            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type=FootageConstants.ITEM_TYPES["ACTION"]["key"],
            )
            footage.actions.set(actions)
            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create action footage...", str(e))

    @staticmethod
    @run_in_background
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
            communities = kwargs.get("communities",[])
            if not FootageConstants.is_copying(act_type):
                for a in events:
                    if a and a.community:
                        communities.append(a.community)

            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type=FootageConstants.ITEM_TYPES["EVENT"]["key"],
            )
            footage.events.set(events)
            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create event footage...", str(e))

    @staticmethod
    @run_in_background
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
            communities = kwargs.get("communities",[])
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
                item_type=FootageConstants.ITEM_TYPES["VENDOR"]["key"],
            )
            footage.vendors.set(items)
            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create vendor footage...", str(e))

    @staticmethod
    @run_in_background
    def create_testimonial_footage(**kwargs):
        try:
            items = kwargs.get("testimonials")
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            notes = kwargs.get("notes", "")
            communities = kwargs.get("communities",[])
            if not FootageConstants.is_copying(act_type):
                for a in items:
                    if a and a.community:
                        communities.append(a.community)

            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type=FootageConstants.ITEM_TYPES["TESTIMONIAL"]["key"],
            )
            footage.testimonials.set(items)
            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create testimonial footage...", str(e))

    @staticmethod
    def create_team_footage(**kwargs):
        try:
            items = kwargs.get("teams",[])
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            related_users = kwargs.get("related_users",[])
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            notes = kwargs.get("notes", "")
            communities = kwargs.get("communities",[])
            for a in items:
                if a and a.communities:
                    coms = [a for a in a.communities.all()]
                    communities = communities + coms

            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type=FootageConstants.ITEM_TYPES["TEAM"]["key"],
            )
            footage.teams.set(items)
            footage.communities.set(communities)
            footage.related_users.set(related_users)
            return footage
        except Exception as e:
            Console.log("Could not create team footage...", str(e))

    @staticmethod
    @run_in_background
    def create_messaging_footage(**kwargs):
        try:
            items = kwargs.get("messages")
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            related_users = kwargs.get("related_users", [])
            teams = kwargs.get("teams", [])

            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            notes = kwargs.get("notes", "")
            communities = []
            for a in items:
                if a and a.community:
                    communities.append(a.community)

            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type=FootageConstants.ITEM_TYPES["MESSAGE"]["key"],
            )
            footage.messages.set(items)
            footage.related_users.set(related_users)
            footage.communities.set(communities)
            footage.teams.set(teams)
            return footage
        except Exception as e:
            Console.log("Could not create messaging footage...", str(e))

    @staticmethod
    @run_in_background
    def create_media_footage(**kwargs):
        try:
            items = kwargs.get("media")
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            communities = kwargs.get("communities",[])
            communities = [c for c in communities if c != None] # Get rid of Nulls
            notes = kwargs.get("notes", "")
            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type=FootageConstants.ITEM_TYPES["MEDIA"]["key"],
            )
            footage.images.set(items)
            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create media footage...", str(e))

    @staticmethod
    @run_in_background
    def create_community_footage(**kwargs):
        try:
            items = kwargs.get("communities")
            ctx = kwargs.get("context")
            actor = kwargs.get("actor")
            # users = kwargs.get("related_users", [])
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            notes = kwargs.get("notes", "")
            footage = Spy.create_footage(
                actor=actor,
                notes=notes,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type=FootageConstants.ITEM_TYPES["COMMUNITY"]["key"],
            )
            footage.communities.set(items)
            return footage
        except Exception as e:
            Console.log("Could not create community footage...", str(e))

    @staticmethod
    @run_in_background
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
            portal = kwargs.get("portal", None)
            portal = portal if portal else FootageConstants.on_admin_portal()
            footage = Spy.create_footage(
                actor=actor,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin,
                item_type=FootageConstants.ITEM_TYPES["AUTH"]["key"],
                portal = portal
            )
            passed_communities = kwargs.get("communities")
            communities = [] 
            if not passed_communities: 
                groups = actor.communityadmingroup_set.all()
                communities = [g.community for g in groups]
            else: communities = passed_communities

            footage.communities.set(communities)
            return footage
        except Exception as e:
            Console.log("Could not create sign in footage...", str(e))
        
        
    @staticmethod
    def create_community_notification_settings_footage(**kwargs):
        try:
            ctx = kwargs.get ("context")
            actor = kwargs.get("actor")
            actor = (
                actor
                if actor
                else UserProfile.objects.filter(email=ctx.user_email).first()
            )
            act_type = kwargs.get("type", None)
            portal = kwargs.get("portal", None)
            portal = portal if portal else FootageConstants.on_admin_portal()
            footage = Spy.create_footage(
                actor=actor,
                activity_type=act_type,
                by_super_admin=ctx.user_is_super_admin if ctx else False,
                item_type=FootageConstants.ITEM_TYPES["COMMUNITY_NOTIFICATION"]["key"],
                portal=portal
            )
            passed_communities = kwargs.get("communities")
            
            footage.communities.set(passed_communities)
            return footage
        except Exception as e:
            Console.log ("Could not create sign in footage...", str (e))
        

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
    def fetch_footages_for_super_admins(**kwargs):
        """
        Fetches list of recent footages for super admins.
        And these will be footages from other super admins
        """
        context: Context = kwargs.get("context")
        user = UserProfile.objects.get(email=context.user_email)
        return (
            Footage.objects.filter(
                portal=FootageConstants.on_admin_portal(), by_super_admin=True
            ).distinct()
            # .exclude(actor=user)
            .order_by("-id")[:LIMIT]
        )

    @staticmethod
    def fetch_footages_for_community_admins(**kwargs):
        """
        Fetch list of recent footages that are related to 
        all the communities a user is in charge of.  
        And that included footages of super admins making changes to content 
        related to cadmins communities
        """
        try:
            
            context: Context = kwargs.get("context", None)
            # email = kwargs.get("email", None)
            user = get_user_from_context(context)
            # actors = []
            if not user:
                return []
            communities = []
            for g in user.communityadmingroup_set.all(): 
                # members = [m.id for m in g.members.all()]
                # actors = actors + members
                communities.append(g.community.id)
            return Footage.objects.filter(
                portal=FootageConstants.on_admin_portal(),
                communities__id__in = communities
            ).exclude(actor__is_super_admin=True).distinct().order_by("-id")[:LIMIT]
        except Exception as e:
            Console.log("Could not fetch footages for community admin", e)

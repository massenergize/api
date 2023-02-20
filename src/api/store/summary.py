import datetime
from _main_.utils.footage.FootageConstants import FootageConstants
from database.models import (
    Community,
    CommunityMember,
    Action,
    Footage,
    Message,
    Testimonial,
    Event,
    Team,
    UserActionRel,
    UserProfile,
)
from _main_.utils.massenergize_errors import (
    MassEnergizeAPIError,
    InvalidResourceError,
    ServerError,
    CustomMassenergizeError,
)
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from django.db.models.query import QuerySet
from sentry_sdk import capture_message
from typing import Tuple
from django.db.models import Q
import pytz

LAST_VISIT = "last-visit"
LAST_WEEK = "last-week"
LAST_MONTH = "last-month"
LAST_YEAR = "last-year"


class SummaryStore:
    def __init__(self):
        self.name = "Summary Store/DB"

    def fetch_user_engagements_for_admins(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        # values = last-visit, last-week, last-month, custom
        time_range = args.get("time_range", None) 
        start_time = args.get("start_time", None)
        end_time = args.get("end_time", None)
        communities = args.get("communities", [])
        today = datetime.datetime.utcnow()
        email = args.get("email") or context.user_email
        is_community_admin = (
            args.get("is_community_admin", False) or context.user_is_community_admin
        )
        is_super_admin = is_community_admin == "False" or  context.user_is_super_admin
       
        today = pytz.utc.localize(today)
        if not time_range:
            return {},CustomMassenergizeError("Please include an appropriate date/time range")
        user = UserProfile.objects.filter(email=email).first()

        wants_all_communities = "all" in communities
        if not communities or wants_all_communities:
            groups = user.communityadmingroup_set.all()
            communities = [ag.community.id for ag in groups]

        # ------------------------------------------------------
        if time_range == LAST_VISIT:
            start_time = self.get_admins_last_visit(email=email)
            end_time = today

        elif time_range == LAST_WEEK:
            start_time = today - datetime.timedelta(days=7)
            end_time = today

        elif time_range == LAST_MONTH:
            start_time = today - datetime.timedelta(days=31)
            end_time = today
        elif time_range == LAST_YEAR:
            start_time = today - datetime.timedelta(days=365)
            end_time = today
        else: # dealing with custom date and time
            _format = "%Y-%m-%dT%H:%M:%SZ"
            start_time = datetime.datetime.strptime(start_time,_format)
            end_time = datetime.datetime.strptime(end_time,_format)
            start_time = pytz.utc.localize(start_time)
            end_time = pytz.utc.localize(end_time)  
            
        # ------------------------------------------------------

        if is_community_admin or (is_super_admin and not wants_all_communities):
            sign_in_query = Q(
                communities__in=communities,
                portal=FootageConstants.on_user_portal(),
                activity_type=FootageConstants.sign_in(),
                created_at__range=[start_time,end_time],
            )
            todo_query = Q(
                status="TODO",
                action__community__in=communities,
                updated_at__range=[start_time,end_time],
                is_deleted=False,
            )
            done_query = Q(
                status="DONE",
                action__community__in=communities,
                updated_at__range=[start_time,end_time],
                is_deleted=False,
            )
        else: # Super Admins
            sign_in_query = Q(
                portal=FootageConstants.on_user_portal(),
                activity_type=FootageConstants.sign_in(),
                created_at__range=[start_time,end_time],
            )
            todo_query = Q(
                status="TODO",
                updated_at__range=[start_time,end_time],
                is_deleted=False,
            )
            done_query = Q(
                status="DONE",
                updated_at__range=[start_time,end_time],
                is_deleted=False,
            )

        user_sign_ins = Footage.objects.values_list("actor__email", flat=True).filter(
            sign_in_query
        )

        todo_interactions = UserActionRel.objects.values_list(
            "action__id", flat=True
        ).filter(todo_query)
        done_interactions = UserActionRel.objects.values_list(
            "action__id", flat=True
        ).filter(done_query)
    
        return {
            "done_interactions": done_interactions,
            "todo_interactions": todo_interactions,
            "user_sign_ins": user_sign_ins,
        }, None

    def next_steps_for_admins(
        self, context: Context, args
    ) -> Tuple[tuple, MassEnergizeAPIError]:
        is_community_admin = (
            args.get("is_community_admin", False) or context.user_is_community_admin
        )

        # try:
        content = {}
        err = None
        if is_community_admin:
            content, err = self.next_steps_for_community_admins(context, args)
        else:
            content, err = self.next_steps_for_super_admins(context, args)

        return content, err

    def get_admins_last_visit(self,
        **kwargs,
    ):  # Use this fxn in nextSteps for sadmin, and cadmin (instead of manual implementation) before PR(BPR)
        user = kwargs.get("user")
        email = kwargs.get("email")
        today = datetime.date.today()

        if not user:
            user = UserProfile.objects.filter(email=email).first()
        # get the footage item for admin's last visit that isnt today
        last_visit = (
            Footage.objects.filter(
                created_at__lt=today,
                actor=user,
                activity_type=FootageConstants.sign_in(),
            )
            .order_by("-created_at")
            .first()
        )
        return last_visit.created_at

    def next_steps_for_community_admins(self, context: Context, args):

        email = context.user_email or args.get(
            "email"
        )  # Just for Postman Testing, remove before PR(BPR)
        current_user = UserProfile.objects.filter(email=email).first()

        if not current_user:
            return {}, CustomMassenergizeError(
                "Sorry, could not find information of currently authenticated admin"
            )

        groups = current_user.communityadmingroup_set.all()
        communities = [ag.community.id for ag in groups]

        testimonials = Testimonial.objects.values_list("id", flat=True).filter(
            community__in=communities, is_approved=False, is_deleted=False
        )
        team_messages = Message.objects.values_list("id", flat=True).filter(
            have_forwarded=False,
            community__in=communities,
            is_team_admin_message=True,
            is_deleted=False,
        )

        messages = Message.objects.values_list("id", flat=True).filter(
            community__in=communities,
            have_replied=False,
            is_team_admin_message=False,
            is_deleted=False,
        )
        users = []
        teams = Team.objects.values_list("id", flat=True).filter(
            primary_community__in=communities, is_published=False, is_deleted=False
        )

        today = datetime.date.today()

        # get the footage item for admin's last visit that isnt today
        last_visit = (
            Footage.objects.filter(
                created_at__lt=today,
                actor=current_user,
                activity_type=FootageConstants.sign_in(),
            )
            .order_by("-created_at")
            .first()
        )
        if last_visit:
            users = UserProfile.objects.values_list("email", flat=True).filter(
                created_at__gt=last_visit.created_at,
                communities__in=communities,
                is_deleted=False,
            )
        return {
            "users": users,
            "testimonials": testimonials,
            "messages": messages,
            "team_messages": team_messages,
            "teams": teams,
            "last_visit": last_visit,
        }, None

    def next_steps_for_super_admins(self, context: Context, args):
        email = context.user_email or args.get(
            "email"
        )  # Just for Postman Testing, remove before PR(BPR)
        current_user = UserProfile.objects.filter(email=email).first()
        if not current_user:
            return {}, CustomMassenergizeError(
                "Sorry, could not find information of currently authenticated admin"
            )

        testimonials = Testimonial.objects.values_list("id", flat=True).filter(
            is_approved=False, is_deleted=False
        )

        team_messages = Message.objects.values_list("id", flat=True).filter(
            have_forwarded=False, is_team_admin_message=True, is_deleted=False
        )
        messages = Message.objects.values_list("id", flat=True).filter(
            have_replied=False, is_team_admin_message=False, is_deleted=False
        )
        users = []
        teams = Team.objects.values_list("id", flat=True).filter(
            is_published=False, is_deleted=False
        )

        today = datetime.date.today()

        # get the footage item for admin's last visit that isnt today
        last_visit = (
            Footage.objects.filter(
                created_at__lt=today,
                actor=current_user,
                activity_type=FootageConstants.sign_in(),
            )
            .order_by("-created_at")
            .first()
        )
       
        if last_visit:
            users = UserProfile.objects.values_list("id", flat=True).filter(
                created_at__gt=today, is_deleted=False
            )
      

        return {
            "users": users,
            "testimonials": testimonials,
            "messages": messages,
            "team_messages": team_messages,
            "teams": teams,
            "last_visit": last_visit,
        }, None

    def _summarize(self, name, value):
        return {"title": name, "value": value, "link": f"/admin/read/{name.lower()}"}

    def summary_for_community_admin(
        self, context: Context, community_id
    ) -> Tuple[list, MassEnergizeAPIError]:
        try:
            if context.user_is_super_admin:
                return self.summary_for_super_admin(context)

            user = UserProfile.objects.get(pk=context.user_id)
            admin_groups = user.communityadmingroup_set.all()
            communities = [ag.community for ag in admin_groups]
            comm_ids = [ag.community.id for ag in admin_groups]

            action_count = Action.objects.filter(community__id__in=comm_ids).count()
            communities_count = len(comm_ids)
            upcoming_events = Event.objects.filter(community__id__in=comm_ids).count()
            teams_count = Team.objects.filter(communities__id__in=comm_ids).count()
            testimonials_count = Testimonial.objects.filter(
                community__id__in=comm_ids
            ).count()
            users_count = (
                CommunityMember.objects.filter(community__id__in=comm_ids)
                .values("user")
                .distinct()
                .count()
            )

            summary = [
                self._summarize("Actions", action_count),
                self._summarize("Communities", communities_count),
                self._summarize("Events", upcoming_events),
                self._summarize("Teams", teams_count),
                self._summarize("Users", users_count),
                self._summarize("Testimonials", testimonials_count),
            ]
            return summary, None
        except Exception as e:
            capture_message(str(e), level="error")
            return {}, CustomMassenergizeError(e)

    def summary_for_super_admin(self, context: Context):
        try:
            action_count = Action.objects.filter(is_deleted=False).count()
            communities_count = Community.objects.filter(is_deleted=False).count()
            upcoming_events = Event.objects.filter(is_deleted=False).count()
            teams_count = Team.objects.filter(is_deleted=False).count()
            testimonials_count = Testimonial.objects.filter(is_deleted=False).count()
            users_count = UserProfile.objects.filter(
                is_deleted=False, accepts_terms_and_conditions=True
            ).count()
            summary = [
                self._summarize("Actions", action_count),
                self._summarize("Communities", communities_count),
                self._summarize("Events", upcoming_events),
                self._summarize("Teams", teams_count),
                self._summarize("Users", users_count),
                self._summarize("Testimonials", testimonials_count),
            ]
            return summary, None

        except Exception as e:
            capture_message(str(e), level="error")
            return None, CustomMassenergizeError(e)

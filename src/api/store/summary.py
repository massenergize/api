import datetime

from django.utils import timezone

from _main_.utils.common import custom_timezone_info, parse_datetime_to_aware
from _main_.utils.footage.FootageConstants import FootageConstants
from api.store.common import make_time_range_from_text
from api.store.utils import get_user_from_context
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
    CustomMassenergizeError,
)
from _main_.utils.context import Context
from _main_.utils.massenergize_logger import log
from typing import Tuple
from django.db.models import Q

CUSTOM = "custom"


class SummaryStore:
    def __init__(self):
        self.name = "Summary Store/DB"

    def fetch_user_engagements_for_admins(
        self, context: Context, args
    ) -> Tuple[dict, MassEnergizeAPIError]:
        # values = last-visit, last-week, last-month, custom
        time_range = args.get("time_range", None)
        start_time = args.get("start_time", None)
        end_time = args.get("end_time", None)
        communities = args.get("communities", [])
        today = timezone.now()
        email = context.user_email
        is_community_admin = (
             context.user_is_community_admin
        )
        is_super_admin = context.user_is_super_admin
        
        today =  today.replace(tzinfo=custom_timezone_info())
        
        if not time_range:
            return {}, CustomMassenergizeError(
                "Please include an appropriate date/time range"
            )
        user = UserProfile.objects.filter(email=email).first()

        wants_all_communities = "all" in communities
        if not communities or wants_all_communities:
            groups = user.communityadmingroup_set.all()
            communities = [ag.community.id for ag in groups]

        # ------------------------------------------------------
        if time_range == CUSTOM: 
            _format = "%Y-%m-%dT%H:%M:%SZ"
            start_time = datetime.datetime.strptime(start_time, _format)
            end_time = datetime.datetime.strptime(end_time, _format)
            start_time = start_time.replace(tzinfo=custom_timezone_info())
            end_time = end_time.replace(tzinfo=custom_timezone_info())
        else:
            [start_time, end_time] = make_time_range_from_text(time_range)
        # ------------------------------------------------------
        
        start_time = timezone.make_aware(start_time)
        end_time = timezone.make_aware(end_time)
        
        if is_community_admin or (is_super_admin and not wants_all_communities):
            testimonial_query = Q(
                is_deleted=False,
                updated_at__range=[start_time, end_time],
                community__in =communities
            )
            sign_in_query = Q(
                communities__in=communities,
                portal=FootageConstants.on_user_portal(),
                activity_type=FootageConstants.sign_in(),
                created_at__range=[start_time, end_time],
            )
            todo_query = Q(
                status="TODO",
                action__community__in=communities,
                updated_at__range=[start_time, end_time],
                is_deleted=False,
            )
            done_query = Q(
                status="DONE",
                action__community__in=communities,
                updated_at__range=[start_time, end_time],
                is_deleted=False,
            )
        else:  # Super Admins
            sign_in_query = Q(
                portal=FootageConstants.on_user_portal(),
                activity_type=FootageConstants.sign_in(),
                created_at__range=[start_time, end_time],
            )
            todo_query = Q(
                status="TODO",
                updated_at__range=[start_time, end_time],
                is_deleted=False,
            )
            done_query = Q(
                status="DONE",
                updated_at__range=[start_time, end_time],
                is_deleted=False,
            )
            testimonial_query = Q(
                is_deleted=False,
                updated_at__range=[start_time, end_time]
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
        testimonials = Testimonial.objects.values_list(
            "id", flat=True
        ).filter(testimonial_query)

        return {
            "done_interactions": done_interactions,
            "todo_interactions": todo_interactions,
            "user_sign_ins": user_sign_ins,
            "testimonials":testimonials
        }, None

    def next_steps_for_admins(
        self, context: Context, args
    ) -> Tuple[tuple, MassEnergizeAPIError]:

        # try:
        content = {}
        err = None

        if context.user_is_super_admin:
              content, err = self.next_steps_for_super_admins(context, args)
        elif context.user_is_community_admin:
            content, err = self.next_steps_for_community_admins(context, args)
        
        return content, err

    def get_admins_last_visit(
        self,
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
        current_user = get_user_from_context(context)

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

        today = parse_datetime_to_aware()

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
        current_user = get_user_from_context(context)
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

        today = parse_datetime_to_aware()

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

            user = get_user_from_context(context)
            if not user:
                return {}, CustomMassenergizeError(
                    "Sorry, could not find information of currently authenticated admin"
                )
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
            log.exception(e)
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
            log.exception(e)
            return None, CustomMassenergizeError(e)

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


class SummaryStore:
    def __init__(self):
        self.name = "Summary Store/DB"

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
        print("Found Last Visit", last_visit)  # REMOVE BEFORE PR(BPR)
        if last_visit:
            users = UserProfile.objects.values_list("id", flat=True).filter(
                created_at__gt=last_visit.created_at, communities__in=communities, is_deleted=False
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
        print(
            "Found Last Visit", last_visit, last_visit.created_at
        )  # REMOVE BEFORE PR(BPR)
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

from database.models import Community, CommunityMember, Action, Testimonial, Event, Team, UserProfile
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from django.db.models.query import QuerySet
from sentry_sdk import capture_message
from typing import Tuple

class SummaryStore:
  def __init__(self):
    self.name = "Summary Store/DB"


  def next_steps_for_admins(self, context: Context, community_id) -> Tuple[dict, MassEnergizeAPIError]:
    try : 
      content = {}
      if context.user_is_admin: 
        content = self.next_steps_for_community_admins(context)
      else: 
        content = self.next_steps_for_super_admins() 
      return content, None
    except Exception as e: 
      capture_message(str(e), level="error")
      return {}, CustomMassenergizeError(e)


  def next_steps_for_community_admins(context : Context): 
    """
      Get all the communities that a cadmin manages 
      Testimonials 
      * Look for testimonials that belong to any of the communities that are not approved 

      Messages 
      * Look for messages that have not been replied to that belong to any of the communities

      Teams 
      * Look for teams that have not been replied to that belong to any of the communities

    """


    pass 

  def next_steps_for_super_admins(context: Context): 
    pass

  def _summarize(self, name, value):
    return {
      "title": name,
      "value": value,
      "link": f'/admin/read/{name.lower()}' 
    }
  

  def summary_for_community_admin(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
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
      testimonials_count = Testimonial.objects.filter(community__id__in=comm_ids).count()
      users_count = CommunityMember.objects.filter(community__id__in=comm_ids).values('user').distinct().count()


      summary = [
        self._summarize("Actions", action_count),
        self._summarize("Communities", communities_count),
        self._summarize("Events", upcoming_events),
        self._summarize("Teams", teams_count),
        self._summarize("Users", users_count),
        self._summarize("Testimonials", testimonials_count)
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
      users_count = UserProfile.objects.filter(is_deleted=False, accepts_terms_and_conditions=True).count()
      summary = [
        self._summarize("Actions", action_count),
        self._summarize("Communities", communities_count),
        self._summarize("Events", upcoming_events),
        self._summarize("Teams", teams_count),
        self._summarize("Users", users_count),
        self._summarize("Testimonials", testimonials_count)
      ]
      return summary, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

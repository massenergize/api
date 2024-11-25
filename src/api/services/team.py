from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from api.store.team import TeamStore
from api.store.message import MessageStore
from api.utils.filter_functions import sort_items
from database.models import TeamMember
from _main_.utils.context import Context
from _main_.utils.constants import ADMIN_URL_ROOT
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL, IS_PROD, IS_CANARY
from .utils import send_slack_message
from _main_.utils.massenergize_logger import log
from typing import Tuple

class TeamService:
  """
  Service Layer for all the teams
  """

  def __init__(self):
    self.store =  TeamStore()
    self.message_store = MessageStore()

  def get_team_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.get_team_info(context, args)
    if err:
      return None, err
    return serialize(team, full=True), None

  def list_teams(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    team, err = self.store.list_teams(context, args)
    if err:
      return None, err
    return serialize_all(team), None

  def team_stats(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    stats, err = self.store.team_stats(context, args)
    if err:
      return None, err
    return stats, None


  def create_team(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.create_team(context, args)
    if err:
      return None, err

    # within store.create_team, an e-mail was sent to the community admin
    # 
    # TODO: the following functionality is needed
    # message to the effect that you have been named as a team admin
    #message_info, err = self.message_store.message_team_admin(context, args)
    #
    # message to community admins that a team was created (needs to be recorded in admin portal because the e-mail may be lost)
    #message_info, err = self.message_store.message_admin(context, args)

    return serialize(team), None


  def update_team(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.update_team(context, args)
    if err:
      return None, err
    return serialize(team), None

  def delete_team(self, args,context) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.delete_team(args,context)
    if err:
      return None, err
    return team.info(), None

  def join_team(self,context, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.join_team(context,args)
    if err:
      return None, err
    return serialize(team), None

  def leave_team(self,context, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.leave_team(context,args)
    if err:
      return None, err
    return serialize(team), None

  def add_member(self, args,context) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.add_team_member(args,context)
    if err:
      return None, err
    return serialize(team), None

  def remove_team_member(self,args,context) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.remove_team_member(args,context)
    if err:
      return None, err
    return serialize(team), None

  def members(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    members, err = self.store.members(context, args)
    if err:
      return None, err
    return paginate(members, context.get_pagination_data()), None

  def members_preferred_names(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    preferred_names, err = self.store.members_preferred_names(context, args)
    if err:
      return None, err
    return preferred_names, None

  def message_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      message, err = self.message_store.message_team_admin(context, args)
      if err:
        return None, err

      # Previously didn't send emails for these messages, which would just show up in the admin site
      # Now email team leaders directly. Message to Cadmin via Slack
      # Message stays in the board of messages in admin interface as before
      # And add that team leaders will directly get messages to them and they are responsible for responding to the welcome team leader email
      team = message.team
      community = team.primary_community
      admin_email = community.owner_email
      admin_name = community.owner_name

      subject = 'A message was sent to the Team Admin for ' + team.name + ' in ' + community.name
      team_members = TeamMember.objects.filter(team=team)
      for member in team_members:
        if member.is_admin:
          user = member.user
          first_name = user.full_name.split(" ")[0]
          if not first_name or first_name == "":
            first_name = user.full_name

          content_variables = {
              'name': first_name,
              "community_name": community.name,
              "community_admin_email": admin_email,
              "community_admin_name": admin_name,
              "team_name": team.name,
              "from_name": message.user_name,
              "email": message.email,
              "subject": message.title,
              "message_body": message.body,
          }
          send_massenergize_rich_email(
            subject, user.email, 'contact_team_admin_email.html', content_variables, None)

      if IS_PROD or IS_CANARY:
        send_slack_message(
          SLACK_SUPER_ADMINS_WEBHOOK_URL, {
          "content": "Message to Team Admin of "+team.name,
          "from_name": message.user_name,
          "email": message.email,
          "subject": message.title,
          "message": message.body,
          "url": f"{ADMIN_URL_ROOT}/admin/edit/{message.id}/message",
          "community": community.name
      }) 

      return serialize(message), None

    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_teams_for_community_admin(self, context:Context, args) -> Tuple[list, MassEnergizeAPIError]:
    teams, err = self.store.list_teams_for_community_admin(context, args)
    if err:
      return None, err
    sorted = sort_items(teams, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_teams_for_super_admin(self, context: Context,args) -> Tuple[list, MassEnergizeAPIError]:
    teams, err = self.store.list_teams_for_super_admin(context,args)
    if err:
      return None, err
    sorted = sort_items(teams, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_actions_completed(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    completed_actions_list, err = self.store.list_actions_completed(context, args)
    if err:
      return None, err
    return paginate(completed_actions_list, context.get_pagination_data()), None



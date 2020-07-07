from _main_.utils.massenergize_errors import NotAuthorizedError, MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from database.models import UserProfile, CommunityMember, Action, Team, UserActionRel, Testimonial, TeamMember
from django.db.models import Q

import traceback
import time

# TODO: proper logging/error handling to match Sam's work
# TODO: actions queries seem to be returning extra actions with "copy" at the end of their title
# TODO: verify that the correct users are being fetched for _community_users_download

class DownloadStore:

  def __init__(self):
    self.name = "Download Store/DB"


  def _get_user_actions_cells(self, user, actions):
    cells = []
    # create collections with constant-time lookup. VERY much worth the up-front compute.
    user_testimonial_action_ids = set([testimonial.action.id if testimonial.action else None
                                for testimonial in Testimonial.objects.filter(user=user)])
    action_id_to_action_rel = {user_action_rel.action.id: user_action_rel
                                for user_action_rel in UserActionRel.objects.filter(user=user)}

    for action in actions:
      user_action_status = ''
      if action.id in user_testimonial_action_ids:
        user_action_status = 'testimonial'
      else:
        user_action_rel = action_id_to_action_rel.get(action.id, None)
        if user_action_rel:
          user_action_status = user_action_rel.status
      cells.append(user_action_status)
    return cells


  def _get_user_teams_cells(self, user, teams):
    cells = []
    user_team_members = TeamMember.objects.filter(user=user).select_related('team')

    for team in teams:
      user_team_status = ''
      team_member = user_team_members.filter(team=team).first()
      if team_member:
        if team_member.is_admin:
          user_team_status = 'admin'
        else:
          user_team_status = 'member'
      cells.append(user_team_status)
    return cells


  def _all_users_download(self):

    users = UserProfile.objects.filter(is_deleted=False)

    actions = Action.objects.filter(is_deleted=False)
    teams = Team.objects.filter(is_deleted=False)

    columns = ['primary community',
                'secondary community',
                'full_name',
                'preferred_name',
                'email',
                'role'] \
                + [action.title for action in actions] \
                + [team.name for team in teams]

    data = []

    for user in users:

      user_communities = user.communities.all()

      if len(user_communities) > 1:
        primary_community, secondary_community = user_communities[0].name, user_communities[1].name
      elif len(user_communities) == 1:
        primary_community, secondary_community = user_communities[0].name, ''
      else:
        primary_community, secondary_community = '', ''

      row = [primary_community,
            secondary_community,
            user.preferred_name if user.preferred_name else '',
            user.full_name,
            user.email,
            'super admin' if user.is_super_admin else
                'community admin' if user.is_community_admin else
                'vendor' if user.is_vendor else
                'community member']

      row += self._get_user_actions_cells(user, actions)
      row += self._get_user_teams_cells(user, teams)

      data.append(row)

    data = sorted(data, key=lambda row : row[0]) # sort by community
    data.insert(0, columns) # insert the column names

    return data


  def _community_users_download(self, community_id):
    users = [cm.user for cm in CommunityMember.objects.filter(community__id=community_id, is_deleted=False).select_related('user')]

    actions = Action.objects.filter(Q(community__id=community_id) | Q(is_global=True)) \
                                                      .filter(is_deleted=False)
    teams = Team.objects.filter(community__id=community_id, is_deleted=False)

    columns = ['full_name',
                'preferred_name',
                'email',
                'role'] \
                + [action.title for action in actions] \
                + [team.name for team in teams]

    data = [columns]

    for user in users:

      row = [user.full_name,
            user.preferred_name if user.preferred_name else '',
            user.email,
            'super admin' if user.is_super_admin else
                'community admin' if user.is_community_admin else
                'vendor' if user.is_vendor else
                'community member']

      row += self._get_user_actions_cells(user, actions)
      row += self._get_user_teams_cells(user, teams)

      data.append(row)

    return data


  def _all_actions_download(self):
    actions = Action.objects.filter(is_deleted=False) \
              .select_related('calculator_action', 'community').prefetch_related('tags')

    columns = ['community',
              'title',
              'average_carbon_points',
              'category',
              'cost',
              'impact']

    data = []

    for action in actions:

      if action.community:
        community = action.community.name if not action.is_global else 'global'
      average_carbon_points = action.calculator_action.average_points \
                          if action.calculator_action else action.average_carbon_score
      category = action.tags.filter(tag_collection__name='Category').first()
      cost = action.tags.filter(tag_collection__name='Cost').first()
      impact = action.tags.filter(tag_collection__name='Impact').first()

      data.append([community if community else '',
                  action.title,
                  average_carbon_points,
                  category.name if category else '',
                  cost.name if cost else '',
                  impact.name if impact else ''])

    data = sorted(data, key=lambda row : row[0]) # sort by community
    data.insert(0, columns) # insert the column names

    return data


  def _community_actions_download(self, community_id):
    actions = Action.objects.filter(Q(community__id=community_id) | Q(is_global=True)) \
      .filter(is_deleted=False).select_related('calculator_action').prefetch_related('tags')

    columns = ['title',
              'average_carbon_points',
              'category',
              'cost',
              'impact']
    
    data = [columns]

    for action in actions:

      average_carbon_points = action.calculator_action.average_points \
                          if action.calculator_action else action.average_carbon_score
      category = action.tags.filter(tag_collection__name='Category').first()
      cost = action.tags.filter(tag_collection__name='Cost').first()
      impact = action.tags.filter(tag_collection__name='Impact').first()

      data.append([action.title,
                  average_carbon_points,
                  category.name if category else '',
                  cost.name if cost else '',
                  impact.name if impact else ''])

    return data


  def users_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        if community_id:
          return self._community_users_download(community_id), None
        else:
          return self._all_users_download(), None
      elif context.user_is_community_admin and community_id:
        return self._community_users_download(community_id), None
      else:
        return None, NotAuthorizedError()
    except Exception as e:
      print(traceback.format_exc())
      return None, CustomMassenergizeError(e)


  def actions_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
          if community_id:
            return self._community_actions_download(community_id), None
          else:
            return self._all_actions_download(), None
      elif context.user_is_community_admin and community_id:
          return self._community_actions_download(community_id), None
      else:
          return None, NotAuthorizedError()
    except Exception as e:
      print(traceback.format_exc())
      return None, CustomMassenergizeError(e)

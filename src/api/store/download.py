from _main_.utils.massenergize_errors import NotAuthorizedError, MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from database.models import UserProfile, CommunityMember, Action, Team, \
UserActionRel, Testimonial, TeamMember, Community, Subscriber
from django.db.models import Q
from sentry_sdk import capture_message

import traceback
# TODO: add CAdmin and Super Admin route for teams download
# TODO: add Super Admin-only route for communities download

class DownloadStore:

  def __init__(self):
    self.name = "Download Store/DB"

    self.action_info_columns = ['title', 'category', 'done_count', 'average_carbon_points', 'testimonials_count', 'impact', 'cost', 'is_global']

    self.user_info_columns = ['name', 'preferred_name', 'role', 'email', 'testimonials_count']


  def _get_cells_from_dict(self, columns, data):
    cells = ['' for _ in range(len(columns))]
    for key, value in data.items():
      if not value:
        continue
      cells[columns.index(key)] = value
    return cells


  def _get_user_info_cells(self, user):
    user_cells = {}
  
    if (isinstance(user, Subscriber)):
        user_cells = {'name': user.name, 'email': user.email, 'role': 'subscriber'}
    else:
        user_testimonials = Testimonial.objects.filter(is_deleted=False, user=user)
        testimonials_count = user_testimonials.count() if user_testimonials else '0'

        user_cells = {'name': user.full_name,
                      'preferred_name': user.preferred_name,
                      'email': user.email,
                      'role' : 'super admin' if user.is_super_admin else
                          'community admin' if user.is_community_admin else
                          'vendor' if user.is_vendor else
                          'community member',
                      'testimonials_count': testimonials_count}

    return self._get_cells_from_dict(self.user_info_columns, user_cells)


  def _get_user_actions_cells(self, user, actions):
    if (isinstance(user, Subscriber)):
      return ['' for _ in range(len(actions))]

    cells = []
    # create collections with constant-time lookup. VERY much worth the up-front compute.
    user_testimonial_action_ids = {testimonial.action.id if testimonial.action else None
                                for testimonial in Testimonial.objects.filter(is_deleted=False,user=user)}
    action_id_to_action_rel = {user_action_rel.action.id: user_action_rel
                                for user_action_rel in UserActionRel.objects.filter(is_deleted=False,user=user)}

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
    if (isinstance(user, Subscriber)):
      return ['' for _ in range(len(teams))]

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


  def _get_action_info_cells(self, action):
    average_carbon_points = action.calculator_action.average_points \
                          if action.calculator_action else action.average_carbon_score

    category_obj = action.tags.filter(tag_collection__name='Category').first()
    category = category_obj.name if category_obj else None
    cost_obj = action.tags.filter(tag_collection__name='Cost').first()
    cost = cost_obj.name if cost_obj else None
    impact_obj = action.tags.filter(tag_collection__name='Impact').first()
    impact = impact_obj.name if impact_obj else None

    done_actions = UserActionRel.objects.filter(is_deleted=False, action=action, status="DONE")
    done_count = done_actions.count() if done_actions else '0'

    action_testimonials = Testimonial.objects.filter(is_deleted=False, action=action)
    testimonials_count = action_testimonials.count() if action_testimonials else '0'
    
    action_cells = {
      'title': action.title, 'average_carbon_points': average_carbon_points,
      'category': category,  'impact': impact,
      'cost': cost, 'is_global': action.is_global,
      'testimonials_count': testimonials_count, 'done_count': done_count
    }
    
    return self._get_cells_from_dict(self.action_info_columns, action_cells)


  def _all_users_download(self):
    users = list(UserProfile.objects.filter(is_deleted=False)) \
        + list(Subscriber.objects.filter(is_deleted=False))
    actions = Action.objects.filter(is_deleted=False)
    teams = Team.objects.filter(is_deleted=False)

    columns = ['primary community',
                'secondary community' ] \
                + self.user_info_columns \
                + [action.title for action in actions] \
                + [team.name for team in teams]
    sub_columns = ['', ''] + ['' for _ in range(len(self.user_info_columns))] \
            + ["ACTION" for _ in range(len(actions))] + ["TEAM" for _ in range(len(teams))]
    data = []

    for user in users:
      if (isinstance(user, Subscriber)):
        if user.community:
          primary_community, secondary_community = user.community.name, ''
        else:
          primary_community, secondary_community = '', ''
      else:
        user_communities = user.communities.all()
        if len(user_communities) > 1:
          primary_community, secondary_community = user_communities[0].name, user_communities[1].name
        elif len(user_communities) == 1:
          primary_community, secondary_community = user_communities[0].name, ''
        else:
          primary_community, secondary_community = '', ''

      row = [primary_community, secondary_community] \
      + self._get_user_info_cells(user) \
      + self._get_user_actions_cells(user, actions) \
      + self._get_user_teams_cells(user, teams)

      data.append(row)

    # sort by community
    data = sorted(data, key=lambda row: row[0])
    # insert the columns
    data.insert(0, sub_columns)
    data.insert(0, columns) 

    return data


  def _community_users_download(self, community_id):
    users = [cm.user for cm in CommunityMember.objects.filter(community__id=community_id, \
            is_deleted=False, user__is_deleted=False).select_related('user')] \
              + list(Subscriber.objects.filter(community__id=community_id, is_deleted=False))
    actions = Action.objects.filter(Q(community__id=community_id) | Q(is_global=True)) \
                                                      .filter(is_deleted=False)
    teams = Team.objects.filter(community__id=community_id, is_deleted=False)

    columns = self.user_info_columns \
                + [action.title for action in actions] \
                + [team.name for team in teams]
    sub_columns = ['' for _ in range(len(self.user_info_columns))] \
            + ["ACTION" for _ in range(len(actions))] + ["TEAM" for _ in range(len(teams))]
    data = [columns, sub_columns]

    for user in users:

      row = self._get_user_info_cells(user) \
      + self._get_user_actions_cells(user, actions) \
      + self._get_user_teams_cells(user, teams)

      data.append(row)

    return data


  def _all_actions_download(self):
    actions = Action.objects.select_related('calculator_action', 'community') \
            .prefetch_related('tags').filter(is_deleted=False)

    columns = ['community'] + self.action_info_columns
    data = []

    for action in actions:

      if action.community:
        community = action.community.name

      data.append([community if community else ''] \
        + self._get_action_info_cells(action))

    data = sorted(data, key=lambda row : row[0]) # sort by community
    data.insert(0, columns) # insert the column names

    return data


  def _community_actions_download(self, community_id):
    actions = Action.objects.filter(Q(community__id=community_id) | Q(is_global=True)) \
      .select_related('calculator_action').prefetch_related('tags').filter(is_deleted=False)

    columns = self.action_info_columns
    data = [columns]

    for action in actions:
      data.append(self._get_action_info_cells(action))

    return data


  def users_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if community_id:
        community_name = Community.objects.get(id=community_id).name
      if context.user_is_super_admin:
        if community_id:
          return (self._community_users_download(community_id), community_name), None
        else:
          return (self._all_users_download(), None), None
      elif context.user_is_community_admin and community_id:
        return (self._community_users_download(community_id), community_name), None
      else:
        return None, NotAuthorizedError()
    except Exception as e:
      traceback.print_exc()
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def actions_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if community_id:
        community_name = Community.objects.get(id=community_id).name
      if context.user_is_super_admin:
          if community_id:
            return (self._community_actions_download(community_id), community_name), None
          else:
            return (self._all_actions_download(), None), None
      elif context.user_is_community_admin and community_id:
          return (self._community_actions_download(community_id), community_name), None
      else:
          return None, NotAuthorizedError()
    except Exception as e:
      traceback.print_exc()
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

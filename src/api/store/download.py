from _main_.utils.massenergize_errors import NotAuthorizedError, MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from database.models import UserProfile, CommunityMember, Action, Team, \
  UserActionRel, Testimonial, TeamMember, Community, Subscriber, Event, RealEstateUnit, \
  Data, TagCollection
from api.store.team import get_team_users
from api.store.tag_collection import TagCollectionStore
from django.db.models import Q
from sentry_sdk import capture_message

class DownloadStore:

  def __init__(self):
    self.name = "Download Store/DB"
    tcs = TagCollectionStore()

    # for testing with empty database, create tag collection
    tag_collections = TagCollection.objects.filter(name='Category')
    if tag_collections.count()<1:
      tagdata = {'name':'Category', 'tags':'Home Energy,Solar,Transportation,Waste & Recycling,Food,Activism & Education,Land, Soil & Water'}
      tcs.create_tag_collection(tagdata)

    self.action_categories = TagCollection.objects.get(name="Category").tag_set.all()

    self.action_info_columns = ['title', 'category', 'carbon_calculator_action', 'done_count', 'yearly_lbs_carbon',
    'total_yearly_lbs_carbon', 'testimonials_count', 'impact', 'cost', 'is_global']

    self.user_info_columns = ['name', 'preferred_name', 'role', 'email', 'created', 'testimonials_count']
    
    self.team_info_columns = ['name', 'members_count', 'parent', 'total_yearly_lbs_carbon', 'testimonials_count']

    self.community_info_columns = ['name', 'location', 'members_count', 'households_count', 'total_households_count', 'teams_count', 'total_yearly_lbs_carbon', 'total_actions_done','actions_done', 'actions_per_member', 'testimonials_count',
    'events_count', 'most_done_action', 'second_most_done_action', 'highest_impact_action', 'second_highest_impact_action'] \
    + [category.name + " (reported)" for category in self.action_categories]        #  + ['actions_done_with_reported', 'households_count_with_reported']


  def _get_cells_from_dict(self, columns, data):
    cells = ['' for _ in range(len(columns))]

    for key, value in data.items():
      if type(value) == int or type(value) == float:
        value = str(value)
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
                      'created': user.created_at.strftime("%Y-%m-%d"),
                      'testimonials_count': testimonials_count}

    return self._get_cells_from_dict(self.user_info_columns, user_cells)

  def _get_user_actions_cells(self, user, actions):
    if (isinstance(user, Subscriber)):
      return ['' for _ in range(len(actions))]

    cells = []
    # create collections with constant-time lookup. VERY much worth the up-front compute.
    user_testimonial_action_ids = {testimonial.action.id if testimonial.action else None
                                for testimonial in Testimonial.objects.filter(is_deleted=False, user=user).select_related('action')}
    action_id_to_action_rel = {user_action_rel.action.id: user_action_rel
                                for user_action_rel in UserActionRel.objects.filter(is_deleted=False, user=user).select_related('action')}

    for action in actions:
      user_action_status = ''
      if action.id in user_testimonial_action_ids:
        user_action_status = 'TESTIMONIAL'
      else:
        user_action_rel = action_id_to_action_rel.get(action.id, None)
        if user_action_rel:
          user_action_status = user_action_rel.status
      cells.append(user_action_status)
    return cells

  def _get_user_teams_cells(self, user, teams):
    if (isinstance(user, Subscriber)):
      return [''] # for _ in range(len(teams))]

    cell_text = ''
    user_team_members = TeamMember.objects.filter(user=user).select_related('team')
    for team in teams:

      team_member = user_team_members.filter(team=team).first()
      if team_member:
        if cell_text != "": cell_text += ", "
        cell_text = cell_text + team.name
        if team_member.is_admin:
          cell_text += "(ADMIN)"

    cells = [cell_text]  
    return cells


  def _get_action_info_cells(self, action):
    average_carbon_points = action.calculator_action.average_points \
                          if action.calculator_action else action.average_carbon_score
    
    cc_action = action.calculator_action.name if action.calculator_action else ''

    category_obj = action.tags.filter(tag_collection__name='Category').first()
    category = category_obj.name if category_obj else None
    cost_obj = action.tags.filter(tag_collection__name='Cost').first()
    cost = cost_obj.name if cost_obj else None
    impact_obj = action.tags.filter(tag_collection__name='Impact').first()
    impact = impact_obj.name if impact_obj else None

    done_count = UserActionRel.objects.filter(is_deleted=False, action=action, status="DONE").count()
    total_carbon_points = str(average_carbon_points * done_count)
    done_count = str(done_count)

    testimonials_count = str(Testimonial.objects.filter(is_deleted=False, action=action).count())
    
    action_cells = {
      'title': action.title, 'yearly_lbs_carbon': average_carbon_points,
      'total_yearly_lbs_carbon': total_carbon_points,
      'carbon_calculator_action' : cc_action,
      'category': category,  'impact': impact,
      'cost': cost, 'is_global': action.is_global,
      'testimonials_count': testimonials_count, 'done_count': done_count
    }
    
    return self._get_cells_from_dict(self.action_info_columns, action_cells)


  def _get_reported_data_rows(self, community):
    rows = []
    for action_category in self.action_categories:
      data = Data.objects.filter(tag=action_category, community=community).first()
      if not data:
        continue
      rows.append(self._get_cells_from_dict(self.action_info_columns, 
                    {'title': 'STATE-REPORTED', 'category' : action_category.name, 'done_count': str(data.value)}))
    return rows


  def _get_team_info_cells(self, team):
    members = get_team_users(team)

    members_count = str(len(members))

    total_carbon_points = 0
    for user in members:
      actions = user.useractionrel_set.all()
      done_actions = actions.filter(status="DONE")
      for done_action in done_actions:
        if done_action.action and done_action.action.calculator_action:
          total_carbon_points += done_action.action.calculator_action.average_points
    total_carbon_points = str(total_carbon_points)

    testimonials_count = 0
    for user in members:
      testimonials_count += Testimonial.objects.filter(is_deleted=False, user=user).count()
    testimonials_count = str(testimonials_count)

    team_cells = {
      'name': team.name, 'members_count': members_count,
      'total_yearly_lbs_carbon': total_carbon_points, 'testimonials_count': testimonials_count
    }
    if team.parent:
      team_cells['parent'] = team.parent.name
    
    return self._get_cells_from_dict(self.team_info_columns, team_cells)


  def _get_team_action_cells(self, team, actions):
    cells = []
    team_users = [tm.user for tm in TeamMember.objects.filter(is_deleted=False, team=team).select_related('user')]
    for action in actions:
      cells.append(str(UserActionRel.objects.filter(action=action, user__in=team_users, status='DONE').count()))
    return cells

  def _get_community_reported_data(self, community):
    community = Community.objects.get(pk=community.id)
    if not community:
      return None
    ret = {}
    for action_category in self.action_categories:
      data = Data.objects.filter(tag=action_category, community=community).first()
      if not data:
        continue
      ret[action_category.name + " (reported)"] = data.reported_value
    return ret


  def _get_community_info_cells(self, community):

    location_string = ''
    if community.is_geographically_focused:
      location_string += '['
      for loc in community.locations.all():
        if location_string != '[':
          location_string += ','        
        location_string += str(loc)
      location_string += ']'

    community_members = CommunityMember.objects.filter(is_deleted=False, community=community)\
                                          .select_related('user')
    users = [cm.user for cm in community_members]
    members_count = community_members.count()
    teams_count = str(Team.objects.filter(is_deleted=False, community=community).count())
    events_count = str(Event.objects.filter(is_deleted=False, community=community).count())
    testimonials_count = str(Testimonial.objects.filter(is_deleted=False, community=community).count())

    actions = Action.objects.filter(Q(community=community) | Q(is_global=True)).filter(is_deleted=False).select_related('calculator_action')

    if community.is_geographically_focused:
      # geographic focus - actions take place where real estate units are located
      households_count = str(RealEstateUnit.objects.filter(is_deleted=False, community=community).count())
      #done_action_rels = UserActionRel.objects.filter(action__in=actions, real_estate_unit__community=community, is_deleted=False, status='DONE').select_related('action__calculator_action')
      done_action_rels = UserActionRel.objects.filter(real_estate_unit__community=community, is_deleted=False, status='DONE').select_related('action__calculator_action')
    else:
      # non-geographic focus - actions attributed to any community members
      households_count = sum([user.real_estate_units.count() for user in users])
      #done_action_rels = UserActionRel.objects.filter(action__in=actions, user__in=users,  is_deleted=False, status='DONE').select_related('action__calculator_action')
      done_action_rels = UserActionRel.objects.filter(user__in=users,  is_deleted=False, status='DONE').select_related('action__calculator_action')

    actions_done = len(done_action_rels)
    total_carbon_points = sum([action_rel.action.calculator_action.average_points
                            if action_rel.action.calculator_action else 0
                            for action_rel in done_action_rels])
    actions_per_member = str(round(actions_done / members_count, 2)) if members_count != 0 else '0'

    action_done_count_map = {action.title: done_action_rels.filter(action=action).count() for action in actions}
    actions_by_done_count = sorted(action_done_count_map.items(), key=lambda item: item[1], reverse=True)

    most_done_action = actions_by_done_count[0][0] if actions_done > 0 and (len(actions_by_done_count) > 0 and actions_by_done_count[0][1] != 0) else ''
    second_most_done_action = actions_by_done_count[1][0] if actions_done > 0 and (len(actions_by_done_count) > 1 and actions_by_done_count[1][1] != 0) else ''

    actions_by_impact = actions.order_by('calculator_action__average_points')
    highest_impact_action = actions_by_impact[0] if actions_done > 0 and len(actions_by_impact) > 0 else ''
    second_highest_impact_action = actions_by_impact[1] if actions_done > 0 and len(actions_by_impact) > 1 else ''
    community_cells = {
      'name': community.name, 'location': location_string, 
      'members_count': str(members_count), 'households_count': households_count,
      'teams_count' : teams_count, 'total_yearly_lbs_carbon' : total_carbon_points,
      'actions_done': str(actions_done), 'actions_per_member': actions_per_member,
      'testimonials_count' : testimonials_count, 'events_count': events_count,
      'most_done_action': most_done_action, 'second_most_done_action': second_most_done_action, 'highest_impact_action': highest_impact_action, 'second_highest_impact_action': second_highest_impact_action
    }

    reported_actions = self._get_community_reported_data(community)
    community_cells.update(reported_actions)
    community_cells['total_actions_done'] = str(actions_done + sum(value for value in reported_actions.values()))

    total_households_count = 0 if not community.goal else community.goal.attained_number_of_households
    total_households_count += RealEstateUnit.objects.filter(community=community).count()
    community_cells['total_households_count'] = total_households_count
    return self._get_cells_from_dict(self.community_info_columns, community_cells)

  def _all_users_download(self):
    users = list(UserProfile.objects.filter(is_deleted=False)) \
        + list(Subscriber.objects.filter(is_deleted=False))
    actions = Action.objects.filter(is_deleted=False)
    teams = Team.objects.filter(is_deleted=False)

    columns = ['primary community',
                'secondary community' ] \
                + self.user_info_columns \
                + ['TEAM'] \
                + [action.title for action in actions]

    sub_columns = ['', ''] + ['' for _ in range(len(self.user_info_columns))] + [''] \
            + ["ACTION" for _ in range(len(actions))] #+ ["TEAM" for _ in range(len(teams))]
    data = []

    for user in users:
      if (isinstance(user, Subscriber)):
        if user.community:
          primary_community, secondary_community = user.community.name, ''
        else:
          primary_community, secondary_community = '', ''
      else:
        # community list which user has associated with
        communities = [cm.community.name for cm in CommunityMember.objects.filter(user=user).select_related('community')]
        # communities of primary real estate unit associated with the user
        reu_community = None
        for reu in user.real_estate_units.all():
          if reu.community:
            reu_community = reu.community.name
            break

        primary_community = secondary_community = ''
        # Primary community comes from a RealEstateUnit
        if reu_community:
          primary_community = reu_community

        for community in communities:
          if community != primary_community:
            if secondary_community != '': secondary_community += ", "
            secondary_community += community

        #if len(communities) > 1:
        #  primary_community, secondary_community = communities[0], communities[1]
        #elif len(communities) == 1:
        #  primary_community, secondary_community = communities[0], ''
        #else:
        #  primary_community, secondary_community = '', ''

      row = [primary_community, secondary_community] \
      + self._get_user_info_cells(user) \
      + self._get_user_teams_cells(user, teams) \
      + self._get_user_actions_cells(user, actions)

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
                + ['TEAM'] \
                + [action.title for action in actions]
                #+ [team.name for team in teams]
    sub_columns = ['' for _ in range(len(self.user_info_columns))]  \
                + [''] \
                + ["ACTION" for _ in range(len(actions))] #+ ["TEAM" for _ in range(len(teams))]
    data = [columns, sub_columns]

    for user in users:

      #BHN 20.1.10 Put teams list in one cell, ahead of actions 
      row = self._get_user_info_cells(user) \
          + self._get_user_teams_cells(user, teams) \
          + self._get_user_actions_cells(user, actions)

      data.append(row)

    return data

  # new 1/11/20 BHN - untested
  def _team_users_download(self, team_id):
    users = [cm.user for cm in TeamMember.objects.filter(team__id=team_id, \
            is_deleted=False, user__is_deleted=False).select_related('user')]

    # Soon teams could span communities, in which case actions list would be larger.  
    # For now, take the first community that a team is associated with
    community_id = Team.objects.get(id=team_id).community.id     
    actions = Action.objects.filter(Q(community__id=community_id) | Q(is_global=True)) \
                                                      .filter(is_deleted=False)

    columns = self.user_info_columns \
                + [action.title for action in actions]
    sub_columns = ['' for _ in range(len(self.user_info_columns))]  \
                + ["ACTION" for _ in range(len(actions))]
    data = [columns, sub_columns]

    for user in users:

      row = self._get_user_info_cells(user) \
          + self._get_user_actions_cells(user, actions)

      data.append(row)

    return data


  def _all_actions_download(self):
    actions = Action.objects.select_related('calculator_action', 'community') \
            .prefetch_related('tags').filter(is_deleted=False)

    columns = ['community'] + self.action_info_columns
    data = []

    for action in actions:

      if not action.is_global and action.community:
        community = action.community.name
      else:
        community = ''

      data.append([community] \
        + self._get_action_info_cells(action))

    for community in Community.objects.filter(is_deleted=False):
      community_reported_rows = self._get_reported_data_rows(community)
      for row in community_reported_rows:
        data.append([community.name] + row)

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

    community = Community.objects.filter(id=community_id).first()
    community_reported_rows = self._get_reported_data_rows(community)
    for row in community_reported_rows:
      data.append(row)

    return data


  def _all_communities_download(self):
    communities = Community.objects.filter(is_deleted=False)
    columns = self.community_info_columns
    data = [columns]

    for community in communities:
      data.append(self._get_community_info_cells(community))

    return data


  def _community_teams_download(self, community_id):
    teams = Team.objects.filter(community__id=community_id, is_deleted=False)
    actions = Action.objects.filter(Q(community__id=community_id) | Q(is_global=True)).filter(is_deleted=False)

    columns = self.team_info_columns + [action.title for action in actions]
    sub_columns = ['' for _ in range(len(self.team_info_columns))] \
            + ["ACTION" for _ in range(len(actions))]
    data = [columns, sub_columns]

    for team in teams:
      data.append(self._get_team_info_cells(team) \
        + self._get_team_action_cells(team, actions))

    return data


  def users_download(self, context: Context, community_id, team_id) -> (list, MassEnergizeAPIError):
    try:
      if team_id:
        community_name = Team.objects.get(id=team_id).name
      elif community_id:
        community_name = Community.objects.get(id=community_id).name

      if context.user_is_super_admin:
        if team_id:
          return (self._team_users_download(team_id), community_name), None
        elif community_id:
          return (self._community_users_download(community_id), community_name), None
        else:

          return (self._all_users_download(), None), None
      elif context.user_is_community_admin:
        if team_id:
          return (self._team_users_download(team_id), community_name), None
        elif community_id:
          return (self._community_users_download(community_id), community_name), None
        else:
          return None, NotAuthorizedError()
      else:
        return None, NotAuthorizedError()
    except Exception as e:
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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def communities_download(self, context: Context) -> (list, MassEnergizeAPIError):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      return (self._all_communities_download(), None), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def teams_download(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_community_admin or context.user_is_super_admin:
          community = Community.objects.get(id=community_id)
          if community:
            return (self._community_teams_download(community.id), community.name), None
          else:
            return None, InvalidResourceError()
      else:
          return None, NotAuthorizedError()
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

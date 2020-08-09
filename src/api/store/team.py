from database.models import Team, UserProfile, Media, Community, TeamMember
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.utils.text import slugify
from _main_.utils.context import Context
from .utils import get_community_or_die, get_user_or_die
from database.models import Team, UserProfile
from sentry_sdk import capture_message

def can_set_parent(parent, this_team=None):
  if parent.parent:
    return False
  if this_team and Team.objects.filter(parent=this_team, is_deleted=False).exists():
    return False
  return True


def get_team_members(team):
  team_members = TeamMember.objects.filter(team=team, is_deleted=False)
  if team.parent:
    return team_members
  else:
    child_teams = Team.objects.filter(parent=team, is_deleted=False)
    child_team_members = TeamMember.objects.filter(team__in=child_teams, is_deleted=False)
    return (team_members | child_team_members).distinct()

class TeamStore:
  def __init__(self):
    self.name = "Team Store/DB"

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    team = Team.objects.get(id=team_id)
    if not team:
      return None, InvalidResourceError()
    return team, None

  def get_team_admins(self, team_id):
    if not team_id:
      return []
    return [a.user for a in TeamMember.objects.filter(is_admin=True, team__id=team_id, is_deleted=False) if a.user is not None]

  def list_teams(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      community = get_community_or_die(context, args)
      user = get_user_or_die(context, args)
      if community:
        teams = Team.objects.filter(community=community)
      elif user:
        teams = user.team_set.all()
      return teams, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def team_stats(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      community = get_community_or_die(context, args)
      teams = Team.objects.filter(community=community)
      ans = []
      for team in teams:
        res = {"members": 0, "households": 0, "actions": 0, "actions_completed": 0, "actions_todo": 0, "carbon_footprint_reduction": 0}
        res["team"] = team.simple_json()
        # team.members deprecated
        # for m in team.members.all():
        members = get_team_members(team)
        res["members"] = members.count()
        for m in members:
          user = m.user
          res["households"] += user.real_estate_units.count()
          actions = user.useractionrel_set.all()
          res["actions"] += len(actions)
          done_actions = actions.filter(status="DONE")
          res["actions_completed"] += done_actions.count()
          res["actions_todo"] += actions.filter(status="TODO").count()
          #for done_action in done_actions:
          #  if done_action.action and done_action.action.calculator_action:
          #    res["carbon_footprint_reduction"] += done_action.action.calculator_action.average_points

        ans.append(res)

      return ans, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_team(self, context:Context, args) -> (dict, MassEnergizeAPIError):
    team = None
    try:
      # generally a Team will have one community, but in principle it could span multiple.  If it 
      community_id = args.pop('community_id', None)
      community_ids = args.pop('community_ids', None)   # in case of a team spanning multiple communities
      logo_file = args.pop('image', None)
      image_files = args.pop('pictures', None)
      video = args.pop('video', None)
      parent_id = args.pop('parent_id', None)

      admin_emails = args.pop('admin_emails', [])
      
      verified_admins = []
      #verify that provided emails are valid user
      for email in admin_emails:
        admin =  UserProfile.objects.filter(email=email).first()
        if admin:
          verified_admins.append(admin)
        else:
          return None, CustomMassenergizeError(f"Email: {email} is not registered with us")
      
      if not verified_admins:
        return None, CustomMassenergizeError(f"Please provide at least one admin's email")

      if community_id:
        community = Community.objects.filter(pk=community_id).first()
        if not community:
          return None, CustomMassenergizeError("Please provide a valid community")
        args["community"] = community
        community_list = None
      elif community_ids:       # the case of multiple communities
        community_list = []
        for community_id in community_ids:
          community = Community.objects.filter(pk=community_id).first()
          if not community:
            return None, CustomMassenergizeError("Please provide a valid community in the list")
          community_list.append(community)
      else:
        return None, CustomMassenergizeError("Please provide a community")
      
      new_team = Team.objects.create(**args)
      team = new_team

      # add multiple communities if that is the case (generally not)
      if community_list:
        for community in community_list:
          new_team.community.add(community)

      # for the case of a sub-team, record the parent
      if parent_id:
        parent = Team.objects.filter(pk=parent_id).first()
        if parent and can_set_parent(parent):
          new_team.parent = parent
        else:
          return None, CustomMassenergizeError("Cannot set parent team")

      if logo_file:
        logo = Media.objects.create(file=logo_file, name=f"{slugify(new_team.name)}-TeamLogo")
        logo.save()
        new_team.logo = logo

      new_team.save()

      for admin in verified_admins:
        teamMember, _ = TeamMember.objects.get_or_create(team=team,user=admin)
        teamMember.is_admin = True
        teamMember.save()

      return new_team, None
    except Exception as e:
      capture_message(str(e), level="error")
      if team:
        team.delete()
      return None, CustomMassenergizeError(str(e))


  def update_team(self, team_id, args) -> (dict, MassEnergizeAPIError):
    try:
      
      community_id = args.pop('community_id', None)
      logo = args.pop('logo', None)
      team = Team.objects.filter(id=team_id)

      parent_id = args.pop('parent_id', None)
      if parent_id:
        parent = Team.objects.filter(pk=parent_id).first()
        if parent and can_set_parent(parent, this_team=team):
          team.parent = parent
        else:
          return None, CustomMassenergizeError("Cannot set parent team")

      team.update(**args)
      team = team.first()

      if team:
        if community_id:
          community = Community.objects.filter(pk=community_id).first()
          if community:
            team.community = community
        
        if logo:
          logo = Media.objects.create(file=logo, name=f"{slugify(team.name)}-TeamLogo")
          logo.save()
          team.logo = logo

        team.save()

      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
    

  def delete_team(self, team_id) -> (dict, MassEnergizeAPIError):
    try:
      teams = Team.objects.filter(id=team_id)
      if not teams:
        return None, InvalidResourceError()


      # team.members deprecated.  Delete TeamMembers separate step
      team = teams.first()
      members = TeamMember.objects.filter(team=team)
      msg = "delete_team:  Team %s deleting %d members" % (team.name,members.count())
      members.delete()
      teams.delete()  # or should that be team.delete()?

      return teams.first(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def join_team(self, team_id, user_id) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      user = UserProfile.objects.get(id=user_id)
      teamMember = TeamMember.create(team=team, user=user)
      teamMember.save()
      #team.members.add(user_id)
      #team.save()
      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

  def leave_team(self, team_id, user_id) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      user = UserProfile.objects.get(id=user_id)
      teamMembers = TeamMember.objects.filter(team=team, user=user)
      teamMembers.delete()

      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

  def add_team_member(self, context: Context, args) -> (Team, MassEnergizeAPIError):
    try:
      team_id = args.pop('team_id', None)
      user = get_user_or_die(context, args)
      status = args.pop('is_admin', None) == 'true'

      if not team_id :
        return None, CustomMassenergizeError("Missing team_id")

      team_member: TeamMember = TeamMember.objects.filter(team__id=team_id, user=user).first()
      if team_member:
        team_member.is_admin = status
        team_member.save()
      else:
        team = Team.objects.filter(pk=team_id).first()
        if not team_id and not user:
          return None, CustomMassenergizeError("Invalid team or user")
        team_member = TeamMember.objects.create(is_admin=status, team=team, user=user)

      return team_member, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def remove_team_member(self, context: Context, args) -> (Team, MassEnergizeAPIError):
    try:
      team_id = args.pop('team_id', None)
      user = get_user_or_die(context, args)
      res = {}
      if team_id and user:
        team_member = TeamMember.objects.filter(team__id=team_id, user=user)
        res = team_member.delete()
      return res, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def members(self, context: Context, args) -> (Team, MassEnergizeAPIError):
    try:
      if not context.user_is_admin():
        return None, NotAuthorizedError()
      team_id = args.get('team_id', None)
      if not team_id:
        return [], CustomMassenergizeError('Please provide a valid team_id')

      members = TeamMember.objects.filter(is_deleted=False, team__id=team_id)
      return members, None
    except Exception:
      return None, InvalidResourceError()


  def members_preferred_names(self, context: Context, args) -> (Team, MassEnergizeAPIError):
    try:
      team_id = args.get('team_id', None)
      if not team_id:
        return [], CustomMassenergizeError('Please provide a valid team_id')

      team = Team.objects.filter(id=team_id).first()
      members = get_team_members(team).select_related("user")
      res = []
      for member in members:
        res.append({"id": member.id, "user_id": member.user.id, "preferred_name": member.user.preferred_name, "is_admin": member.is_admin and member.team == team})

      return res, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, InvalidResourceError()


  def list_teams_for_community_admin(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        return self.list_teams_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      community_id = args.pop('community_id', None)
      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]
        teams = Team.objects.filter(community__id__in = comm_ids, is_deleted=False).select_related('logo', 'community')
        return teams, None

      teams = Team.objects.filter(community__id = community_id, is_deleted=False).select_related('logo', 'community')
      return teams, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_teams_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      teams = Team.objects.filter(is_deleted=False).select_related('logo', 'community')
      return teams, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

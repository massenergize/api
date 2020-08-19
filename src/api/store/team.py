from database.models import Team, UserProfile, Media, Community, TeamMember
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.utils.text import slugify
from _main_.utils.context import Context
from .utils import get_community_or_die, get_user_or_die
from database.models import Team, UserProfile
from sentry_sdk import capture_message


class TeamStore:
  def __init__(self):
    self.name = "Team Store/DB"

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    team = Team.objects.get(id=team_id)
    if not team:
      return None, InvalidResourceError()
    return team, None

  def get_team_admins(self, context, team_id):
    if not team_id:
      return []
    return [a.user for a in TeamMember.objects.filter(is_admin=True, is_deleted=False) if a.user is not None]

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
        members = TeamMember.objects.filter(team=team)
        res["members"] = members.count()
        for m in members:
          user = m.user
          res["households"] += user.real_estate_units.count()
          actions = user.useractionrel_set.all()
          res["actions"] += len(actions)
          done_actions = actions.filter(status="DONE").prefetch_related('action__calculator_action')
          res["actions_completed"] += done_actions.count()
          res["actions_todo"] += actions.filter(status="TODO").count()
          for done_action in done_actions:
            if done_action.action and done_action.action.calculator_action:
              res["carbon_footprint_reduction"] += done_action.action.calculator_action.average_points

        ans.append(res)

      return ans, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_team(self, context:Context, args) -> (dict, MassEnergizeAPIError):
    team = None
    try:
      community_id = args.pop('community_id', None)
      image = args.pop('image', None)
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
        
      else:
        return None, CustomMassenergizeError("Please provide a community")

      args["community"] = community
      new_team = Team.objects.create(**args)
      team = new_team

      if image:
        logo = Media.objects.create(file=image, name=f"{slugify(new_team.name)}-TeamLogo")
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

      members = TeamMember.objects.filter(is_deleted=False, team__id=team_id).select_related("user")
      res = []
      for member in members:
        res.append({"id": member.id, "preferred_name": member.user.preferred_name, "is_admin": member.is_admin})

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

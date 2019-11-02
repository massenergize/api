from database.models import Team, UserProfile, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.utils.text import slugify

class TeamStore:
  def __init__(self):
    self.name = "Team Store/DB"

  def get_team_info(self, team_id) -> (dict, MassEnergizeAPIError):
    team = Team.objects.get(id=team_id)
    if not team:
      return None, InvalidResourceError()
    return team, None


  def list_teams(self, args) -> (list, MassEnergizeAPIError):
    try:
      user_id = args.pop('user_id', None)
      user_email = args.pop('user_email', None)
      # args['is_published'] = True
      args['is_deleted'] = False
      teams = Team.objects.filter(**args)
      res = []
      if user_id:
        user = UserProfile.objects.get(id=user_id)
        for t in teams:
          if (user in t.members.all()) or (user in t.admins.all()):
            res.append(t)
        return res, None
      elif user_email:
        user = UserProfile.objects.get(email=user_email)
        for t in teams:
          if (user in t.members.all()) or (user in t.admins.all()):
            res.append(t)
        return res, None
      else:
        res = teams
      return res, None
    except Exception as e:
      return None, CustomMassenergizeError(e)



  def create_team(self, user_id, args) -> (dict, MassEnergizeAPIError):
    try:
      community_id = args.pop('community_id', None)
      image = args.pop('image', None)
      new_team = Team.objects.create(**args)

      if image:
       new_team.logo = image

      if community_id:
        community = Community.objects.get(pk=community_id).first()
        if community:
          new_team.community = community

      
      new_team.save()
      new_team.members.add(user_id)
      new_team.admins.add(user_id)
      new_team.save()
      return new_team, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def update_team(self, team_id, args) -> (dict, MassEnergizeAPIError):
    try:
      print(args)
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
      return None, CustomMassenergizeError(e)
    


  def delete_team(self, team_id) -> (dict, MassEnergizeAPIError):
    teams = Team.objects.filter(id=team_id)
    if not teams:
      return None, InvalidResourceError()


  def join_team(self, team_id, user_id) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      team.members.add(user_id)
      team.save()
      return team, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def leave_team(self, team_id, user_id) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      team.members.remove(user_id)
      team.admins.remove(user_id)
      team.save()
      return team, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def add_team_admin(self, team_id, user_id, email) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      if email:
        user = UserProfile.objects.get(email=email)
      elif user_id:
        user = UserProfile.objects.get(pk=user_id)
      team.admins.add(user)
      
      if user not in team.members.all():
        team.members.add(user)

      team.save()
      return team, None
    except Exception:
      return None, InvalidResourceError()

  def remove_team_admin(self, team_id, user_id, email) -> (Team, MassEnergizeAPIError):
    try:
      team = Team.objects.get(id=team_id)
      if email:
        user = UserProfile.objects.get(email=email)
      elif user_id:
        user = UserProfile.objects.get(pk=user_id)
      team.admins.remove(user)
      team.save()
      return team, None
    except Exception:
      return None, InvalidResourceError()


  def list_teams_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    teams = Team.objects.filter(community__id = community_id)
    return teams, None


  def list_teams_for_super_admin(self):
    try:
      teams = Team.objects.all()
      return teams, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))
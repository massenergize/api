from database.models import Menu, Team, TeamMember
from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context

class MiscellaneousStore:
  def __init__(self):
    self.name = "Miscellaneous Store/DB"

  def navigation_menu_list(self, context: Context, args) -> (list, CustomMassenergizeError):
    try:
      main_menu = Menu.objects.all()
      return main_menu, None
    except Exception as e:
      return None, CustomMassenergizeError(e)

  def backfill(self, context: Context, args) -> (list, CustomMassenergizeError):
    return self.backfill_teams(context, args)

  def backfill_teams(self, context: Context, args) -> (list, CustomMassenergizeError):
    try:
      teams = Team.objects.all()
      for team in teams:
        members = team.members.all()
        for member in members:
          team_member: TeamMembers = TeamMember.objects.filter(user=member, team=team).first()
          if team_member:
            team_member.is_admin = False
            team_member.save()
          if not team_member:
            team_member = TeamMember.objects.create(user=member, team=team, is_admin=False)

        admins = team.admins.all()
        for admin in admins:
          team_member: TeamMembers = TeamMember.objects.filter(user=admin, team=team).first()
          if team_member:
            team_member.is_admin = True
            team_member.save()
          else:
            team_member = TeamMember.objects.create(user=admin, team=team, is_admin=True)


      return {'status': 'done'}, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


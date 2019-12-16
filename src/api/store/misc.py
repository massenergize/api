from database.models import Menu, Team, TeamMember, CommunityMember, CommunityAdminGroup, UserProfile
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
    # return self.backfill_community_members(context, args)

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

      return {'teams_member_backfill': 'done'}, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def backfill_community_members(self, context: Context, args) -> (list, CustomMassenergizeError):
    try:
      users = UserProfile.objects.all()
      for user in users:
        for community in user.communities.all():
          community_member: CommunityMember = CommunityMember.objects.filter(community=community, user=user).first()

          if community_member:
            community_member.is_admin = False
            community_member.save()
          else:
            community_member = CommunityMember.objects.create(community=community, user=user, is_admin=False)

      admin_groups = CommunityAdminGroup.objects.all()
      for group in admin_groups:
        for member in group.members.all():
          community_member : CommunityMember = CommunityMember.objects.filter(community=group.community, user=member).first()
          if community_member:
            community_member.is_admin = True
            community_member.save()
          else:
            community_member = CommunityMember.objects.create(community=group.community, user=member, is_admin=True)

      return {'name':'community_member_backfill', 'status': 'done'}, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


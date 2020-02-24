from database.models import Community, Tag, Menu, Team, TeamMember, CommunityMember, RealEstateUnit, CommunityAdminGroup, UserProfile, Data, TagCollection, UserActionRel, Data
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
    # return self.backfill_teams(context, args)
    # return self.backfill_community_members(context, args)
    return self.backfill_graph_default_data(context, args)
    # return self.backfill_real_estate_units(context, args)
    # return self.backfill_tag_data(context, args)

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

  def backfill_graph_default_data(self, context: Context, args):
    try:
      for community in Community.objects.all():
        for tag in TagCollection.objects.get(name__icontains="Category").tag_set.all():
          d = Data.objects.filter(community=community, name=tag.name).first()
          if d:
            val = 0
#            user_actions = UserActionRel.objects.filter(action__community=community, status="DONE")
            user_actions = UserActionRel.objects.filter(real_estate_unit__community=community, status="DONE")
            for user_action in user_actions:
              if user_action.action and user_action.action.tags.filter(pk=tag.id).exists():
                val += 1
            
            print(val, d)
            d.value = val
            d.save()
      return {'graph_default_data': 'done'}, None


    except Exception as e:
      return None, CustomMassenergizeError(e)


  def backfill_real_estate_units(self, context: Context, args):
    try:
      for user_action in UserActionRel.objects.all():
        print(user_action.real_estate_unit, user_action.action.community)
        if not user_action.real_estate_unit.community:
          user_action.real_estate_unit.community = user_action.action.community
        user_action.real_estate_unit.unit_type = (user_action.real_estate_unit.unit_type or 'residential').lower()
        user_action.real_estate_unit.save()
        if not user_action.real_estate_unit.community:
          user_action.real_estate_unit.delete()

      return {'backfill_real_estate_units': 'done'}, None


    except Exception as e:
      return None, CustomMassenergizeError(e)


  def backfill_tag_data(self, context: Context, args):
    try:
      for data in Data.objects.all():
        if data.tag and data.tag.name == "Lighting":
          home_energy_data = Data.objects.filter(community=data.community, tag__name="Home Energy").first()
          print(data, home_energy_data)
          if home_energy_data:
            home_energy_data.value += data.value
            home_energy_data.reported_value += data.reported_value
            home_energy_data.save()
            data.delete()

      return {'backfill_real_estate_units': 'done'}, None


    except Exception as e:
      return None, CustomMassenergizeError(e)
from database.models import Community, Tag, Menu, Team, TeamMember, CommunityMember, RealEstateUnit, CommunityAdminGroup, UserProfile, Data, TagCollection, UserActionRel, Data, Location
from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from .utils import find_reu_community, split_location_string, check_location
from sentry_sdk import capture_message

class MiscellaneousStore:
  def __init__(self):
    self.name = "Miscellaneous Store/DB"

  def navigation_menu_list(self, context: Context, args) -> (list, CustomMassenergizeError):
    try:
      main_menu = Menu.objects.all()
      return main_menu, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def backfill(self, context: Context, args) -> (list, CustomMassenergizeError):
    # return self.backfill_teams(context, args)
    # return self.backfill_community_members(context, args)
    # return self.backfill_graph_default_data(context, args)
    return self.backfill_real_estate_units(context, args)
    # return self.backfill_tag_data(context, args)

  def backfill_teams(self, context: Context, args) -> (list, CustomMassenergizeError):
    try:
      teams = Team.objects.all()
      for team in teams:
        members = team.members.all()
        for member in members:
          team_member = TeamMember.objects.filter(user=member, team=team).first()
          if team_member:
            team_member.is_admin = False
            team_member.save()
          if not team_member:
            team_member = TeamMember.objects.create(user=member, team=team, is_admin=False)

        admins = team.admins.all()
        for admin in admins:
          team_member = TeamMember.objects.filter(user=admin, team=team).first()
          if team_member:
            team_member.is_admin = True
            team_member.save()
          else:
            team_member = TeamMember.objects.create(user=admin, team=team, is_admin=True)

      return {'teams_member_backfill': 'done'}, None
    except Exception as e:
      capture_message(str(e), level="error")
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
      capture_message(str(e), level="error")
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
            
            d.value = val
            d.save()
      return {'graph_default_data': 'done'}, None


    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def backfill_real_estate_units(self, context: Context, args):
    try:
      # BHN - Feb 2021 - assign all real estate units to geographic communities
      # Set the community of a real estate unit based on the location of the real estate unit.  
      # This defines what geographic community, if any gets credit
      # For now, check for zip code
      reu_all = RealEstateUnit.objects.all()   
      print("Number of real estate units:" + str(reu_all.count()))
      print("Number of real estate units non deleted:" + str(reu_all.filter(is_deleted=False).count()))

      userProfiles = UserProfile.objects.prefetch_related('real_estate_units').filter(is_deleted=False)
      print("number of user profiles:" + str(userProfiles.count()))

      # loop over profiles and realEstateUnits associated with them
      for userProfile in userProfiles:
        msg = "User: %s (%s) - %s" % (userProfile.full_name, userProfile.email, userProfile.created_at.strftime("%Y-%m-%d"))
        print(msg)

        for reu in userProfile.real_estate_units.all():
          street = unit_number = city = county = state = zip = ""
          loc = reu.location    # a JSON field
          zip = None

          if loc:
            #if not isinstance(loc,str):   
            #  # one odd case in dev DB, looked like a Dict
            #  print("REU location not a string: "+str(loc)+" Type="+str(type(loc)))
            #  loc = loc["street"]
  
            loc_parts = split_location_string(loc)
            if len(loc_parts)>= 4:
              # deal with a couple odd cases
              if loc_parts[2].find("Denver")>=0:
                street = loc_parts[0]
                city = loc_parts[2]
                state = loc_parts[3]
                zip = "80203"
                print("Denver - bogus address")
              else:  
                street = loc_parts[0]
                city = loc_parts[1]
                state = loc_parts[2]
                zip = loc_parts[3].strip()
                if not zip or (len(zip)!=5 and len(zip)!=10):
                  print("Invalid zipcode: "+zip+", setting to 00000")
                  zip = "00000"
            else:
              # deal with odd cases which were encountered in the database
              zip = "00000"
              state = "MA"      # may be wrong occasionally
              if loc.find("Wayland")>=0 or loc.find("Fields Lane")>=0:
                city = "Wayland"
                zip = "01778"
              elif loc.find("Concord")>=0:
                city = "Concord"
                zip = "01742"
              elif loc.find("Falmouth")>=0:
                city = "Falmouth"
                zip = "02540"
              elif loc.find("Ithaca")>=0:
                city = "Ithaca"
                state = "NY"
                zip = "14850"
              elif loc.find("Rochester")>=0:
                city = "Rochester"
                state = "NY"
                zip = "14627"
              elif loc.find("Whitefield")>=0:
                city = "Whitefield"
                state = "NH"
                zip = "03598"
              print("Zipcode assigned "+zip)

            # create the Location for the RealEstateUnit        
            location_type, valid = check_location(street, unit_number, city, state, zip)
            if not valid:
              print("check_location returns: "+location_type)
              continue
  
            newloc, created = Location.objects.get_or_create(
              location_type = location_type,
              street = street,
              unit_number = unit_number,
              zipcode = zip,
              city = city,
              county = county,
              state = state
            )
            if created:
              msg = "Location with zipcode %s created: location_type=%s street=%s unit_number=%s city=%s county=%s state=%s" % (zip, location_type, street, unit_number, city, county, state)
              print()
            else:
              print("Location with zipcode "+zip+" found")
            reu.address = newloc
            reu.save()
  
          else:
            # no location was stored?  
            print("No location recorded for RealEstateUnit "+str(reu))
  
            # fixes for some missing addresses in Prod DB
            zip = "00000"
            cn = ""
            if userProfile.communities:
              cn = userProfile.communities.first().name
            elif reu.community:
              cn = reu.community.name
              
            if cn=="Energize Wayland":
              zip = "01778"
            elif cn=="Energize Framingham":
              zip = "01701"
            elif cn == "Cooler Concord":
              zip = "01742"
            elif cn == "Green Newton":
              zip = "02460"
            
            location_type = "ZIP_CODE_ONLY"
            newloc, created = Location.objects.get_or_create(
              location_type = location_type,
              street = street,
              unit_number = unit_number,
              zipcode = zip,
              city = city,
              county = county,
              state = state
            )
            if created:
              print("Location with zipcode "+zip+" created")
            else:
              print("Location with zipcode "+zip+" found")
            reu.address = newloc
            reu.save()
  
          # determine which, if any, community this household is actually in
          community = find_reu_community(reu)
          if community:
            print("Adding the REU with zipcode " + zip + " to the community " + community.name)
            reu.community = community
  
          elif reu.community:
            print("REU not located in any community, but was labeled as belonging to the community "+reu.community.name)
            reu.community = None
          reu.save()

      return {'backfill_real_estate_units': 'done'}, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def backfill_tag_data(self, context: Context, args):
    try:
      for data in Data.objects.all():
        if data.tag and data.tag.name == "Lighting":
          home_energy_data = Data.objects.filter(community=data.community, tag__name="Home Energy").first()
          if home_energy_data:
            home_energy_data.value += data.value
            home_energy_data.reported_value += data.reported_value
            home_energy_data.save()
            data.delete()

      return {'backfill_real_estate_units': 'done'}, None


    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

from database.models import Community, Tag, Menu, Team, TeamMember, CommunityMember, RealEstateUnit, CommunityAdminGroup, UserProfile, Data, TagCollection, UserActionRel, Data, Location
from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
import zipcodes
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
      print("Number of real estate units:" + str(RealEstateUnit.objects.all().count()))
      for reu in RealEstateUnit.objects.all():
        street = unit_number = city = county = state = zip = ""
        loc = reu.location    # a JSON field
        if reu.address:
          zip = reu.address.zipcode
        elif loc:
          if not isinstance(loc,str):   
            # one odd case in dev DB, looked like a Dict
            print("REU location not a string: "+str(loc)+" Type="+str(type(loc)))
            loc = loc["street"]

          loc_parts = loc.capitalize().replace(", ", ",").split(',')
          if len(loc_parts)>= 4:
            # deal with a couple odd cases
            if loc.find("Denver")<=0:
              street = loc_parts[0]
              city = loc_parts[2]
              state = loc_parts[3]
              zip = "80203"
              print("Denver")
            else:  
              street = loc_parts[0]
              city = loc_parts[1]
              state = loc_parts[2]
              zip = loc_parts[3]
              if not zip or len(zip)!=5:
                print("Invalid zipcode, setting to 00000")
                zip = "00000"
              else:
                print("Zipcode found "+zip)
          else:
            # deal with odd cases
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
          location_type = 'FULL_ADDRESS'
          if zip and not street: # and not city and not county and not state:
            location_type = 'ZIP_CODE_ONLY'
          elif state and not zip and not city and not county:
            location_type = 'STATE_ONLY'
          elif city and not zip and not street:
            location_type = 'CITY_ONLY'
          elif county and not city:
            location_type = 'COUNTY_ONLY'

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
          print(newloc)
          reu.address = newloc
          reu.save()
          print("REU saved ")

        else:
          # no location was stored?
          print("No location recorded for RealEstateUnit "+str(reu))
          zip = "00000"
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
          print(newloc)
          reu.address = newloc
          reu.save()

        # this is currently a bogus community, the one signed into when the profile was created
        # communityId = args.pop('community_id', None) or args.pop('community', None) 
        #communityId = None 
        # determine which, if any, community this household is actually in
        communities = Community.objects.filter(is_deleted=False, is_geographically_focused=True)
        found = False
        for community in communities:
          geography_type = community.geography_type
          for location in community.location_set.all():
            if geography_type == 'ZIPCODE':
              if zip==location.zipcode:
                found = True
                #print('Found REU with zipcode '+zip+' within community')
                if reu.community.id != community.id:
                  print('Adding the REU with zipcode '+zip+" to the community "+community.name)
                  reu.community = community
                break
            elif geography_type == 'CITY':
              if reu.community and reu.community.geography_type != 'ZIPCODE':
                reu_city = zipcodes.matching(zip)
                print(reu_city)
              pass
            elif geography_type == 'COUNTY':
              pass
            elif geography_type == 'STATE':
              pass
            elif geography_type == 'COUNTRY':
              pass
          if not found and reu.community and reu.community.id == community.id:
            print("REU not located in this community, but was labeled as belonging to the community")

          if found:
            break
        if not found:
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

from database.models import UserProfile, CommunityMember, EventAttendee, RealEstateUnit, Location, UserActionRel, \
  Vendor, Action, Data, Community, Media, TeamMember, Team
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, \
  CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.emailer.send_email import send_massenergize_email
from _main_.utils.context import Context
from _main_.settings import DEBUG
from django.db.models import F
from sentry_sdk import capture_message
from .utils import get_community, get_user, get_user_or_die, get_community_or_die, get_admin_communities, remove_dups, \
  find_reu_community, split_location_string, check_location
import json
from typing import Tuple


def _get_or_create_reu_location(args, user=None):
  unit_type = args.pop('unit_type', None)
  location = args.pop('location', None)
  
  # this address location now will contain the parsed address      
  address = args.pop('address', None)
  if address:
    # address passed as a JSON string  
    address = json.loads(address)
    street = address.get('street', '')
    unit_number = address.get('unit_number', '')
    zipcode = address.get('zipcode', '')
    city = address.get('city', '')
    county = address.get('county', '')
    state = address.get('state', '')
    country = address.get('country', 'US')
  else:
    # Legacy: get address from location string
    loc_parts = split_location_string(location)
    street = unit_number = city = county = state = zipcode = None
    if len(loc_parts) >= 4:
      street = loc_parts[0]
      unit_number = ''
      city = loc_parts[1]
      county = ''
      state = loc_parts[2]
      zipcode = loc_parts[3]
      country = 'US'
  
  # check location is valid
  location_type, valid = check_location(street, unit_number, city, state, zipcode, county, country)
  if not valid:
    raise Exception(location_type)
  
  reuloc, created = Location.objects.get_or_create(
    location_type=location_type,
    street=street,
    unit_number=unit_number,
    zipcode=zipcode,
    city=city,
    county=county,
    state=state,
    country=country
  )
  
  if created:
    print("Location with zipcode " + zipcode + " created for user " + user.preferred_name)
  else:
    print("Location with zipcode " + zipcode + " found for user " + user.preferred_name)
  return reuloc

def _update_action_data_totals(action, household, value):        
  # update community totals for this action
  for t in action.tags.all():

    # for geographic communities, we update the community where the household is
    community = action.community
    if action.community.is_geographically_focused:
      community = household.community

    data = Data.objects.filter(community=community, tag=t)
    if data:
      data.update(value=F("value") + value)

    elif value>0:
      # data for this community, action does not exist so create one
      d = Data(tag=t, community=community, value=value, name=f"{t.name}")
      d.save()


class UserStore:
  def __init__(self):
    self.name = "UserProfile Store/DB"
  
  def _has_access(self, context: Context, user_id=None, email=None):
    """
    Checks to make sure if the user has access to the user profile they want to 
    access
    """
    if (not user_id and not email):
      return False
    
    if not context.user_is_logged_in:
      return False
    
    if context.user_is_admin():
      # TODO: update this to only super admins.  Do specific checks for 
      # community admins to make sure user is in their community first
      return True
    
    if user_id and (context.user_id == user_id):
      return True
    
    if email and (context.user_email == email):
      return True
    
    return False


  def _add_action_rel(self, context: Context, args, status):
    """
    Creates a UserActionRel to record the action as completed or to do
    """
    try:
      user = get_user_or_die(context, args)
      if not user:
        return None, CustomMassenergizeError("sign_in_required / provide user_id or user_email")

      action_id = args.get("action_id", None)
      household_id = args.get("household_id", None)
      vendor_id = args.get("vendor_id", None) 

      date_completed = args.get("date_completed", None)
      carbon_impact = args.get("carbon_impact", 0)
      
      action: Action = Action.objects.get(id=action_id)
      if not action:
        return None, CustomMassenergizeError("Please provide a valid action_id")
      
      if household_id:
        household: RealEstateUnit = RealEstateUnit.objects.get(id=household_id)
      else:
        household = user.real_estate_units.all().first()
      
      if not household:
        household = RealEstateUnit(name=f"{user.preferred_name}'s Home'")
        household.save()
        user.real_estate_units.add(household)
      
      vendor = None
      if vendor_id:
        vendor = Vendor.objects.get(id=vendor_id)  # not required
      
      # if this already exists as a todo just move it over
      action_rels = UserActionRel.objects.filter(user=user, real_estate_unit=household, action=action)
      if action_rels:

        oldstatus = action_rels.first().status
        action_rels.update(status=status,
                  date_completed=date_completed,
                  carbon_impact=carbon_impact
                  )
        action_rel = action_rels.first()
      
      else:
        # create a new one since we didn't find it existed before
        action_rel = UserActionRel(
          user=user,
          action=action,
          real_estate_unit=household,
          status=status,
          date_completed=date_completed,
          carbon_impact=carbon_impact
        )
        oldstatus = None
      
      if vendor_id:
        action_rel.vendor = vendor
      action_rel.save()

      if status == "DONE" and oldstatus != "DONE":
        _update_action_data_totals(action, household, +1)  # add one to action totals
      elif status == "TODO" and oldstatus == "DONE":
        _update_action_data_totals(action, household, -1)  # subtract one from action totals

      return action_rel, None
    except Exception as e:
      capture_message(str(e), level="error")
      import traceback
      traceback.print_exc()
      return None, CustomMassenergizeError(str(e))
  

  def get_user_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      # email = args.get('email', None)
      # user_id = args.get('user_id', None)
      
      # if not self._has_access(context, user_id, email):
      #   return None, CustomMassenergizeError("permission_denied")
      
      user = get_user_or_die(context, args)
      return user, None
    
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
  
  def remove_household(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      household_id = args.get('household_id', None)
      if not household_id:
        return None, CustomMassenergizeError("Please provide household_id")
      
      return RealEstateUnit.objects.get(pk=household_id).delete(), None
    
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
  
  def add_household(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      user = get_user_or_die(context, args)
      name = args.pop('name', None)
      unit_type = args.pop('unit_type', None)
      
      reuloc = _get_or_create_reu_location(args, user)
      reu = RealEstateUnit.objects.create(name=name, unit_type=unit_type)
      reu.address = reuloc
      
      community = find_reu_community(reu)
      if community: reu.community = community
      reu.save()
      user.real_estate_units.add(reu)
      user.save()
      
      return reu, None
    
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
  
  def edit_household(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      user = get_user_or_die(context, args)
      name = args.pop('name', None)
      unit_type = args.pop('unit_type', None)
      household_id = args.get('household_id', None)
      if not household_id:
        return None, CustomMassenergizeError("Please provide household_id")
      
      reuloc = _get_or_create_reu_location(args, user)
      
      reu = RealEstateUnit.objects.get(pk=household_id)
      reu.name = name
      reu.unit_type = args.get("unit_type", "RESIDENTIAL")
      reu.address = reuloc
      
      verbose = DEBUG
      community = find_reu_community(reu, verbose)
      if community:
        if verbose: print(
          "Updating the REU with zipcode " + reu.address.zipcode + " to the community " + community.name)
        reu.community = community
      
      reu.save()
      return reu, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
  
  def list_households(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      user = get_user_or_die(context, args)
      
      return user.real_estate_units.all(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
  
  def list_users(self, community_id) -> Tuple[list, MassEnergizeAPIError]:
    community, err = get_community(community_id)
    
    if not community:
      print(err)
      return [], None
    return community.userprofile_set.all(), None
  
  def list_events_for_user(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      user = get_user_or_die(context, args)
      if not user:
        return []
      return EventAttendee.objects.filter(user=user), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def check_user_imported(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      email_address = args.get('email', None)
      profile = UserProfile.objects.filter(email=email_address).first()
      # if user hasn't accepted T&C, need to finish that
      if not profile.accepts_terms_and_conditions:
        name = profile.full_name.split()
        first_name = name[0]
        last_name = name[-1]  # if no delimiter, first_name may be same as last_name
        return {"imported": True, "firstName": first_name, "lastName": last_name, "preferredName": first_name}, None
      return {"imported": False}, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def complete_imported_user(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      email_address = args['email']
      profile = UserProfile.objects.filter(email=email_address).first()
      if profile.accepts_terms_and_conditions:
        return MassenergizeResponse(data={"completed": False}), None
      return MassenergizeResponse(data={"completed": True}), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def create_user(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      
      email = args.get('email', None)
      community = get_community_or_die(context, args)
      
      # allow home address to be passed in
      location = args.pop('location', '')
      profile_picture = args.pop("profile_picture", None)
      
      if not email:
        return None, CustomMassenergizeError("email required for sign up")
      user = UserProfile.objects.filter(email=email).first()
      if not user:
        new_user: UserProfile = UserProfile.objects.create(
          full_name=args.get('full_name'),
          preferred_name=args.get('preferred_name', None),
          email=args.get('email'),
          is_vendor=args.get('is_vendor', False),
          accepts_terms_and_conditions=args.pop('accepts_terms_and_conditions', False),
          preferences={'color': args.get('color', '')}
        )
        
        if profile_picture:
          pic = Media()
          pic.name = f'{new_user.full_name} profpic'
          pic.file = profile_picture
          pic.media_type = 'image'
          pic.save()
          
          new_user.profile_picture = pic
          new_user.save()
      
      
      else:
        new_user: UserProfile = user
        # if user was imported but profile incomplete, updates user with info submitted in form
        if not new_user.accepts_terms_and_conditions:
          new_user.accepts_terms_and_conditions = args.pop('accepts_terms_and_conditions', False)
          is_vendor = args.get('is_vendor', False)
          preferences = {'color': args.get('color')}
      
      community_member_exists = CommunityMember.objects.filter(user=new_user, community=community).exists()
      if not community_member_exists:
        # add them as a member to community 
        CommunityMember.objects.create(user=new_user, community=community)
        
        # create their first household
        household = RealEstateUnit.objects.create(name="Home", unit_type="residential", community=community,
                                                  location=location)
        new_user.real_estate_units.add(household)
      
      res = {
        "user": new_user,
        "community": community
      }
      return res, None
    
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def update_user(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      user_id = args.get('id', None)
      email = args.get('email', None)
      profile_picture = args.pop("profile_picture", None)
      
      if not self._has_access(context, user_id, email):
        return None, CustomMassenergizeError("permission_denied")
      
      if context.user_is_logged_in and ((context.user_id == user_id) or (context.user_is_admin())):
        users = UserProfile.objects.filter(id=user_id)
        if not users:
          return None, InvalidResourceError()
        
        users.update(**args)
        user = users.first()
        
        if profile_picture:
          if profile_picture == "reset":
            user.profile_picture = None
            user.save()
          else:
            pic = Media()
            pic.name = f'{user.full_name} profpic'
            pic.file = profile_picture
            pic.media_type = 'image'
            pic.save()
            
            user.profile_picture = pic
            user.save()
        
        return user, None
      else:
        return None, CustomMassenergizeError('permission_denied')
    
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def delete_user(self, context: Context, user_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      if not user_id:
        return None, InvalidResourceError()
      
      # check to make sure the one deleting is an admin
      if not context.user_is_admin():
        
        # if they are not an admin make sure they can only delete themselves
        if context.user_id != user_id:
          return None, NotAuthorizedError()
      
      users = UserProfile.objects.filter(id=user_id)
      users.update(is_deleted=True)
      return users.first(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def list_users_for_community_admin(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    try:
      if context.user_is_super_admin:
        return self.list_users_for_super_admin(context)
      
      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()
      
      community, err = get_community(community_id)
      
      if not community and context.user_id:
        communities, err = get_admin_communities(context)
        comm_ids = [c.id for c in communities]
        users = [cm.user for cm in CommunityMember.objects.filter(community_id__in=comm_ids, user__is_deleted=False)]
        
        # now remove all duplicates
        users = remove_dups(users)
        
        return users, None
      elif not community:
        print(err)
        return [], None
      
      users = [cm.user for cm in
               CommunityMember.objects.filter(community=community, is_deleted=False, user__is_deleted=False)]
      users = remove_dups(users)
      return users, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def list_users_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      users = UserProfile.objects.filter(is_deleted=False, accepts_terms_and_conditions=True)
      return users, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
  
  def add_action_todo(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    return self._add_action_rel(context, args, "TODO")

  def add_action_completed(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    return self._add_action_rel(context, args, "DONE")

  def list_todo_actions(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      
      if not context.user_is_logged_in:
        return [], CustomMassenergizeError("sign_in_required")
      
      user = get_user_or_die(context, args)
      household_id = args.get("household_id", None)
      
      if household_id:
        todo = UserActionRel.objects.filter(status="TODO", user=user, real_state_unit__id=household_id)
      else:
        todo = UserActionRel.objects.filter(status="TODO", user=user)
      
      return todo, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
  
  def list_completed_actions(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      
      if not context.user_is_logged_in:
        return [], CustomMassenergizeError("sign_in_required")
      
      user = get_user_or_die(context, args)
      household_id = args.get("household_id", None)
      
      if household_id:
        todo = UserActionRel.objects.filter(status="DONE", user=user, real_state_unit__id=household_id)
      else:
        todo = UserActionRel.objects.filter(status="DONE", user=user)
      
      return todo, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
  
  def remove_user_action(self, context: Context, user_action_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      if not context.user_is_logged_in:
        return [], CustomMassenergizeError("sign_in_required")
      
      user_action = UserActionRel.objects.get(pk=user_action_id)
      oldstatus = user_action.status
      action = user_action.action
      reu = user_action.real_estate_unit

      result = user_action.delete()

      # if action had been marked as DONE, decrement community total for the action
      if oldstatus == "DONE":
        _update_action_data_totals(action, reu, -1)

      return result, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
  
  def add_invited_user(self, context: Context, args, first_name, last_name, email) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      # query users by user id, find the user that is sending the request
      cadmin = UserProfile.objects.filter(id=context.user_id).first()

      #find the community that the user is the admin of. In the next section, populate user profiles with that information
      community_id = args.get("community_id", None)
      community = Community.objects.filter(id=community_id).first()

      location = community.location.get("city", "")
      if location != "":
        location += ", "
      location += community.location.get("state", "MA")
      location = "in " + location
      
      team_name = args.get('team_name', None)
      team = None
      if team_name and team_name != "none":
        team = Team.objects.filter(name=team_name).first()

      user = UserProfile.objects.filter(email=email).first()
      if not user:
        if not email or email == "":
          return None, CustomMassenergizeError(
            "The user (" + first_name + " " + last_name + ") lacks a valid email address. Please make sure all your users have valid email addresses listed.")
        new_user: UserProfile = UserProfile.objects.create(
          full_name=first_name + ' ' + last_name,
          preferred_name=first_name + last_name[0].upper(),
          email=email,
          is_vendor=False,
          accepts_terms_and_conditions=False
        )
        new_user.save()
        if community:
          new_user.communities.add(community)
      else:
        new_user: UserProfile = user

      
      team_leader = None
      if team:
        admins = TeamMember.objects.filter(team=team, is_admin=True)  
        if admins:
          team_leader: UserProfile = admins.first().user

        new_member, _ = TeamMember.objects.get_or_create(user=new_user, team=team)
        new_member.save()
        team.save()
        
      new_user.save()
      ret = { 'cadmin': cadmin.full_name,
              'cadmin_email': cadmin.email,
              'community': community.name,
              'community_logo': community.logo.file.url,
              'community_info': community.about_community,
              'location': location,
              'subdomain': community.subdomain,
              'first_name': first_name, 
              'full_name': new_user.full_name,
              'email': email,
              'preferred_name': new_user.preferred_name}
      if team and team_leader:
        ret['team_name'] = team_name,
        ret['team_leader'] = team_leader.full_name,
        ret['team_leader_firstname'] = team_leader.full_name.split(" ")[0],
        ret['team_leader_email'] = team_leader.email,
 
      return ret, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


from database.models import UserProfile, CommunityMember, EventAttendee, RealEstateUnit, Location, UserActionRel, \
  Vendor, Action, Data, Community, Media, TeamMember, Team, Testimonial
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, \
  CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from _main_.settings import DEBUG
from django.db.models import F
from sentry_sdk import capture_message
from .utils import get_community, get_user, get_user_or_die, get_community_or_die, get_admin_communities, remove_dups, \
  find_reu_community, split_location_string, check_location
import json
from typing import Tuple
from api.services.utils import send_slack_message
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL
from api.utils.constants import STANDARD_USER, INVITED_USER, GUEST_USER
from datetime import datetime

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
    street = unit_number = city = county = state = zipcode = country = None
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

def _update_action_data_totals(action, household, delta): 

  # data corruption has been seen, and this routine is one possible culprit
  if abs(delta)>1:
    # this is only used to increment or decrement values by one.  Something wrong here
    msg = "_update_action_data_totals: data corruption check 1: delta %d" % (delta)
    raise Exception(msg)

  # update community totals for this action
  for t in action.tags.all():

    # for geographic communities, we update the community where the household is
    community = action.community
    if action.community.is_geographically_focused:
      community = household.community

    # take note of community action goal, to avoid data corruption
    actions_goal = 1000
    if community.goal:
      actions_goal = max(community.goal.target_number_of_actions, actions_goal)

    data = Data.objects.filter(community=community, tag=t)
    if data:
      # protect against going below 0
      #  data.update(value=F("value") + value)
      d = data.first()

      oldvalue = d.value
      if oldvalue > actions_goal:
        # oldvalue already too high
        msg = "_update_action_data_totals: data corruption check 2: old value %d" % (oldvalue)
        raise Exception(msg)

      value = max(oldvalue + delta, 0)
      if value != oldvalue:

        # check for data corruption:
        if abs(value-oldvalue)>1:
          # this is only used to increment or decrement values by one.  Something wrong here
          msg = "_update_action_data_totals: data corruption check 3: old value %d, new value %d" % (oldvalue, value)
          raise Exception(msg)


        d.value = value
        d.save()

    elif delta>0:
      # data for this community, action does not exist so create one
      d = Data.objects.create(value=delta, name=f"{t.name}")
      d.community=community
      d.tag = t

      #final check for corruption:
      if d.value > actions_goal:
        # oldvalue already too high
        msg = "_update_action_data_totals: data corruption check 4: d.value %d" % (d.value)
        raise Exception(msg)

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
      send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {"text": str(e)+str(context)}) 
      capture_message(str(e), level="error")
      import traceback
      traceback.print_exc()
      return None, CustomMassenergizeError(e)
  

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
      return None, CustomMassenergizeError(e)
  
  def remove_household(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      household_id = args.get('household_id', None)
      if not household_id:
        return None, CustomMassenergizeError("Please provide household_id")
      
      return RealEstateUnit.objects.get(pk=household_id).delete(), None
    
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
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
      return None, CustomMassenergizeError(e)
  
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
      return None, CustomMassenergizeError(e)
  
  def list_households(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      user = get_user_or_die(context, args)
      
      return user.real_estate_units.all(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def list_users(self, community_id) -> Tuple[list, MassEnergizeAPIError]:
    community, err = get_community(community_id)
    
    if not community:
      print(err)
      return [], None
    return community.userprofile_set.all(), None
  
  def list_publicview(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    community_id = args.pop('community_id', None)
    community, err = get_community(community_id)    
    if not community:
      print(err)
      return [], None

    LEADERBOARD_MINIMUM = 100
    min_points = args.get("min_points", LEADERBOARD_MINIMUM)

    publicview = []

    community_users = [
            cm.user
            for cm in CommunityMember.objects.filter(
                community__id=community_id,
                is_deleted=False,
                user__is_deleted=False,
                #user__accepts_terms_and_conditions=True,   # include guests, not by name
            ).select_related("user")
        ]

    #summary includes only publicly viewable info, not id, email or full name
    for user in community_users:
      summary = user.summary()
      action_points = summary["actions_done_points"] + summary["actions_todo_points"]
      if action_points > min_points:
        publicview.append(summary)

    return publicview, None
  
  def list_events_for_user(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      user = get_user_or_die(context, args)
      if not user:
        return [], None
      return EventAttendee.objects.filter(user=user), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def check_user_imported(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      email_address = args.get('email', None)
      profile = UserProfile.objects.filter(email=email_address).first()
      # if user hasn't accepted T&C, need to finish that
      if profile and not profile.accepts_terms_and_conditions:
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

      # added for special case of guest users, mark them as such in user_info
      user_info = args.get('user_info', None)     
      full_name = args.get('full_name')
      preferred_name = args.get('preferred_name', None)
      is_guest = args.pop('is_guest', False)

      new_user_type = STANDARD_USER
      if is_guest:
        new_user_type = GUEST_USER

      if not user_info or user_info == {}:
        user_info = { 'user_type': new_user_type }
      else:
        user_info['user_type'] = new_user_type

      # allow home address to be passed in
      location = args.pop('location', '')
      profile_picture = args.pop("profile_picture", None)
      color = args.pop('color', '')
      
      if not email:
        return None, CustomMassenergizeError("email required for sign up")
      email = email.lower()     # avoid multiple copies

      new_user_email = False
      existing_user = UserProfile.objects.filter(email=email).first()
      if not existing_user:
        user: UserProfile = UserProfile.objects.create(
          full_name=full_name,
          preferred_name=preferred_name,
          email=email,
          is_vendor=args.get('is_vendor', False),
          accepts_terms_and_conditions=args.pop('accepts_terms_and_conditions', False),
        )
        
        if profile_picture:
          pic = Media()
          pic.name = f'{user.full_name} profpic'
          pic.file = profile_picture
          pic.media_type = 'image'
          pic.save()
          
          user.profile_picture = pic
          user.save()
      
        if color:
          user.preferences = {'color': color}
          user.save()

        if user_info:
          user.user_info = user_info
          user.save()

        new_user_email = user.accepts_terms_and_conditions # user completes profile

      else:   # user exists
        # while calling users.create with existing user isn't normal, it can happen for different cases:
        # 1. User used to exist but firebase profile wasn't found.  Probably User had been 'deleted' but still existed in database
        # 2. User was an guest or invited user (partial profile), signing in for real, with complete profile
        # 3. User was an invited user (partial profile), signing in as a guest.  Don't update the name
        # 4. User was a standard user, signing in as a guest user.  Don't update the profile

        user: UserProfile = existing_user

        existing_user_type = STANDARD_USER
        if not user.accepts_terms_and_conditions:
          if user.user_info:
            existing_user_type = user.user_info.get('user_type',STANDARD_USER)

        if new_user_type != GUEST_USER:
          # case 1 or 2: update existing user profile with this new info

          # if user name changed, update it
          if full_name != user.full_name:
            user.full_name = full_name

          if preferred_name:
            user.preferred_name = preferred_name

          if user_info:
            user.user_info = user_info

          # if user was imported but profile incomplete, updates user with info submitted in form
          if not user.accepts_terms_and_conditions:
            user.accepts_terms_and_conditions = args.pop('accepts_terms_and_conditions', False)
            new_user_email = user.accepts_terms_and_conditions  # user completes profile
       
      community_member_exists = CommunityMember.objects.filter(user=user, community=community).exists()
      if not community_member_exists:
        # add them as a member to community 
        CommunityMember.objects.create(user=user, community=community)
        
      # create their first household, if a location was specified, and if they don't have a household
      reu = user.real_estate_units.all()
      if reu.count() == 0:
        household = RealEstateUnit.objects.create(name="Home", unit_type="residential", community=community,
                                                  location=location)
        user.real_estate_units.add(household)

      user.save()
      
      res = {
        "user": user,
        "community": community,
        "new_user_email": new_user_email,
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
      user = users.first()
      old_email = user.email
      new_email = "DELETED-" + datetime.today().strftime('%Y%m%d-%H%M') + "-" + old_email 
      users.update(is_deleted=True, email=new_email)

      user = users.first()

      if user.profile_picture:
        # don't unlink, just mark ad deleted
        profile_picture = user.profile_picture
        profile_picture.is_deleted = True
        profile_picture.save()

      # mark all real_estate_units is_deleted=true
      for reu in user.real_estate_units.all():
        reu.is_deleted = True
        reu.save()

      #if a CommunityMember links to user, mark is_deleted=true
      communityMembers = CommunityMember.objects.filter(user=user, is_deleted=False)
      for communityMember in communityMembers:
        communityMember.is_deleted = True
        communityMember.save()

      # if a Team includes on Admins, remove it and notify other admins. if no other admins notify cadmin
      teams = user.team_admins.filter(is_deleted=False)
      for team in teams:
        team.admins.remove(user)
        # Don't bother with the notify
        # if team.admins.count() == 0:
        #  community_admin = team.primary_community.owner_email
        #  msg = "User %s has been deleted, and Team %s no longer has a Team Admin" % (old_email, team.name)
        #  cadmin_messages.append(msg)

      # SKIP team.members which isn't used

      # if a TeamMember links to user, mark is_deleted=true
      teamMembers = TeamMember.objects.filter(user=user, is_deleted=False)
      for teamMember in teamMembers:
        teamMember.is_deleted = True
        teamMember.save()

      # if a CommunityAdminGroup includes, remove it, notify lead cadmin
      cadmin_groups = user.communityadmingroup_set.all()
      for cadmin_group in cadmin_groups:
        cadmin_group.members.remove(user)

      # skip UserGroup which isn't used

      # if an EventAttendee - mark is_deleted=true
      event_attendees = EventAttendee.objects.filter(user=user, is_deleted=False)
      for event_attendee in event_attendees:
        event_attendee.is_deleted = True
        event_attendee.save()

      # if a Testimonial by user, mark is_delted=true, notify cadmin
      for testimonial in Testimonial.objects.filter(user=user, is_deleted=False):
        testimonial.is_deleted = True
        testimonial.save()

      # mark any UserActionRels is_deleted=true
      for ual in UserActionRel.objects.filter(user=user, is_deleted=False):
        ual.is_deleted=True
        ual.save()

      # SKIP - if a Vendor includes as onboarding contact, notify cadmin

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
      return None, CustomMassenergizeError(e)
  
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
      return None, CustomMassenergizeError(e)
  
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
      return None, CustomMassenergizeError(e)
  
  def remove_user_action(self, context: Context, user_action_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      if not context.user_is_logged_in:
        return [], CustomMassenergizeError("sign_in_required")
      
      # Allow for the possibility that a UserActionRel may have been deleted
      user_action = UserActionRel.objects.filter(pk=user_action_id)
      if user_action:
        user_action = user_action.first()
        oldstatus = user_action.status
        action = user_action.action
        reu = user_action.real_estate_unit

        result = user_action.delete()

        # if action had been marked as DONE, decrement community total for the action
        if oldstatus == "DONE":
          _update_action_data_totals(action, reu, -1)

      else:
        # didn't find the action: something missing from database - probably a previous error -- no consequence
        result = None

      return result, None
    except Exception as e:
      send_slack_message(SLACK_SUPER_ADMINS_WEBHOOK_URL, {"text": str(e)+str(context)}) 
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
  
  def add_invited_user(self, context: Context, args, first_name, last_name, email) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      # query users by user id, find the user that is sending the request
      cadmin = UserProfile.objects.filter(id=context.user_id).first()

      #find the community that the user is the admin of. In the next section, populate user profiles with that information
      community_id = args.get("community_id", None)
      community = Community.objects.filter(id=community_id).first()

      city = community.location.get("city", None)
      state = community.location.get("state", None)

      location = ""
      if city or state:
        location = "in "
        if city and city != "": 
          location += city + ", "
        if state and state != "":
          location += state

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
        ret['team_name'] = team_name
        ret['team_leader'] = team_leader.full_name
        ret['team_leader_firstname'] = team_leader.full_name.split(" ")[0]
        ret['team_leader_email'] = team_leader.email
        ret['team_id'] = team.id

      return ret, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


from database.models import UserProfile, CommunityMember, EventAttendee, RealEstateUnit, UserActionRel, Vendor, Action, Data, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from django.db.models import F
from .utils import get_community, get_user, get_user_or_die, get_community_or_die, get_admin_communities

class UserStore:
  def __init__(self):
    self.name = "UserProfile Store/DB"

  def get_user_info(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)
      return user, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def remove_household(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      household_id = args.get('household_id', None) or args.get('household_id', None)
      if not household_id:
        return None, CustomMassenergizeError("Please provide household_id")
      return RealEstateUnit.objects.get(pk=household_id).delete(), None

    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def add_household(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)
      name = args.pop('name', None)
      unit_type=args.pop('unit_type', None)
      location=args.pop('location', None)
      communityId = args.pop('community_id', None) or args.pop('community', None) 

      new_unit = RealEstateUnit.objects.create(name=name, unit_type=unit_type,location=location)
      new_unit.save()

      user.real_estate_units.add(new_unit)
      if communityId:
        community = Community.objects.get(id=communityId)
        new_unit.community = community

      new_unit.save()

      return new_unit, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def edit_household(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)
      name = args.pop('name', None)
      household_id = args.get('household_id', None)
      unit_type=args.pop('unit_type', None)
      location=args.pop('location', None)
      communityId = args.pop('community_id', None) or args.pop('community', None) 

      if not household_id:
        return None, CustomMassenergizeError("Please provide household_id")

      new_unit = RealEstateUnit.objects.get(pk=household_id)
      new_unit.name = name
      new_unit.unit_type = unit_type
      new_unit.location = location

      if communityId:
        community = Community.objects.get(id=communityId)
        new_unit.community = community

      new_unit.save()

      return new_unit, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def list_households(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)

      return user.real_estate_units.all(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def list_users(self, community_id) -> (list, MassEnergizeAPIError):
    community,err = get_community(community_id)
    
    if not community:
      return [], None
    return community.userprofile_set.all(), None

  def list_events_for_user(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)
      if not user:
        return []
      return EventAttendee.objects.filter(attendee=user), None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def create_user(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      email = args.get('email', None) 
      community = get_community_or_die(context, args)


      # allow home address to be passed in
      location = args.pop('location', '')

      if not email:
        return None, CustomMassenergizeError("email required for sign up")
      
      user = UserProfile.objects.filter(email=email).first()
      if not user:
        new_user: UserProfile = UserProfile.objects.create(
          full_name = args.get('full_name'), 
          preferred_name = args.get('preferred_name', None), 
          email = args.get('email'), 
          is_vendor = args.get('is_vendor', False), 
          accepts_terms_and_conditions = args.pop('accepts_terms_and_conditions', False)
        )
      else:
        new_user: UserProfile = user.first()


      community_member_exists = CommunityMember.objects.filter(user=new_user, community=community).exists()
      if not community_member_exists:
        # add them as a member to community 
        CommunityMember.objects.create(user=new_user, community=community)

        #create their first household
        household = RealEstateUnit.objects.create(name="Home", unit_type="residential", community=community, location=location)
        new_user.real_estate_units.add(household)
    
      
      res = {
        "user": new_user,
        "community": community or global_community
      }
      return res, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def update_user(self, user_id, args) -> (dict, MassEnergizeAPIError):
    user = UserProfile.objects.filter(id=user_id)
    if not user:
      return None, InvalidResourceError()
    user.update(**args)
    return user, None


  def delete_user(self, user_id) -> (dict, MassEnergizeAPIError):
    users = UserProfile.objects.filter(id=user_id)
    if not users:
      return None, InvalidResourceError()


  def list_users_for_community_admin(self,  context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        return self.list_users_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      community, err = get_community(community_id)

      if not community and context.user_id:
        communities, err =  get_admin_communities(context)
        comm_ids = [c.id for c in communities]      
        users = set(cm.user for cm in CommunityMember.objects.filter(community_id__in=comm_ids))
        return users, None
      elif not community:
        return [], None

      users = CommunityMember.objects.filter(community=community, is_deleted=False)
      return users, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def list_users_for_super_admin(self, context: Context):
    try:
      # if not context.user_is_super_admin:
      #   return None, NotAuthorizedError()
      users = UserProfile.objects.filter(is_deleted=False)
      return users, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))


  def add_action_todo(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      # if not context.user_is_logged_in:
      #   return CustomMassenergizeError("Sign in required")
      user = get_user_or_die(context, args)
      action_id = args.get("action_id", None)
      household_id = args.get("household_id", None)
      vendor_id = args.get("vendor_id", None)
    
      if not user:
        return None, CustomMassenergizeError("Sign in required / provide user_id or user_email")

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

      if vendor_id:
        vendor = Vendor.objects.get(id=vendor_id) #not required

      #if this already exists as a todo just move it over
      completed = UserActionRel.objects.filter(user=user, real_estate_unit=household, action=action)
      if completed:
        #TODO: update action stats
        completed.update(status="TODO")
        return completed.first(), None
 
      
      # create a new one since we didn't find it existed before
      new_user_action_rel = UserActionRel(user=user, action=action, real_estate_unit=household, status="TODO")

      if vendor_id:
        new_user_action_rel.vendor = vendor
      
      new_user_action_rel.save()

      return new_user_action_rel, None
    except Exception as e:
      import traceback
      traceback.print_exc()
      return None, CustomMassenergizeError(str(e))

  def add_action_completed(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      # if not context.user_is_logged_in:
      #   return None, CustomMassenergizeError("Sign in required")
      
      user_id = context.user_id or args.get('user_id')
      user_email = context.user_email or args.get('user_email')
      action_id = args.get("action_id", None)
      household_id = args.get("household_id", None)
      vendor_id = args.get("vendor_id", None)

      user = None
      if user_id:
        user = UserProfile.objects.get(id=user_id)
      elif user_email:
        user = UserProfile.objects.get(email=user_email)

      if not user:
        return None, CustomMassenergizeError("Sign in required / Provide user_id")

      action = Action.objects.get(id=action_id)
      if not action:
        return None, CustomMassenergizeError("Please provide an action_id")

      household = RealEstateUnit.objects.get(id=household_id)
      if not household:
        return None, CustomMassenergizeError("Please provide a household_id")


      # update all data points
      for t in action.tags.all():
        data = Data.objects.filter(community=action.community, tag=t)
        if data:
          data.update(value=F("value") + 1)

        else:
          #data for this community, action does not exist so create one
          d = Data(tag=t, community=action.community, value=1, name=f"{t.name}")
          d.save()
      

      #if this already exists as a todo just move it over
      completed = UserActionRel.objects.filter(user=user, real_estate_unit=household, action=action)
      if completed:
        completed.update(status="DONE")
        return completed.first(), None

      # create a new one since we didn't find it existed before
      new_user_action_rel = UserActionRel(user=user, action=action, real_estate_unit=household, status="DONE")

      if vendor_id:
        vendor = Vendor.objects.get(id=vendor_id) #not required
        new_user_action_rel.vendor = vendor

      new_user_action_rel.save()

      return new_user_action_rel, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def list_todo_actions(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      if not context.user_is_logged_in:
        return [], CustomMassenergizeError("Sign in required")
      
      user = get_user_or_die(context, args)
      household_id = args.get("household_id", None)

      if household_id:
        todo = UserActionRel.objects.filter(status="TODO", user=user, real_state_unit__id=household_id) 
      else:
        todo = UserActionRel.objects.filter(status="TODO", user=user) 

      return todo, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def list_completed_actions(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      if not context.user_is_logged_in:
        return [], CustomMassenergizeError("Sign in required")
      
      user = get_user_or_die(context, args)
      household_id = args.get("household_id", None)

      if household_id:
        todo = UserActionRel.objects.filter(status="DONE", user=user, real_state_unit__id=household_id) 
      else:
        todo = UserActionRel.objects.filter(status="DONE", user=user) 
      
      return todo, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))
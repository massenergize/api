from database.models import UserProfile, RealEstateUnit, UserActionRel, Vendor, Action, Data
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from django.db.models import F

class UserStore:
  def __init__(self):
    self.name = "UserProfile Store/DB"

  def get_user_info(self, user_id) -> (dict, MassEnergizeAPIError):
    try:
      user = UserProfile.objects.get(id=user_id)
      return user, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def list_users(self, community_id) -> (list, MassEnergizeAPIError):
    users = UserProfile.objects.filter(community__id=community_id)
    if not users:
      return [], None
    return [t.simple_json() for t in users], None


  def create_user(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_user = UserProfile.objects.create(**args)
      new_user.save()
      return new_user, None
    except Exception:
      return None, ServerError()


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


  def list_users_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    users = UserProfile.objects.filter(community__id = community_id)
    return users, None


  def list_users_for_super_admin(self):
    try:
      users = UserProfile.objects.all()
      return users, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))


  def add_action_todo(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      if not context.user_is_logged_in:
        return CustomMassenergizeError("Sign in required")
      
      user_id = context.user_id
      action_id = args.get("action_id", None)
      household_id = args.get("household_id", None)
      vendor_id = args.get("vendor_id", None)

      user = UserProfile.objects.get(id=user_id)
      if not user:
        return None, CustomMassenergizeError("Sign in required")

      action: Action = Action.objects.get(id=action_id)
      if not action:
        return None, CustomMassenergizeError("Please provide an action_id")

      household: RealEstateUnit = RealEstateUnit.objects.get(id=household_id)
      if not household:
        return None, CustomMassenergizeError("Please provide a household_id")

      vendor = Vendor.objects.get(id=vendor_id) #not required

      #if this already exists as a todo just move it over
      completed = UserActionRel.objects.filter(user=user, real_estate_unit=household, action=action)
      if completed:
        #TODO: update action stats
        completed.update(status="TODO")
        return completed.first(), None
 
      # update all data points
      for t in action.tags:
        data = Data.objects.filter(community=action.community, tag=t)
        if data:
          data.update(value=max(F("value") - 1, 0)) #we never want to go negative

        else:
          #data for this community, action does not exist so create one
          d = Data(tag=t, community=action.community, value=0, name=f"{t.name}")
          d.save()
      
      # create a new one since we didn't find it existed before
      new_user_action_rel = UserActionRel(user=user, action=action, real_estate_unit=household, status="TODO")

      if vendor_id:
        new_user_action_rel.vendor = vendor
      
      new_user_action_rel.save()

      return new_user_action_rel, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))



  def add_action_completed(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      if not context.user_is_logged_in:
        return None, CustomMassenergizeError("Sign in required")
      
      user_id = context.user_id
      action_id = args.get("action_id", None)
      household_id = args.get("household_id", None)
      vendor_id = args.get("vendor_id", None)


      user = UserProfile.objects.get(id=user_id)
      if not user:
        return None, CustomMassenergizeError("Sign in required")

      action = Action.objects.get(id=action_id)
      if not action:
        return None, CustomMassenergizeError("Please provide an action_id")

      household = RealEstateUnit.objects.get(id=household_id)
      if not household:
        return None, CustomMassenergizeError("Please provide a household_id")

      vendor = Vendor.objects.get(id=vendor_id) #not required

      #if this already exists as a todo just move it over
      completed = UserActionRel.objects.filter(user=user, real_estate_unit=household, action=action)
      if completed:
        completed.update(status="DONE")
        return completed.first(), None

      # create a new one since we didn't find it existed before
      new_user_action_rel = UserActionRel(user=user, action=action, real_estate_unit=household, status="DONE")

      if vendor_id:
        new_user_action_rel.vendor = vendor

      # update all data points
      for t in action.tags:
        data = Data.objects.filter(community=action.community, tag=t)
        if data:
          data.update(value=F("value") + 1)

        else:
          #data for this community, action does not exist so create one
          d = Data(tag=t, community=action.community, value=1, name=f"{t.name}")
          d.save()
      
      new_user_action_rel.save()

      return new_user_action_rel, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def list_todo_actions(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      if not context.user_is_logged_in:
        return CustomMassenergizeError("Sign in required")
      
      user_id = context.user_id
      household_id = args.get("household_id", None)

      if household_id:
        todo = UserActionRel.objects.filter(status="TODO", user__id=user_id, real_state_unit__id=household_id) 
      else:
        todo = UserActionRel.objects.filter(status="TODO", user__id=user_id) 
      
      return todo, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def list_completed_actions(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      if not context.user_is_logged_in:
        return CustomMassenergizeError("Sign in required")
      
      user_id = context.user_id
      household_id = args.get("household_id", None)

      if household_id:
        todo = UserActionRel.objects.filter(status="DONE", user__id=user_id, real_state_unit__id=household_id) 
      else:
        todo = UserActionRel.objects.filter(status="DONE", user__id=user_id) 
      
      return todo, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))
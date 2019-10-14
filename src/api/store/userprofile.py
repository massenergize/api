from database.models import UserProfile, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

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
      new_user = UserProfile.create(**args)
      new_user.save()
      return new_user.full_json(), None
    except Exception:
      return None, ServerError()


  def update_user(self, user_id, args) -> (dict, MassEnergizeAPIError):
    user = UserProfile.objects.filter(id=user_id)
    if not user:
      return None, InvalidResourceError()
    user.update(**args)
    return user.full_json(), None


  def delete_user(self, user_id) -> (dict, MassEnergizeAPIError):
    users = UserProfile.objects.filter(id=user_id)
    if not users:
      return None, InvalidResourceError()


  def list_users_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    users = UserProfile.objects.filter(community__id = community_id)
    return [t.simple_json() for t in users], None


  def list_users_for_super_admin(self):
    try:
      users = UserProfile.objects.all()
      return [t.simple_json() for t in users], None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))
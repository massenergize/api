from database.models import Policy, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class PolicyStore:
  def __init__(self):
    self.name = "Policy Store/DB"

  def get_policy_info(self, policy_id) -> (dict, MassEnergizeAPIError):
    policy = Policy.objects.filter(id=policy_id)
    if not policy:
      return None, InvalidResourceError()
    return policy.full_json(), None


  def list_policies(self, community_id) -> (list, MassEnergizeAPIError):
    policies = Policy.objects.filter(community__id=community_id)
    if not policies:
      return [], None
    return [t.simple_json() for t in policies], None


  def create_policy(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_policy = Policy.create(**args)
      new_policy.save()
      return new_policy.full_json(), None
    except Exception:
      return None, ServerError()


  def update_policy(self, policy_id, args) -> (dict, MassEnergizeAPIError):
    policy = Policy.objects.filter(id=policy_id)
    if not policy:
      return None, InvalidResourceError()
    policy.update(**args)
    return policy.full_json(), None


  def delete_policy(self, policy_id) -> (dict, MassEnergizeAPIError):
    policies = Policy.objects.filter(id=policy_id)
    if not policies:
      return None, InvalidResourceError()


  def list_policies_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    policies = Policy.objects.filter(community__id = community_id)
    return [t.simple_json() for t in policies], None


  def list_policies_for_super_admin(self):
    try:
      policies = Policy.objects.all()
      return [t.simple_json() for t in policies], None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))
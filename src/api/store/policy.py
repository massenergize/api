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
    return policy, None


  def list_policies(self, community_id) -> (list, MassEnergizeAPIError):
    policies = Policy.objects.filter(community__id=community_id)
    if not policies:
      return [], None
    return policies, None


  def create_policy(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_policy = Policy.objects.create(**args)
      new_policy.save()
      return new_policy, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def update_policy(self, policy_id, args) -> (dict, MassEnergizeAPIError):
    try:
      policy = Policy.objects.filter(id=policy_id)
      if not policy:
        return None, InvalidResourceError()
      policy.update(**args)
      return policy.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def delete_policy(self, policy_id) -> (Policy, MassEnergizeAPIError):
    try:
      #find the policy
      policies_to_delete = Policy.objects.filter(id=policy_id)
      policies_to_delete.update(is_deleted=True, community=None)
      if not policies_to_delete:
        return None, InvalidResourceError()
      return policies_to_delete.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def copy_policy(self, policy_id) -> (Policy, MassEnergizeAPIError):
    try:
      #find the policy
      policy_to_copy = Policy.objects.filter(id=policy_id).first()
      if not policy_to_copy:
        return None, InvalidResourceError()
      
      new_policy = policy_to_copy
      new_policy.pk = None
      new_policy.name = policy_to_copy.name + ' Copy'
      new_policy.save()
      return new_policy, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def list_policies_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    policies = Policy.objects.filter(community__id = community_id)
    return policies, None


  def list_policies_for_super_admin(self):
    try:
      policies = Policy.objects.all()
      return policies, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))
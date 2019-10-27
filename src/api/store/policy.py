from database.models import Policy, UserProfile, Community
_main_.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse

class PolicyStore:
  def __init__(self):
    self.name = "Policy Store/DB"

  def get_policy_info(self, policy_id) -> (dict, MassEnergizeAPIError):
    policy = Policy.objects.get(id=policy_id)
    if not policy:
      return None, InvalidResourceError()
    return policy, None


  def list_policies(self, community_id) -> (list, MassEnergizeAPIError):
    policies = Policy.objects.filter(community__id=community_id)
    if not policies:
      return [], None
    return policies, None


  def create_policy(self, community_id, args) -> (dict, MassEnergizeAPIError):
    try:
      new_policy = Policy.objects.create(**args)
      new_policy.save()
      if community_id:
        community = Community.objects.get(id=community_id)
        community.policies.add(new_policy)
        community.save()
      return new_policy, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def update_policy(self, policy_id, args) -> (dict, MassEnergizeAPIError):
    try:
      print(args)
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
      policies_to_delete.update(is_deleted=True)
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
    policies = Policy.objects.filter(community__id = community_id, is_deleted=False)
    return policies, None


  def list_policies_for_super_admin(self):
    try:
      policies = Policy.objects.filter(is_deleted=False)
      return policies, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))
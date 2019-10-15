from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.utils.common import serialize, serialize_all
from api.store.policy import PolicyStore

class PolicyService:
  """
  Service Layer for all the policies
  """

  def __init__(self):
    self.store =  PolicyStore()

  def get_policy_info(self, policy_id) -> (dict, MassEnergizeAPIError):
    policy, err = self.store.get_policy_info(policy_id)
    if err:
      return None, err
    return serialize(policy), None

  def list_policies(self, policy_id) -> (list, MassEnergizeAPIError):
    policy, err = self.store.list_policies(policy_id)
    if err:
      return None, err
    return serialize(policy), None


  def create_policy(self, community_id, args) -> (dict, MassEnergizeAPIError):
    policy, err = self.store.create_policy(community_id, args)
    if err:
      return None, err
    return serialize(policy), None


  def update_policy(self, policy_id, args) -> (dict, MassEnergizeAPIError):
    policy, err = self.store.update_policy(policy_id, args)
    if err:
      return None, err
    return serialize(policy), None

  def delete_policy(self, policy_id) -> (dict, MassEnergizeAPIError):
    policy, err = self.store.delete_policy(policy_id)
    if err:
      return None, err
    return serialize(policy), None

  def copy_policy(self, policy_id) -> (dict, MassEnergizeAPIError):
    policy, err = self.store.copy_policy(policy_id)
    if err:
      return None, err
    return serialize(policy), None

  def list_policies_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    policies, err = self.store.list_policies_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(policies), None


  def list_policies_for_super_admin(self) -> (list, MassEnergizeAPIError):
    policies, err = self.store.list_policies_for_super_admin()
    if err:
      return None, err
    return serialize_all(policies, full=True), None

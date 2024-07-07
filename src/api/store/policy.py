from api.utils.api_utils import is_admin_of_community
from database.models import Policy, UserProfile, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, NotAuthorizedError, CustomMassenergizeError
from _main_.utils.context import Context
from django.db.models import Q
from _main_.utils.massenergize_logger import log
from typing import Tuple

class PolicyStore:
  def __init__(self):
    self.name = "Policy Store/DB"

  def get_policy_info(self, policy_id) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      policy = Policy.objects.get(id=policy_id)
      if not policy:
        return None, InvalidResourceError()
      return policy, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def list_policies(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      policies = Policy.objects.filter(is_deleted=False)
      return policies, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def create_policy(self,context, community_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      key = args.pop("key",{})
      new_policy = Policy.objects.create(**args, more_info ={"key":key})
      new_policy.save()
      if community_id:
        # if community admin check if is admin of the community_admin
        if not is_admin_of_community(context, community_id):
          return None, NotAuthorizedError()
        community = Community.objects.get(id=community_id)
        community.policies.add(new_policy)
        community.save()
      return new_policy, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def update_policy(self, context, policy_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      key = args.pop("key",{})
      community_id = args.pop("community_id", None)
      policy = Policy.objects.filter(id=policy_id)
      if not policy:
        return None, InvalidResourceError()
      
      # if community is passed, check if is admin of the community
      if community_id:
        if not is_admin_of_community(context, community_id):
            return None, NotAuthorizedError()
      policy.update(**args)
      policy: Policy = policy.first()
      policy.more_info = {**(policy.more_info or {}), "key":key}
      policy.save()
      if policy and community_id:
        community: Community = Community.objects.filter(pk=community_id).first()
        if community:
          community.policies.add(policy)
          community.save()
      return policy, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def delete_policy(self, context,policy_id) -> Tuple[Policy, MassEnergizeAPIError]:
    try:
      #find the policy
      policies_to_delete = Policy.objects.filter(id=policy_id)
      if not policies_to_delete:
        return None, InvalidResourceError()
      # this is only necessary if cadmins can perform CRUD operations on policies
      if not policies_to_delete.first().is_global:
        community = policies_to_delete.first().community_policies.all().first()
        if not is_admin_of_community(context,community.id):
            return None, NotAuthorizedError()
        
      policies_to_delete.update(is_deleted=True)
      return policies_to_delete.first(), None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def copy_policy(self, policy_id) -> Tuple[Policy, MassEnergizeAPIError]:
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
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_policies_for_community_admin(self, context: Context,_) -> Tuple[list, MassEnergizeAPIError]: 
    """
      For sadmins it should retrieve all policies as  before, but for community admins, 
      retrieve specific ones (Because we need TOS, Privacy Policy & MOUS) available even for cadmins
    """
    try:
      if context.user_is_super_admin:
        return self.list_policies_for_super_admin(context)
      
      policies = Policy.objects.filter(Q(more_info__key="terms-of-service") | Q(more_info__key="privacy-policy") | Q(more_info__key="mou")).distinct() 
      return policies, None
      
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)
    
  def list_policies_for_community_admin_old(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    try:
      if context.user_is_super_admin:
        return self.list_policies_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, CustomMassenergizeError("Sign in as a valid community admin")

      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        communities = [ag.community.policies for ag in admin_groups]
        policies = None
        for ag in admin_groups:
          if not policies:
            policies = ag.community.policies.all().filter(is_deleted=False)
          else:
            policies |= ag.community.policies.all().filter(is_deleted=False)

        return policies, None

      community: Community = Community.objects.get(pk=community_id)
      policies = community.policies.all().filter(is_deleted=False)
      policies |= Policy.objects.filter(is_global=True, is_deleted=False)
      return policies, None
 
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_policies_for_super_admin(self, context: Context):
    try:
      policies = Policy.objects.filter(is_deleted=False)
      return policies, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

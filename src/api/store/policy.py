from database.models import Policy, UserProfile, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from django.db.models import Q
from sentry_sdk import capture_message
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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_policies(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    try:
      policies = Policy.objects.filter(is_deleted=False)
      return policies, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_policy(self, community_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      new_policy = Policy.objects.create(**args)
      new_policy.save()
      if community_id:
        community = Community.objects.get(id=community_id)
        community.policies.add(new_policy)
        community.save()
      return new_policy, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def update_policy(self, policy_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      community_id = args.pop("community_id", None)
      policy = Policy.objects.filter(id=policy_id)
      if not policy:
        return None, InvalidResourceError()

      policy.update(**args)
      policy: Policy = policy.first()
      if policy and community_id:
        community: Community = Community.objects.filter(pk=community_id).first()
        if community:
          community.policies.add(policy)
          community.save()
      return policy, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def delete_policy(self, policy_id) -> Tuple[Policy, MassEnergizeAPIError]:
    try:
      #find the policy
      policies_to_delete = Policy.objects.filter(id=policy_id)
      policies_to_delete.update(is_deleted=True)
      if not policies_to_delete:
        return None, InvalidResourceError()
      return policies_to_delete.first(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def list_policies_for_community_admin(self, context: Context, community_id) -> Tuple[list, MassEnergizeAPIError]:
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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_policies_for_super_admin(self, context: Context):
    try:
      policies = Policy.objects.filter(is_deleted=False)
      return policies, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

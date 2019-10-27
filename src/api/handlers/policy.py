"""Handler file for all routes pertaining to policies"""

from _main_.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.policy import PolicyService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class PolicyHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = PolicyService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/policies.info", self.info()) 
    self.add("/policies.create", self.create())
    self.add("/policies.copy", self.copy())
    self.add("/policies.add", self.create())
    self.add("/policies.list", self.list())
    self.add("/policies.update", self.update())
    self.add("/policies.delete", self.delete())
    self.add("/policies.remove", self.delete())

    #admin routes
    self.add("/policies.listForCommunityAdmin", self.community_admin_list())
    self.add("/policies.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def policy_info_view(request) -> None: 
      args = get_request_contents(request)
      policy_id = args.pop('policy_id', None)
      policy_info, err = self.service.get_policy_info(policy_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return policy_info_view


  def create(self) -> function:
    def create_policy_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.pop('community_id', None)
      args.pop('is_global', None)
      policy_info, err = self.service.create_policy(community_id ,args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return create_policy_view


  def list(self) -> function:
    def list_policy_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      policy_info, err = self.service.list_policies(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return list_policy_view


  def copy(self) -> function:
    def copy_policy_view(request) -> None: 
      args = get_request_contents(request)
      policy_id = args.pop('policy_id', None)
      policy_info, err = self.service.copy_policy(policy_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return copy_policy_view


  def update(self) -> function:
    def update_policy_view(request) -> None: 
      args = get_request_contents(request)
      policy_id = args.pop('policy_id', None)
      policy_info, err = self.service.update_policy(policy_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return update_policy_view


  def delete(self) -> function:
    def delete_policy_view(request) -> None: 
      args = get_request_contents(request)
      policy_id = args.pop('policy_id', None)
      policy_info, err = self.service.delete_policy(policy_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return delete_policy_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.pop('community_id', None)
      policies, err = self.service.list_policies_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policies)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      policies, err = self.service.list_policies_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policies)
    return super_admin_list_view
"""Handler file for all routes pertaining to policies"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_bool
from api.services.policy import PolicyService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required

class PolicyHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = PolicyService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/policies.info", self.info) 
    self.add("/policies.create", self.create)
    self.add("/policies.copy", self.copy)
    self.add("/policies.add", self.create)
    self.add("/policies.list", self.list)
    self.add("/policies.update", self.update)
    self.add("/policies.delete", self.delete)
    self.add("/policies.remove", self.delete)

    #admin routes
    self.add("/policies.listForCommunityAdmin", self.community_admin_list)
    self.add("/policies.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    policy_id = args.pop('policy_id', None)
    policy_info, err = self.service.get_policy_info(policy_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=policy_info)

  @admins_only
  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    is_global = args.pop('is_global', None)
    if is_global:
      args["is_global"] = parse_bool(is_global)
    policy_info, err = self.service.create_policy(community_id ,args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=policy_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    policy_info, err = self.service.list_policies(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=policy_info)

  @admins_only
  def copy(self, request):
    context: Context = request.context
    args: dict = context.args
    policy_id = args.pop('policy_id', None)
    policy_info, err = self.service.copy_policy(policy_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=policy_info)

  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    policy_id = args.pop('policy_id', None)
    is_global = args.pop('is_global', None)
    if is_global:
      args["is_global"] = parse_bool(is_global)
    policy_info, err = self.service.update_policy(policy_id, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=policy_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    policy_id = args.pop('policy_id', None)
    policy_info, err = self.service.delete_policy(policy_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=policy_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    policies, err = self.service.list_policies_for_community_admin(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=policies)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    policies, err = self.service.list_policies_for_super_admin(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=policies)

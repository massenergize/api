"""Handler file for all routes pertaining to actions"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import parse_list, parse_bool, check_length, rename_field
from api.services.action import ActionService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required


class ActionHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = ActionService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/actions.info", self.info) 
    self.add("/actions.create", self.create)
    self.add("/actions.add", self.create)
    self.add("/actions.list", self.list)
    self.add("/actions.update", self.update)
    self.add("/actions.delete", self.delete)
    self.add("/actions.remove", self.delete)
    self.add("/actions.copy", self.copy)

    #admin routes
    self.add("/actions.listForCommunityAdmin", self.community_admin_list)
    self.add("/actions.listForSuperAdmin", self.super_admin_list)


  def info(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args: dict = context.args
    # verify the body of the incoming request
    v: Validator = Validator()
    v.expect("action_id", str, is_required=True)
    v.rename("id", "action_id")
    args, err = v.verify(args, strict=True)
    if err:
      return err
    
    action_id = args.pop('action_id', None)
    action_info, err = self.service.get_action_info(context, action_id)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


  @admins_only
  def create(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("community_id", int, is_required=False)
      .expect("calculator_action", int, is_required=False)
      .expect("image", "file", is_required=False, options={"is_logo": True})
      .expect("title", str, is_required=False, options={"min_length": 4, "max_length": 40})
      .expect("rank", int, is_required=False)
      .expect("is_global", bool, is_required=False)
      .expect("is_published", bool, is_required=False)
      .expect("tags", list, is_required=False)
      .expect("vendors", list, is_required=False)
    )

    args, err = self.validator.verify(args)
    if err:
      return err

    action_info, err = self.service.create_action(context, args)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


  def list(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    subdomain = args.pop('subdomain', None)
    action_info, err = self.service.list_actions(context, community_id, subdomain)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


  @admins_only
  def update(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("action_id", int, is_required=True)
      .expect("title", str, is_required=False, options={"min_length": 4, "max_length": 40})
      .expect("calculator_action", int, is_required=False)
      .expect("image", "file", is_required=False, options={"is_logo": True})
      .expect("rank", int, is_required=False)
      .expect("is_global", bool, is_required=False)
      .expect("is_published", bool, is_required=False)
      .expect("tags", list, is_required=False)
      .expect("vendors", list, is_required=False)
    )

    args, err = self.validator.verify(args)
    if err:
      return err
    
    action_info, err = self.service.update_action(context, args)
    if err:
      return err      
      
    return MassenergizeResponse(data=action_info)


  @admins_only
  def copy(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args: dict = context.args
    action_id = args.pop('action_id', None)
    action_info, err = self.service.copy_action(context, action_id)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


  @admins_only
  def delete(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args: dict = context.args
    action_id = args.pop('action_id', None)
    action_info, err = self.service.delete_action(context, action_id)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


  @admins_only
  def community_admin_list(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    actions, err = self.service.list_actions_for_community_admin(context, community_id)
    if err:
      return err
    return MassenergizeResponse(data=actions)


  @super_admins_only
  def super_admin_list(self, request) -> MassenergizeResponse: 
    context: Context = request.context
    args: dict = context.args
    actions, err = self.service.list_actions_for_super_admin(context)
    if err:
      return err
    return MassenergizeResponse(data=actions)

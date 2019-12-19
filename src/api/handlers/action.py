"""Handler file for all routes pertaining to actions"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import parse_list, parse_bool, check_length, rename_field
from api.services.action import ActionService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator

class ActionHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = ActionService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/actions.info", self.info()) 
    self.add("/actions.create", self.create())
    self.add("/actions.add", self.create())
    self.add("/actions.list", self.list())
    self.add("/actions.update", self.update())
    self.add("/actions.delete", self.delete())
    self.add("/actions.remove", self.delete())
    self.add("/actions.copy", self.copy())

    #admin routes
    self.add("/actions.listForCommunityAdmin", self.community_admin_list())
    self.add("/actions.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def action_info_view(request) -> None: 
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
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return action_info_view


  def create(self) -> function:
    def create_action_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      success, err = check_length(args, 'title', min_length=4, max_length=25)
      if not success:
        return MassenergizeResponse(error=str(err))
      community_id = args.pop('community_id', None)
      args['tags'] = parse_list(args.pop('tags', []))
      args['vendors'] = parse_list(args.pop('vendors', []))
      args['is_global'] = parse_bool(args.pop('is_global', False))
      args['is_published'] = parse_bool(args.pop('is_published', False))
      action_info, err = self.service.create_action(context, community_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return create_action_view


  def list(self) -> function:
    def list_action_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop('community_id', None)
      subdomain = args.pop('subdomain', None)
      action_info, err = self.service.list_actions(context, community_id, subdomain)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return list_action_view


  def update(self) -> function:
    def update_action_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      success, err = check_length(args, 'title', min_length=4, max_length=40)
      if not success:
        return MassenergizeResponse(error=str(err))
      args = rename_field(args, 'action_id', 'id')
      args['tags'] = parse_list(args.pop('tags', []))
      args['vendors'] = parse_list(args.pop('vendors', []))
      args['is_global'] = parse_bool(args.pop('is_global', False))
      args['is_published'] = parse_bool(args.pop('is_published', False))
      action_id = args.pop('id', None)
      action_info, err = self.service.update_action(context, action_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)      
        
      return MassenergizeResponse(data=action_info)
    return update_action_view

  def copy(self) -> function:
    def copy_action_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      action_id = args.pop('action_id', None)
      action_info, err = self.service.copy_action(context, action_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return copy_action_view

    
  def delete(self) -> function:
    def delete_action_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      action_id = args.pop('action_id', None)
      action_info, err = self.service.delete_action(context, action_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return delete_action_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop("community_id", None)
      actions, err = self.service.list_actions_for_community_admin(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      actions, err = self.service.list_actions_for_super_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions)
    return super_admin_list_view
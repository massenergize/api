"""Handler file for all routes pertaining to actions"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_list, parse_bool, check_length, rename_field
from api.services.action import ActionService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

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
      args = get_request_contents(request)
      action_id = args.pop('action_id', None)
      action_info, err = self.service.get_action_info(action_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return action_info_view


  def create(self) -> function:
    def create_action_view(request) -> None: 
      args = get_request_contents(request)
      success, err = check_length(args, 'title', min_length=5, max_length=25)
      if not success:
        return MassenergizeResponse(error=str(err))
      community_id = args.pop('community_id', None)
      args['tags'] = parse_list(args.pop('tags', []))
      args['vendors'] = parse_list(args.pop('vendors', []))
      args['is_global'] = parse_bool(args.pop('vendors', False))
      args['is_published'] = parse_bool(args.pop('is_published', False))
      action_info, err = self.service.create_action(community_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return create_action_view


  def list(self) -> function:
    def list_action_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.pop('community_id', None)
      subdomain = args.pop('subdomain', None)
      action_info, err = self.service.list_actions(community_id, subdomain)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return list_action_view


  def update(self) -> function:
    def update_action_view(request) -> None: 
      args = get_request_contents(request)
      success, err = check_length(args, 'title', min_length=5, max_length=25)
      if not success:
        return MassenergizeResponse(error=str(err))
      args = rename_field(args, 'action_id', 'id')
      args['tags'] = parse_list(args.pop('tags', []))
      args['vendors'] = parse_list(args.pop('vendors', []))
      args['is_global'] = parse_bool(args.pop('is_global', False))
      args['is_published'] = parse_bool(args.pop('is_published', False))
      action_id = args.pop('id', None)
      action_info, err = self.service.update_action(action_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)      
        
      return MassenergizeResponse(data=action_info)
    return update_action_view

  def copy(self) -> function:
    def copy_action_view(request) -> None: 
      args = get_request_contents(request)
      action_id = args.pop('action_id', None)
      action_info, err = self.service.copy_action(action_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return copy_action_view

    
  def delete(self) -> function:
    def delete_action_view(request) -> None: 
      args = get_request_contents(request)
      action_id = args.pop('action_id', None)
      action_info, err = self.service.delete_action(action_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=action_info)
    return delete_action_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      actions, err = self.service.list_actions_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      actions, err = self.service.list_actions_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions)
    return super_admin_list_view
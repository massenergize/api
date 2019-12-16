"""Handler file for all routes pertaining to communities"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_location, parse_bool, check_length, rename_field
from api.services.community import CommunityService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator

#TODO: install middleware to catch authz violations
#TODO: add logger

class CommunityHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = CommunityService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/communities.info", self.info()) 
    self.add("/communities.create", self.create())
    self.add("/communities.add", self.create())
    self.add("/communities.list", self.list())
    self.add("/communities.update", self.update())
    self.add("/communities.delete", self.delete())
    self.add("/communities.remove", self.delete())
    self.add("/communities.graphs", self.info())
    self.add("/communities.data", self.info())
    self.add("/communities.join", self.join())
    self.add("/communities.leave", self.leave())

    #admin routes
    self.add("/communities.listForCommunityAdmin", self.community_admin_list())
    self.add("/communities.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def community_info_view(request) -> None:
      context: Context = request.context
      args: dict = context.args
      args = rename_field(args, 'community_id', 'id')
      community_info, err = self.service.get_community_info(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return community_info_view

  def join(self) -> function:
    def join_community_view(request) -> None:
      context: Context = request.context
      args: dict = context.args
      community_info, err = self.service.join_community(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return join_community_view

  def leave(self) -> function:
    def leave_community_view(request) -> None:
      context: Context = request.context
      args: dict = context.args
      community_info, err = self.service.leave_community(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return leave_community_view


  def create(self) -> function:
    def create_community_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body()

      args['accepted_terms_and_conditions'] = parse_bool(args.pop('accepted_terms_and_conditions', None))
      if not args['accepted_terms_and_conditions']:
        return MassenergizeResponse(error="Please accept the terms and conditions")
      
      ok, err = check_length(args, 'name', 3, 25)
      if not ok:
        return MassenergizeResponse(error=str(err))
      
      ok, err = check_length(args, 'subdomain', 4, 20)
      if not ok:
        return MassenergizeResponse(error=str(err))
        
      args['is_geographically_focused'] = parse_bool(args.pop('is_geographically_focused', None))
      args['is_published'] = parse_bool(args.pop('is_published', None))
      args['is_approved'] = parse_bool(args.pop('is_approved', None))

      args = rename_field(args, 'image', 'logo')
      args = parse_location(args)
      if not args['is_geographically_focused']:
        args.pop('location', None)
      
      community_info, err = self.service.create_community(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return create_community_view


  def list(self) -> function:
    def list_community_view(request) -> None: 
      context: Context  = request.context
      args = context.args
      community_info, err = self.service.list_communities(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return list_community_view


  def update(self) -> function:
    def update_community_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      args = rename_field(args, 'community_id', 'id')
      community_id = args.pop('id', None)
      if not community_id:
        return MassenergizeResponse(error='Please provide an ID')

      if(args.get('name', None)):
        ok, err = check_length(args, 'name', 3, 25)
        if not ok:
          return MassenergizeResponse(error=str(err))
      
      if(args.get('subdomain', None)):
        ok, err = check_length(args, 'subdomain', 4, 20)
        if not ok:
          return MassenergizeResponse(error=str(err))

      if(args.get('is_geographically_focused', False)):
        args['is_geographically_focused'] = parse_bool(args.pop('is_geographically_focused', False))
      if(args.get('is_published', None)):
        args['is_published'] = parse_bool(args.pop('is_published', None))
      if(args.get('is_approved', None)):
        args['is_approved'] = parse_bool(args.pop('is_approved', None))

      args = rename_field(args, 'image', 'logo')
      args = parse_location(args)
      community_info, err = self.service.update_community(community_id ,args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return update_community_view


  def delete(self) -> function:
    def delete_community_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      args = rename_field(args, 'community_id', 'id')
      community_info, err = self.service.delete_community(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return delete_community_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body()
      communities, err = self.service.list_communities_for_community_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=communities)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body()
      communities, err = self.service.list_communities_for_super_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=communities)
    return super_admin_list_view


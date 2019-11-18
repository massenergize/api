"""Handler file for all routes pertaining to graphs"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_list, parse_bool, check_length, rename_field, parse_int
from api.services.graph import GraphService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator


class GraphHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = GraphService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/graphs.info", self.info()) 
    self.add("/graphs.create", self.create())
    self.add("/graphs.add", self.create())
    self.add("/graphs.list", self.list())
    self.add("/graphs.actions.completed", self.graph_actions_completed())
    self.add("/graphs.communities.impact", self.graph_community_impact())
    self.add("/graphs.update", self.update())
    self.add("/graphs.data.update", self.update())
    self.add("/graphs.delete", self.delete())
    self.add("/graphs.remove", self.delete())

    #admin routes
    self.add("/graphs.listForCommunityAdmin", self.community_admin_list())
    self.add("/graphs.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def graph_info_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      args = rename_field(args, 'graph_id', 'id')
      graph_info, err = self.service.get_graph_info(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=graph_info)
    return graph_info_view


  def create(self) -> function:
    def create_graph_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      args = rename_field(args, 'community_id', 'community')
      args = rename_field(args, 'action_id', 'action')
      args = rename_field(args, 'vendor_id', 'vendor')
      args['tags'] = parse_list(args.get('tags', []))

      is_approved = args.pop("is_approved", None)
      if is_approved:
        args["is_approved"] = parse_bool(is_approved)
      is_published = args.get("is_published", None)
      if is_published:
        args["is_published"] = parse_bool(is_published)
      
      graph_info, err = self.service.create_graph(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=graph_info)
    return create_graph_view


  def list(self) -> function:
    def list_graph_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args

      # verify the body of the incoming request
      v: Validator = Validator()
      v.expect("community_id", str, False)
      v.expect("subdomain", str, False)
      v.rename("id", "community_id")
      args, err = v.verify(args, strict=True)
      if err:
        return err
      
      graph_info, err = self.service.list_graphs(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=graph_info)
    return list_graph_view

  def graph_actions_completed(self) -> function:
    def graph_actions_completed_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args

      # verify the body of the incoming request
      v: Validator = Validator()
      v.expect("community_id", str, False)
      v.expect("subdomain", str, False)
      v.rename("id", "community_id")
      args, err = v.verify(args, strict=True)
      if err:
        return err
      
      graph_info, err = self.service.graph_actions_completed(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=graph_info)
    return graph_actions_completed_view

  def graph_community_impact(self) -> function:
    def graph_community_impact_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args

      # verify the body of the incoming request
      v: Validator = Validator()
      v.expect("community_id", str, False)
      v.expect("subdomain", str, False)
      v.rename("id", "community_id")
      args, err = v.verify(args, strict=True)
      if err:
        return err
      
      graph_info, err = self.service.graph_community_impact(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=graph_info)
    return graph_community_impact_view


  def update(self) -> function:
    def update_graph_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      graph_info, err = self.service.update_graph(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=graph_info)
    return update_graph_view


  def delete(self) -> function:
    def delete_graph_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      graph_id = args.pop('graph_id', None)
      graph_info, err = self.service.delete_graph(context, graph_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=graph_info)
    return delete_graph_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop("community_id", None)
      graphs, err = self.service.list_graphs_for_community_admin(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=graphs)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      graphs, err = self.service.list_graphs_for_super_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=graphs)
    return super_admin_list_view
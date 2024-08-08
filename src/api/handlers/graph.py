"""Handler file for all routes pertaining to graphs"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import parse_list, parse_bool, rename_field, parse_int
from api.services.graph import GraphService
from _main_.utils.massenergize_response import MassenergizeResponse
#from types import FunctionType as function
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only, login_required


class GraphHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = GraphService()
    self.registerRoutes()
    # understand data problem
    self.debug_data_fix()

  def registerRoutes(self) -> None:
    self.add("/graphs.info", self.info) 
    self.add("/graphs.create", self.create)
    self.add("/graphs.add", self.create)
    self.add("/graphs.list", self.list)
    self.add("/graphs.actions.completed", self.graph_actions_completed)
    self.add("/graphs.actions.completed.byTeam", self.graph_actions_completed_by_team)
    self.add("/graphs.communities.impact", self.graph_community_impact)
    self.add("/graphs.update", self.update)
    self.add("/graphs.data.update", self.update)
    self.add("/graphs.delete", self.delete)
    self.add("/graphs.remove", self.delete)

    self.add("/data.update", self.update_data)
    self.add("/data.delete", self.delete_data)

    #admin routes
    self.add("/graphs.listForCommunityAdmin", self.community_admin_list)
    self.add("/graphs.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'graph_id', 'id')
    graph_info, err = self.service.get_graph_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=graph_info)

  @admins_only
  def create(self, request):
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
      return err
    return MassenergizeResponse(data=graph_info)

  @admins_only
  def list(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    v = self.validator
    v.expect("community_id", str, False)
    v.expect("subdomain", str, False)
    v.rename("id", "community_id")
    args, err = v.verify(args, strict=True)
    if err:
      return err
    
    graph_info, err = self.service.list_graphs(context, args)
    if err:
      return err
    return MassenergizeResponse(data=graph_info)

  
  def graph_actions_completed(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    v = self.validator
    v.expect("community_id", str, False)
    v.expect("subdomain", str, False)
    v.rename("id", "community_id")
    args, err = v.verify(args, strict=True)
    if err:
      return err
    
    graph_info, err = self.service.graph_actions_completed(context, args)
    if err:
      return err
    return MassenergizeResponse(data=graph_info)


  def graph_actions_completed_by_team(self, request):
    context: Context = request.context
    args: dict = context.args

    v = self.validator
    v.expect("team_id", str, False)
    args, err = v.verify(args, strict=True)
    if err:
      return err

    graph_info, err = self.service.graph_actions_completed_by_team(context, args)
    if err:
      return err
    return MassenergizeResponse(data=graph_info)


  def graph_community_impact(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    v = self.validator
    v.expect("community_id", str, False)
    v.expect("subdomain", str, False)
    v.rename("id", "community_id")
    args, err = v.verify(args, strict=True)
    if err:
      return err
    
    graph_info, err = self.service.graph_community_impact(context, args)
    if err:
      return err
    return MassenergizeResponse(data=graph_info)

  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args

    # 9/29/21 moved from home_page_settings route
    args['goal'] = {
      'initial_number_of_actions': parse_int(args.pop('initial_number_of_actions', 0)) or 0,
      'target_number_of_actions': parse_int(args.pop('target_number_of_actions', 0)) or 0,
      'initial_number_of_households': parse_int(args.pop('initial_number_of_households', 0)) or 0,
      'target_number_of_households': parse_int(args.pop('target_number_of_households', 0)) or 0,
      'initial_carbon_footprint_reduction': parse_int(args.pop('initial_carbon_footprint_reduction', 0)) or 0,
      'target_carbon_footprint_reduction': parse_int(args.pop('target_carbon_footprint_reduction', 0)) or 0,
    }
    args.pop('attained_number_of_households', None)
    args.pop('attained_number_of_actions', None)
    args.pop('attained_carbon_footprint_reduction', None)
    args.pop('organic_attained_number_of_households', None)
    args.pop('organic_attained_number_of_actions', None)
    args.pop('organic_attained_carbon_footprint_reduction', None)

    graph_info, err = self.service.update_graph(context, args)
    if err:
      return err
    return MassenergizeResponse(data=graph_info)

  @login_required
  def update_data(self, request):
    context: Context = request.context
    args: dict = context.args
    graph_info, err = self.service.update_data(context, args)
    if err:
      return err
    return MassenergizeResponse(data=graph_info)


  @admins_only
  def delete_data(self, request):
    context: Context = request.context
    args: dict = context.args
    data_id = args.get('data_id', None)
    if not data_id:
      return MassenergizeResponse(error="invalid_resource")
    graph_info, err = self.service.delete_data(context, args)
    if err:
      return err
    return MassenergizeResponse(data=graph_info)


  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    graph_id = args.pop('graph_id', None)
    graph_info, err = self.service.delete_graph(context, graph_id)
    if err:
      return err
    return MassenergizeResponse(data=graph_info)


  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    graphs, err = self.service.list_graphs_for_community_admin(context, community_id)
    if err:
      return err
    return MassenergizeResponse(data=graphs)


  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    graphs, err = self.service.list_graphs_for_super_admin(context)
    if err:
      return err
    return MassenergizeResponse(data=graphs)

  def debug_data_fix(self) -> None:
    self.service.debug_data_fix()
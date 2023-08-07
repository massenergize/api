"""Handler file for all routes pertaining to communities"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import parse_location, parse_bool, check_length, rename_field
from api.services.community import CommunityService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from api.decorators import admins_only, super_admins_only, login_required
from _main_.utils.massenergize_errors import CustomMassenergizeError

class CommunityHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = CommunityService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/communities.info", self.info) 
    self.add("/communities.create", self.create)
    self.add("/communities.add", self.create)
    self.add("/communities.list", self.list)
    self.add("/communities.update", self.update)
    self.add("/communities.delete", self.delete)
    self.add("/communities.remove", self.delete)
    self.add("/communities.graphs", self.info)
    self.add("/communities.data", self.info)
    self.add("/communities.join", self.join)
    self.add("/communities.leave", self.leave)
    self.add("/communities.custom.website.add", self.add_custom_website)
    self.add("/communities.actions.completed", self.actions_completed)

    #admin routes
    self.add("/communities.listForCommunityAdmin", self.community_admin_list)
    self.add("/communities.others.listForCommunityAdmin", self.list_other_communities_for_cadmin)
    self.add("/communities.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('community_id', int)
    self.validator.expect('subdomain', str)
    self.validator.rename('id', 'community_id')   
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    community_info, err = self.service.get_community_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=community_info)


  @login_required
  def join(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    # self.validator.expect("user_id", str, is_required=True) # the API already knows the user through the context
    self.validator.expect("community_id", int, is_required=True)
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    # test for perms
    # executor_id = context.user_id

    # if executor_id == args.get("user_id", None) or context.user_is_admin():
    community_info, err = self.service.join_community(context, args)
    # else:
    #   return CustomMassenergizeError("Executor doesn't have sufficient permissions to use community.join on this user")
    if err:
      return err
    return MassenergizeResponse(data=community_info)


  @login_required
  def leave(self, request):
    context: Context = request.context
    args: dict = context.args

    # verify the body of the incoming request
    # self.validator.expect("user_id", str, is_required=True)
    self.validator.expect("community_id", int, is_required=True)
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    # test for perms
    # executor_id = context.user_id

    # if executor_id == args.get("user_id", None):
    community_info, err = self.service.leave_community(context, args)
    # else:
    #   return CustomMassenergizeError("Executor doesn't have sufficient permissions to use community.leave on this user")

    if err:
      return err
    return MassenergizeResponse(data=community_info)


  @super_admins_only
  def create(self, request):
    context: Context  = request.context
    args = context.get_request_body()

    args['accepted_terms_and_conditions'] = parse_bool(args.pop('accepted_terms_and_conditions', None))
    if not args['accepted_terms_and_conditions']:
      return CustomMassenergizeError("Please accept the terms and conditions")
    
    ok, err = check_length(args, 'name', 3, 25)
    if not ok:
      return err
    
    ok, err = check_length(args, 'subdomain', 4, 20)
    if not ok:
      return err
      
    args['is_geographically_focused'] = parse_bool(args.pop('is_geographically_focused', False))
    args['is_demo'] = parse_bool(args.pop('is_demo', False))
    args['is_published'] = parse_bool(args.pop('is_published', False))
    args['is_approved'] = parse_bool(args.pop('is_approved', False))

    args = rename_field(args, 'image', 'logo')

    args = parse_location(args)
    if not args['is_geographically_focused']:
      args.pop('location', None)
    
    community_info, err = self.service.create_community(context, args)
    if err:
      return err
    return MassenergizeResponse(data=community_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("zipcode", str, is_required=False)
    self.validator.expect("max_distance", int, is_required=False)

    args, err = self.validator.verify(args)
    if err:
        return err

    community_info, err = self.service.list_communities(context, args)
    if err:
        return err
    return MassenergizeResponse(data=community_info)

  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args

    args = rename_field(args, 'id', 'community_id')
    community_id = args.get('community_id', None)
    if not community_id:
      return CustomMassenergizeError('Please provide an ID')

    if(args.get('name', None)):
      ok, err = check_length(args, 'name', 3, 25)
      if not ok:
        return err
    
    if(args.get('subdomain', None)):
      ok, err = check_length(args, 'subdomain', 4, 20)
      if not ok:
        return err

    if(args.get('owner_name', None)):
      args['owner_name'] = args.get('owner_name', None)
    if(args.get('owner_email', None)):
      args['owner_email'] = args.get('owner_email', None)
    if(args.get('owner_phone_number', None)):
      args['owner_phone_number'] = args.get('owner_phone_number', None)
    
    if(args.get('is_geographically_focused', False)):
      args['is_geographically_focused'] = parse_bool(args.pop('is_geographically_focused', False))
    if(args.get('is_demo', False)):
      args['is_demo'] = parse_bool(args.pop('is_demo', False))
    if(args.get('is_published', None)):
      args['is_published'] = parse_bool(args.pop('is_published', None))
    if(args.get('is_approved', None)):
      args['is_approved'] = parse_bool(args.pop('is_approved', None))

    # eliminate if accidently provided
    remove = args.pop('facebook_link', None)
    remove = args.pop('twitter_link', None)
    remove = args.pop('instagram_link', None)

    args = rename_field(args, 'image', 'logo')
    args = parse_location(args)

    community_info, err = self.service.update_community(context, args)
    if err:
      return err
    return MassenergizeResponse(data=community_info)


  @super_admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("id", int, is_required=True)
    self.validator.rename("community_id", "id")

    args, err = self.validator.verify(args)
    if err:
      return err

    community_info, err = self.service.delete_community(args,context)
    if err:
      return err
    return MassenergizeResponse(data=community_info)


  @admins_only 
  def list_other_communities_for_cadmin(self, request):
    context: Context  = request.context
  
    communities, err = self.service.list_other_communities_for_cadmin(context)
    if err:
      return err
    return MassenergizeResponse(data=communities)

  @admins_only
  def community_admin_list(self, request):  
    context: Context  = request.context
    #args = context.get_request_body()
    communities, err = self.service.list_communities_for_community_admin(context)
    if err:
      return err
    return MassenergizeResponse(data=communities)


  @super_admins_only
  def super_admin_list(self, request):
    context: Context  = request.context
    #args = context.get_request_body()
    communities, err = self.service.list_communities_for_super_admin(context)
    if err:
      return err
    return MassenergizeResponse(data=communities)


  @admins_only
  def add_custom_website(self, request):
    context: Context  = request.context
    args: dict = context.args
    # verify the body of the incoming request
    self.validator.expect("website", str, is_required=True)
    self.validator.expect("subdomain", str)
    self.validator.expect("community_id", int)
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err

    communities, err = self.service.add_custom_website(context, args)
    if err:
      return err
    return MassenergizeResponse(data=communities)

  def actions_completed(self, request): 
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('community_id', int, is_required=False)
    self.validator.expect('subdomain', str, is_required=False)
    self.validator.expect('communities', "str_list", is_required=False)
    self.validator.expect('actions', "str_list", is_required=False)
    self.validator.expect('time_range', str, is_required=False)
    self.validator.expect('end_date', str, is_required=False)
    self.validator.expect('start_date', str, is_required=False)
    args, err = self.validator.verify(args)
    if err:
      return err

    community_completed_actions, err = self.service.list_actions_completed(context, args)
    if err:
      return err
    return MassenergizeResponse(data=community_completed_actions)



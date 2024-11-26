"""Handler file for all routes pertaining to actions"""

from _main_.utils.route_handler import RouteHandler
from api.services.action import ActionService
from _main_.utils.massenergize_response import MassenergizeResponse
#from types import FunctionType as function
from _main_.utils.context import Context
from api.decorators import admins_only, cached_request, super_admins_only, login_required
from api.store.common import expect_media_fields


class ActionHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = ActionService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/actions.info", self.info) 
    self.add("/actions.create", self.create)
    self.add("/actions.add", self.submit)
    self.add("/actions.submit", self.submit)
    self.add("/actions.list", self.list)
    self.add("/actions.update", self.update)
    self.add("/actions.delete", self.delete)
    self.add("/actions.remove", self.delete)
    self.add("/actions.rank", self.rank)
    self.add("/actions.copy", self.copy)

    #admin routes
    self.add("/actions.listForCommunityAdmin", self.community_admin_list)
    self.add("/actions.listForSuperAdmin", self.super_admin_list)


  def info(self, request): 
    context: Context = request.context
    args: dict = context.args
    
    # verify the body of the incoming request
    self.validator.expect("id", str, is_required=True)
    self.validator.rename("action_id", "id")
    args, err = self.validator.verify(args, strict=True)
    if err:
      return err
    
    action_info, err = self.service.get_action_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


  @admins_only
  def create(self, request): 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("community_id", int, is_required=False)
      .expect("calculator_action", int, is_required=False)
      .expect("image", "str_list", is_required=False, options={"is_logo": True})
      .expect("title", str, is_required=True, options={"min_length": 4, "max_length": 40})
      .expect("rank", int, is_required=False)
      .expect("is_global", bool, is_required=False)
      .expect("is_published", bool, is_required=False)
      .expect('is_approved', bool)
      .expect("tags", list, is_required=False)
      .expect("vendors", list, is_required=False)
    )
    args, err = self.validator.verify(args)
    if err:
      return err

    # not a user submitted action
    args["is_approved"] = args.pop("is_approved", True)

    action_info, err = self.service.create_action(context, args)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


# same as create, except this is for user submitted actions
  @login_required
  def submit(self, request): 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("title", str, is_required=True, options={"min_length": 4, "max_length": 40})
      .expect("community_id", int, is_required=True) #fromContext
      .expect("image", "file", is_required=False, options={"is_logo": True})
      .expect("vendors", list, is_required=False)
      .expect("action_id", str, is_required=False)
    )
    expect_media_fields(self)

    args, err = self.validator.verify(args)
    if err:
      return err

    # user submitted action, so notify the community admins
    user_submitted = True
  
    is_edit = args.get("action_id", None)

    if is_edit:
      action_info, err = self.service.update_action(context, args, user_submitted)
    else:
      args["is_approved"] = False
      action_info, err = self.service.create_action(context, args, user_submitted)
    if err:
      return err
    return MassenergizeResponse(data=action_info)

  @cached_request
  def list(self, request): 
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('community_id', int, is_required=False)
    self.validator.expect('subdomain', str, is_required=False)



    args, err = self.validator.verify(args)
    if err:
      return err

    action_info, err = self.service.list_actions(context, args)

    if err:
      return err
    return MassenergizeResponse(data=action_info)



  # @admins_only
  # changed to @Login_Required so I can edit the action as the creator and admin
  @login_required
  def update(self, request): 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("action_id", int, is_required=True)
      .expect("title", str, is_required=False, options={"min_length": 4, "max_length": 40})
      .expect("calculator_action", int, is_required=False)
      .expect("image", "str_list", is_required=False, options={"is_logo": True})
      .expect("rank", int, is_required=False)
      .expect("is_global", bool, is_required=False)
      .expect("is_approved", bool, is_required=False)
      .expect("is_published", bool, is_required=False)
      .expect("tags", list, is_required=False)
      .expect("vendors", list, is_required=False)
    )

    expect_media_fields(self)

    args, err = self.validator.verify(args)
    if err:
      return err
    
    action_info, err = self.service.update_action(context, args)
    if err:
      return err      
      
    return MassenergizeResponse(data=action_info)


  @admins_only
  def rank(self, request): 
    context: Context = request.context
    args = context.get_request_body() 
    (self.validator
      .expect("id", int, is_required=True)
      .expect("rank", int, is_required=True)
      .rename("action_id", "id")
    )

    args, err = self.validator.verify(args)
    if err:
      return err
    
    action_info, err = self.service.rank_action(args,context)
    if err:
      return err      
      
    return MassenergizeResponse(data=action_info)


  @admins_only
  def copy(self, request): 
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("action_id", int, None)
    args, err = self.validator.verify(args)
    if err:
      return err   

    action_info, err = self.service.copy_action(context, args)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


  @admins_only
  def delete(self, request): 
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("action_id", int, is_required=True)
    args, err = self.validator.verify(args)
    if err:
      return err   

    action_info, err = self.service.delete_action(context, args)
    if err:
      return err
    return MassenergizeResponse(data=action_info)


  @admins_only
  def community_admin_list(self, request): 
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("community_id", int, is_required=False)
    self.validator.expect("action_ids", list, is_required=False)
    args, err = self.validator.verify(args)
    if err:
      return err

    actions, err = self.service.list_actions_for_community_admin(context, args)
    if err:
      return err
    return MassenergizeResponse(data=actions)


  @super_admins_only
  def super_admin_list(self, request): 
    context: Context = request.context
    args: dict = context.args
    self.validator.expect("community_id", int, is_required=False)
    self.validator.expect("action_ids", list, is_required=False)
    args, err = self.validator.verify(args)
    if err:
      return err
    actions, err = self.service.list_actions_for_super_admin(context)
    if err:
      return err
    return MassenergizeResponse(data=actions)

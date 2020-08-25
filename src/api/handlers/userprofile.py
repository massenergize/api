"""Handler file for all routes pertaining to users"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.userprofile import UserService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator



class UserHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = UserService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/users.info", self.info) 
    self.add("/users.create", self.create)
    self.add("/users.add", self.create)
    self.add("/users.list", self.list)
    self.add("/users.update", self.update)
    self.add("/users.delete", self.delete)
    self.add("/users.remove", self.delete)
    self.add("/users.actions.completed.add", self.add_action_completed)
    self.add("/users.actions.todo.add", self.add_action_todo)
    self.add("/users.actions.todo.list", self.list_actions_todo)
    self.add("/users.actions.completed.list", self.list_actions_completed)
    self.add("/users.actions.remove", self.remove_user_action)
    self.add("/users.households.add", self.add_household)
    self.add("/users.households.edit", self.edit_household)
    self.add("/users.households.remove", self.remove_household)
    self.add("/users.households.list", self.list_households)
    self.add("/users.events.list", self.list_events)


    #admin routes
    self.add("/users.listForCommunityAdmin", self.community_admin_list)
    self.add("/users.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.get_user_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    validator: Validator = Validator()
    args, err = (validator
      .expect("accepts_terms_and_conditions", bool, is_required=True)
      .expect("email", str, is_required=True)
      .expect("full_name", str, is_required=True)
      .expect("preferred_name", str, is_required=True)
      .expect("is_vendor", bool, is_required=True)
      .verify(context.args)
    )
    if err:
      return err
    user_info, err = self.service.create_user(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    #user_id = args.pop('user_id', None)
    user_info, err = self.service.list_users(community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def list_actions_todo(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.list_actions_todo(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  def list_actions_completed(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.list_actions_completed(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def remove_user_action(self, request):
    context: Context = request.context
    args: dict = context.args
    user_action_id = args.get('user_action_id', None)
    if not user_action_id:
      return MassenergizeResponse(error="invalid_resource")

    user_info, err = self.service.remove_user_action(context, user_action_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.update_user(args.get("id", None), args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    user_id = args.get("id", None) or args.get("user_id", None)
    user_info, err = self.service.delete_user(context, user_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    users, err = self.service.list_users_for_community_admin(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=users)


  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    users, err = self.service.list_users_for_super_admin(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=users)

  def add_action_todo(self, request):
    context: Context = request.context
    
    validator: Validator = Validator()
    args, err = (validator
      .expect("action_id", str, is_required=True)
      .expect("household_id", str, is_required=False)
      .verify(context.args)
    )
    if err:
      return err
    user_info, err = self.service.add_action_todo(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def add_action_completed(self, request):
    context: Context = request.context
    
    validator: Validator = Validator()
    args, err = (validator
      .expect("action_id", str, is_required=True)
      .expect("household_id", str, is_required=False)
      .verify(context.args)
    )
    if err:
      return err

    user_info, err = self.service.add_action_completed(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def list_households(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.get_user_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  def remove_household(self, request):
    context: Context = request.context
    args: dict = context.args

    user_info, err = self.service.remove_household(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  def add_household(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.add_household(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

  def edit_household(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.edit_household(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)


  def list_events(self, request):
    context: Context = request.context
    args: dict = context.args
    user_info, err = self.service.list_events_for_user(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=user_info)

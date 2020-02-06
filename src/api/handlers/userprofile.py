"""Handler file for all routes pertaining to users"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents
from api.services.userprofile import UserService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator

#TODO: install middleware to catch authz violations
#TODO: add logger

class UserHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = UserService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/users.info", self.info()) 
    self.add("/users.create", self.create())
    self.add("/users.add", self.create())
    self.add("/users.list", self.list())
    self.add("/users.update", self.update())
    self.add("/users.delete", self.delete())
    self.add("/users.remove", self.delete())
    self.add("/users.actions.completed.add", self.add_action_completed())
    self.add("/users.actions.todo.add", self.add_action_todo())
    self.add("/users.actions.todo.list", self.list_actions_todo())
    self.add("/users.actions.completed.list", self.list_actions_completed())
    self.add("/users.households.add", self.add_household())
    self.add("/users.households.edit", self.edit_household())
    self.add("/users.households.remove", self.remove_household())
    self.add("/users.households.list", self.list_households())
    self.add("/users.events.list", self.list_events())


    #admin routes
    self.add("/users.listForCommunityAdmin", self.community_admin_list())
    self.add("/users.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def user_info_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.get_user_info(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return user_info_view


  def create(self) -> function:
    def create_user_view(request) -> None: 
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
      print(user_info, err)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return create_user_view


  def list(self) -> function:
    def list_user_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      user_info, err = self.service.list_users(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return list_user_view

  def list_actions_todo(self) -> function:
    def list_actions_todo_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.list_actions_todo(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return list_actions_todo_view

  def list_actions_completed(self) -> function:
    def list_actions_completed_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.list_actions_completed(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return list_actions_completed_view


  def update(self) -> function:
    def update_user_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.update_user(args.get("id", None), args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return update_user_view


  def delete(self) -> function:
    def delete_user_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_id = args.get("id", None)
      user_info, err = self.service.delete_user(args.get("id", None))
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return delete_user_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop("community_id", None)
      users, err = self.service.list_users_for_community_admin(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=users)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      users, err = self.service.list_users_for_super_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=users)
    return super_admin_list_view

  def add_action_todo(self) -> function:
    def add_action_todo_view(request) -> None: 
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
    return add_action_todo_view


  def add_action_completed(self) -> function:
    def add_action_completed_view(request) -> None: 
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
    return add_action_completed_view


  def list_households(self) -> function:
    def list_households_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.get_user_info(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return list_households_view

  def remove_household(self) -> function:
    def remove_household_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args

      user_info, err = self.service.remove_household(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return remove_household_view

  def add_household(self) -> function:
    def add_household_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.add_household(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return add_household_view

  def edit_household(self) -> function:
    def edit_household_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.edit_household(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return edit_household_view

  def list_events(self) -> function:
    def list_events_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      user_info, err = self.service.list_events_for_user(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=user_info)
    return list_events_view

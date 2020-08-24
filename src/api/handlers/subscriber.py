"""Handler file for all routes pertaining to subscribers"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_bool
from api.services.subscriber import SubscriberService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator

#TODO: install middleware to catch authz violations
#TODO: add logger

class SubscriberHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = SubscriberService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/subscribers.info", self.info()) 
    self.add("/subscribers.create", self.create())
    self.add("/subscribers.copy", self.copy())
    self.add("/subscribers.add", self.create())
    self.add("/subscribers.list", self.list())
    self.add("/subscribers.update", self.update())
    self.add("/subscribers.delete", self.delete())
    self.add("/subscribers.remove", self.delete())

    #admin routes
    self.add("/subscribers.listForCommunityAdmin", self.community_admin_list())
    self.add("/subscribers.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def subscriber_info_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      subscriber_id = args.pop('subscriber_id', None)
      subscriber_info, err = self.service.get_subscriber_info(subscriber_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=subscriber_info)
    return subscriber_info_view


  def create(self) -> function:
    def create_subscriber_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args

      validator: Validator = Validator()
      (validator
        .add("name", str, is_required=True)
        .add("email", str, is_required=True)
        .add("community", str, is_required=False)
      )

      args, err = validator.verify(args)
      if err:
        return err
      
      community_id = args.pop('community_id', None)

      subscriber_info, err = self.service.create_subscriber(community_id ,args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=subscriber_info)
    return create_subscriber_view


  def list(self) -> function:
    def list_subscriber_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      subscriber_info, err = self.service.list_subscribers(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=subscriber_info)
    return list_subscriber_view


  def copy(self) -> function:
    def copy_subscriber_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      subscriber_id = args.pop('subscriber_id', None)
      subscriber_info, err = self.service.copy_subscriber(subscriber_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=subscriber_info)
    return copy_subscriber_view


  def update(self) -> function:
    def update_subscriber_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      subscriber_id = args.pop('subscriber_id', None)
      is_global = args.pop('is_global', None)
      if is_global:
        args["is_global"] = parse_bool(is_global)
      subscriber_info, err = self.service.update_subscriber(subscriber_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=subscriber_info)
    return update_subscriber_view


  def delete(self) -> function:
    def delete_subscriber_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      subscriber_id = args.pop('subscriber_id', None)
      subscriber_info, err = self.service.delete_subscriber(subscriber_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data='Sorry to see you go, you have been unsubscribed from our mailing lists')
    return delete_subscriber_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop('community_id', None)
      subscribers, err = self.service.list_subscribers_for_community_admin(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=subscribers)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      subscribers, err = self.service.list_subscribers_for_super_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=subscribers)
    return super_admin_list_view
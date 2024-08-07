"""Handler file for all routes pertaining to subscribers"""

from _main_.utils.common import parse_bool, parse_int, rename_field
from _main_.utils.context import Context
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.route_handler import RouteHandler
from api.decorators import admins_only, super_admins_only
from api.services.subscriber import SubscriberService


class SubscriberHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = SubscriberService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/subscribers.info", self.info) 
    self.add("/subscribers.create", self.create)
    self.add("/subscribers.copy", self.copy)
    self.add("/subscribers.add", self.create)
    self.add("/subscribers.list", self.list)
    self.add("/subscribers.update", self.update)
    self.add("/subscribers.delete", self.delete)
    self.add("/subscribers.remove", self.delete)

    #admin routes
    self.add("/subscribers.listForCommunityAdmin", self.community_admin_list)
    self.add("/subscribers.listForSuperAdmin", self.super_admin_list)

  @admins_only
  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    subscriber_id = args.pop('subscriber_id', None)
    if subscriber_id and not isinstance(subscriber_id, int):
        subscriber_id = parse_int(subscriber_id)
    subscriber_info, err = self.service.get_subscriber_info(subscriber_id)
    if err:
      return err
    return MassenergizeResponse(data=subscriber_info)


  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'community_id', 'community')

    (self.validator
      .add("name", str, is_required=True)
      .add("email", str, is_required=True)
      .add("community_id", str, is_required=False)
    )

    args, err = self.validator.verify(args)
    if err:
      return err
  
    community_id = args.pop('community', None)
    if community_id and not isinstance(community_id, int):
        community_id = parse_int(community_id)
    subscriber_info, err = self.service.create_subscriber(community_id ,args)
    if err:
      return err
    return MassenergizeResponse(data=subscriber_info)

  @admins_only
  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    user_id = args.pop('user_id', None)
    subscriber_info, err = self.service.list_subscribers(context,community_id, user_id)
    if err:
      return err
    return MassenergizeResponse(data=subscriber_info)

  @admins_only
  def copy(self, request):
    context: Context = request.context
    args: dict = context.args
    subscriber_id = args.pop('subscriber_id', None)
    subscriber_info, err = self.service.copy_subscriber(subscriber_id)
    if err:
      return err
    return MassenergizeResponse(data=subscriber_info)

  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    subscriber_id = args.pop('subscriber_id', None)
    is_global = args.pop('is_global', None)
    if is_global:
      args["is_global"] = parse_bool(is_global)
    subscriber_info, err = self.service.update_subscriber(subscriber_id, args)
    if err:
      return err
    return MassenergizeResponse(data=subscriber_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args

    subscriber_id = args.pop('subscriber_id', None)
    if subscriber_id and not isinstance(subscriber_id, int):
        subscriber_id = parse_int(subscriber_id)
    subscriber_info, err = self.service.delete_subscriber(subscriber_id)
    if err:
      return err
    return MassenergizeResponse(data='Sorry to see you go, you have been unsubscribed from our mailing lists')

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    subscribers, err = self.service.list_subscribers_for_community_admin(context, community_id)
    if err:
      return err

    return MassenergizeResponse(data=subscribers)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    subscribers, err = self.service.list_subscribers_for_super_admin(context)
    if err:
      return err

    return MassenergizeResponse(data=subscribers)

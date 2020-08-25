#message admin
#admin reply
#message subscribers
#messages.list
"""Handler file for all routes pertaining to messages"""

from _main_.utils.route_handler import RouteHandler
#import _main_.utils.common as utils
from _main_.utils.common import get_request_contents, rename_field, parse_bool, parse_location, parse_list, validate_fields, parse_string
from api.services.message import MessageService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import CustomMassenergizeError
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required

class MessageHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = MessageService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/messages.info", self.info)
    self.add("/messages.delete", self.delete)
    self.add("/messages.listForCommunityAdmin", self.community_admin_list)
    self.add("/messages.listTeamAdminMessages", self.team_admin_list)
    self.add("/messages.replyFromCommunityAdmin", self.reply_from_community_admin)
    self.add("/messages.forwardToTeamAdmins", self.forward_to_team_admins)

  @admins_only
  def info(self, request):
    context: Context  = request.context
    args = context.get_request_body()
    args = rename_field(args, 'message_id', 'id')
    message_info, err = self.service.get_message_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=message_info)

  @admins_only
  def forward_to_team_admins(self, request):
    context: Context  = request.context
    args = context.get_request_body()
    message_info, err = self.service.forward_to_team_admins(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=message_info)

  @admins_only
  def reply_from_community_admin(self, request):
    context: Context  = request.context
    args = context.get_request_body()
    message_info, err = self.service.reply_from_community_admin(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=message_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'message_id', 'id')
    message_id = args.pop('id', None)
    if not message_id:
      return CustomMassenergizeError("Please Provide Message Id")
    message_info, err = self.service.delete_message(message_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=message_info)

  @admins_only
  def team_admin_list(self, request):
    context: Context = request.context
    messages, err = self.service.list_team_admin_messages_for_community_admin(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=messages)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    messages, err = self.service.list_community_admin_messages_for_community_admin(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=messages)

#message admin
#admin reply
#message subscribers
#messages.list
"""Handler file for all routes pertaining to messages"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import rename_field
from api.services.message import MessageService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.context import Context
from api.decorators import admins_only

class MessageHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = MessageService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/messages.info", self.info)
    self.add("/messages.delete", self.delete)
    self.add("/messages.listForCommunityAdmin", self.community_admin_list)
    self.add("/messages.listForSuperAdmin", self.community_admin_list)
    self.add("/messages.listTeamAdminMessages", self.team_admin_list)
    self.add("/messages.replyFromCommunityAdmin", self.reply_from_community_admin)
    self.add("/messages.forwardToTeamAdmins", self.forward_to_team_admins)
    self.add("/messages.send", self.send_message)
    self.add("/messages.listScheduled", self.list_scheduled_messages)

  @admins_only
  def info(self, request):
    context: Context  = request.context
    args = context.get_request_body()
    args = rename_field(args, 'message_id', 'id')
    message_info, err = self.service.get_message_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=message_info)

  @admins_only
  def forward_to_team_admins(self, request):
    context: Context  = request.context
    args = context.get_request_body()
    message_info, err = self.service.forward_to_team_admins(context, args)
    if err:
      return err
    return MassenergizeResponse(data=message_info)

  @admins_only
  def reply_from_community_admin(self, request):
    context: Context  = request.context
    args = context.get_request_body()
    message_info, err = self.service.reply_from_community_admin(context, args)
    if err:
      return err
    return MassenergizeResponse(data=message_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'message_id', 'id')
    message_id = args.pop('id', None)
    if not message_id:
      return CustomMassenergizeError("Please Provide Message Id")
    message_info, err = self.service.delete_message(message_id,context)
    if err:
      return err
    return MassenergizeResponse(data=message_info)
  
  @admins_only
  def send_message(self, request):
    context: Context = request.context
    args: dict = context.args
    self.validator.expect("id",str, is_required=False)
    self.validator.expect("subject",str, is_required=False)
    self.validator.expect("message",str, is_required=False)
    self.validator.expect("sub_audience_type",str, is_required=False)
    self.validator.expect("audience",str, is_required=False)
    self.validator.expect("schedule",str, is_required=False)
    self.validator.expect("community_ids",str, is_required=False)
    self.validator.expect("audience_type",str, is_required=True)

    message_info, err = self.service.send_message(context,args)
    
    if err:
      return err
    return MassenergizeResponse(data=message_info)

  @admins_only
  def team_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    self.validator.expect("message_ids",list, is_required=False)
 
    args, err = self.validator.verify(args, strict=True)
    messages, err = self.service.list_team_admin_messages_for_community_admin(context,args)
    if err:
      return err
    return MassenergizeResponse(data=messages)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    self.validator.expect("message_ids",list, is_required=False)

    args, err = self.validator.verify(args, strict=True)
    messages, err = self.service.list_community_admin_messages_for_community_admin(context, args)
    if err:
      return err

    return MassenergizeResponse(data=messages)
  
  @admins_only
  def list_scheduled_messages(self, request):
    context: Context = request.context
    args: dict = context.args
    self.validator.expect("message_ids",list, is_required=False)

    args, err = self.validator.verify(args, strict=True)
    messages, err = self.service.list_scheduled_messages(context, args)
    if err:
      return err

    return MassenergizeResponse(data=messages)

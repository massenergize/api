from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize
from _main_.utils.pagination import paginate
from api.store.message import MessageStore
from api.store.team import TeamStore
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email
from _main_.utils.massenergize_logger import log
from typing import Tuple
from api.utils.api_utils import get_sender_email

from api.utils.filter_functions import sort_items

class MessageService:
  """
  Service Layer for all the messages
  """

  def __init__(self):
    self.store =  MessageStore()
    self.team_store = TeamStore()

  def get_message_info(self, context, message_id) -> Tuple[dict, MassEnergizeAPIError]:
    message, err = self.store.get_message_info(context, message_id)
    if err:
      return None, err
    return serialize(message, full=True), None

  def reply_from_community_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      message, err = self.store.get_message_info(context, args)
      if err:
        return None, err
      
      is_inbound = args.get("is_inbound", False)
      
      new_args = {
          "parent": message,
          'community_id': message.community.pk,
          'title': args.get('title'),
          'body': args.get('body'),
          'email': args.get('to'),
          'from': args.get('from_email'),
        }

      reply, create_err = self.store.message_admin(context, new_args)
      if create_err:
        return None, create_err

      title = args.pop('title', None)
      to = args.pop('to', None)
      body = args.pop('body', None)
      orig_date = message.created_at.strftime("%Y-%m-%d %H:%M")
      from_email = get_sender_email(message.community.id)
      
      old_body = "\r\n\r\n============================================\r\nIn reply to the following message received "+orig_date + ":\r\n\r\n" + message.body
      
      if is_inbound:
        reply_body = f'Hello {message.user_name},\r\n\r\nThanks for reaching out!\r\n {body} \r\n\r\nPlease let me know if you have any questions.\r\n\r\nSincerely,\r\n{reply.user.full_name}' + old_body
      else:
        reply_body = body + old_body

      success = send_massenergize_email(title, reply_body, to, from_email)
      if success:
        message.have_replied = True
        message.save()
      # attached_file = args.pop('attached_file', None)
      #
      # return reply message
      return serialize(reply), None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def forward_to_team_admins(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      # the message may have been modified, so don't just send the old one

      message, err = self.store.update_message_to_team_admin(context, args)
      if err:
        return None, err

      team_id = message.team.pk if message.team else None
      team_admins, err = self.team_store.get_team_admins(context, team_id)

      if(err):
        return None, err

      sender_name = message.user_name or (message.user and message.user.full_name)
      sender_email  = message.email or (message.user and message.user.email)
      raw_msg = message.body
      title = f"FW: {message.title}"

      body = f"\n\
      Hi Team Leader,\n\
      I am forwarding a message for you from our MassEnergize community portal.\n\
      Your friendly Community Admin.\n\n\
      Sender: {sender_name}\n\
      Sender's email: {sender_email}\n\
      Sender's message: \n\
      {raw_msg}\
      "

      for admin in team_admins:
        to = admin.email
        if not to:
          continue

        success = send_massenergize_email(title, body, to)
        if success:
          message.have_forwarded = True
          message.save()

     
      # attached_file = args.pop('attached_file', None)

      return serialize(message), None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def delete_message(self, message_id,context) -> Tuple[dict, MassEnergizeAPIError]:
    message, err = self.store.delete_message(message_id,context)
    if err:
      return None, err
    return serialize(message), None
  
  def send_message(self, context,args) -> Tuple[dict, MassEnergizeAPIError]:
    message, err = self.store.send_message(context,args)
    if err:
      return None, err
    return serialize(message), None


  def list_community_admin_messages_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    messages, err = self.store.list_community_admin_messages(context, args)
    if err:
      return None, err
    sorted = sort_items(messages, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None
  
  def list_scheduled_messages(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    args["is_scheduled"] = True
    messages, err = self.store.list_community_admin_messages(context, args)
    if err:
      return None, err
    sorted = sort_items(messages, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_team_admin_messages_for_community_admin(self, context: Context,args) -> Tuple[list, MassEnergizeAPIError]:
    messages, err = self.store.list_team_admin_messages(context,args)
    if err:
      return None, err
    sorted = sort_items(messages, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None

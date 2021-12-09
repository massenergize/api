from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.message import MessageStore
from api.store.team import TeamStore
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email
from typing import Tuple

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

  def reply_from_community_admin(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    message, err = self.store.get_message_info(context, args)
    if err:
      return None, err
    title = args.pop('title', None)
    to = args.pop('to', None)
    body = args.pop('body', None)
    success = send_massenergize_email(title, body, to)
    if success:
      message.have_replied = True
      message.save()
    # attached_file = args.pop('attached_file', None)    
    return success, None

  def forward_to_team_admins(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:

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

    return True, None


  def delete_message(self, message_id) -> Tuple[dict, MassEnergizeAPIError]:
    message, err = self.store.delete_message(message_id)
    if err:
      return None, err
    return serialize(message), None


  def list_community_admin_messages_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    messages, err = self.store.list_community_admin_messages(context, args)
    if err:
      return None, err
    return serialize_all(messages), None


  def list_team_admin_messages_for_community_admin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    messages, err = self.store.list_team_admin_messages(context)
    if err:
      return None, err
    return serialize_all(messages), None

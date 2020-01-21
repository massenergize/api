from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.message import MessageStore
from api.store.team import TeamStore
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email

class MessageService:
  """
  Service Layer for all the messages
  """

  def __init__(self):
    self.store =  MessageStore()
    self.team_store = TeamStore()

  def get_message_info(self, context, message_id) -> (dict, MassEnergizeAPIError):
    message, err = self.store.get_message_info(context, message_id)
    if err:
      return None, err
    return serialize(message, full=True), None

  def reply_from_community_admin(self, context, args) -> (list, MassEnergizeAPIError):
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

  def reply_from_team_admin(self, context, args) -> (list, MassEnergizeAPIError):
    message, err = self.store.get_message_info(context, args)
    if err:
      return None, err
    team_id = message.team.pk if message.team else None
    team_admins = self.team_store.get_team_admins(context, team_id)
    title = args.pop('title', None)
    body = args.pop('body', None)
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


  def delete_message(self, message_id) -> (dict, MassEnergizeAPIError):
    message, err = self.store.delete_message(message_id)
    if err:
      return None, err
    return serialize(message), None


  def list_community_admin_messages_for_community_admin(self, context: Context, args) -> (list, MassEnergizeAPIError):
    messages, err = self.store.list_community_admin_messages(context, args)
    if err:
      return None, err
    return serialize_all(messages), None


  def list_team_admin_messages_for_super_admin(self, context: Context, args) -> (list, MassEnergizeAPIError):
    messages, err = self.store.list_team_admin_messages(context, args)
    if err:
      return None, err
    return serialize_all(messages), None

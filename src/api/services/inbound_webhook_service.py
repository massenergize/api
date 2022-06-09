from _main_.utils.emailer.send_email import send_massenergize_email
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from api.store.message import MessageStore
from api.store.task_queue import TaskQueueStore
from _main_.utils.context import Context
from typing import Tuple

from database.models import Message


class InboundWebhookService:
  """
  Service Layer for all the inbound webhooks
  """

  def __init__(self):
    self.store = MessageStore()

  def process_inbound_message(self, context: Context, args) -> Tuple[str, MassEnergizeAPIError]:
    '''for inbound action to trigger webhook, message have to be sent or replied to the inbound server email'''
    '''Users reply to admin reply should also be saved in the database'''
    From = args.get('From')
    msg = args.get('TextBody')
    raw_title = args.get('Subject')
    title = raw_title.replace('Re: ', '')
   
  #  This is not the most efficient way to do this, but it's the only way to get the message id from webhook payload.
    parent = Message.objects.filter(title=title).first()

    if parent:
      new_args = {
          "parent": parent,
          'community_id': parent.community.pk,
          'title': raw_title,
          'body': msg,
          'email': From,
        }

      reply, create_err = self.store.message_admin(context, new_args)
      if create_err:
        return None, create_err

      title = raw_title
      to = parent.email
      body = msg
      orig_date = parent.created_at.strftime("%Y-%m-%d %H:%M")

      reply_body = body + "\r\n\r\n============================================\r\nIn reply to the following message received "+orig_date + ":\r\n\r\n" + parent.body
      success = send_massenergize_email(title, reply_body, to)
      if success:
        parent.have_replied = True
        parent.save()
    return "Success", None

  
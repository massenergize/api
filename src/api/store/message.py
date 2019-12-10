from database.models import Message, UserProfile, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, NotAuthorizedError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.utils.text import slugify
import random
from _main_.utils.context import Context
from django.db.models import Q
from .utils import get_community_or_die, get_admin_communities
from _main_.utils.context import Context

class MessageStore:
  def __init__(self):
    self.name = "Message Store/DB"

  def get_message_info(self, context, args) -> (dict, MassEnergizeAPIError):
    try:
      message_id = args.pop('message_id', None) or args.pop('id', None)
      
      if not message_id:
        return None, InvalidResourceError()
      message = Message.objects.filter(pk=message_id).first()

      if not message:
        return None, InvalidResourceError()

      return message, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)

  def reply_from_team_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    try:
      message_id = args.pop('message_id', None) or args.pop('id', None)
      
      if not message_id:
        return None, InvalidResourceError()
      message = Message.objects.filter(pk=message_id).first()

      if not message:
        return None, InvalidResourceError()

      return message, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def reply_from_community_admin(self, context, args) -> (dict, MassEnergizeAPIError):
    try:
      message_id = args.pop('message_id', None) or args.pop('id', None)
      title = args.pop('title', None)
      body = args.pop('body', None)
      # attached_file = args.pop('attached_file', None)

      if not message_id:
        return None, InvalidResourceError()
      message = Message.objects.filter(pk=message_id).first()

      if not message:
        return None, InvalidResourceError()

      return message, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def delete_message(self, message_id) -> (dict, MassEnergizeAPIError):
    try:
      messages = Message.objects.filter(id=message_id)
      messages.update(is_deleted=True)
      #TODO: also remove it from all places that it was ever set in many to many or foreign key
      return messages.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_community_admin_messages(self, context: Context, args):
    try:
      admin_communities, err = get_admin_communities(context)
      if context.user_is_community_admin:
        messages = Message.objects.filter(is_deleted=False, is_team_admin_message=False, community__id__in=[c.id for c in admin_communities])
      elif context.user_is_super_admin:
        messages = Message.objects.filter(is_deleted=False)
      else:
        messages = []

      return messages, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))

  def list_team_admin_messages(self, context: Context, args):
    try:
      admin_communities, err = get_admin_communities(context)
      if context.user_is_community_admin:
        messages = Message.objects.filter(is_deleted=False, is_team_admin_message=True, community__id__in=[c.id for c in admin_communities])
      elif context.user_is_super_admin:
        messages = Message.objects.filter(is_deleted=False)
      else:
        messages = []

      return messages, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))
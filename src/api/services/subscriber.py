from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize
from _main_.utils.pagination import paginate
from api.store.subscriber import SubscriberStore
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from _main_.utils.constants import COMMUNITY_URL_ROOT, ME_LOGO_PNG
from _main_.utils.massenergize_logger import log
from typing import Tuple
from api.utils.api_utils import get_sender_email

from api.utils.filter_functions import sort_items

class SubscriberService:
  """
  Service Layer for all the subscribers
  """

  def __init__(self):
    self.store =  SubscriberStore()

  def get_subscriber_info(self, subscriber_id) -> Tuple[dict, MassEnergizeAPIError]:
    subscriber, err = self.store.get_subscriber_info(subscriber_id)
    if err:
      return None, err
    return serialize(subscriber, full=True), None

  def list_subscribers(self,context, subscriber_id) -> Tuple[list, MassEnergizeAPIError]:
    subscriber, err = self.store.list_subscribers(context,subscriber_id)
    if err:
      return None, err
    return paginate(subscriber, context.args.get("page", 1), context.args.get("limit",100)), None


  def create_subscriber(self, community_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      subscriber, err = self.store.create_subscriber(community_id, args)
      if err:
        return None, err
      
      from_email = get_sender_email(subscriber.community.id)

      subject = 'Thank you for subscribing'
      content_variables = {
        'name': subscriber.name,
        'id': subscriber.id,
        'logo': subscriber.community.logo.file.url if subscriber.community and subscriber.community.logo else ME_LOGO_PNG,
        'community': subscriber.community.name if subscriber.community and subscriber.community.name else 'MassEnergize',
        'homelink': '%s/%s' %(COMMUNITY_URL_ROOT, subscriber.community.subdomain) if subscriber.community else COMMUNITY_URL_ROOT
      }
      send_massenergize_rich_email(subject, subscriber.email, 'subscriber_registration_email.html', content_variables, from_email)

      return serialize(subscriber), None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

  def update_subscriber(self, subscriber_id, args) -> Tuple[dict, MassEnergizeAPIError]:
    subscriber, err = self.store.update_subscriber(subscriber_id, args)
    if err:
      return None, err
    return serialize(subscriber), None

  def delete_subscriber(self, subscriber_id) -> Tuple[dict, MassEnergizeAPIError]:
    subscriber, err = self.store.delete_subscriber(subscriber_id)
    if err:
      return None, err
    return serialize(subscriber), None

  def copy_subscriber(self, subscriber_id) -> Tuple[dict, MassEnergizeAPIError]:
    subscriber, err = self.store.copy_subscriber(subscriber_id)
    if err:
      return None, err
    return serialize(subscriber), None

  def list_subscribers_for_community_admin(self, context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    subscribers, err = self.store.list_subscribers_for_community_admin(context, community_id)
    if err:
      return None, err
    sorted = sort_items(subscribers, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_subscribers_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
    subscribers, err = self.store.list_subscribers_for_super_admin(context)
    if err:
      return None, err
    sorted = sort_items(subscribers, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None

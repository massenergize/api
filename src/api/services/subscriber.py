from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.subscriber import SubscriberStore
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_rich_email

from _main_.utils.constants import COMMUNITY_URL_ROOT


class SubscriberService:
  """
  Service Layer for all the subscribers
  """

  def __init__(self):
    self.store =  SubscriberStore()

  def get_subscriber_info(self, subscriber_id) -> (dict, MassEnergizeAPIError):
    subscriber, err = self.store.get_subscriber_info(subscriber_id)
    if err:
      return None, err
    return serialize(subscriber, full=True), None

  def list_subscribers(self, subscriber_id) -> (list, MassEnergizeAPIError):
    subscriber, err = self.store.list_subscribers(subscriber_id)
    if err:
      return None, err
    return serialize(subscriber), None


  def create_subscriber(self, community_id, args) -> (dict, MassEnergizeAPIError):
    subscriber, err = self.store.create_subscriber(community_id, args)
    if err:
      return None, err
    
    subject = 'Thank you for subscribing'
    content_variables = {
      'name': subscriber.name,
      'id': subscriber.id,
      'logo': subscriber.community.logo.file.url if subscriber.community and subscriber.community.logo else 'https://s3.us-east-2.amazonaws.com/community.massenergize.org/static/media/logo.ee45265d.png',
      'community': subscriber.community.name if subscriber.community and subscriber.community.name else 'MassEnergize',
      'homelink': '%s/%s' %(COMMUNITY_URL_ROOT, subscriber.community.subdomain) if subscriber.community else COMMUNITY_URL_ROOT
    }
    send_massenergize_rich_email(subject, subscriber.email, 'subscriber_registration_email.html', content_variables)

    return serialize(subscriber), None


  def update_subscriber(self, subscriber_id, args) -> (dict, MassEnergizeAPIError):
    subscriber, err = self.store.update_subscriber(subscriber_id, args)
    if err:
      return None, err
    return serialize(subscriber), None

  def delete_subscriber(self, subscriber_id) -> (dict, MassEnergizeAPIError):
    subscriber, err = self.store.delete_subscriber(subscriber_id)
    if err:
      return None, err
    return serialize(subscriber), None

  def copy_subscriber(self, subscriber_id) -> (dict, MassEnergizeAPIError):
    subscriber, err = self.store.copy_subscriber(subscriber_id)
    if err:
      return None, err
    return serialize(subscriber), None

  def list_subscribers_for_community_admin(self, context, community_id) -> (list, MassEnergizeAPIError):
    subscribers, err = self.store.list_subscribers_for_community_admin(context, community_id)
    if err:
      return None, err
    return serialize_all(subscribers, full=True), None


  def list_subscribers_for_super_admin(self, context) -> (list, MassEnergizeAPIError):
    subscribers, err = self.store.list_subscribers_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(subscribers, full=True), None

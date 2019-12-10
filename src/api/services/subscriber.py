from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.subscriber import SubscriberStore
from _main_.utils.context import Context

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
    #send email here
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

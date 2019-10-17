from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.utils.common import serialize, serialize_all
from api.store.event import EventStore

class EventService:
  """
  Service Layer for all the events
  """

  def __init__(self):
    self.store =  EventStore()

  def get_event_info(self, event_id) -> (dict, MassEnergizeAPIError):
    event, err = self.store.get_event_info(event_id)
    if err:
      return None, err
    return serialize(event), None

  def list_events(self, community_id, user_id) -> (list, MassEnergizeAPIError):
    events, err = self.store.list_events(community_id, user_id)
    if err:
      return None, err
    return serialize_all(events), None


  def create_event(self, args) -> (dict, MassEnergizeAPIError):
    event, err = self.store.create_event(args)
    if err:
      return None, err
    return serialize(event), None


  def update_event(self, args) -> (dict, MassEnergizeAPIError):
    event, err = self.store.update_event(args)
    if err:
      return None, err
    return serialize(event), None

  def delete_event(self, args) -> (dict, MassEnergizeAPIError):
    event, err = self.store.delete_event(args)
    if err:
      return None, err
    return serialize(event), None


  def list_events_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    events, err = self.store.list_events_for_community_admin(community_id)
    if err:
      return None, err
    return serialize_all(events), None


  def list_events_for_super_admin(self) -> (list, MassEnergizeAPIError):
    events, err = self.store.list_events_for_super_admin()
    if err:
      return None, err
    return serialize_all(events), None

from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.event import EventStore
from _main_.utils.context import Context

class EventService:
  """
  Service Layer for all the events
  """

  def __init__(self):
    self.store =  EventStore()

  def get_event_info(self, context, event_id) -> (dict, MassEnergizeAPIError):
    event, err = self.store.get_event_info(context, event_id)
    if err:
      return None, err
    return serialize(event), None

  def rsvp(self, context, event_id) -> (dict, MassEnergizeAPIError):
    event, err = self.store.rsvp(context, event_id)
    if err:
      return None, err
    return serialize(event), None

  def rsvp_update(self, context, event_id, status) -> (dict, MassEnergizeAPIError):
    event, err = self.store.rsvp_update(context, event_id, status)
    if err:
      return None, err
    return serialize(event), None

  def rsvp_remove(self, context, rsvp_id) -> (dict, MassEnergizeAPIError):
    event, err = self.store.rsvp_remove(context, rsvp_id)
    if err:
      return None, err
    return event, None

  def copy_event(self, context, event_id) -> (dict, MassEnergizeAPIError):
    event, err = self.store.copy_event(context, event_id)
    if err:
      return None, err
    return serialize(event), None

  def list_events(self, context, community_id, subdomain, user_id) -> (list, MassEnergizeAPIError):
    events, err = self.store.list_events(context, community_id, subdomain, user_id)
    if err:
      return None, err
    return serialize_all(events), None


  def create_event(self, context, args) -> (dict, MassEnergizeAPIError):
    event, err = self.store.create_event(context, args)
    if err:
      return None, err
    return serialize(event), None


  def update_event(self, context, event_id, args) -> (dict, MassEnergizeAPIError):
    event, err = self.store.update_event(context, event_id, args)
    if err:
      return None, err
    return serialize(event), None

  def delete_event(self, context, args) -> (dict, MassEnergizeAPIError):
    event, err = self.store.delete_event(context, args)
    if err:
      return None, err
    return serialize(event), None


  def list_events_for_community_admin(self, context, community_id) -> (list, MassEnergizeAPIError):
    events, err = self.store.list_events_for_community_admin(context, community_id)
    if err:
      return None, err
    return serialize_all(events), None


  def list_events_for_super_admin(self, context) -> (list, MassEnergizeAPIError):
    events, err = self.store.list_events_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(events), None

from database.models import Event, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class EventStore:
  def __init__(self):
    self.name = "Event Store/DB"

  def get_event_info(self, event_id) -> (dict, MassEnergizeAPIError):
    event = Event.objects.filter(id=event_id)
    if not event:
      return None, InvalidResourceError()
    return event.full_json(), None


  def list_events(self, community_id) -> (list, MassEnergizeAPIError):
    events = Event.objects.filter(community__id=community_id)
    if not events:
      return [], None
    return [t.simple_json() for t in events], None


  def create_event(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_event = Event.create(**args)
      new_event.save()
      return new_event.full_json(), None
    except Exception:
      return None, ServerError()


  def update_event(self, event_id, args) -> (dict, MassEnergizeAPIError):
    event = Event.objects.filter(id=event_id)
    if not event:
      return None, InvalidResourceError()
    event.update(**args)
    return event.full_json(), None


  def delete_event(self, event_id) -> (dict, MassEnergizeAPIError):
    events = Event.objects.filter(id=event_id)
    if not events:
      return None, InvalidResourceError()


  def list_events_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    events = Event.objects.filter(community__id = community_id)
    return [t.simple_json() for t in events], None


  def list_events_for_super_admin(self):
    try:
      events = Event.objects.all()
      return [t.simple_json() for t in events], None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))
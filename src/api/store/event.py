from database.models import Event, UserProfile, EventAttendee
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse
from django.db.models import Q

class EventStore:
  def __init__(self):
    self.name = "Event Store/DB"

  def get_event_info(self, event_id) -> (dict, MassEnergizeAPIError):
    try:
      events_selected = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(id=event_id)
      event = events_selected.first()
      if not event:
        return None, InvalidResourceError()
      return event, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_events(self, community_id, subdomain, user_id) -> (list, MassEnergizeAPIError):
    if community_id:
      #TODO: also account for communities who are added as invited_communities
      query =Q(community__id=community_id)
      events = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(query)
    elif subdomain:
      query =  Q(community__subdomain=subdomain)
      events = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(query)

    elif user_id:
      events = EventAttendee.objects.filter(attendee=user_id)
    else:
      events = []
    if not events:
      return [], None
    return events, None


  def create_event(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_event = Event.objects.create(**args)
      new_event.save()
      return new_event, None
    except Exception:
      return None, ServerError()


  def update_event(self, event_id, args) -> (dict, MassEnergizeAPIError):
    event = Event.objects.filter(id=event_id)
    if not event:
      return None, InvalidResourceError()
    event.update(**args)
    return event, None


  def delete_event(self, event_id) -> (dict, MassEnergizeAPIError):
    events = Event.objects.filter(id=event_id)
    if not events:
      return None, InvalidResourceError()


  def list_events_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    events = Event.objects.filter(community__id = community_id)
    return events, None


  def list_events_for_super_admin(self):
    try:
      events = Event.objects.all()
      return events, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))
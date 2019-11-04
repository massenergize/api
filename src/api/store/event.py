from database.models import Event, UserProfile, EventAttendee, Media
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
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
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      new_event = Event.objects.create(**args)

      if image:
        media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
        new_event.image = media
      
      new_event.save()

      if tags:
        new_event.tags.set(tags)
      
      return new_event, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def update_event(self, event_id, args) -> (dict, MassEnergizeAPIError):
    try:
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      events = Event.objects.filter(id=event_id)
      events.update(**args)
      
      event = events.first()
      if not event:
        return None, CustomMassenergizeError(f"No event with id: {event_id}")

      if image:
        media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
        event.image = media
      
      event.save()

      if tags:
        event.tags.set(tags)
      
      return event, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def delete_event(self, event_id) -> (dict, MassEnergizeAPIError):
    try:
      events = Event.objects.filter(id=event_id)
      if not events:
        return None, InvalidResourceError()
      events.delete()
      return events, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


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
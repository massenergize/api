from database.models import Event, UserProfile, EventAttendee, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.db.models import Q
from _main_.utils.context import Context
from random import randint

class EventStore:
  def __init__(self):
    self.name = "Event Store/DB"

  def get_event_info(self, context: Context, event_id) -> (dict, MassEnergizeAPIError):
    try:
      events_selected = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(id=event_id)
      event = events_selected.first()
      if not event:
        return None, InvalidResourceError()
      return event, None
    except Exception as e:
      return None, CustomMassenergizeError(e)

  def copy_event(self, context: Context, event_id) -> (dict, MassEnergizeAPIError):
    try:
      events_selected = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(id=event_id)
      event_to_copy: Event = events_selected.first()
      if not event_to_copy:
        return None, InvalidResourceError()
      
      old_tags = event_to_copy.tags.all()
      event_to_copy.pk = None
      new_event = event_to_copy 
      new_event.name = f"{event_to_copy.name}-Copy-{randint(1, 1000)}"
      new_event.is_published=False
      new_event.start_date_and_time = event_to_copy.start_date_and_time
      new_event.end_date_and_time = event_to_copy.end_date_and_time
      new_event.description = event_to_copy.description
      new_event.featured_summary = event_to_copy.featured_summary
      new_event.location = event_to_copy.location
      new_event.save()

      #copy tags over
      for t in old_tags:
        new_event.tags.add(t)

      return new_event, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def list_events(self, context: Context, community_id, subdomain, user_id) -> (list, MassEnergizeAPIError):
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


  def create_event(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      community = args.pop("community_id", None)

      have_address = args.pop('have_address', False)
      if not have_address:
        args['location'] = None

      if community:
        community = Community.objects.get(pk=community)
        if not community:
          return None, CustomMassenergizeError("Please provide a valid community_id")

      new_event: Event = Event.objects.create(**args)
      if community:
        new_event.community = community

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


  def update_event(self, context: Context, event_id, args) -> (dict, MassEnergizeAPIError):
    try:
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      events = Event.objects.filter(id=event_id)

      have_address = args.pop('have_address', False)
      if not have_address:
        args['location'] = None

      community = args.pop("community_id", None)
      if community:
        community = Community.objects.get(pk=community)
      
      events.update(**args)

      event: Event = events.first()
      if not event:
        return None, CustomMassenergizeError(f"No event with id: {event_id}")

      events.update(**args)

      if image:
        media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
        event.image = media
      
      if community:
        event.community = community
      
      event.save()

      if tags:
        event.tags.set(tags)
      
      return event, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def delete_event(self, context: Context, event_id) -> (dict, MassEnergizeAPIError):
    try:
      events = Event.objects.filter(id=event_id)
      if not events:
        return None, InvalidResourceError()
      
      if len(events) > 1:
        return None, CustomMassenergizeError("Deleting multiple events not supported")

      events.delete()
      return events.first(), None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def list_events_for_community_admin(self, context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        return self.list_events_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      if not community_id:
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]
        events = Event.objects.filter(Q(community__id__in = comm_ids) | Q(is_global=True), is_deleted=False).select_related('image', 'community').prefetch_related('tags')
        return events, None

      events = Event.objects.filter(Q(community__id = community_id) | Q(is_global=True), is_deleted=False).select_related('image', 'community').prefetch_related('tags')
      return events, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def list_events_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      events = Event.objects.filter(is_deleted=False).select_related('image', 'community').prefetch_related('tags')
      return events, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))
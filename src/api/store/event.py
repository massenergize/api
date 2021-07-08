from database.models import Event, RecurringEventException, UserProfile, EventAttendee, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.db.models import Q
from _main_.utils.context import Context
from sentry_sdk import capture_message
from .utils import get_user_or_die

class EventStore:
  def __init__(self):
    self.name = "Event Store/DB"

  def get_event_info(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop("event_id")

      events_selected = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(id=event_id)
      event = events_selected.first()
      if not event:
        return None, InvalidResourceError()
      return event, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def copy_event(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop("event_id")

      events_selected = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(id=event_id)
      event_to_copy: Event = events_selected.first()
      if not event_to_copy:
        return None, InvalidResourceError()
      
      old_tags = event_to_copy.tags.all()
      event_to_copy.pk = None
      new_event = event_to_copy 
      new_event.name = event_to_copy.name + "-Copy"
      new_event.is_published=False
      new_event.is_global = False
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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_events(self, context: Context, args) -> (list, MassEnergizeAPIError):
    community_id = args.pop("community_id", None)
    subdomain = args.pop("subdomain", None)
    user_id = args.pop("user_id", None)

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
    
    if not context.is_sandbox and events:
      events = events.filter(is_published=True)
  
    return events, None


  def create_event(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    print(args)
    try:
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      community = args.pop("community_id", None)
      recurring  = args.pop('is_recurring', False)
      recurring_type = args.pop('recurring_type', None)
      separation_count = args.pop('separation_count', None)
      day_of_week = None
      week_of_month = None
      if recurring_type == "week":
        day_of_week = args.pop("day_of_week", None)
      elif recurring_type == "month":
        week_of_month = args.pop("week_of_month", None)
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

      if recurring and (day_of_week or week_of_month): 
        new_event.is_recurring = True
        new_event.recurring_details = {
          "recurring_type": recurring_type, 
          "separation_count": separation_count, 
          "day_of_week": day_of_week, 
          "week_of_month": week_of_month
        }
        print("event recurring details: ")
        print(new_event.recurring_details)
        
      new_event.save()

      if tags:
        new_event.tags.set(tags)
      
      return new_event, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def update_event(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop('event_id', None)
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      recurring  = args.pop('recurring', False)
      recurring_details = args.pop('recurring_details', None)
      events = Event.objects.filter(id=event_id)

      have_address = args.pop('have_address', False)
      if not have_address:
        args['location'] = None

      community = args.pop("community_id", None)
      if community:
        community = Community.objects.filter(pk=community).first()
      
      events.update(**args)

      event: Event = events.first()
      if not event:
        return None, CustomMassenergizeError(f"No event with id: {event_id}")

      if image:
        media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
        event.image = media
      
      if community:
        event.community = community
      else:
        event.community = None

      if recurring and recurring_details: 
        event.is_recurring = True
        event.recurring_details = recurring_details
        print("event recurring details: ")
        print(event.recurring_details)

      event.save()

      if tags:
        event.tags.set(tags)
      
      return event, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def reschedule_recurring_event(self, args) -> (dict, MassEnergizeAPIError):
    try: 
      id = args.get('id', None)
      start_date_and_time = args.get('startDateTime', None)
      end_date_and_time = args.get('endDateTime', None)

      event = Event.objects.filter(id=id).first()
      rescheduled_event = Event.objects.create(**args)
      
      # can reschedule events more than 1 event in advance
      if event.is_recurring:
        rescheduled = RecurringEventException.objects.create(
          event = event, 
          rescheduled_event = rescheduled_event
        )
      else: 
        return None, MassEnergizeAPIError("Pinged reshcedule_recurring_event endpoint, but cannot reschedule an instance of a non recurring event")
    except Exception as e: 
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def delete_recurring_event(self, args) -> (dict, MassEnergizeAPIError):
    pass

  def rank_event(self, args) -> (dict, MassEnergizeAPIError):
    try:
      id = args.get('id', None)
      rank = args.get('rank', None)
      if id and rank:

        events = Event.objects.filter(id=id)
        events.update(rank=rank)
        return events.first(), None
      else:
        raise Exception("Rank and ID not provided to events.rank")
      
    except Exception as e:
      capture_message(str(e), level="error")
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
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_events_for_community_admin(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      community_id = args.pop("community_id", None)

      if context.user_is_super_admin:
        return self.list_events_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      # community_id coming from admin portal is 'undefined'
      if not community_id or community_id=='undefined':
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]
        events = Event.objects.filter(Q(community__id__in = comm_ids) | Q(is_global=True), is_deleted=False).select_related('image', 'community').prefetch_related('tags')
        return events, None

      events = Event.objects.filter(Q(community__id = community_id) | Q(is_global=True), is_deleted=False).select_related('image', 'community').prefetch_related('tags')
      return events, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_events_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      events = Event.objects.filter(is_deleted=False).select_related('image', 'community').prefetch_related('tags')
      return events, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def rsvp(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop("event_id", None)
      args: dict = context.args
      user = get_user_or_die(context, args)
      event = Event.objects.filter(pk=event_id).first()
      if not event:
        return None, InvalidResourceError()

      event_attendee = EventAttendee.objects.create(
        event=event, attendee=user, status="RSVP")

      return event_attendee, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def rsvp_update(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop("event_id", None)
      status = args.pop("status", "SAVE")

      args: dict = context.args
      user = get_user_or_die(context, args)
      event = Event.objects.filter(pk=event_id).first()
      if not event:
        return None, InvalidResourceError()

      event_attendee = EventAttendee.objects.filter(
        event=event, attendee=user).update(status=status)

      return event_attendee, None
      
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def rsvp_remove(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      rsvp_id = args.pop("rsvp_id", None)

      result = EventAttendee.objects.filter(pk=rsvp_id).delete()
      return result, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
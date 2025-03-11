import json

from celery.result import AsyncResult
from django.utils import timezone

from _main_.utils.footage.FootageConstants import FootageConstants
from _main_.utils.footage.spy import Spy
from _main_.utils.utils import is_url_valid
from _main_.utils.common import custom_timezone_info, local_time, parse_datetime_to_aware
from api.store.common import get_media_info, make_media_info
from api.tests.common import RESET, makeUserUpload
from api.utils.api_utils import is_admin_of_community
from api.utils.filter_functions import get_events_filter_params
from database.models import Event, RecurringEventException, UserProfile, EventAttendee, Media, Community, \
    EventNudgeSetting
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, CustomMassenergizeError, \
    NotAuthorizedError
from django.db.models import Q, F
from _main_.utils.context import Context
from _main_.utils.massenergize_logger import log

from database.utils.settings.model_constants.events import EventConstants
from task_queue.database_tasks.update_recurring_events import update_recurring_event
from .utils import get_user_from_context, get_user_or_die, get_new_title
import datetime
from datetime import timedelta
import calendar
from typing import Tuple
from zoneinfo import ZoneInfo


def _local_datetime(date_and_time):
    """
    Converts a UTC datetime string to local datetime in Massachusetts time zone.
    """    # Parse the datetime string to a datetime object
    try:
        # Try parsing the datetime string with the first format
        dt = datetime.datetime.strptime(str(date_and_time), '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        # If it fails, try the second format
        dt = datetime.datetime.strptime(str(date_and_time), '%Y-%m-%d %H:%M:%S%z')
    # Specify the Massachusetts time zone
    massachusetts_zone = ZoneInfo('America/New_York')

    # Convert time zone from UTC to Massachusetts time zone
    local_datetime = dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(massachusetts_zone)
    return local_datetime

def _UTC_datetime(date_and_time):
    """
    Converts a local Massachusetts datetime string to UTC datetime.
    """
    # Parse the datetime string to a datetime object
    dt = datetime.datetime.strptime(str(date_and_time), '%Y-%m-%d %H:%M:%S')

    # Specify the Massachusetts time zone
    massachusetts_zone = ZoneInfo('America/New_York')

    # Convert time zone from Massachusetts to UTC
    UTC_datetime = dt.replace(tzinfo=massachusetts_zone).astimezone(ZoneInfo('UTC'))
    return UTC_datetime


def _check_recurring_date(start_date_and_time, end_date_and_time, day_of_week, week_of_month):
    converter = {"first": 1, "second": 2, "third": 3, "fourth": 4}

    if start_date_and_time and end_date_and_time:
        # the date check below fails because the local date (in Massachusetts) is different than the UTC date
        local_start = _local_datetime(start_date_and_time)
        local_end = _local_datetime(end_date_and_time)

        # check if weekday matches the start_date_and_time
        if calendar.day_name[local_start.weekday()] != day_of_week:
            return True, "Starting date and time does not match the recurrence pattern for the event"

        # if necessary, check if week of month matches the start_date...
        if week_of_month:
            # let's say the date passed in represents the Nth occurence of a particular weekday in the month
            # we find N
            # get the first instance of the same weekday in the month
            obj = calendar.Calendar()
            date_of_first_weekday = 1
            for d in obj.itermonthdates(int(local_start.year), int(local_start.month)):
                if int(d.day >= 8):
                    continue
                d1 = datetime.datetime(int(d.year), int(d.month), int(d.day))
                if calendar.day_name[d1.weekday()] == day_of_week:
                    date_of_first_weekday = int(d1.day)
                    diff = local_start.day - date_of_first_weekday
                    break
            if converter[week_of_month] - 1 != diff / 7:
                return True, "Starting date and time does not match the recurrence pattern for the event"

        # TODO: check that starting date and time is earlier than ending date and time (need to edit substring thingy)

        # check that if the event does not go longer than a day (recurring events cannot go longer than 1 day)
        if local_start.date() != local_end.date():
            return True, "Recurring events must only last 1 day. Make sure your starting date and ending date are the same"

    return False, "No problem with recurring dates"


class EventStore:
    def __init__(self):
        self.name = "Event Store/DB"

    def get_event_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:

            event_id = args.pop("event_id")

            events_selected = Event.objects.filter(id=event_id).select_related('image', 'community').prefetch_related(
                'tags', 'invited_communities')
            event = events_selected.first()
            if not event:
                return None, InvalidResourceError()
            return event, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def copy_event(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            event_id = args.pop("event_id")

            events_selected = Event.objects.select_related('image', 'community').prefetch_related('tags',
                                                                                                  'invited_communities').filter(
                id=event_id)
            event_to_copy: Event = events_selected.first()
            if not event_to_copy:
                return None, InvalidResourceError()

            old_tags = event_to_copy.tags.all()

            # the copy will have "-Copy" appended to the name; if that already exists, keep it but update specifics
            new_name = get_new_title(None, event_to_copy.name) + "-Copy"
            existing_event = Event.objects.filter(name=new_name, community=None).first()
            if existing_event:
                # keep existing event with that name
                new_event = existing_event
                # copy specifics from the event to copy
                new_event.start_date_and_time = event_to_copy.start_date_and_time
                new_event.end_date_and_time = event_to_copy.end_date_and_time
                new_event.description = event_to_copy.description
                new_event.rsvp_enabled = event_to_copy.rsvp_enabled
                new_event.rsvp_email = event_to_copy.rsvp_email
                new_event.rsvp_message = event_to_copy.rsvp_message
                new_event.image = event_to_copy.image
                new_event.featured_summary = event_to_copy.featured_summary
                new_event.location = event_to_copy.location
                new_event.more_info = event_to_copy.more_info
                new_event.external_link = event_to_copy.external_link
                new_event.external_link_type = event_to_copy.external_link_type
                new_event.event_type = event_to_copy.event_type
                if not (event_to_copy.is_recurring == None):
                    new_event.is_recurring = event_to_copy.is_recurring
                    new_event.recurring_details = event_to_copy.recurring_details

            else:
                new_event = event_to_copy
                new_event.pk = None
                new_event.name = new_name

            new_event.archive = False
            new_event.is_published = False
            new_event.is_global = False

            # keep record of who made the copy
            if context.user_email:
                user = UserProfile.objects.filter(email=context.user_email).first()
                if user:
                    new_event.user = user

            new_event.save()

            for tag in old_tags:
                new_event.tags.add(tag)
                new_event.save()

            # ----------------------------------------------------------------
            Spy.create_event_footage(events=[new_event, event_to_copy], context=context, type=FootageConstants.copy(),
                                     notes=f"Copied from ID({event_to_copy.id}) to ({new_event.id})")
            # ----------------------------------------------------------------
            return new_event, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_recurring_event_exceptions(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            community_id = args.pop("community_id", None)
            subdomain = args.pop("subdomain", None)
            user_id = args.pop("user_id", None)
            event_id = args.pop("event_id", None)

            if community_id:
                # TODO: also account for communities who are added as invited_communities
                query = Q(community__id=community_id)
                events = Event.objects.select_related('image', 'community').prefetch_related('tags',
                                                                                             'invited_communities').filter(
                    query)

            elif subdomain:
                query = Q(community__subdomain=subdomain)
                events = Event.objects.select_related('image', 'community').prefetch_related('tags',
                                                                                             'invited_communities').filter(
                    query)

            elif user_id:
                events = EventAttendee.objects.filter(user_id=user_id)

            elif event_id:
                events = Event.objects.filter(id=event_id).select_related('image', 'community').prefetch_related('tags',
                                                                                                                 'invited_communities')

            else:
                # not information required
                raise Exception("events.exceptions.list requires community, subdomain, user or event id")

            exceptions = []
            for event in events.all():
                e = RecurringEventException.objects.filter(event=event).first()
                if e:
                    exceptions.append(event.id)

            return exceptions, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_events(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        community_id = context.args.pop("community_id", None)
        subdomain = args.pop("subdomain", None)
        user_id = args.pop("user_id", None)
        shared = []

        today = parse_datetime_to_aware()
        shared_months = 2
        hosted_months = 6
        earliest_shared = today - timedelta(weeks=4*shared_months)
        earliest_hosted = today - timedelta(weeks=4*hosted_months)

        if community_id:
            # TODO: also account for communities who are added as invited_communities
            events = Event.objects.select_related('image', 'community').prefetch_related('tags','invited_communities').filter(community__id=community_id, start_date_and_time__gte=earliest_hosted)

            # Find events that have been shared to this community
            community = Community.objects.get(pk=community_id)

            if community:
                shared = community.events_from_others.filter(is_published=True, start_date_and_time__gte=earliest_shared).exclude(community_id=community_id)

        elif subdomain:
            community = Community.objects.get(subdomain=subdomain)
            events = Event.objects.select_related('image', 'community').prefetch_related('tags','invited_communities').filter(community__id=community.id, start_date_and_time__gte=earliest_hosted)
            
            if community: 
                shared = community.events_from_others.filter(is_published=True, start_date_and_time__gte=earliest_shared).exclude(community_id=community.id)

        elif user_id:
            events = EventAttendee.objects.filter(user_id=user_id)

        else:
            events = []

        if not context.is_sandbox and events:
            if context.user_is_logged_in and not context.user_is_admin():
                events = events.filter(Q(user__id=context.user_id) | Q(is_published=True))
            else:
                events = events.filter(is_published=True)
        all_events = [*events, *shared]

        return all_events, None

    def create_event(self, context: Context, args, user_submitted) -> Tuple[dict, MassEnergizeAPIError]:

        try:
            image = args.pop('image', None)
            tags = args.pop('tags', [])
            community = args.pop("community_id", None)
            user_email = args.pop('user_email', context.user_email)
            image_info = make_media_info(args)

            start_date_and_time = args.get('start_date_and_time', None)
            end_date_and_time = args.get('end_date_and_time', None)
            is_recurring = args.pop('is_recurring', False)

            recurring_type = args.pop('recurring_type', None)
            separation_count = args.pop('separation_count', None)
            day_of_week = args.pop('day_of_week', None)
            week_of_month = args.pop("week_of_month", None)
            final_date = args.pop('final_date', None)
            publicity_selections = args.pop("publicity_selections", [])

            if end_date_and_time < start_date_and_time:
                return None, CustomMassenergizeError("Please provide an end date and time that comes after the start date and time.")

            if args.get('is_published', False):
                args['published_at'] = local_time()

            if is_recurring:
                if final_date:
                    final_date = _local_datetime(final_date).date()

                local_start = _local_datetime(start_date_and_time)
                local_end = _local_datetime(end_date_and_time)

                # if specified a different end date from start date, fix this
                if local_start.date() != local_end.date():
                    end_datetime = datetime.datetime.combine(local_start.date(), local_end.timetz())
                    end_datetime = end_datetime.replace(tzinfo=local_end.tzinfo)
                    end_date_and_time = end_datetime.astimezone(timezone.utc)

            if separation_count:
                separation_count = int(separation_count)

            if recurring_type != "month":
                week_of_month = None

            event_type = args.get('event_type', None)
            if event_type == "in-person":
                args['external_link'] = None
            elif event_type == "online":
                args['location'] = None

            if args.get('external_link', None):
                is_link_valid = is_url_valid(args.get("external_link"))
                if not is_link_valid:
                    return None, CustomMassenergizeError("Please provide a valid link for the event.")

            if community:
                community = Community.objects.get(pk=community)
                if not community:
                    return None, CustomMassenergizeError("Please provide a valid community_id")

            new_event: Event = Event.objects.create(**args)
            if community:
                new_event.community = community

            user_media_upload = None
            if image:  # now, images will always come as an array of ids
                if user_submitted:
                    name = f'ImageFor {new_event.name} Event'
                    media = Media.objects.create(name=name, file=image)
                    user_media_upload = makeUserUpload(media=media, info=image_info, communities=[community])
                else:
                    media = Media.objects.filter(pk=image[0]).first()
                new_event.image = media

            if tags:
                new_event.tags.set(tags)

            user = None
            if user_email:
                user_email = user_email.strip()
                # verify that provided emails are valid user
                if not UserProfile.objects.filter(email=user_email).exists():
                    return None, CustomMassenergizeError(f"Email: {user_email} is not registered with us")

                user = UserProfile.objects.filter(email=user_email).first()
                if user:
                    new_event.user = user
                    if user_media_upload:
                        user_media_upload.user = user
                        user_media_upload.save()

            if publicity_selections:
                new_event.communities_under_publicity.set(publicity_selections)

            if is_recurring:

                # check that the event's start date coincides with the recurrence pattern if it is listed as recurring
                err, message = _check_recurring_date(start_date_and_time, end_date_and_time, day_of_week, week_of_month)
                if err:
                    return None, CustomMassenergizeError(message)

                if recurring_type == "week" and week_of_month:
                    return None, CustomMassenergizeError("Cannot fill out week of month field if your event is weekly")

                new_event.is_recurring = True
                new_event.recurring_details = {
                    "recurring_type": recurring_type,
                    "separation_count": separation_count,
                    "day_of_week": day_of_week,
                    "week_of_month": week_of_month,
                    "final_date": str(final_date)
                }

            new_event.save()
            
            # create a task to reschedule event after current end date
            if new_event.is_recurring:
                update_recurring_event(new_event.id)
            # ----------------------------------------------------------------
            Spy.create_event_footage(events=[new_event], context=context, actor=new_event.user,
                                     type=FootageConstants.create(), notes=f"Event ID({new_event.id})")
            # ----------------------------------------------------------------
            return new_event, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_event(self, context: Context, args, user_submitted) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            event_id = args.pop('event_id', None)
            events = Event.objects.filter(id=event_id)
            image_info = make_media_info(args)

            publicity_selections = args.pop("publicity_selections", [])
            shared_to = args.pop("shared_to", [])

            if not events:
                return None, InvalidResourceError()
            event = events.first()

            # check if requesting user is the action creator, super admin or community admin else throw error
            creator = str(event.user_id)
            community = event.community
            if context.user_id == creator:
                # action creators can't currently modify once published
                if event.is_published and not context.user_is_admin():
                    # ideally this would submit changes to the community admin to publish
                    return None, CustomMassenergizeError(
                        "Unable to modify event once published.  Please contact Community Admin to do this")
            else:
                # otherwise you must be an administrator
                if not context.user_is_admin():
                    return None, NotAuthorizedError()

                # check if user is community admin and is also an admin of the community that created the event
                if community:
                    if not is_admin_of_community(context, community.id):
                        return None, NotAuthorizedError()

            image = args.pop('image', None)
            tags = args.pop('tags', [])

            start_date_and_time = args.get('start_date_and_time', None)
            end_date_and_time = args.get('end_date_and_time', None)

            is_recurring = args.pop('is_recurring', False)
            recurring_type = args.pop('recurring_type', None)
            separation_count = args.pop('separation_count', None)
            day_of_week = args.pop('day_of_week', None)
            week_of_month = args.pop("week_of_month", None)
            rescheduled_start_datetime = args.pop('rescheduled_start_datetime', False)
            rescheduled_end_datetime = args.pop('rescheduled_end_datetime', False)
            upcoming_is_cancelled = args.pop("upcoming_is_cancelled", None)
            upcoming_is_rescheduled = args.pop('upcoming_is_rescheduled', None)
            final_date = args.pop('final_date', None)

            community_id = args.pop("community_id", None)
            is_approved = args.pop('is_approved', None)
            is_published = args.pop('is_published', None)

            if is_published:
                args['published_at'] = parse_datetime_to_aware()
            else:
                args['published_at'] = None

            if start_date_and_time and end_date_and_time:
                if end_date_and_time < start_date_and_time:
                    return None, CustomMassenergizeError(
                        "Please provide an end date and time that comes after the start date and time.")
            if is_recurring:

                if final_date:
                    final_date = _local_datetime(final_date).date()

                # validate recurring details before updating event
                local_start = _local_datetime(start_date_and_time)
                local_end = _local_datetime(end_date_and_time)

                # if specified a different end date from start date, fix it
                if local_start.date() != local_end.date():
                    # fix the end_date_and_time to have same date as start
                    end_datetime = datetime.datetime.combine(local_start.date(), local_end.time())
                    end_date_and_time = _UTC_datetime(end_datetime).strftime('%Y-%m-%dT%H:%M:%SZ')
                    args["end_date_and_time"] = end_date_and_time

                if separation_count:
                    separation_count = int(separation_count)

                if recurring_type != "month":
                    week_of_month = None

                # check that the event's start date coincides with the recurrence pattern if it is listed as recurring
                err, message = _check_recurring_date(start_date_and_time, end_date_and_time, day_of_week, week_of_month)
                if err:
                    return None, CustomMassenergizeError(message)

                # this seems to be an invalid check.  Even for monthly events, you have the day_of_week
                # if week_of_month: return None, CustomMassenergizeError("Cannot fill out week of month field if your event is weekly")
                if recurring_type == "week" and week_of_month:
                    return None, CustomMassenergizeError("Cannot fill out week of month field if your event is weekly")

                if upcoming_is_cancelled and upcoming_is_rescheduled:
                    return None, CustomMassenergizeError(
                        "Cannot cancel and reschedule next instance of a recurring event at the same time")

            # BHN - temporarily back out this change until we have user submitted events
            ### if not is_approved and is_published:
            ###    return None, CustomMassenergizeError("Cannot publish event that is not approved.")

            event_type = args.get('event_type', None)
            if event_type == "in-person":
                args['external_link'] = None
            elif event_type == "online":
                args['location'] = None

            if args.get('external_link', None):
                is_link_valid = is_url_valid(args.get("external_link"))
                if not is_link_valid:
                    return None, CustomMassenergizeError("Please provide a valid link for the event.")

            #  preventing the user from approving event if they are not an admin
            if not context.user_is_admin():
                args.pop('is_approved', None)
                args.pop('is_published', None)

            # update the event instance
            events.update(**args)
            event: Event = events.first()

            if community_id:
                community = Community.objects.filter(pk=community_id).first()
                if community:
                    event.community = community
                else:
                    event.community = None

            if image:  # now, images will always come as an array of ids, or "reset" string
                if user_submitted:
                    if "ImgToDel" in image:
                        event.image = None
                    else:
                        image = Media.objects.create(file=image, name=f'ImageFor {event.name} Event')
                        event.image = image
                        makeUserUpload(media=image, info=image_info, user=event.user, communities=[community])
                else:
                    if image[0] == RESET:  # if image is reset, delete the existing image
                        event.image = None
                    else:
                        media = Media.objects.filter(id=image[0]).first()
                        event.image = media

            if event.image:
                old_image_info, can_save_info = get_media_info(event.image)
                # There are media objects that do not have user upload references. (because we didnt have that model at the time of upload) that's why we need to check first
                if can_save_info:
                    event.image.user_upload.info.update({**old_image_info, **image_info})
                    event.image.user_upload.save()

            if tags:
                event.tags.set(tags)

            if publicity_selections:
                event.communities_under_publicity.set(publicity_selections)

            if shared_to:
                first = shared_to[0]
                if first == "reset":
                    event.shared_to.clear()
                else:
                    event.shared_to.set(shared_to)

            if is_recurring:

                event.is_recurring = True
                event.recurring_details = {
                    "recurring_type": recurring_type,
                    "separation_count": separation_count,
                    "day_of_week": day_of_week,
                    "week_of_month": week_of_month,
                    "final_date": str(final_date)
                }

                # CAdmin is cancelling the upcoming event instance
                event.recurring_details["is_cancelled"] = upcoming_is_cancelled

                # check if there was a previously rescheduled event instance
                rescheduled: RecurringEventException = RecurringEventException.objects.filter(event=event).first()

                # CAdmin is rescheduling the upcoming event instance
                if upcoming_is_rescheduled:
                    # only create the event and recurring event exception if the event is being newly rescheduled,
                    # otherwise, don't do anything
                    if not rescheduled:

                        rescheduled_event = Event.objects.create(
                            name=event.name + " (rescheduled)",
                            featured_summary=event.featured_summary,
                            start_date_and_time=rescheduled_start_datetime,
                            end_date_and_time=rescheduled_end_datetime,
                            description=event.description,
                            community=event.community,
                            location=event.location,
                            image=event.image,
                            archive=event.archive,
                            is_global=event.is_global,
                            external_link=event.external_link,
                            external_link_type=event.external_link_type,
                            more_info=event.more_info,
                            is_deleted=event.is_deleted,
                            is_published=event.is_published,
                            rank=event.rank,
                            is_recurring=False,
                            recurring_details=None
                        )
                        rescheduled_event.save()

                        old_tags = event.tags.all()
                        old_communities = event.invited_communities.all()

                        for t in old_tags:
                            rescheduled_event.tags.add(t)
                        for c in old_communities:
                            rescheduled_event.invited_communities.add(c)

                        rescheduled_event.save()

                        rescheduled = RecurringEventException.objects.create(
                            event=event,
                            former_time=event.start_date_and_time,
                            rescheduled_event=rescheduled_event
                        )
                    #
                    # they are trying to modify an existing event that is rescheduled
                    elif rescheduled:
                        ev = rescheduled.rescheduled_event
                        ev.start_date_and_time = rescheduled_start_datetime
                        ev.end_date_and_time = rescheduled_end_datetime
                        ev.save()
                    rescheduled.save()

                # CAdmin is not rescheduling the upcoming event instance
                else:
                    # this is a new update = there was a previously rescheduled event, now the CAdmin wants to get rid of it
                    if rescheduled:
                        rescheduled.rescheduled_event.delete()
                        rescheduled.delete()
                    

            if (is_approved != None and
                (is_approved != event.is_approved)):  # If changed
                event.is_approved = is_approved

            if (is_published != None and
                (is_published != event.is_published)):  # If changed
                event.is_published = is_published

            if event.is_approved == False and event.is_published == True:  # An event can't be published and not approved
                event.is_approved == True  # Approve an event if an admin publishes it

            # successful return
            event.save()
            
            # create a task to reschedule event after current end date
            if event.is_recurring:
                update_recurring_event(event.id)

            # ----------------------------------------------------------------
            Spy.create_event_footage(events=[event], context=context, type=FootageConstants.update(),
                                     notes=f"Event ID({event_id})")
            # ----------------------------------------------------------------
            return event, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def update_recurring_event_date(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        community_id = args.pop("community_id", None)
        subdomain = args.pop("subdomain", None)
        user_id = args.pop("user_id", None)

        if community_id:
            # TODO: also account for communities who are added as invited_communities
            query = Q(community__id=community_id)
            events = Event.objects.select_related('image', 'community').prefetch_related('tags',
                                                                                         'shared_to').filter(
                query, is_published=True, is_recurring=True, is_deleted=False)

        elif subdomain:
            # testing only
            query = Q(community__subdomain=subdomain)
            events = Event.objects.select_related('image', 'community').prefetch_related('tags',
                                                                                         'shared_to').filter(
                query, is_published=True, is_recurring=True, is_deleted=False)


        elif user_id:
            events = EventAttendee.objects.filter(user_id=user_id)

        else:
            events = []

        today =  parse_datetime_to_aware()

        for event in events:
            # protect against recurring event with no recurring details saved
            if not event.is_recurring or not event.recurring_details or not event.recurring_details['separation_count']:
                continue

            starttime = event.start_date_and_time.strftime("%H:%M:%S+00:00")

            # nothing to do if scheduled event in the future
            if event.start_date_and_time > today:
                continue

            # if the final date is in the past, don't update the date

            final_date = event.recurring_details.get('final_date', None)

            if final_date and final_date != 'None':
                final_date = final_date + ' ' + starttime
                final_date = datetime.datetime.strptime(final_date, "%Y-%m-%d %H:%M:%S+00:00")
                final_date = final_date.replace(tzinfo=custom_timezone_info())
                if today > final_date:
                    continue

            # weekdays = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
            converter = {"first": 1, "second": 2, "third": 3, "fourth": 4}

            try:
                sep_count = int(event.recurring_details['separation_count'])

                start_date = event.start_date_and_time
                end_date = event.end_date_and_time
                duration = end_date - start_date
                if event.recurring_details['recurring_type'] == "week":
                    while (start_date < today):
                        start_date += timedelta(7 * sep_count)
                        end_date = start_date + duration
                    event.start_date_and_time = start_date
                    event.end_date_and_time = end_date
                elif event.recurring_details['recurring_type'] == "month":

                    while (start_date < today):
                        # use timedelta to get the new month
                        new_month = start_date + timedelta((sep_count * 31) + 1)

                        # find the corresponding ith day of the jth month

                        obj = calendar.Calendar()
                        date_of_first_weekday = 1

                        for day in obj.itermonthdates(int(new_month.year), int(new_month.month)):
                            if int(day.day) >= 8:
                                continue
                            d1 = datetime.datetime(int(day.year), int(day.month), int(day.day), tzinfo=custom_timezone_info())
                            if calendar.day_name[d1.weekday()] == event.recurring_details['day_of_week']:
                                date_of_first_weekday = int(day.day)
                                break

                        upcoming_date = date_of_first_weekday + (
                                (converter[event.recurring_details['week_of_month']] - 1) * 7)
                        
                        start_date = datetime.datetime(new_month.year, new_month.month, upcoming_date, start_date.hour,
                                              start_date.minute,
                                              tzinfo=custom_timezone_info())
                    event.start_date_and_time = start_date
                    event.end_date_and_time = start_date + duration

                event.save()
                exception = RecurringEventException.objects.filter(event=event).first()
                exception_former_time = exception.former_time.replace(tzinfo=custom_timezone_info()) if exception else None
                event_start_date_and_time = event.start_date_and_time.replace(tzinfo=custom_timezone_info())
                
                if exception and (exception_former_time < event_start_date_and_time):
                    exception.delete()

            except Exception as e:
                print(str(e))
                return CustomMassenergizeError(e)
        return None, None

    def rank_event(self, args, context: Context) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            id = args.get('id', None)
            rank = args.get('rank', None)
            if id and rank:

                events = Event.objects.filter(id=id)
                events.update(rank=rank)
                event = events.first()
                # ----------------------------------------------------------------
                Spy.create_event_footage(actions=[event], context=context, type=FootageConstants.update(),
                                         notes=f"Rank updated to - {rank}")
                # ----------------------------------------------------------------
                return events.first(), None
            else:
                raise Exception("Rank and ID not provided to events.rank")

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def delete_event(self, context: Context, event_id) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            events = Event.objects.filter(id=event_id)
            if not events:
                return None, InvalidResourceError()
            
            event_community = events.first().community
            if event_community and not is_admin_of_community(context, event_community.id):
                return None, NotAuthorizedError()

            if len(events) > 1:
                return None, CustomMassenergizeError("Deleting multiple events not supported")
            event = events.first()
            events.delete()

            # ----------------------------------------------------------------
            Spy.create_event_footage(events=[], context=context, type=FootageConstants.delete(),
                                     notes=f"Deleted ID({event_id})")
            # ----------------------------------------------------------------
            return event, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def fetch_other_events_for_cadmin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        """
        * Look for events from a given list of communities that are open to everyone,
        * Or are open to any of the admin's communities 
        * With the exclude variable set, we list events from every community, excluding ones from the given 
        * community list  
        * Or
        * And in all cases, dont return templates
    """
        try:
            ids = args.get("community_ids")
            excluded = args.get("exclude", False)
            events = []
            admin_of = []
            filter_params = get_events_filter_params(context.get_params())

            user = UserProfile.objects.filter(email=context.user_email).first()
            today = parse_datetime_to_aware()
            if user:
                admin_of = [g.community.id for g in user.communityadmingroup_set.all()]

            if excluded:
                # Find all events that are open in any community, but exclude events from the selected communities
                events = Event.objects.filter(
                    Q(start_date_and_time__gte=today, is_published=True, publicity=EventConstants.open(),
                      is_global=False) | Q(start_date_and_time__gte=today, is_published=True,
                                           publicity=EventConstants.open_to(),
                                           communities_under_publicity__id__in=admin_of)).exclude(
                    community__id__in=ids).order_by("-id")

            else:
                # Find events that have publicity as open, and belong to the selected community, OR, find events that from any of the listed communities that are open to any of the admins communities
                events = Event.objects.filter(
                    Q(start_date_and_time__gte=today, is_published=True, community__id__in=ids,
                      publicity=EventConstants.open(), is_global=False) | Q(start_date_and_time__gte=today,
                                                                            is_published=True, community__id__in=ids,
                                                                            publicity=EventConstants.open_to(),
                                                                            communities_under_publicity__id__in=admin_of,
                                                                            is_global=False)).distinct().order_by("-id")
            return events.filter(*filter_params).distinct(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_events_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            community_id = args.pop("community_id", None)
            community_ids = [community_id] if community_id else []

            if context.user_is_super_admin:
                return self.list_events_for_super_admin(context)

            elif not context.user_is_community_admin:
                return None, NotAuthorizedError()
            
            if community_id and not is_admin_of_community(context, community_id):
                return None, NotAuthorizedError()

            if community_id == 0:
                # return actions from all communities
                return self.list_events_for_super_admin(context)
            
            filter_params = get_events_filter_params(context.get_params())
            filters_to_exclude = []
            # community_id coming from admin portal is 'undefined'
            if not community_id:
                user = UserProfile.objects.get(pk=context.user_id)
                admin_groups = user.communityadmingroup_set.all()
                community_ids.extend([ag.community.id for ag in admin_groups])
                filters_to_exclude.append(Q(name__contains=" (rescheduled)"))
                
            # don't return the events that are rescheduled instances of recurring events - these should be edited by CAdmins in the recurring event's edit form,
            # not as their own separate events
            events = Event.objects.filter(Q(community__id__in=community_ids) | Q(is_global=True), *filter_params,
                                              is_deleted=False).exclude(*filters_to_exclude).select_related(
                    'image', 'community').prefetch_related('tags')
            
            shared = Event.objects.filter(shared_to__id__in=community_ids).select_related('image', 'community').prefetch_related('tags')
            
            all_events = events | shared
            
            return all_events.distinct(), None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def list_events_for_super_admin(self, context: Context):
        try:
            # don't return the events that are rescheduled instances of recurring events - these should be edited by CAdmins in the recurring event's edit form,
            # not as their own separate events
            filter_params = get_events_filter_params(context.get_params())

            events = Event.objects.filter(*filter_params, is_deleted=False).exclude(
                name__contains=" (rescheduled)").select_related('image', 'community').prefetch_related('tags')
            return events, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def get_rsvp_list(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        try:
            event_id = args.pop("event_id", None)
            # TODO: return list of attendees for all events of a community
            # community_id = args.pop("community_id", None)

            if event_id:
                event = Event.objects.filter(pk=event_id).first()
                if not event:
                    return None, InvalidResourceError()

                event_attendees = EventAttendee.objects.filter(event=event)
                return event_attendees, None

            else:
                return None, InvalidResourceError()

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def get_rsvp_status(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            event_id = args.pop("event_id", None)
            args: dict = context.args
            user = get_user_or_die(context, args)
            event = Event.objects.filter(pk=event_id).first()
            if not event:
                return None, InvalidResourceError()

            event_attendee = EventAttendee.objects.filter(event=event, user=user)
            if event_attendee:
                return event_attendee.first(), None
            else:
                return None, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def rsvp_update(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            event_id = args.pop("event_id", None)
            status = args.pop("status", "SAVE")
            user = get_user_from_context(context)
            event = Event.objects.filter(pk=event_id).first()
            if not event:
                return None, InvalidResourceError()

            event_attendees = EventAttendee.objects.filter(event=event, user=user, is_deleted=False)
            if event_attendees:
                event_attendee = event_attendees.first()
                if status == "Not Going":
                    event_attendee.delete()
                else:
                    event_attendee.status = status
                    event_attendee.save()
            elif status != "Not Going":
                event_attendee = EventAttendee.objects.create(event=event, user=user, status=status)
            else:
                return None, None
            return event_attendee, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def rsvp_remove(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            rsvp_id = args.pop("rsvp_id", None)
            event_id = args.pop("event_id", None)
            user = get_user_from_context(context)

            if rsvp_id:
                result = EventAttendee.objects.filter(pk=rsvp_id).delete()
            elif event_id:
                event = Event.objects.filter(pk=event_id).first()
                if not event:
                    return None, InvalidResourceError()
                result = EventAttendee.objects.filter(event=event, user=user).delete()
            else:
                raise Exception("events.rsvp.remove: must specify rsvp or event id")

            return result, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)

    def share_event(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            event_id = args.pop("event_id", None)
            event = Event.objects.filter(id=event_id).first()
            shared_to = args.pop("shared_to", None)
            if shared_to:
                first = shared_to[0]
                if first == "reset":
                    event.shared_to.clear()
                else:
                    event.shared_to.set(shared_to)
            event.save()

            return event, None
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)
    
    def create_event_reminder_settings(self, context: Context, args) -> Tuple[EventNudgeSetting, MassEnergizeAPIError]:
        try:
            
            event_id = args.pop("event_id", None)
            communities = args.pop("community_ids", [])
            
            user = get_user_from_context(context)
            is_all_communities = communities and communities[0].lower() == "all"
            
            event = Event.objects.filter(id=event_id).first()
            if not event:
                return None, CustomMassenergizeError("Event with the given ID does not exist")
            
            settings, exists = EventNudgeSetting.objects.get_or_create(event=event, **args)
            
            if is_all_communities:
                if context.user_is_super_admin:
                    communities = Community.objects.filter(is_deleted=False).values_list('id', flat=True)
                elif context.user_is_community_admin:
                    communities = [c.id for c in user.communityadmingroup_set.all()] if user else []
                    communities = communities + event.communities_shared_to()
                EventNudgeSetting.objects.filter(event=event).exclude(id=settings.id if settings else None).delete()
            else:
                other_nudge_settings = EventNudgeSetting.objects.filter(event=event,communities__in=communities).exclude(id=settings.id)
                for nudge_setting in other_nudge_settings:
                    for community in communities:
                        nudge_setting.communities.remove(community)
                        nudge_setting.save()
            
            if exists:
                settings.communities.add(*communities)
                settings.last_updated_by = user
                settings.save()
            else:
                settings.creator = user
                settings.communities.set(communities)
                settings.last_updated_by = user
                settings.save()
            
            return event, None
        
        
        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(e)


    def delete_event_reminder_settings(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
        try:
            nudge_settings_id = args.get("nudge_settings_id")
            if not nudge_settings_id:
                return None, CustomMassenergizeError("Nudge settings ID not provided")

            try:
                nudge_settings = EventNudgeSetting.objects.get(id=nudge_settings_id)
            except EventNudgeSetting.DoesNotExist:
                return None, CustomMassenergizeError(f"Nudge settings with ID {nudge_settings_id} does not exist")

            if not context.user_is_super_admin and (nudge_settings.creator_id != context.user_id or not is_admin_of_community(context, nudge_settings.event.community.id)):
                return None, NotAuthorizedError()

            nudge_settings.delete()

            return {"success": True}, None

        except Exception as e:
            log.exception(e)
            return None, CustomMassenergizeError(str(e))

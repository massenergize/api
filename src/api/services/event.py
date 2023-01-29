from datetime import date
from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from api.store.event import EventStore
from _main_.utils.constants import ADMIN_URL_ROOT, COMMUNITY_URL_ROOT, ME_LOGO_PNG
from _main_.settings import SLACK_SUPER_ADMINS_WEBHOOK_URL
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from .utils import send_slack_message
from api.store.utils import get_user_or_die
from typing import Tuple
from sentry_sdk import capture_message
from django.utils.safestring import mark_safe
#import datetime
#from datetime import timedelta
#
#def _local_datetime(date_and_time):
#  # the local date (in Massachusetts) is different than the UTC date
#  # need to also save the location (as a Location) and get the time zone from that.
#  # KLUGE: assume Massachusetts for now                    
#  dt = datetime.datetime.strptime(str(date_and_time), '%Y-%m-%d %H:%M:%S+00:00')
#  local_datetime = dt - timedelta(hours=4)
#  return local_datetime


class EventService:
  """
  Service Layer for all the events
  """

  def __init__(self):
    self.store =  EventStore()

  def get_event_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    event, err = self.store.get_event_info(context, args)
    if err:
      return None, err
    return serialize(event), None

  def get_rsvp_list(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    rsvps, err = self.store.get_rsvp_list(context, args)
    if err:
      return None, err
    return serialize_all(rsvps), None

  def get_rsvp_status(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    event, err = self.store.get_rsvp_status(context, args)
    if err:
      return None, err
    return serialize(event), None

  def rsvp_update(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      event_attendee, err = self.store.rsvp_update(context, args)
      if err:
        return None, err

      if event_attendee and event_attendee.status == "Going":
        event = event_attendee.event

        event_name = event.name

        # may add these event details
        #date_and_time = _local_datetime(event.start_date_and_time)
        #event_details = "Date and time: " + str(date_and_time)
        #if event.location:
        #  event_details += "/nLocation: " + event.location

        if event.rsvp_email:
          user_email = event_attendee.user.email
          user_name = event_attendee.user.full_name

          first_name = user_name.split(" ")[0]
          if not first_name or first_name == "":
            first_name = user_name

          community = event.community
          community_logo =  community.logo.file.url if community and community.logo else ME_LOGO_PNG
          community_name = community.name

          # need to validate e-mails from community admins
          #from_email = community.owner_email
          from_email = None

          homelink = f'{COMMUNITY_URL_ROOT}/{community.subdomain}'


          subject = 'Thank you for registering for ' + event_name

          content_variables = {
            'name': first_name,
            'community': community_name,
            'event_name': event_name,
            'event_link': f"{homelink}/events/{event.id}",
            'custom_message': mark_safe(event.rsvp_message),
            'homelink': homelink,
            'contactlink': f'{homelink}/contactus',
            'logo': community_logo,
            'privacylink': f"{homelink}/policies?name=Privacy%20Policy"
          }

          send_massenergize_rich_email(
              subject, user_email, 'event_rsvp_email.html', content_variables, from_email)


      return serialize(event_attendee), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def rsvp_remove(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    event, err = self.store.rsvp_remove(context, args)
    if err:
      return None, err
    return event, None

  def copy_event(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    event, err = self.store.copy_event(context, args)
    if err:
      return None, err
    return serialize(event), None

  def list_recurring_event_exceptions(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    exceptions, err = self.store.list_recurring_event_exceptions(context, args)
    if err: 
      print(err)
      return None, err
    return exceptions, None

  def update_recurring_event_date(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    events, err = self.store.update_recurring_event_date(context, args)
    if err:
      return None, err
    
    return serialize_all(events), None

  def list_events(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    
    events, err = self.store.list_events(context, args)
    if err:
      return None, err
    return serialize_all(events), None


  def create_event(self, context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      event, err = self.store.create_event(context, args)
      if err:
        return None, err

      if user_submitted:

        # For now, send e-mail to primary community contact for a site
        admin_email = event.community.owner_email
        admin_name = event.community.owner_name
        first_name = admin_name.split(" ")[0]
        if not first_name or first_name == "":
          first_name = admin_name

        community_name = event.community.name

        user = get_user_or_die(context, args)
        if user:
          name = user.full_name
          email = user.email
        else:
          return None, CustomMassenergizeError('Event submission incomplete')

        subject = 'User Event Submitted'

        content_variables = {
          'name': first_name,
          'community_name': community_name,
          'url': f"{ADMIN_URL_ROOT}/admin/edit/{event.id}/event",
          'from_name': name,
          'email': email,
          'title': event.title,
          'body': event.description,
        }
        send_massenergize_rich_email(
              subject, admin_email, 'event_submitted_email.html', content_variables)

        send_slack_message(
            #SLACK_COMMUNITY_ADMINS_WEBHOOK_URL, {
            SLACK_SUPER_ADMINS_WEBHOOK_URL, {
            "content": "User submitted Event for "+community_name,
            "from_name": name,
            "email": email,
            "subject": event.title,
            "message": event.description,
            "url": f"{ADMIN_URL_ROOT}/admin/edit/{event.id}/event",
            "community": community_name
        }) 

      return serialize(event), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def update_event(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    event, err = self.store.update_event(context, args)
    if err:
      return None, err
    return serialize(event), None

  def rank_event(self, args, context) -> Tuple[dict, MassEnergizeAPIError]:
    event, err = self.store.rank_event(args,context)
    if err:
      return None, err
    return serialize(event), None

  def delete_event(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    event, err = self.store.delete_event(context, args)
    if err:
      return None, err
    return serialize(event), None


  def list_events_for_community_admin(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    events, err = self.store.list_events_for_community_admin(context, args)
    if err:
      return None, err
    return serialize_all(events), None

  def fetch_other_events_for_cadmin(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    events, err = self.store.fetch_other_events_for_cadmin(context, args)
    if err:
      return None, err
    return serialize_all(events), None


  def list_events_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
    events, err = self.store.list_events_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(events), None

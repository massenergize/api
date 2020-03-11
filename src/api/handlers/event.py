"""Handler file for all routes pertaining to events"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_list, parse_bool, check_length, parse_date, parse_int, parse_location
from api.services.event import EventService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator

#TODO: install middleware to catch authz violations
#TODO: add logger

class EventHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = EventService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/events.info", self.info()) 
    self.add("/events.create", self.create())
    self.add("/events.add", self.create())
    self.add("/events.copy", self.copy())
    self.add("/events.list", self.list())
    self.add("/events.update", self.update())
    self.add("/events.delete", self.delete())
    self.add("/events.remove", self.delete())
    self.add("/events.rsvp", self.rsvp())
    self.add("/events.todo", self.save_for_later())

    #admin routes
    self.add("/events.listForCommunityAdmin", self.community_admin_list())
    self.add("/events.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def event_info_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      event_id = args.pop('event_id', None)
      event_info, err = self.service.get_event_info(context, event_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return event_info_view

  def copy(self) -> function:
    def copy_event(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      event_id = args.pop('event_id', None)
      event_info, err = self.service.copy_event(context, event_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return copy_event


  def rsvp(self) -> function:
    def rsvp_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      event_id = args.pop('event_id', None)
      event_info, err = self.service.get_event_info(context, event_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return rsvp_view

  def save_for_later(self) -> function:
    def save_for_later_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      event_id = args.pop('event_id', None)
      event_info, err = self.service.get_event_info(context, event_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return save_for_later_view


  def create(self) -> function:
    def create_event_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      ok, err = check_length(args, 'name', min_length=5, max_length=100)
      if not ok:
        return MassenergizeResponse(error=str(err), status=err.status)
      args['tags'] = parse_list(args.get('tags', []))
      args['is_global'] = parse_bool(args.pop('is_global', None))
      args['archive'] = parse_bool(args.pop('archive', None))
      args['is_published'] = parse_bool(args.pop('is_published', None))
      args['have_address'] =  parse_bool(args.pop('have_address', False))
      args = parse_location(args)

      event_info, err = self.service.create_event(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return create_event_view


  def list(self) -> function:
    def list_event_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop('community_id', None)
      subdomain = args.pop('subdomain', None)
      user_id = args.pop('user_id', None)
      event_info, err = self.service.list_events(context, community_id, subdomain, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return list_event_view


  def update(self) -> function:
    def update_event_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      event_id = args.pop('event_id', None)
      ok, err = check_length(args, 'name', min_length=5, max_length=100)
      if not ok:
        return MassenergizeResponse(error=str(err), status=err.status)

      args['tags'] = parse_list(args.get('tags', []))
      args['is_global'] = parse_bool(args.pop('is_global', None))
      args['archive'] = parse_bool(args.pop('archive', None))
      args['is_published'] = parse_bool(args.pop('is_published', None))
      args['have_address'] =  parse_bool(args.pop('have_address', False))
      args = parse_location(args)

      event_info, err = self.service.update_event(context, event_id, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return update_event_view


  def delete(self) -> function:
    def delete_event_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      event_id = args.get("event_id", None)
      event_info, err = self.service.delete_event(context, event_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return delete_event_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop("community_id", None)
      events, err = self.service.list_events_for_community_admin(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=events)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      events, err = self.service.list_events_for_super_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=events)
    return super_admin_list_view
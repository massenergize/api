"""Handler file for all routes pertaining to events"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_list, parse_bool, check_length, parse_date, parse_int
from api.services.event import EventService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

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
    self.add("/events.list", self.list())
    self.add("/events.update", self.update())
    self.add("/events.delete", self.delete())
    self.add("/events.remove", self.delete())

    #admin routes
    self.add("/events.listForCommunityAdmin", self.community_admin_list())
    self.add("/events.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def event_info_view(request) -> None: 
      args = request.context.args
      event_id = args.pop('event_id', None)
      event_info, err = self.service.get_event_info(event_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return event_info_view


  def create(self) -> function:
    def create_event_view(request) -> None: 
      args = request.context.args
      print(args)
      ok, err = check_length(args, 'name', min_length=5, max_length=100)
      if not ok:
        return MassenergizeResponse(error=str(err), status=err.status)


      args['start_date_and_time'] = parse_date(args.get('start_date_and_time', ''))
      args['end_date_and_time'] = parse_date(args.get('end_date_and_time', ''))
      args['tags'] = parse_list(args.get('tags', []))
      args['is_global'] = parse_bool(args.pop('is_global', None))


      event_info, err = self.service.create_event(args)
      print(event_info)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return create_event_view


  def list(self) -> function:
    def list_event_view(request) -> None: 
      args = request.context.args
      community_id = args.pop('community_id', None)
      subdomain = args.pop('subdomain', None)
      user_id = args.pop('user_id', None)
      event_info, err = self.service.list_events(community_id, subdomain, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return list_event_view


  def update(self) -> function:
    def update_event_view(request) -> None: 
      args = request.context.args
      print(args)
      event_id = args.pop('event_id', None)
      ok, err = check_length(args, 'name', min_length=5, max_length=100)
      if not ok:
        return MassenergizeResponse(error=str(err), status=err.status)

      args['tags'] = parse_list(args.get('tags', []))
      args['is_global'] = parse_bool(args.pop('is_global', None))

      event_info, err = self.service.update_event(event_id, args)
      print(event_info)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return update_event_view


  def delete(self) -> function:
    def delete_event_view(request) -> None: 
      args = request.context.args
      event_id = args[id]
      event_info, err = self.service.delete_event(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return delete_event_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = request.context.args
      community_id = args.pop("community_id", None)
      events, err = self.service.list_events_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=events)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = request.context.args
      events, err = self.service.list_events_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=events)
    return super_admin_list_view
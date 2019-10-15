"""Handler file for all routes pertaining to events"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.event import EventService
from api.utils.massenergize_response import MassenergizeResponse
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
      args = get_request_contents(request)
      event_info, err = self.service.get_event_info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return event_info_view


  def create(self) -> function:
    def create_event_view(request) -> None: 
      args = get_request_contents(request)
      event_info, err = self.service.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return create_event_view


  def list(self) -> function:
    def list_event_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      event_info, err = self.service.list_events(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return list_event_view


  def update(self) -> function:
    def update_event_view(request) -> None: 
      args = get_request_contents(request)
      event_info, err = self.service.update_event(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return update_event_view


  def delete(self) -> function:
    def delete_event_view(request) -> None: 
      args = get_request_contents(request)
      event_id = args[id]
      event_info, err = self.service.delete_event(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=event_info)
    return delete_event_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      events, err = self.service.list_events_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=events)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      events, err = self.service.list_events_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=events)
    return super_admin_list_view
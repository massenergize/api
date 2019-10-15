"""Handler file for all routes pertaining to communities"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.community import CommunityService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class CommunityHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = CommunityService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/communities.info", self.info()) 
    self.add("/communities.create", self.create())
    self.add("/communities.add", self.create())
    self.add("/communities.list", self.list())
    self.add("/communities.update", self.update())
    self.add("/communities.delete", self.delete())
    self.add("/communities.remove", self.delete())

    #admin routes
    self.add("/communities.listForCommunityAdmin", self.service_admin_list())
    self.add("/communities.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def community_info_view(request) -> None: 
      args = get_request_contents(request)
      community_info, err = self.service.get_community_info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return community_info_view


  def create(self) -> function:
    def create_community_view(request) -> None: 
      args = get_request_contents(request)
      community_info, err = self.service.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return create_community_view


  def list(self) -> function:
    def list_community_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args["community__id"]
      user_id = args["user_id"]
      community_info, err = self.service.list_communities(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return list_community_view


  def update(self) -> function:
    def update_community_view(request) -> None: 
      args = get_request_contents(request)
      community_info, err = self.service.update_community(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return update_community_view


  def delete(self) -> function:
    def delete_community_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args[id]
      community_info, err = self.service.delete_community(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=community_info)
    return delete_community_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      communities, err = self.service.list_communities_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=communities)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      communities, err = self.service.list_communities_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=communities)
    return super_admin_list_view
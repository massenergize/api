"""Handler file for all routes pertaining to testimonials"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.testimonial import TestimonialService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class TestimonialHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = TestimonialService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/testimonials.info", self.info()) 
    self.add("/testimonials.create", self.create())
    self.add("/testimonials.add", self.create())
    self.add("/testimonials.list", self.list())
    self.add("/testimonials.update", self.update())
    self.add("/testimonials.delete", self.delete())
    self.add("/testimonials.remove", self.delete())

    #admin routes
    self.add("/testimonials.listForCommunityAdmin", self.community_admin_list())
    self.add("/testimonials.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def testimonial_info_view(request) -> None: 
      args = get_request_contents(request)
      testimonial_info, err = self.service.get_testimonial_info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=testimonial_info)
    return testimonial_info_view


  def create(self) -> function:
    def create_testimonial_view(request) -> None: 
      args = get_request_contents(request)
      testimonial_info, err = self.service.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=testimonial_info)
    return create_testimonial_view


  def list(self) -> function:
    def list_testimonial_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args["community__id"]
      user_id = args["user_id"]
      testimonial_info, err = self.service.list_testimonials(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=testimonial_info)
    return list_testimonial_view


  def update(self) -> function:
    def update_testimonial_view(request) -> None: 
      args = get_request_contents(request)
      testimonial_info, err = self.service.update_testimonial(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=testimonial_info)
    return update_testimonial_view


  def delete(self) -> function:
    def delete_testimonial_view(request) -> None: 
      args = get_request_contents(request)
      testimonial_id = args[id]
      testimonial_info, err = self.service.delete_testimonial(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=testimonial_info)
    return delete_testimonial_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      testimonials, err = self.service.list_testimonials_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=testimonials)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      testimonials, err = self.service.list_testimonials_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=testimonials)
    return super_admin_list_view
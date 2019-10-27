"""Handler file for all routes pertaining to testimonials"""

from _main_.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_list, parse_bool, check_length, rename_field, parse_int
from api.services.testimonial import TestimonialService
from _main_.utils.massenergize_response import MassenergizeResponse
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
      args = rename_field(args, 'testimonial_id', 'id')
      testimonial_info, err = self.service.get_testimonial_info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=testimonial_info)
    return testimonial_info_view


  def create(self) -> function:
    def create_testimonial_view(request) -> None: 
      args = get_request_contents(request)
      args = rename_field(args, 'community_id', 'community')
      args = rename_field(args, 'action_id', 'action')
      args = rename_field(args, 'vendor_id', 'vendor')
      args['tags'] = parse_list(args.get('tags', []))
      args['is_approved'] = parse_bool(args.pop('is_approved', None))
      testimonial_info, err = self.service.create_testimonial(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=testimonial_info)
    return create_testimonial_view


  def list(self) -> function:
    def list_testimonial_view(request) -> None: 
      args = get_request_contents(request)
      args = rename_field(args, 'community_id', 'community__id')
      args = rename_field(args, 'subdomain', 'community__subdomain')
      args = rename_field(args, 'user_id', 'user__id')
      args = rename_field(args, 'user_email', 'user__email')
      testimonial_info, err = self.service.list_testimonials(args)
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
      testimonial_id = args.pop('testimonial_id', None)
      testimonial_info, err = self.service.delete_testimonial(testimonial_id)
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
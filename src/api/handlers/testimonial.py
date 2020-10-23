"""Handler file for all routes pertaining to testimonials"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_list, parse_bool, check_length, rename_field, parse_int
from api.services.testimonial import TestimonialService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required


class TestimonialHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = TestimonialService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/testimonials.info", self.info) 
    self.add("/testimonials.create", self.create)
    self.add("/testimonials.add", self.create)
    self.add("/testimonials.list", self.list)
    self.add("/testimonials.update", self.update)
    self.add("/testimonials.delete", self.delete)
    self.add("/testimonials.remove", self.delete)

    #admin routes
    self.add("/testimonials.listForCommunityAdmin", self.community_admin_list)
    self.add("/testimonials.listForSuperAdmin", self.super_admin_list)

  # not @login_required
  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'testimonial_id', 'id')
    testimonial_info, err = self.service.get_testimonial_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=testimonial_info)

  @login_required
  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'community_id', 'community')
    args = rename_field(args, 'action_id', 'action')
    args = rename_field(args, 'vendor_id', 'vendor')
    args = rename_field(args, 'preferredName', 'preferred_name')
    args['tags'] = parse_list(args.get('tags', []))

    # check validity - these should be IDs
    community = args.get('community', None)
    if community and not isinstance(community, int):
        args["community"] = parse_int(community)

    action = args.get('action', None)
    if action and not isinstance(action, int):
        args["action"] = parse_int(action)

    vendor = args.get('vendor', None)
    if vendor and not isinstance(vendor, int):
        args["vendor"] = parse_int(vendor)

      # To do, if we decide: 
      # if user specifies other_vendor and passed to API - should record it as an unapproved vendor

    is_approved = args.pop("is_approved", None)
    if is_approved:
      args["is_approved"] = parse_bool(is_approved)
    is_published = args.get("is_published", None)
    if is_published:
      args["is_published"] = parse_bool(is_published)

    # no anonymous option anymore
    args["anonymous"] = False
 
    testimonial_info, err = self.service.create_testimonial(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=testimonial_info)

  def list(self, request):
    context = request.context
    args = context.args
    testimonial_info, err = self.service.list_testimonials(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=testimonial_info)

  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    
    is_approved = args.pop("is_approved", None)
    if is_approved:
      args["is_approved"] = parse_bool(is_approved)
    is_published = args.get("is_published", None)
    if is_published:
      args["is_published"] = parse_bool(is_published)
    args = rename_field(args, 'community_id', 'community')
    args = rename_field(args, 'action_id', 'action')
    args = rename_field(args, 'vendor_id', 'vendor')
    args['tags'] = parse_list(args.get('tags', []))
    testimonial_id = args.pop("testimonial_id", None)
    testimonial_info, err = self.service.update_testimonial(context, testimonial_id, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=testimonial_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    testimonial_id = args.pop('testimonial_id', None)
    testimonial_info, err = self.service.delete_testimonial(context, testimonial_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=testimonial_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    testimonials, err = self.service.list_testimonials_for_community_admin(context, community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=testimonials)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    testimonials, err = self.service.list_testimonials_for_super_admin(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=testimonials)

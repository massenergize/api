"""Handler file for all routes pertaining to testimonials"""

from _main_.utils.context import Context
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.route_handler import RouteHandler
from api.decorators import admins_only, login_required, super_admins_only
from api.services.testimonial import TestimonialService
from api.store.common import expect_media_fields


class TestimonialHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = TestimonialService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/testimonials.info", self.info)
    self.add("/testimonials.create", self.create)
    self.add("/testimonials.add", self.submit)
    self.add("/testimonials.submit", self.submit)
    self.add("/testimonials.list", self.list)
    self.add("/testimonials.update", self.update)
    self.add("/testimonials.delete", self.delete)
    self.add("/testimonials.remove", self.delete)
    self.add("/testimonials.rank", self.rank)

    # admin routes
    self.add("/testimonials.listForCommunityAdmin", self.community_admin_list)
    self.add("/testimonials.listForSuperAdmin", self.super_admin_list)

  def info(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", int, is_required=True)
    self.validator.rename("testimonial_id", "id")
    args, err = self.validator.verify(args)

    if err:
      return err

    testimonial_info, err = self.service.get_testimonial_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=testimonial_info)

  @admins_only
  def create(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("title", str, is_required=True)
    self.validator.expect('community', int)
    self.validator.expect('action', int)
    self.validator.expect('vendor', int)
    self.validator.expect("tags", list)
    self.validator.expect("is_approved", bool)
    self.validator.expect("is_published", bool)
    self.validator.rename('community_id', 'community')
    self.validator.rename('action_id', 'action')
    self.validator.rename('vendor_id', 'vendor')
    self.validator.rename('preferredName', 'preferred_name')
    self.validator.expect("image", "str_list")
    args, err = self.validator.verify(args)

    if err:
      return err

    # no anonymous option anymore
    # args["anonymous"] = False

    testimonial_info, err = self.service.create_testimonial(context, args)
    if err:
      return err
    return MassenergizeResponse(data=testimonial_info)

# same as create, except this is for user submitted testimonials
  @login_required
  def submit(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("title", str, is_required=True)
    self.validator.expect('community', int)
    self.validator.expect('action', int)
    self.validator.expect('vendor', int)
    self.validator.rename('community_id', 'community')
    self.validator.rename('action_id', 'action')
    self.validator.rename('vendor_id', 'vendor')
    self.validator.rename('preferredName', 'preferred_name')
    self.validator.expect('testimonial_id', str)
    self.validator.expect("image", "file", is_required=False)
    expect_media_fields(self)
    args, err = self.validator.verify(args)

    if err:
      return err

    # no anonymous option anymore
    # args["anonymous"] = False

    # user submitted testimonial, so notify the community admins
    user_submitted = True
    is_edit = args.pop("testimonial_id", None)

    if is_edit:
      testimonial_info, err = self.service.update_testimonial(context, args)
    else:
      testimonial_info, err = self.service.create_testimonial(context, args, user_submitted)
    if err:
      return err
    return MassenergizeResponse(data=testimonial_info)

  def list(self, request):
    context = request.context
    args = context.args

    self.validator.expect("community_id", int)
    self.validator.expect("subdomain", str)
    self.validator.expect("community_ids", list)

    args, err = self.validator.verify(args)
    if err:
      return err

    testimonial_info, err = self.service.list_testimonials(context, args)

    if err:
      return err
    return MassenergizeResponse(data=testimonial_info)

  # @admins_only
  # changed to @Login_Required so I can edit the testimonial as the creator and admin
  @login_required
  def update(self, request):

    # check if admin or user who submitted the testimonial
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", int, is_required=True)
    self.validator.expect("is_approved", bool)
    self.validator.expect("is_published", bool)
    self.validator.expect("community", int)
    self.validator.expect("action", int)
    self.validator.expect("vendor", int)
    self.validator.expect("tags", list)
    self.validator.rename("testimonial_id", "id")
    self.validator.rename('community_id', 'community')
    self.validator.rename('action_id', 'action')
    self.validator.rename('vendor_id', 'vendor')
    self.validator.expect("image", "str_list")
    self.validator.expect("help_link", str, is_required=False)

    expect_media_fields(self)
    args, err = self.validator.verify(args)

    if err:
      return err

    testimonial_info, err = self.service.update_testimonial(context, args)
    if err:
      return err
    return MassenergizeResponse(data=testimonial_info)

  @admins_only
  def rank(self, request):
    """ Update the rank of a testimonial, nothing else """
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("id", int, is_required=True)
    self.validator.expect("rank", int, is_required=True)
    self.validator.rename("testimonial_id", "id")

    args, err = self.validator.verify(args)
    if err:
      return err

    testimonial_info, err = self.service.rank_testimonial(args,context)
    if err:
      return err
    return MassenergizeResponse(data=testimonial_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    testimonial_id = args.pop('testimonial_id', None)
    testimonial_info, err = self.service.delete_testimonial(context, testimonial_id)
    if err:
      return err
    return MassenergizeResponse(data=testimonial_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    # community_id = args.pop("community_id", None)
    self.validator.expect("testimonial_ids", list, is_required=False)
    args, err = self.validator.verify(args)
    if err:
      return err
    
    testimonials, err = self.service.list_testimonials_for_community_admin(context, args)
    if err:
      return err
    return MassenergizeResponse(data=testimonials)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    self.validator.expect("testimonial_ids", list, is_required=False)
    args, err = self.validator.verify(args)
    if err:
      return err
    testimonials, err = self.service.list_testimonials_for_super_admin(context,args)
    if err:
      return err
    return MassenergizeResponse(data=testimonials)

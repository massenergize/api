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
        self.add("/testimonials.rank", self.rank)

        # admin routes
        self.add("/testimonials.listForCommunityAdmin",
                 self.community_admin_list)
        self.add("/testimonials.listForSuperAdmin", self.super_admin_list)

    def info(self, request):
        context: Context = request.context
        args: dict = context.args

        self.validator.expect("id", int, is_required=True)
        self.validator.rename("testimonial_id", "id")
        args, err = self.validator.verify(args)

        if err:
            return err

        testimonial_info, err = self.service.get_testimonial_info(
            context, args)
        if err:
            return MassenergizeResponse(error=str(err), status=err.status)
        return MassenergizeResponse(data=testimonial_info)

    @login_required
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
        args, err = self.validator.verify(args)

        if err:
            return err

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
        args, err = self.validator.verify(args)

        if err:
            return err

        testimonial_info, err = self.service.update_testimonial(context, args)
        if err:
            return MassenergizeResponse(error=str(err), status=err.status)
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

        testimonial_info, err = self.service.rank_testimonial(args)
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
        testimonials, err = self.service.list_testimonials_for_community_admin(
            context, community_id)
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

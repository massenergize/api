"""Handler file for all routes pertaining to vendors"""

from _main_.utils.route_handler import RouteHandler
import _main_.utils.common as utils
from _main_.utils.common import get_request_contents, rename_field, parse_bool, parse_location, parse_list, validate_fields, parse_string
from api.services.vendor import VendorService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator

#TODO: install middleware to catch authz violations
#TODO: add logger

class VendorHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = VendorService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/vendors.info", self.info()) 
    self.add("/vendors.create", self.create())
    self.add("/vendors.add", self.create())
    self.add("/vendors.list", self.list())
    self.add("/vendors.update", self.update())
    self.add("/vendors.delete", self.delete())
    self.add("/vendors.remove", self.delete())
    self.add("/vendors.publish", self.publish())

    #admin routes
    self.add("/vendors.listForCommunityAdmin", self.community_admin_list())
    self.add("/vendors.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def vendor_info_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body()
      args = rename_field(args, 'vendor_id', 'id')
      vendor_info, err = self.service.get_vendor_info(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return vendor_info_view

  def publish(self) -> function:
    def vendor_info_view(request) -> None: 
      args = get_request_contents(request)
      args = rename_field(args, 'vendor_id', 'id')
      args['is_published'] =True
      vendor_info, err = self.service.update(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return vendor_info_view


  def create(self) -> function:
    def create_vendor_view(request) -> None:
      context: Context  = request.context
      args = context.get_request_body() 
      validator: Validator = Validator()
      (validator
        .add("accepted_terms_and_conditions", bool)
        .add("key_contact_name", str)
        .add("key_contact_email", str)
        .add("name", str)
        .add("email", str)
        .add("is_verified", str)
        .add("phone_number", str)
        .add("have_address", bool)
        .add("is_verified", bool, is_required=False)
        .add("communities", list, is_required=False)
        .add("service_area_states", list, is_required=False)
        .add("properties_serviced", list, is_required=False)
      )

      args, err = validator.verify(args)
      if err:
        return err

      if not args.pop('accepted_terms_and_conditions', False):
        return MassenergizeResponse(error="Please accept terms the Terms And Conditions to Proceed")
      
      args = parse_location(args)
      if not args.pop('have_address', None):
        args.pop('location')

      args['key_contact'] = {
        "name": args.pop('key_contact_name', None),
        "email": args.pop('key_contact_email', None)
      } 

      vendor_info, err = self.service.create_vendor(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return create_vendor_view


  def list(self) -> function:
    def list_vendor_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body()
      community_id = args.pop('community_id', None)
      
      vendor_info, err = self.service.list_vendors(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return list_vendor_view


  def update(self) -> function:
    def update_vendor_view(request) -> None: 
      args = get_request_contents(request)
      vendor_info, err = self.service.update_vendor(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return update_vendor_view


  def delete(self) -> function:
    def delete_vendor_view(request) -> None: 
      args = get_request_contents(request)
      vendor_id = args[id]
      vendor_info, err = self.service.delete_vendor(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return delete_vendor_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      vendors, err = self.service.list_vendors_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendors)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      vendors, err = self.service.list_vendors_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendors)
    return super_admin_list_view
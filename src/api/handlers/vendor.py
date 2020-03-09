"""Handler file for all routes pertaining to vendors"""

from _main_.utils.route_handler import RouteHandler
import _main_.utils.common as utils
from _main_.utils.common import get_request_contents, rename_field, parse_bool, parse_location, parse_list, validate_fields, parse_string
from api.services.vendor import VendorService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import CustomMassenergizeError
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
    self.add("/vendors.copy", self.copy())
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
      context: Context = request.context
      args: dict = context.args
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
        .expect("key_contact_name", str)
        .expect("key_contact_email", str)
        .expect("onboarding_contact_email", str)
        .expect("name", str)
        .expect("email", str)
        .expect("phone_number", str)
        .expect("have_address", bool)
        .expect("is_verified", bool)
        .expect("is_published", bool)
        .expect("communities", list, is_required=False)
        .expect("service_area_states", list, is_required=False)
        .expect("properties_serviced", list, is_required=False)
        .expect("image", "file", is_required=False)
        .expect("tags", list, is_required=False)
        .expect("location", "location", is_required=False)
      )

      args, err = validator.verify(args)
      if err:
        return err

      args = parse_location(args)

      #TODO: remove this after deploy
      args.pop('accept_terms_and_conditions', None)

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
      vendor_info, err = self.service.list_vendors(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return list_vendor_view


  def update(self) -> function:
    def update_vendor_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body() 
      args = rename_field(args, 'id', 'vendor_id')
      validator: Validator = Validator()
      (validator
        .expect("vendor_id", int)
        .expect("key_contact_name", str, is_required=False)
        .expect("key_contact_email", str, is_required=False)
        .expect("onboarding_contact_email", str, is_required=False)
        .expect("name", str, is_required=False)
        .expect("email", str, is_required=False)
        .expect("is_verified", bool, is_required=False)
        .expect("phone_number", str, is_required=False)
        .expect("have_address", bool, is_required=False)
        .expect("is_published", bool, is_required=False)
        .expect("communities", list, is_required=False)
        .expect("service_area_states", list, is_required=False)
        .expect("properties_serviced", list, is_required=False)
        .expect("tags", list, is_required=False)
        .expect("image", "file", is_required=False)
        .expect("location", "location", is_required=False)
      )

      args, err = validator.verify(args)
      if err:
        return err

      args['key_contact'] = {}
      key_contact_name = args.pop('key_contact_name', None)
      key_contact_email = args.pop('key_contact_email', None)
      if key_contact_name:
        args['key_contact']["name"] = key_contact_name
      if key_contact_email:
        args['key_contact']["email"] = key_contact_email


      vendor_info, err = self.service.update_vendor(context, args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return update_vendor_view


  def delete(self) -> function:
    def delete_vendor_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      args = rename_field(args, 'vendor_id', 'id')
      vendor_id = args.pop('id', None)
      if not vendor_id:
        return CustomMassenergizeError("Please Provide Vendor Id")
      vendor_info, err = self.service.delete_vendor(vendor_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendor_info)
    return delete_vendor_view


  def copy(self) -> function:
    def copy_vendor_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      args = rename_field(args, 'vendor_id', 'id')
      vendor_id = args.pop('id', None)
      if not vendor_id:
        return CustomMassenergizeError("Please Provide Vendor Id")
      vendor_info, err = self.service.copy_vendor(vendor_id)
      if err:
        return err
      return MassenergizeResponse(data=vendor_info)
    return copy_vendor_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      community_id = args.pop("community_id", None)
      vendors, err = self.service.list_vendors_for_community_admin(context, community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendors)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      context: Context = request.context
      args: dict = context.args
      vendors, err = self.service.list_vendors_for_super_admin(context)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=vendors)
    return super_admin_list_view
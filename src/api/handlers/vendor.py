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
from api.decorators import admins_only, cached_request, super_admins_only, login_required
from api.store.common import expect_media_fields



class VendorHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = VendorService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/vendors.info", self.info) 
    self.add("/vendors.create", self.create)
    self.add("/vendors.add", self.submit)
    self.add("/vendors.submit", self.submit)
    self.add("/vendors.list", self.list)
    self.add("/vendors.update", self.update)
    self.add("/vendors.copy", self.copy)
    #self.add("/vendors.rank", self.rank) TODO    
    self.add("/vendors.delete", self.delete)
    self.add("/vendors.remove", self.delete)

    #admin routes
    self.add("/vendors.listForCommunityAdmin", self.community_admin_list)
    self.add("/vendors.listForSuperAdmin", self.super_admin_list)

  
  def info(self, request):
    context: Context  = request.context
    args = context.get_request_body()
    args = rename_field(args, 'vendor_id', 'id')
    vendor_info, err = self.service.get_vendor_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=vendor_info)

  @admins_only
  def create(self, request):
    
    context: Context  = request.context
    args = context.get_request_body() 

    (self.validator.expect("key_contact_name", str)
      .expect("key_contact_email", str)
      .expect("onboarding_contact_email", str)
      .expect("name", str)
      .expect("email", str)
      .expect("phone_number", str)
      .expect("have_address", bool)
      .expect("is_verified", bool)
      .expect("website", str, is_required=False)
      .expect("is_published", bool)
      .expect('is_approved', bool)
      .expect("communities", list, is_required=False)
      .expect("service_area_states", 'str_list', is_required=False)
      .expect("properties_serviced", 'str_list', is_required=False)
      .expect("image", "str_list", is_required=False)
      .expect("tags", list, is_required=False)
      .expect("location", "location", is_required=False)
    )

    args, err = self.validator.verify(args)
    if err:
      return err

    # not user submitted
    args["is_approved"] = args.pop("is_approved", True) 

    vendor_info, err = self.service.create_vendor(context, args)
    if err:
      return err
    return MassenergizeResponse(data=vendor_info)

  @login_required
  def submit(self, request):
    
    context: Context  = request.context
    args = context.get_request_body() 

    (self.validator.expect("key_contact_name", str)
      .expect("key_contact_email", str)
      .expect("onboarding_contact_email", str)
      .expect("name", str)
      .expect("email", str)
      .expect("phone_number", str)
      .expect("have_address", bool)
      .expect("is_verified", bool)
      .expect("website", str, is_required=False)
      .expect("is_published", bool)
      .expect("communities", list, is_required=False)
      .expect("service_area_states", 'str_list', is_required=False)
      .expect("properties_serviced", 'str_list', is_required=False)
      .expect("image", "file", is_required=False)
      .expect("tags", list, is_required=False)
      .expect("location", str, is_required=False)
      .expect("vendor_id", str)
    
    ) 
  
    expect_media_fields(self)

    args, err = self.validator.verify(args)
    if err:
      return err

    # user submitted vendor, so notify the community admins
    user_submitted = True
    is_edit = args.get("vendor_id", None)

    if is_edit:
      vendor_info, err = self.service.update_vendor(context, args, user_submitted)
    else:
      vendor_info, err = self.service.create_vendor(context, args, user_submitted)
    if err:
      return err
    return MassenergizeResponse(data=vendor_info)

  @cached_request
  def list(self, request):
    context: Context  = request.context
    args = context.get_request_body()      
    vendor_info, err = self.service.list_vendors(context, args)
    if err:
      return err
    return MassenergizeResponse(data=vendor_info)

  @login_required
  def update(self, request):
    context: Context  = request.context
    args = context.get_request_body() 
    (self.validator
      .rename("id","vendor_id")
      .expect("vendor_id", int)
      .expect("key_contact_name", str, is_required=False)
      .expect("key_contact_email", str, is_required=False)
      .expect("onboarding_contact_email", str, is_required=False)
      .expect("name", str, is_required=False)
      .expect("email", str, is_required=False)
      .expect("website", str, is_required=False)
      .expect("is_verified", bool, is_required=False)
      .expect("phone_number", str, is_required=False)
      .expect("have_address", bool, is_required=False)
      .expect("is_published", bool, is_required=False)
      .expect("is_approved", bool, is_required=False)
      .expect("communities", list, is_required=False)
      .expect("service_area_states", 'str_list', is_required=False)
      .expect("properties_serviced", 'str_list', is_required=False)
      .expect("tags", list, is_required=False)
      .expect("image", "str_list", is_required=False)
      .expect("location", "location", is_required=False)
    )

    expect_media_fields(self)
    args, err = self.validator.verify(args)
    if err:
      return err

    vendor_info, err = self.service.update_vendor(context, args)
    if err:
      return err
    return MassenergizeResponse(data=vendor_info)

  @admins_only
  def rank(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('id', int, is_required=True)
    self.validator.expect('rank', int, is_required=True)
    self.validator.rename('vendor_id', 'id')

    args, err = self.validator.verify(args)
    if err:
      return err

    vendor_info, err = self.service.rank_vendor(args,context)
    if err:
      return err
    return MassenergizeResponse(data=vendor_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'vendor_id', 'id')
    vendor_id = args.pop('id', None)
    if not vendor_id:
      return CustomMassenergizeError("Please Provide Vendor Id")
    vendor_info, err = self.service.delete_vendor(vendor_id,context)
    if err:
      return err
    return MassenergizeResponse(data=vendor_info)

  @admins_only
  def copy(self, request):
    context: Context = request.context
    args: dict = context.args
    vendor_id = args.get('vendor_id', None)
    
    if not vendor_id:
      return CustomMassenergizeError("Please Provide Vendor Id")
    vendor_info, err = self.service.copy_vendor(context, args)
    if err:
      return err
    return MassenergizeResponse(data=vendor_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("community_id", int, is_required=False)

    args, err = self.validator.verify(args)
    if err:
      return err
    vendors, err = self.service.list_vendors_for_community_admin(context, args)

    if err:
      return err
    return MassenergizeResponse(data=vendors)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    vendors, err = self.service.list_vendors_for_super_admin(context)
    if err:
      return err
    return MassenergizeResponse(data=vendors)

"""Handler file for all routes pertaining to organizations"""

from _main_.utils.route_handler import RouteHandler
import _main_.utils.common as utils
from _main_.utils.common import get_request_contents, rename_field, parse_bool, parse_location, parse_list, validate_fields, parse_string
from api.services.organization import OrganizationService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import CustomMassenergizeError
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required
from api.store.common import expect_media_fields



class OrganizationHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = OrganizationService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/organizations.info", self.info) 
    self.add("/organizations.create", self.create)
    self.add("/organizations.add", self.submit)
    self.add("/organizations.submit", self.submit)
    self.add("/organizations.list", self.list)
    self.add("/organizations.update", self.update)
    self.add("/organizations.copy", self.copy)
    #self.add("/organizations.rank", self.rank) TODO    
    self.add("/organizations.delete", self.delete)
    self.add("/organizations.remove", self.delete)

    #admin routes
    self.add("/organizations.listForCommunityAdmin", self.community_admin_list)
    self.add("/organizations.listForSuperAdmin", self.super_admin_list)

  
  def info(self, request):
    context: Context  = request.context
    args = context.get_request_body()
    args = rename_field(args, 'organization_id', 'id')
    organization_info, err = self.service.get_organization_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=organization_info)

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

    organization_info, err = self.service.create_organization(context, args)
    if err:
      return err
    return MassenergizeResponse(data=organization_info)

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
      .expect("organization_id", str)
    
    ) 
    # self.validator.expect("size", str)
    # self.validator.expect("size_text", str)
    # self.validator.expect("description")
    # self.validator.expect("underAge", bool)
    # self.validator.expect("copyright", bool)
    # self.validator.expect("copyright_att", str)
    # self.validator.expect("guardian_info", str)

    self = expect_media_fields(self)

    args, err = self.validator.verify(args)
    if err:
      return err

    # user submitted organization, so notify the community admins
    user_submitted = True
    is_edit = args.get("organization_id", None)

    if is_edit:
      organization_info, err = self.service.update_organization(context, args, user_submitted)
    else:
      organization_info, err = self.service.create_organization(context, args, user_submitted)
    if err:
      return err
    return MassenergizeResponse(data=organization_info)


  def list(self, request):
    context: Context  = request.context
    args = context.get_request_body()      
    organization_info, err = self.service.list_organizations(context, args)
    if err:
      return err
    return MassenergizeResponse(data=organization_info)

  @login_required
  def update(self, request):
    context: Context  = request.context
    args = context.get_request_body() 
    (self.validator
      .rename("id","organization_id")
      .expect("organization_id", int)
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

    self = expect_media_fields(self)
    args, err = self.validator.verify(args)
    if err:
      return err

    organization_info, err = self.service.update_organization(context, args)
    if err:
      return err
    return MassenergizeResponse(data=organization_info)

  @admins_only
  def rank(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('id', int, is_required=True)
    self.validator.expect('rank', int, is_required=True)
    self.validator.rename('organization_id', 'id')

    args, err = self.validator.verify(args)
    if err:
      return err

    organization_info, err = self.service.rank_organization(args,context)
    if err:
      return err
    return MassenergizeResponse(data=organization_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'organization_id', 'id')
    organization_id = args.pop('id', None)
    if not organization_id:
      return CustomMassenergizeError("Please Provide Organization Id")
    organization_info, err = self.service.delete_organization(organization_id,context)
    if err:
      return err
    return MassenergizeResponse(data=organization_info)

  @admins_only
  def copy(self, request):
    context: Context = request.context
    args: dict = context.args
    organization_id = args.get('organization_id', None)
    
    if not organization_id:
      return CustomMassenergizeError("Please Provide Organization Id")
    organization_info, err = self.service.copy_organization(context, args)
    if err:
      return err
    return MassenergizeResponse(data=organization_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("community_id", int, is_required=False)

    args, err = self.validator.verify(args)
    if err:
      return err
    organizations, err = self.service.list_organizations_for_community_admin(context, args)

    if err:
      return err
    return MassenergizeResponse(data=organizations)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    organizations, err = self.service.list_organizations_for_super_admin(context)
    if err:
      return err
    return MassenergizeResponse(data=organizations)

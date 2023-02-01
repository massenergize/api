"""Handler file for all routes pertaining to admins"""

from _main_.utils.route_handler import RouteHandler
import _main_.utils.common as utils
from _main_.utils.common import get_request_contents, rename_field, parse_bool, parse_location, parse_list, validate_fields, parse_string
from api.services.admin import AdminService
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.massenergize_errors import CustomMassenergizeError
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required


class AdminHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = AdminService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/admins.super.add", self.add_super_admin) 
    self.add("/admins.super.remove", self.remove_super_admin) 
    self.add("/admins.super.list", self.list_super_admin) 
    self.add("/admins.community.add", self.add_community_admin) 
    self.add("/admins.community.remove", self.remove_community_admin) 
    self.add("/admins.community.list", self.list_community_admin) 
    self.add("/admins.messages.add", self.message) 
    self.add("/admins.messages.list", self.list_messages) 

  @super_admins_only
  def add_super_admin(self, request):
    context: Context  = request.context
    args = context.get_request_body() 

    (self.validator
      .add("name", str, is_required=True)
      .add("email", str, is_required=True)
    )

    args, err = self.validator.verify(args)
    if err:
      return err

    admin_info, err = self.service.add_super_admin(context, args)
    if err:
      return err
    return MassenergizeResponse(data=admin_info)

  @super_admins_only
  def remove_super_admin(self, request): 
    context: Context  = request.context
    args = context.get_request_body() 

    (self.validator
      .add("user_id", str)
      .add("email", str)
    )
    args, err = self.validator.verify(args)
    if err:
      return err

    admin_info, err = self.service.remove_super_admin(context, args)
    if err:
      return err
    return MassenergizeResponse(data=admin_info)

  @super_admins_only
  def list_super_admin(self, request): 
    context: Context  = request.context
    args = context.get_request_body()
    admin_info, err = self.service.list_super_admin(context, args)
    if err:
      return err
    meta = admin_info.get("meta")
    data = admin_info.get("items")
    return MassenergizeResponse(data=data, meta=meta)

  @admins_only
  def add_community_admin(self, request): 
    context: Context  = request.context
    args = context.get_request_body()

    (self.validator
      .expect("name", str, is_required=True)
      .expect("email", str, is_required=True)
      .expect("community_id", str)
      .expect("subdomain", str)
    )

    args, err = self.validator.verify(args)
    if err:
      return err

    admin_info, err = self.service.add_community_admin(context, args)
    if err:
      return err
    return MassenergizeResponse(data=admin_info)

  @admins_only
  def remove_community_admin(self, request): 
    context: Context  = request.context
    args = context.get_request_body()

    (self.validator
      .add("user_id", str)
      .add("email", str)
      .add("community_id", str)
      .add("subdomain", str)
    )

    args, err = self.validator.verify(args)
    if err:
      return err

    admin_info, err = self.service.remove_community_admin(context, args)
    if err:
      return err
    return MassenergizeResponse(data=admin_info)

  @admins_only
  def list_community_admin(self, request): 
    context: Context  = request.context
    args = context.get_request_body() 

    self.validator.add("community_id", str).add("subdomain", str)

    args, err = self.validator.verify(args)
    if err:
      return err

    admin_info, err = self.service.list_community_admin(context, args)
    if err:
      return err

    return MassenergizeResponse(data=admin_info)


  def message(self, request): 
    context: Context  = request.context
    args = context.get_request_body() 

    (self.validator
      .add("community_id", int)
      .add("subdomain", str, is_required=False)
    )

    args, err = self.validator.verify(args)
    if err:
      return err

    admin_info, err = self.service.message_admin(context, args)
    if err:
      return err
    return MassenergizeResponse(data=admin_info)


  @admins_only
  def list_messages(self, request):
    context: Context  = request.context
    args = context.get_request_body() 

    (self.validator
      .add("community_id", str, is_required=False)
      .add("subdomain", str, is_required=False)
    )

    args, err = self.validator.verify(args)
    if err:
      return err

    admin_info, err = self.service.list_admin_messages(context, args)
    if err:
      return err
    return MassenergizeResponse(data=admin_info)


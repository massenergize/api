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

#TODO: install middleware to catch authz violations
#TODO: add logger

class AdminHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = AdminService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/admins.super.add", self.add_super_admin()) 
    self.add("/admins.super.remove", self.remove_super_admin()) 
    self.add("/admins.super.list", self.list_super_admin()) 
    self.add("/admins.community.add", self.add_community_admin()) 
    self.add("/admins.community.remove", self.remove_community_admin()) 
    self.add("/admins.community.list", self.list_community_admin()) 
    self.add("/admins.message", self.message()) 


  def add_super_admin(self) -> function:
    def add_super_admin_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body() 
      validator: Validator = Validator()
      (validator
        .add("name", str, is_required=True)
        .add("email", str, is_required=True)
      )

      args, err = validator.verify(args)
      if err:
        return err

      admin_info, err = self.service.add_super_admin(context, args)
      if err:
        return err
      return MassenergizeResponse(data=admin_info)
    return add_super_admin_view


  def remove_super_admin(self) -> function:
    def remove_super_admin_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body() 
      validator: Validator = Validator()
      (validator
        .add("user_id", str, is_required=False)
        .add("email", str, is_required=False)
      )
      print(args)
      args, err = validator.verify(args)
      if err:
        return err

      admin_info, err = self.service.remove_super_admin(context, args)
      if err:
        return err
      return MassenergizeResponse(data=admin_info)
    return remove_super_admin_view


  def list_super_admin(self) -> function:
    def list_super_admin_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body() 
      admin_info, err = self.service.list_super_admin(context, args)
      if err:
        return err
      return MassenergizeResponse(data=admin_info)
    return list_super_admin_view


  def add_community_admin(self) -> function:
    def add_community_admin_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body() 
      validator: Validator = Validator()
      (validator
        .add("name", str, is_required=True)
        .add("email", str, is_required=True)
        .add("community_id", str, is_required=False)
        .add("subdomain", str, is_required=False)
      )

      args, err = validator.verify(args)
      if err:
        return err

      admin_info, err = self.service.add_community_admin(context, args)
      if err:
        return err
      return MassenergizeResponse(data=admin_info)
    return add_community_admin_view


  def remove_community_admin(self) -> function:
    def remove_community_admin_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body() 
      validator: Validator = Validator()
      (validator
        .add("user_id", str, is_required=False)
        .add("email", str, is_required=False)
        .add("community_id", str, is_required=False)
        .add("subdomain", str, is_required=False)
      )

      args, err = validator.verify(args)
      if err:
        return err

      admin_info, err = self.service.remove_community_admin(context, args)
      if err:
        return err
      return MassenergizeResponse(data=admin_info)
    return remove_community_admin_view


  def list_community_admin(self) -> function:
    def list_community_admin_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body() 
      validator: Validator = Validator()
      (validator
        .add("community_id", str, is_required=False)
        .add("subdomain", str, is_required=False)
      )

      args, err = validator.verify(args)
      if err:
        return err

      admin_info, err = self.service.list_community_admin(context, args)
      if err:
        return err
      return MassenergizeResponse(data=admin_info)
    return list_community_admin_view

  def message(self) -> function:
    def message_admin_view(request) -> None: 
      context: Context  = request.context
      args = context.get_request_body() 
      validator: Validator = Validator()
      (validator
        .add("community_id", str, is_required=False)
        .add("subdomain", str, is_required=False)
      )

      args, err = validator.verify(args)
      if err:
        return err

      admin_info, err = self.service.list_community_admin(context, args)
      if err:
        return err
      return MassenergizeResponse(data=admin_info)
    return message_admin_view


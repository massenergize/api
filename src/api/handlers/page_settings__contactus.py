"""Handler file for all routes pertaining to contact_us_page_settings"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field
from api.services.page_settings__contactus import ContactUsPageSettingsService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator


class ContactUsPageSettingsHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = ContactUsPageSettingsService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/contact_us_page_settings.info", self.info) 
    self.add("/contact_us_page_settings.create", self.create)
    self.add("/contact_us_page_settings.add", self.create)
    self.add("/contact_us_page_settings.list", self.list)
    self.add("/contact_us_page_settings.update", self.update)
    self.add("/contact_us_page_settings.delete", self.delete)
    self.add("/contact_us_page_settings.remove", self.delete)

    #admin routes
    self.add("/contact_us_page_settings.listForCommunityAdmin", self.community_admin_list)
    self.add("/contact_us_page_settings.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'community_id', 'community__id')
    args = rename_field(args, 'subdomain', 'community__subdomain')
    args = rename_field(args, 'contact_us_page_id', 'id')
    contact_us_page_setting_info, err = self.service.get_contact_us_page_setting_info(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=contact_us_page_setting_info)


  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    contact_us_page_setting_info, err = self.service.create_contact_us_page_setting(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=contact_us_page_setting_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    user_id = args.pop('user_id', None)
    contact_us_page_setting_info, err = self.service.list_contact_us_page_settings(community_id, user_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=contact_us_page_setting_info)


  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    contact_us_page_setting_info, err = self.service.update_contact_us_page_setting(args.get("id", None), args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=contact_us_page_setting_info)


  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    contact_us_page_setting_id = args.get("id", None)
    contact_us_page_setting_info, err = self.service.delete_contact_us_page_setting(args.get("id", None))
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=contact_us_page_setting_info)


  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    contact_us_page_settings, err = self.service.list_contact_us_page_settings_for_community_admin(community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=contact_us_page_settings)


  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    contact_us_page_settings, err = self.service.list_contact_us_page_settings_for_super_admin()
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=contact_us_page_settings)

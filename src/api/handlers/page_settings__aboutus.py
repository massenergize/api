"""Handler file for all routes pertaining to about_us_page_settings"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field
from api.services.page_settings__aboutus import AboutUsPageSettingsService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required

class AboutUsPageSettingsHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = AboutUsPageSettingsService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/about_us_page_settings.info", self.info) 
    self.add("/about_us_page_settings.create", self.create)
    self.add("/about_us_page_settings.add", self.create)
    self.add("/about_us_page_settings.list", self.list)
    self.add("/about_us_page_settings.update", self.update)
    self.add("/about_us_page_settings.delete", self.delete)
    self.add("/about_us_page_settings.remove", self.delete)

    #admin routes
    self.add("/about_us_page_settings.listForCommunityAdmin", self.community_admin_list)
    self.add("/about_us_page_settings.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'community_id', 'community__id')
    args = rename_field(args, 'subdomain', 'community__subdomain')
    args = rename_field(args, 'about_us_page_id', 'id')
    about_us_page_setting_info, err = self.service.get_about_us_page_setting_info(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=about_us_page_setting_info)

  @admins_only
  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    about_us_page_setting_info, err = self.service.create_about_us_page_setting(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=about_us_page_setting_info)

  @super_admins_only
  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    user_id = args.pop('user_id', None)
    about_us_page_setting_info, err = self.service.list_about_us_page_settings(community_id, user_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=about_us_page_setting_info)

  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    about_us_page_setting_info, err = self.service.update_about_us_page_setting(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=about_us_page_setting_info)

  @super_admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    about_us_page_setting_id = args.get("id", None)
    about_us_page_setting_info, err = self.service.delete_about_us_page_setting(args.get("id", None))
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=about_us_page_setting_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    about_us_page_settings, err = self.service.list_about_us_page_settings_for_community_admin(community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=about_us_page_settings)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    about_us_page_settings, err = self.service.list_about_us_page_settings_for_super_admin()
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=about_us_page_settings)

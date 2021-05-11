"""Handler file for all routes pertaining to contact_us_page_settings"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field
from api.services.page_settings import PageSettingsService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required


class PageSettingsHandler(RouteHandler):

  def __init__(self, pageName, dataModel):
    super().__init__()
    self.pageName = pageName
    if not pageName:
      raise Exception('PageSettingsHandler: no page name supplied')
    self.registerRoutes(pageName)
    self.service = PageSettingsService(dataModel)


  def registerRoutes(self, pageName):
    self.add("/"+pageName+"_page_settings.info", self.info) 
    self.add("/"+pageName+"_page_settings.create", self.create)
    self.add("/"+pageName+"_page_settings.add", self.create)
    self.add("/"+pageName+"_page_settings.list", self.list)
    self.add("/"+pageName+"_page_settings.update", self.update)
    self.add("/"+pageName+"_page_settings.delete", self.delete)
    self.add("/"+pageName+"_page_settings.remove", self.delete)

    #admin routes
    self.add("/"+pageName+"_page_settings.listForCommunityAdmin", self.community_admin_list)
    self.add("/"+pageName+"_page_settings.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'community_id', 'community__id')
    args = rename_field(args, 'subdomain', 'community__subdomain')
    args = rename_field(args, self.pageName+'_page_id', 'id')
    page_setting_info, err = self.service.get_page_setting_info(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=page_setting_info)

  @super_admins_only
  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    page_setting_info, err = self.service.create_page_setting(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=page_setting_info)

  @admins_only
  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    page_setting_info, err = self.service.list_page_settings(community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=page_setting_info)

  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args
    page_setting_info, err = self.service.update_page_setting(args.get("id", None), args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=page_setting_info)

  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    page_setting_id = args.get("id", None)
    page_setting_info, err = self.service.delete_page_setting(args.get("id", None))
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=page_setting_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop("community_id", None)
    page_settings, err = self.service.list_page_settings_for_community_admin(community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=page_settings)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    page_settings, err = self.service.list_page_settings_for_super_admin()
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=page_settings)

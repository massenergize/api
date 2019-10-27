"""Handler file for all routes pertaining to about_us_page_settings"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field
from api.services.page_settings__aboutus import AboutUsPageSettingsService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class AboutUsPageSettingsHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = AboutUsPageSettingsService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/about_us_page_settings.info", self.info()) 
    self.add("/about_us_page_settings.create", self.create())
    self.add("/about_us_page_settings.add", self.create())
    self.add("/about_us_page_settings.list", self.list())
    self.add("/about_us_page_settings.update", self.update())
    self.add("/about_us_page_settings.delete", self.delete())
    self.add("/about_us_page_settings.remove", self.delete())

    #admin routes
    self.add("/about_us_page_settings.listForCommunityAdmin", self.community_admin_list())
    self.add("/about_us_page_settings.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def about_us_page_setting_info_view(request) -> None: 
      args = get_request_contents(request)
      args = rename_field(args, 'community_id', 'community__id')
      args = rename_field(args, 'subdomain', 'community__subdomain')
      args = rename_field(args, 'about_us_page_id', 'id')
      about_us_page_setting_info, err = self.service.get_about_us_page_setting_info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=about_us_page_setting_info)
    return about_us_page_setting_info_view


  def create(self) -> function:
    def create_about_us_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      about_us_page_setting_info, err = self.service.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=about_us_page_setting_info)
    return create_about_us_page_setting_view


  def list(self) -> function:
    def list_about_us_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      about_us_page_setting_info, err = self.service.list_about_us_page_settings(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=about_us_page_setting_info)
    return list_about_us_page_setting_view


  def update(self) -> function:
    def update_about_us_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      about_us_page_setting_info, err = self.service.update_about_us_page_setting(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=about_us_page_setting_info)
    return update_about_us_page_setting_view


  def delete(self) -> function:
    def delete_about_us_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      about_us_page_setting_id = args[id]
      about_us_page_setting_info, err = self.service.delete_about_us_page_setting(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=about_us_page_setting_info)
    return delete_about_us_page_setting_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      about_us_page_settings, err = self.service.list_about_us_page_settings_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=about_us_page_settings)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      about_us_page_settings, err = self.service.list_about_us_page_settings_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=about_us_page_settings)
    return super_admin_list_view
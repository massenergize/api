"""Handler file for all routes pertaining to home_page_settings"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.page_settings__home import HomePageSettingsService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class HomePageSettingsHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.home_page_setting = HomePageSettingsService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/home_page_settings.info", self.info()) 
    self.add("/home_page_settings.create", self.create())
    self.add("/home_page_settings.add", self.create())
    self.add("/home_page_settings.list", self.list())
    self.add("/home_page_settings.update", self.update())
    self.add("/home_page_settings.delete", self.delete())
    self.add("/home_page_settings.remove", self.delete())

    #admin routes
    self.add("/home_page_settings.listForCommunityAdmin", self.community_admin_list())
    self.add("/home_page_settings.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def home_page_setting_info_view(request) -> None: 
      args = get_request_contents(request)
      home_page_setting_info, err = self.home_page_setting.info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=home_page_setting_info)
    return home_page_setting_info_view


  def create(self) -> function:
    def create_home_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      home_page_setting_info, err = self.home_page_setting.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=home_page_setting_info)
    return create_home_page_setting_view


  def list(self) -> function:
    def list_home_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args["community__id"]
      user_id = args["user_id"]
      home_page_setting_info, err = self.home_page_setting.list_home_page_settings(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=home_page_setting_info)
    return list_home_page_setting_view


  def update(self) -> function:
    def update_home_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      home_page_setting_info, err = self.home_page_setting.update_home_page_setting(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=home_page_setting_info)
    return update_home_page_setting_view


  def delete(self) -> function:
    def delete_home_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      home_page_setting_id = args[id]
      home_page_setting_info, err = self.home_page_setting.delete_home_page_setting(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=home_page_setting_info)
    return delete_home_page_setting_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      home_page_settings, err = self.home_page_setting.list_home_page_settings_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=home_page_settings)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      home_page_settings, err = self.home_page_setting.list_home_page_settings_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=home_page_settings)
    return super_admin_list_view
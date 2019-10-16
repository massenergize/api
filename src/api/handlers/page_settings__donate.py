"""Handler file for all routes pertaining to donate_page_settings"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.page_settings__donate import DonatePageSettingsService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class DonatePageSettingsHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = DonatePageSettingsService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/donate_page_settings.info", self.info()) 
    self.add("/donate_page_settings.create", self.create())
    self.add("/donate_page_settings.add", self.create())
    self.add("/donate_page_settings.list", self.list())
    self.add("/donate_page_settings.update", self.update())
    self.add("/donate_page_settings.delete", self.delete())
    self.add("/donate_page_settings.remove", self.delete())

    #admin routes
    self.add("/donate_page_settings.listForCommunityAdmin", self.community_admin_list())
    self.add("/donate_page_settings.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def donate_page_setting_info_view(request) -> None: 
      args = get_request_contents(request)
      donate_page_setting_info, err = self.service.get_donate_page_setting_info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=donate_page_setting_info)
    return donate_page_setting_info_view


  def create(self) -> function:
    def create_donate_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      donate_page_setting_info, err = self.service.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=donate_page_setting_info)
    return create_donate_page_setting_view


  def list(self) -> function:
    def list_donate_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      donate_page_setting_info, err = self.service.list_donate_page_settings(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=donate_page_setting_info)
    return list_donate_page_setting_view


  def update(self) -> function:
    def update_donate_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      donate_page_setting_info, err = self.service.update_donate_page_setting(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=donate_page_setting_info)
    return update_donate_page_setting_view


  def delete(self) -> function:
    def delete_donate_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      donate_page_setting_id = args[id]
      donate_page_setting_info, err = self.service.delete_donate_page_setting(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=donate_page_setting_info)
    return delete_donate_page_setting_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      donate_page_settings, err = self.service.list_donate_page_settings_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=donate_page_settings)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      donate_page_settings, err = self.service.list_donate_page_settings_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=donate_page_settings)
    return super_admin_list_view
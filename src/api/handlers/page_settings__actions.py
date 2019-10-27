"""Handler file for all routes pertaining to actions_page_settings"""

from _main_.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field
from api.services.page_settings__actions import ActionsPageSettingsService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class ActionsPageSettingsHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = ActionsPageSettingsService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/actions_page_settings.info", self.info()) 
    self.add("/actions_page_settings.create", self.create())
    self.add("/actions_page_settings.add", self.create())
    self.add("/actions_page_settings.list", self.list())
    self.add("/actions_page_settings.update", self.update())
    self.add("/actions_page_settings.delete", self.delete())
    self.add("/actions_page_settings.remove", self.delete())

    #admin routes
    self.add("/actions_page_settings.listForCommunityAdmin", self.community_admin_list())
    self.add("/actions_page_settings.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def actions_page_setting_info_view(request) -> None: 
      args = get_request_contents(request)
      args = rename_field(args, 'community_id', 'community__id')
      args = rename_field(args, 'subdomain', 'community__subdomain')
      args = rename_field(args, 'actions_page_id', 'id')
      actions_page_setting_info, err = self.service.get_actions_page_setting_info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions_page_setting_info)
    return actions_page_setting_info_view


  def create(self) -> function:
    def create_actions_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      actions_page_setting_info, err = self.service.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions_page_setting_info)
    return create_actions_page_setting_view


  def list(self) -> function:
    def list_actions_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      actions_page_setting_info, err = self.service.list_actions_page_settings(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions_page_setting_info)
    return list_actions_page_setting_view


  def update(self) -> function:
    def update_actions_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      actions_page_setting_info, err = self.service.update_actions_page_setting(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions_page_setting_info)
    return update_actions_page_setting_view


  def delete(self) -> function:
    def delete_actions_page_setting_view(request) -> None: 
      args = get_request_contents(request)
      actions_page_setting_id = args[id]
      actions_page_setting_info, err = self.service.delete_actions_page_setting(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions_page_setting_info)
    return delete_actions_page_setting_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      actions_page_settings, err = self.service.list_actions_page_settings_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions_page_settings)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      actions_page_settings, err = self.service.list_actions_page_settings_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=actions_page_settings)
    return super_admin_list_view
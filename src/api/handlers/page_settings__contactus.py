"""Handler file for all routes pertaining to contact_us_page_settings"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field
from api.services.page_settings__contactus import ContactUsPageSettingsService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class ContactUsPageSettingsHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = ContactUsPageSettingsService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/contact_us_page_settings.info", self.info()) 
    self.add("/contact_us_page_settings.create", self.create())
    self.add("/contact_us_page_settings.add", self.create())
    self.add("/contact_us_page_settings.list", self.list())
    self.add("/contact_us_page_settings.update", self.update())
    self.add("/contact_us_page_settings.delete", self.delete())
    self.add("/contact_us_page_settings.remove", self.delete())

    #admin routes
    self.add("/contact_us_page_settings.listForCommunityAdmin", self.community_admin_list())
    self.add("/contact_us_page_settings.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def contact_us_page_setting_info_view(request) -> None: 
      args = request.context.args
      args = rename_field(args, 'community_id', 'community__id')
      args = rename_field(args, 'subdomain', 'community__subdomain')
      args = rename_field(args, 'contact_us_page_id', 'id')
      contact_us_page_setting_info, err = self.service.get_contact_us_page_setting_info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=contact_us_page_setting_info)
    return contact_us_page_setting_info_view


  def create(self) -> function:
    def create_contact_us_page_setting_view(request) -> None: 
      args = request.context.args
      contact_us_page_setting_info, err = self.service.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=contact_us_page_setting_info)
    return create_contact_us_page_setting_view


  def list(self) -> function:
    def list_contact_us_page_setting_view(request) -> None: 
      args = request.context.args
      community_id = args.pop('community_id', None)
      user_id = args.pop('user_id', None)
      contact_us_page_setting_info, err = self.service.list_contact_us_page_settings(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=contact_us_page_setting_info)
    return list_contact_us_page_setting_view


  def update(self) -> function:
    def update_contact_us_page_setting_view(request) -> None: 
      args = request.context.args
      contact_us_page_setting_info, err = self.service.update_contact_us_page_setting(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=contact_us_page_setting_info)
    return update_contact_us_page_setting_view


  def delete(self) -> function:
    def delete_contact_us_page_setting_view(request) -> None: 
      args = request.context.args
      contact_us_page_setting_id = args[id]
      contact_us_page_setting_info, err = self.service.delete_contact_us_page_setting(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=contact_us_page_setting_info)
    return delete_contact_us_page_setting_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = request.context.args
      community_id = args.pop("community_id", None)
      contact_us_page_settings, err = self.service.list_contact_us_page_settings_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=contact_us_page_settings)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = request.context.args
      contact_us_page_settings, err = self.service.list_contact_us_page_settings_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=contact_us_page_settings)
    return super_admin_list_view
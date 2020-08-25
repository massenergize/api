"""Handler file for all routes pertaining to home_page_settings"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, rename_field, rename_fields, parse_bool, parse_list, check_length, parse_int
from api.services.page_settings__home import HomePageSettingsService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required

class HomePageSettingsHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = HomePageSettingsService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/home_page_settings.info", self.info) 
    self.add("/home_page_settings.publish", self.info) 
    self.add("/home_page_settings.create", self.create)
    self.add("/home_page_settings.add", self.create)
    self.add("/home_page_settings.list", self.list)
    self.add("/home_page_settings.update", self.update)
    self.add("/home_page_settings.delete", self.delete)
    self.add("/home_page_settings.remove", self.delete)

    #admin routes
    self.add("/home_page_settings.listForCommunityAdmin", self.community_admin_list)
    self.add("/home_page_settings.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'community_id', 'community__id')
    args = rename_field(args, 'subdomain', 'community__subdomain')
    args = rename_field(args, 'home_page_id', 'id')
    home_page_setting_info, err = self.service.get_home_page_setting_info(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=home_page_setting_info)

  @admins_only
  def publish(self, request):
    context: Context = request.context
    args: dict = context.args
    home_page_id = args.pop('home_page_id', None)
    home_page_setting_info, err = self.service.get_home_page_setting_publish(home_page_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=home_page_setting_info)

  @admins_only
  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    home_page_setting_info, err = self.service.create_home_page_setting(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=home_page_setting_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    home_page_setting_info, err = self.service.list_home_page_settings(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=home_page_setting_info)

  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args

    #featured links
    args['show_featured_links'] = parse_bool(args.pop('show_featured_links', True))
    args['featured_links'] = [
      {
        'title': args.pop('icon_box_1_title', ''),
        'link': args.pop('icon_box_1_link', ''),
        'icon': args.pop('icon_box_1_icon', ''),
        'description': args.pop('icon_box_1_description', '')
      },
      {
        'title': args.pop('icon_box_2_title', ''),
        'link': args.pop('icon_box_2_link', ''),
        'icon': args.pop('icon_box_2_icon', ''),
        'description': args.pop('icon_box_2_description', '')
      },
      {
        'title': args.pop('icon_box_3_title', ''),
        'link': args.pop('icon_box_3_link', ''),
        'icon': args.pop('icon_box_3_icon', ''),
        'description': args.pop('icon_box_3_description', '')
      },
      {
        'title': args.pop('icon_box_4_title', ''),
        'link': args.pop('icon_box_4_link', ''),
        'icon': args.pop('icon_box_4_icon', ''),
        'description': args.pop('icon_box_4_description', '')
      },
    ]
    #checks for length
    for t in args["featured_links"]:
      if len(t["description"]) >  40:
        return MassenergizeResponse(error=f"Description text for {t['title']} should be less than 40 characters")

    # events
    args['show_featured_events'] = parse_bool(args.pop('show_featured_events', True))
    args['featured_events'] = parse_list(args.pop('featured_events', []))

    #statistics
    args['show_featured_stats'] = parse_bool(args.pop('show_featured_stats'))
    args['goal'] = {
      'attained_number_of_actions': parse_int(args.pop('attained_number_of_actions', 0)),
      'target_number_of_actions': parse_int(args.pop('target_number_of_actions', 0)),
      'attained_number_of_households': parse_int(args.pop('attained_number_of_households', 0)),
      'target_number_of_households': parse_int(args.pop('target_number_of_households', 0)),
      'attained_carbon_footprint_reduction': parse_int(args.pop('attained_carbon_footprint_reduction', 0)),
      'target_carbon_footprint_reduction': parse_int(args.pop('target_carbon_footprint_reduction', 0))
    }

    args.pop('organic_attained_number_of_households', None)
    args.pop('organic_attained_number_of_actions', None)
    args.pop('organic_attained_carbon_footprint_reduction', None)

    home_page_setting_info, err = self.service.update_home_page_setting(args)

    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=home_page_setting_info)

  @super_admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    home_page_id = args.pop('home_page_id', None)
    home_page_setting_info, err = self.service.delete_home_page_setting(home_page_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=home_page_setting_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    home_page_settings, err = self.service.list_home_page_settings_for_community_admin(community_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=home_page_settings)

  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    home_page_settings, err = self.service.list_home_page_settings_for_super_admin()
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=home_page_settings)

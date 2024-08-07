"""Handler file for all routes pertaining to home_page_settings"""

from _main_.utils.common import parse_bool, parse_list, rename_field
from _main_.utils.context import Context
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.route_handler import RouteHandler
from api.decorators import admins_only, super_admins_only
from api.services.page_settings__home import HomePageSettingsService


class HomePageSettingsHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = HomePageSettingsService()
    self.registerRoutes()

  def registerRoutes(self):
    self.add("/home_page_settings.info", self.info) 
    self.add("/home_page_settings.create", self.create)
    self.add("/home_page_settings.add", self.create)
    self.add("/home_page_settings.list", self.list)
    self.add("/home_page_settings.update", self.update)
    self.add("/home_page_settings.delete", self.delete)
    self.add("/home_page_settings.remove", self.delete)
    self.add("/home_page_settings.addEvent", self.add_event)

    #admin routes
    self.add("/home_page_settings.listForCommunityAdmin", self.community_admin_list)
    self.add("/home_page_settings.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    args = rename_field(args, 'home_page_id', 'id')
    home_page_setting_info, err = self.service.get_home_page_setting_info(context, args)
    if err:
      return err
    return MassenergizeResponse(data=home_page_setting_info)

  @admins_only
  def create(self, request):
    context: Context = request.context
    args: dict = context.args
    home_page_setting_info, err = self.service.create_home_page_setting(args)
    if err:
      return err
    return MassenergizeResponse(data=home_page_setting_info)
  
  @admins_only
  def add_event(self, request):
    context: Context = request.context
    args: dict = context.args
    home_page_setting_info, err = self.service.add_event(args)
    if err:
      return err
    return MassenergizeResponse(data=home_page_setting_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args
    home_page_setting_info, err = self.service.list_home_page_settings(args)
    if err:
      return err
    return MassenergizeResponse(data=home_page_setting_info)

  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args

    images = args.get("images", None)
    if images: 
      args["images"] = images.split(",")

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

    # 9/29/21 goals setting moved to graphs.update, to consolidate input from admin portal

    home_page_setting_info, err = self.service.update_home_page_setting(args)
    if err:
      return err
    return MassenergizeResponse(data=home_page_setting_info)


  @super_admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    home_page_id = args.pop('home_page_id', None)
    home_page_setting_info, err = self.service.delete_home_page_setting(home_page_id)
    if err:
      return err
    return MassenergizeResponse(data=home_page_setting_info)

  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args
    community_id = args.pop('community_id', None)
    home_page_settings, err = self.service.list_home_page_settings_for_community_admin(community_id)
    if err:
      return err
    return MassenergizeResponse(data=home_page_settings)

  @super_admins_only
  def super_admin_list(self, request):
    home_page_settings, err = self.service.list_home_page_settings_for_super_admin()
    if err:
      return err
    return MassenergizeResponse(data=home_page_settings)

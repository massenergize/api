from database.models import HomePageSettings, UserProfile, Media
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context

class HomePageSettingsStore:
  def __init__(self):
    self.name = "HomePageSettings Store/DB"

  def get_home_page_setting_info(self, args) -> (dict, MassEnergizeAPIError):
    try:
      home_page_setting = HomePageSettings.objects.filter(**args).first()
      if not home_page_setting:
        return None, InvalidResourceError()
      return home_page_setting, None
    except Exception as e:
      return None, CustomMassenergizeError(e)


  def list_home_page_settings(self, community_id) -> (list, MassEnergizeAPIError):
    home_page_settings = HomePageSettings.objects.filter(community__id=community_id)
    if not home_page_settings:
      return [], None
    return home_page_settings, None


  def create_home_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_home_page_setting = HomePageSettings.create(**args)
      new_home_page_setting.save()
      return new_home_page_setting, None
    except Exception:
      return None, ServerError()


  def update_home_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      home_page_id = args.get('id', None)
      home_page_setting = HomePageSettings.objects.filter(id=home_page_id).first()
      if not home_page_setting:
        return None, InvalidResourceError()

      #events
      if (args.get('show_featured_events', None)):
        featured_events = args.pop('featured_events', [])
        home_page_setting.featured_events.set(featured_events)
      else:
        args.pop('featured_events', [])


      #stats
      goal_updates = args.pop('goal', None)
      if (args.get('show_featured_stats', None)):
        if goal_updates and home_page_setting and home_page_setting.community and home_page_setting.community.goal:
          community_goal = home_page_setting.community.goal

          attained_number_of_actions = goal_updates.get('attained_number_of_actions', None)
          if attained_number_of_actions:
            community_goal.attained_number_of_actions = attained_number_of_actions
          

          target_number_of_actions = goal_updates.get('target_number_of_actions', None)
          if target_number_of_actions:
            community_goal.target_number_of_actions = target_number_of_actions
          

          attained_number_of_households= goal_updates.get('attained_number_of_households', None)
          if attained_number_of_households:
            community_goal.attained_number_of_households = attained_number_of_households
          

          target_number_of_households = goal_updates.get('target_number_of_households', None)
          if attained_number_of_actions:
            community_goal.target_number_of_households = target_number_of_households

          community_goal.save()
      

      #featured links
      if (not args.get('show_featured_links', False)):
        featured_links = args.pop('featured_links', None)

      #images
      current_images = home_page_setting.images.all()

      image_1 = args.pop('image_1', None)
      image_2 = args.pop('image_2', None)
      image_3 = args.pop('image_3', None)
      
      current_image_1 = current_images[0]
      current_image_2 = current_images[1]
      current_image_3 = current_images[2]


      if image_1:
        current_image_1 = Media(file=image_1, name=f"FeaturedImage1-{home_page_setting.community.name}", order=1)
        current_image_1.save()

      if image_2:
        current_image_2 = Media(file=image_2, name=f"FeaturedImage2-{home_page_setting.community.name}", order=2)
        current_image_2.save()

      if image_3:
        current_image_3 = Media(file=image_3, name=f"FeaturedImage3-{home_page_setting.community.name}", order=3)
        current_image_3.save()
      
      home_page_setting.images.set([current_image_1, current_image_2, current_image_3])
      home_page_setting.save()


      #now, update the other fields in one swing
      HomePageSettings.objects.filter(id=home_page_id).update(**args)
      return home_page_setting, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)


  def delete_home_page_setting(self, home_page_setting_id) -> (dict, MassEnergizeAPIError):
    home_page_settings = HomePageSettings.objects.filter(id=home_page_setting_id)
    if not home_page_settings:
      return None, InvalidResourceError()


  def list_home_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    home_page_settings = HomePageSettings.objects.filter(community__id = community_id)
    return home_page_settings, None


  def list_home_page_settings_for_super_admin(self):
    try:
      home_page_settings = HomePageSettings.objects.all()
      return home_page_settings, None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))
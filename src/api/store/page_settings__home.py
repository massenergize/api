import json
from api.store.utils import get_community_or_die
from api.tests.common import RESET
from database.models import HomePageSettings, ImageSequence, UserProfile, Media, Event
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from _main_.utils.massenergize_logger import log
from typing import Tuple
from _main_.utils.metrics import timed


class HomePageSettingsStore:
  def __init__(self):
    self.name = "HomePageSettings Store/DB"

  @timed
  def get_home_page_setting_info(self,context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      args['community'] = get_community_or_die(context, args)
      home_page_setting = HomePageSettings.objects.filter(**args).prefetch_related('images').first()
      if not home_page_setting:
        return None, InvalidResourceError()
      return home_page_setting, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def list_home_page_settings(self, community_id) -> Tuple[list, MassEnergizeAPIError]:
    home_page_settings = HomePageSettings.objects.filter(community__id=community_id)
    if not home_page_settings:
      return [], None
    return home_page_settings, None


  def create_home_page_setting(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      new_home_page_setting = HomePageSettings.create(**args)
      new_home_page_setting.save()
      return new_home_page_setting, None
    except Exception:
      return None, ServerError()
    
  def add_event(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      res = {}
      community_id = args.get('community_id')
      event_id = args.get("event_id")
      event = Event.objects.filter(id=event_id).first()
      home_page_setting = HomePageSettings.objects.filter(community__id=community_id).first()
      event_already_exist =  home_page_setting.featured_events.filter(id=event_id).exists()
      if event_already_exist:
         home_page_setting.featured_events.remove(event)
         res = {
           "msg":f"{event.name} has been removed from your home page",
           "status":False
         }
      else:
        home_page_setting.featured_events.add(event)
        res = {
           "msg":f"{event.name} has been added to your home page",
           "status":True
         }
      home_page_setting.save()
      return res, None
    except Exception:
      return None, ServerError()



  def update_home_page_setting(self, args) -> Tuple[dict, MassEnergizeAPIError]:
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

      # goals to be moved to graphs.update
      #stats
      #goal_updates = args.pop('goal', None)
      #if (args.get('show_featured_stats', None)):
        #if goal_updates and home_page_setting and home_page_setting.community and home_page_setting.community.goal:
        #  community_goal = home_page_setting.community.goal
#
        #  initial_number_of_actions = goal_updates.get('initial_number_of_actions', None)
        #  if initial_number_of_actions != None:
        #    community_goal.initial_number_of_actions = initial_number_of_actions
        #  
        #  target_number_of_actions = goal_updates.get('target_number_of_actions', None)
        #  if target_number_of_actions != None:
        #    community_goal.target_number_of_actions = target_number_of_actions
        #  
#
        #  initial_number_of_households= goal_updates.get('initial_number_of_households', None)
        #  if initial_number_of_households != None:
        #    community_goal.initial_number_of_households = initial_number_of_households
        #  
        #  target_number_of_households = goal_updates.get('target_number_of_households', None)
        #  if target_number_of_actions != None:
        #    community_goal.target_number_of_households = target_number_of_households
#
#
        #  initial_carbon_footprint_reduction = goal_updates.get('initial_carbon_footprint_reduction', None)
        #  if initial_carbon_footprint_reduction != None:
        #    community_goal.initial_carbon_footprint_reduction = initial_carbon_footprint_reduction
        #  
        #  target_carbon_footprint_reduction = goal_updates.get('target_carbon_footprint_reduction', None)
        #  if target_carbon_footprint_reduction != None:
        #    community_goal.target_carbon_footprint_reduction = target_carbon_footprint_reduction
#
#
        #  community_goal.save()

      #featured links (copy logic from featured_events)
      if (args.get('show_featured_links', None)):
        featured_links = args.pop('featured_links', None)
        home_page_setting.featured_links = featured_links
      else:
        args.pop('featured_links', [])

      #images
      images = args.pop("images", None)
      if images: 
        if images[0] == RESET: 
          home_page_setting.images.clear()
        else:
          new_sequence = json.dumps(images)
          found_images = [ Media.objects.filter(id = img_id).first() for img_id in images ]
          home_page_setting.images.clear() 
          home_page_setting.images.set(found_images)
          
          sequence_obj = home_page_setting.image_sequence 
          if sequence_obj: 
            ImageSequence.objects.filter(id = sequence_obj.id).update(sequence = new_sequence)
          else: # First time creating a sequence Obj for homepage images
            name = f"Homepage settings Id - {home_page_id} - for community({home_page_setting.community.id}, {home_page_setting.community.name}) "
            image_sequence = ImageSequence.objects.create(name = name, sequence= new_sequence) 
            home_page_setting.image_sequence = image_sequence

      home_page_setting.save()


      #now, update the other fields in one swing
      HomePageSettings.objects.filter(id=home_page_id).update(**args)
      home_page_setting.refresh_from_db()
      return home_page_setting, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)


  def delete_home_page_setting(self, home_page_setting_id) -> Tuple[dict, MassEnergizeAPIError]:
    home_page_settings = HomePageSettings.objects.filter(id=home_page_setting_id)
    if not home_page_settings:
      return None, InvalidResourceError()


  def list_home_page_settings_for_community_admin(self, community_id) -> Tuple[list, MassEnergizeAPIError]:
    home_page_settings = HomePageSettings.objects.filter(community__id = community_id)
    return home_page_settings, None


  def list_home_page_settings_for_super_admin(self):
    try:
      home_page_settings = HomePageSettings.objects.all()
      return home_page_settings, None
    except Exception as e:
      log.exception(e)
      return None, CustomMassenergizeError(e)

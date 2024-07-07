from _main_.utils.massenergize_logger import log
from _main_.utils.massenergize_errors import CustomMassenergizeError, MassEnergizeAPIError
from _main_.utils.pagination import paginate
from api.store.community import CommunityStore
from _main_.utils.common import serialize, serialize_all
from _main_.utils.context import Context
from typing import Tuple

from api.utils.filter_functions import sort_items

class CommunityService:
  """
  Service Layer for all the communities
  """
  

  def __init__(self):
    self.store =  CommunityStore()

  def get_community_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    community, err = self.store.get_community_info(context, args)
    if err:
      return None, err

    return serialize(community, full=True), None

  def join_community(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    user, err = self.store.join_community(context, args)
    if err:
      return None, err

    #send an email to the community admin
    return serialize(user, full=True), None

  def leave_community(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    user, err = self.store.leave_community(context, args)
    if err:
      return None, err

    #send an email to the community admin
    return serialize(user, full=True), None

  def list_communities(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    communities, err = self.store.list_communities(context, args)
    if err:
      return None, err
    return serialize_all(communities, info=True), None


  def create_community(self,context, args) -> Tuple[dict, MassEnergizeAPIError]:
    community, err = self.store.create_community(context, args)
    if err:
      return None, err
    
    # send all emails
    return serialize(community), None


  def update_community(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    community, err = self.store.update_community(context ,args)
    if err:
      return None, err
    return serialize(community), None

  def delete_community(self, args,context) -> Tuple[dict, MassEnergizeAPIError]:
    community, err = self.store.delete_community(args,context)
    if err:
      return None, err
    return serialize_all(community), None


  def fetch_admins_of(self, args,context: Context) -> Tuple[list, MassEnergizeAPIError]:
    groups, err = self.store.fetch_admins_of(args,context)
    if err:
      return None, err
    # Concept here is that: We group all unique admins together for every community. 
    try:
      obj = {}
      for group in groups: 
        com = group.community.simple_json() 
        _id = com.get("id")
        found = obj.get(_id) or {}
        found["community"] = com
        old_members = found.get("members") or {}
        new_members = {str(m.id) : m.simple_json() for m in group.members.all()}
        members ={**old_members, **new_members}
        found["members"] = members 
        obj[_id] = found
      return obj, None
    except Exception as e: 
      log.error(e)
      return None,CustomMassenergizeError(e)
    # sorted = sort_items(communities, context.get_params())
    # return paginate(sorted, context.get_pagination_data()), None
  
  def list_other_communities_for_cadmin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    communities, err = self.store.list_other_communities_for_cadmin(context)
    if err:
      return None, err
    sorted = sort_items(communities, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None

  def list_communities_for_community_admin(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    communities, err = self.store.list_communities_for_community_admin(context, args)
    if err:
      return None, err
    sorted = sort_items(communities, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None


  def list_communities_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
    communities, err = self.store.list_communities_for_super_admin(context)
    if err:
      return None, err
    sorted = sort_items(communities, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None

  def add_custom_website(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
    communities, err = self.store.add_custom_website(context, args)
    if err:
      return None, err
    return serialize(communities), None

  def get_graphs(self, context) -> Tuple[list, MassEnergizeAPIError]:
    communities, err = self.store.list_communities_for_super_admin(context)
    if err:
      return None, err
    return communities, None

  def list_actions_completed(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    completed_actions_list, err = self.store.list_actions_completed(context, args)
    if err:
      return None, err
    return serialize_all(completed_actions_list), None
  
  def list_community_features(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    feature_flags, err = self.store.list_community_features(context, args)
    if err:
      return None, err
    return feature_flags, None
  
  def request_feature_for_community(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    feature_flag, err = self.store.request_feature_for_community(context, args)
    if err:
      return None, err
    return feature_flag, None
  
  def update_community_notification_settings(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    nudge_settings, err = self.store.update_community_notification_settings(context, args)
    if err:
      return None, err
    return nudge_settings, None

  def list_community_notification_settings(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
        nudge_settings, err = self.store.list_community_notification_settings(context, args)
        if err:
            return None, err
        return nudge_settings, None
  
  def list_communities_feature_flags(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    feature_flags, err = self.store.list_communities_feature_flags(context, args)
    if err:
      return None, err
    return feature_flags, None



from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.pagination import paginate
from api.store.community import CommunityStore
from _main_.utils.common import serialize, serialize_all
from _main_.utils.emailer.send_email import send_massenergize_rich_email
from _main_.utils.emailer.email_types import COMMUNITY_REGISTRATION_EMAIL
from _main_.utils.context import Context
from typing import Tuple

from api.utils.filter_functions import sort_items

class CommunityService:
  """
  Service Layer for all the communities
  """
  

  def __init__(self):
    self.store =  CommunityStore()

  def get_community_info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
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
    sorted = sort_items(communities, context.args.get("params"))
    return paginate(sorted, args.get('page', 1), args.get("limit")), None


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


  def list_other_communities_for_cadmin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    communities, err = self.store.list_other_communities_for_cadmin(context)
    if err:
      return None, err
    return serialize_all(communities), None

  def list_communities_for_community_admin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    communities, err = self.store.list_communities_for_community_admin(context)
    if err:
      return None, err
    sorted = sort_items(communities, context.args.get("params"))
    return paginate(sorted, context.args.get("page", 1), context.args.get("limit")), None


  def list_communities_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
    communities, err = self.store.list_communities_for_super_admin(context)
    if err:
      return None, err
    sorted = sort_items(communities, context.args.get("params"))
    return paginate(sorted, context.args.get("page", 1), context.args.get("limit")), None

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
    return paginate(completed_actions_list, args.get('page', 1), args.get("limit")), None



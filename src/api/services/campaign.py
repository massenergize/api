from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.common import serialize, serialize_all
from _main_.utils.pagination import paginate
from _main_.utils.context import Context
from api.store.campaign import CampaignStore
from api.utils.filter_functions import sort_items
from sentry_sdk import capture_message
from typing import Tuple

class CampaignService:
  """
  Service Layer for all the campaigns
  """

  def __init__(self):
    self.store =  CampaignStore()

  def get_campaign_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    campaign, err = self.store.get_Campaign_info(context, args)
    if err:
      return None, err
    return serialize(campaign, full=True), None

  def list_campaigns(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    campaigns, err = self.store.list_campaigns(context, args)
    if err:
      return None, err
    return serialize_all(campaigns), None


  def create_campaign(self, context: Context, args, user_submitted=False) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      campaign, err = self.store.create_campaign(context, args, user_submitted)
      if err:
        return None, err
      return serialize(campaign), None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def update_campaign(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    campaign, err = self.store.update_campaigns(context, args)
    if err:
      return None, err
    return serialize(campaign), None


  def delete_campaign(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    campaign, err = self.store.delete_campaign(context, args)
    if err:
      return None, err
    return serialize(campaign), None


  def list_campaigns_for_admins(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    campaigns, err = self.store.list_campaigns_for_admins(context, args)
    if err:
      return None, err
    sorted = sort_items(campaigns, context.get_params())
    return paginate(sorted, context.get_pagination_data()), None
  


  def add_campaign_manager(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.add_campaign_manager(context, args)
    if err:
      return None, err
    return serialize(res, full=True), None


  def remove_campaign_manager(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    campaign_manager, err = self.store.remove_campaign_manager(context, args)
    if err:
      return None, err
    return serialize(campaign_manager, full=True), None


  def add_campaign_community(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.add_campaign_community(context, args)
    if err:
      return None, err
    return serialize(res, full=True), None


  def remove_campaign_community(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.remove_campaign_community(context, args)
    if err:
      return None, err
    return serialize(res, full=True), None
  

  def add_campaign_technology(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.add_campaign_technology(context, args)
    if err:
      return None, err
    return serialize(res, full=True), None


  def remove_campaign_technology(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.remove_campaign_technology(context, args)
    if err:
      return None, err
    return serialize(res, full=True), None

  def create_campaign_technology_testimonial(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.create_campaign_technology_testimonial(context, args)
    if err:
      return None, err
    return serialize(res, full=True), None

  def update_campaign_technology_testimonial(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.update_campaign_technology_testimonial(context, args)
    if err:
      return None, err
    return serialize(res, full=True), None
  

  def create_campaign_technology_comment(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.create_campaign_technology_comment(context, args)
    if err:
      return None, err
    return serialize(res, full=True), None

  def update_campaign_technology_comment(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.update_campaign_technology_comment(context, args)
    if err:
      return None, err
    return serialize(res, full=True), None
  

  def list_campaign_technology_comments(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.list_campaign_technology_comments(context, args)
    if err:
      return None, err
    return serialize_all(res), None
  

  def list_campaign_technology_testimonials(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.list_campaign_technology_testimonials(context, args)
    if err:
      return None, err
    return serialize_all(res), None
  

  def list_campaign_managers(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.list_campaign_managers(context, args)
    if err:
      return None, err
    return serialize_all(res), None
  

  def list_campaign_communities(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.list_campaign_communities(context, args)
    if err:
      return None, err
    return serialize_all(res), None
  

  def list_campaign_technologies(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    res, err = self.store.list_campaign_technologies(context, args)
    if err:
      return None, err
    return serialize_all(res), None


  def list_campaign_events(self, context, args) -> Tuple[list, MassEnergizeAPIError]:
      res, err = self.store.list_campaign_events(context)
      if err:
        return None, err
      return serialize_all(res), None
  

  def add_campaign_partners(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
      res, err = self.store.add_campaign_partners(context, args)
      if err:
        return None, err
      return serialize(res, full=True), None
  

  def remove_campaign_partners(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
      res, err = self.store.remove_campaign_partners(context, args)
      if err:
        return None, err
      return serialize(res, full=True), None
  

  def add_campaign_event(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
      res, err = self.store.add_campaign_event(context, args)
      if err:
        return None, err
      return serialize(res, full=True), None
  

  def remove_campaign_event(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
      res, err = self.store.remove_campaign_event(context, args)
      if err:
        return None, err
      return serialize(res, full=True), None

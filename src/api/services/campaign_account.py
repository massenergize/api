from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from api.store.campaign_account import CampaignAccountStore
from typing import Tuple

class CampaignAccountService:
  """
  Service Layer for all the campaigns
  """

  def __init__(self):
    self.store =  CampaignAccountStore()


  def create_campaign_account(self, context, args)-> Tuple[dict, MassEnergizeAPIError]:
    res, err = self.store.create_campaign_account(context, args)
    if err:
      return None, err
    
    return serialize(res, full=True), None
  

  def update_campaign_account(self, context, args)-> Tuple[dict, MassEnergizeAPIError]:
    res, err = self.store.update_campaign_account(context, args)
    if err:
      return None, err
    
    return serialize(res, full=True), None
  
  def delete_campaign_account(self, context, args)-> Tuple[dict, MassEnergizeAPIError]:
    res, err = self.store.delete_campaign_account(context, args)
    if err:
      return None, err
    
    return serialize(res, full=True), None
  
  def list_campaign_accounts_for_admins(self, context, args)-> Tuple[dict, MassEnergizeAPIError]:
    res, err = self.store.list_campaign_accounts_for_admins(context, args)
    if err:
      return None, err
    
    return serialize_all(res, full=True), None
  

  def info(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign_account, err = self.store.get_campaign_account_info(context, args)
        if err:
            return None, err
        
        return serialize(campaign_account, full=True), None
  

  def add_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign_account, err = self.store.add_admin_to_campaign_account(context, args)
        if err:
            return None, err
        return serialize(campaign_account, full=True), None
  

  def remove_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign_account, err = self.store.remove_admin_from_campaign_account(context, args)
        if err:
            return None, err
        return serialize(campaign_account, full=True), None
  
  def update_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
        campaign_account, err = self.store.update_admin(context, args)
        if err:
            return None, err
        return serialize(campaign_account, full=True), None
     

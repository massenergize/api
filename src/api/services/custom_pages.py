from typing import Tuple
from _main_.utils.common import serialize, serialize_all
from _main_.utils.context import Context
from _main_.utils.massenergize_errors import MassEnergizeAPIError
from api.store.custom_pages import CustomPagesStore


class CustomPagesService:
  """
  Service Layer for all the custom pages
  """
  

  def __init__(self):
    self.store =  CustomPagesStore()

  def create_community_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      page, err = self.store.create_community_custom_page(context, args)
      if err:
        return None, err
      
      return serialize(page), None
    except Exception as e:
      return None, MassEnergizeAPIError(str(e))
  
  def update_community_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]: 
    try:
      page, err = self.store.update_community_custom_page(context, args)
      if err:
        return None, err
      return serialize(page), None
    except Exception as e:
      return None, MassEnergizeAPIError(str(e))
  
  def delete_community_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:

      page, err = self.store.delete_community_custom_page(context, args)

      if err:
        return None, err
      return serialize(page), None
    except Exception as e:
      return None, MassEnergizeAPIError(str(e))

  def list_community_custom_pages(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      pages, err = self.store.list_community_custom_pages(context, args)
      if err:
        return None, err
      return serialize_all(pages), None
    except Exception as e:
      return None, MassEnergizeAPIError(str(e))


  def community_custom_page_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:

        page, err = self.store.community_custom_page_info(context, args)
        if err:
          return None, err
        return serialize(page), None
    except Exception as e:
        return None, MassEnergizeAPIError(str(e))
    

  def share_community_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
        page, err = self.store.share_community_custom_page(context, args)
        if err:
          return None, err
        return serialize(page), None
    except Exception as e:
        return None, MassEnergizeAPIError(str(e))
    
    
  def publish_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
        page, err = self.store.publish_custom_page(context, args)
        if err:
          return None, err
        return serialize(page), None
    except Exception as e:
        return None, MassEnergizeAPIError(str(e))
    
  def get_custom_pages_for_user_portal(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
        page, err = self.store.get_custom_pages_for_user_portal(context, args)
        if err:
          return None, err
        return page, None
    except Exception as e:
        return None, MassEnergizeAPIError(str(e))
    
  
  def list_custom_pages_from_other_communities(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
        pages, err = self.store.list_custom_pages_from_other_communities(context, args)
        if err:
          return None, err
        return serialize_all(pages), None
    except Exception as e:
        return None, MassEnergizeAPIError(str(e))
    
  def copy_custom_page(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
        page, err = self.store.copy_custom_page(context, args)
        if err:
          return None , err
        return serialize(page), None
    except Exception as e:
        return None, MassEnergizeAPIError(str(e))



  
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
      page_id = args.pop('page_id', None)
      if not page_id:
        return None, MassEnergizeAPIError("Missing page_id")
      page, err = self.store.delete_community_custom_page(context, page_id)
      if err:
        return None, err
      return serialize(page), None
    except Exception as e:
      return None, MassEnergizeAPIError(str(e))

  def list_community_custom_pages(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      pages, err = self.store.list_community_custom_pages(context, args)
      if err:
        return None
      return serialize_all(pages), None
    except Exception as e:
      return None, MassEnergizeAPIError(str(e))


  def community_custom_page_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
        page_id = args.pop('page_id', None)
        if not page_id:
          return None, MassEnergizeAPIError("Missing page_id")
        page, err = self.store.community_custom_page_info(context, page_id)
        if err:
          return None, err
        return serialize(page), None
    except Exception as e:
        return None, MassEnergizeAPIError(str(e))

  
  def create_custom_page_block(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
        block, err = self.store.create_custom_page_block(context, args)
        if err:
          return None, err
        return serialize(block), None
    except Exception as e:
        return None, MassEnergizeAPIError(str(e))
    

  def update_custom_page_block(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
        block, err = self.store.update_custom_page_block(context, args)
        if err:
          return None, err
        return serialize(block), None
    except Exception as e:
        return None, MassEnergizeAPIError(str(e))

  def delete_custom_page_block(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    try:
      block_id = args.pop('block_id', None)
      if not block_id:
        return None, MassEnergizeAPIError("Missing block_id")
      block, err = self.store.delete_custom_page_block(context, block_id)
      if err:
        return None, err
      return serialize(block), None
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



  